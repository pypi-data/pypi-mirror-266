from datetime import datetime, UTC
from abc import ABC
from typing import Optional, List
import logging as log
from lgt_jobs.lgt_common.slack_client.web_client import SlackWebClient, SlackMessageConvertService
from lgt_jobs.lgt_data.helpers import get_help_text
from lgt_jobs.lgt_data.model import ChatMessage, UserModel, UserContact, DedicatedBotModel
from lgt_jobs.lgt_data.mongo_repository import UserMongoRepository, DedicatedBotRepository, UserContactsRepository, \
    ChatRepository
from pydantic import BaseModel
from lgt_jobs.lgt_data.enums import SourceType, ImageName
from lgt_jobs.runner import BaseBackgroundJob, BaseBackgroundJobData, BackgroundJobRunner
from lgt_jobs.env import portal_url
from lgt_jobs.smtp import SendMailJobData, SendMailJob

"""
Load slack chat history
"""


class LoadChatHistoryJobData(BaseBackgroundJobData, BaseModel):
    user_id: str
    template_path: str = 'lgt_jobs/templates/new_message.html'


class LoadChatHistoryJob(BaseBackgroundJob, ABC):
    chat_repo = ChatRepository()
    contacts_repo = UserContactsRepository()

    @property
    def job_data_type(self) -> type:
        return LoadChatHistoryJobData

    def exec(self, data: LoadChatHistoryJobData):
        user = UserMongoRepository().get(data.user_id)
        if user.subscription_expired_at.replace(tzinfo=UTC) < datetime.now(UTC):
            log.info(f"[LoadChatHistoryJob]: {user.email} has expired subscription")
            return
        bots = DedicatedBotRepository().get_all(only_valid=True, user_id=user.id, source_type=SourceType.SLACK)
        if not bots:
            return
        last_message = None
        last_message_contact = None
        last_message_bot = None
        contacts_groups = self.contacts_repo.find_grouped_actual_contacts(user.id, spam=False, with_chat_only=False)
        for bot in bots:
            contacts = contacts_groups.get(bot.source.source_id)
            if not contacts:
                continue

            log.info(f"[LoadChatHistoryJob]: processing {len(contacts)} contacts for user: {user.email}")
            for contact in contacts:
                message = self._update_history(user=user, contact=contact, bot=bot)

                if not message:
                    continue

                if not last_message:
                    last_message_bot = bot
                    last_message = message
                    last_message_contact = contact

                if message.created_at > last_message.created_at and message.user == contact.sender_id:
                    last_message_bot = bot
                    last_message = message
                    last_message_contact = contact

        has_to_be_notified = (not user.new_message_notified_at or
                              (last_message and last_message.created_at > user.new_message_notified_at))

        if last_message and has_to_be_notified and last_message.user == last_message_contact.sender_id:
            LoadChatHistoryJob._notify_about_new_messages(user, last_message_contact, last_message_bot,
                                                          data.template_path)
            UserMongoRepository().set(data.user_id, new_message_notified_at=datetime.now(UTC))

    def _get_new_messages(self, contact: UserContact, bot: DedicatedBotModel, slack_chat: List[ChatMessage]):
        messages = self.chat_repo.get_list(sender_id=contact.sender_id, bot_id=bot.id)
        new_messages = []
        for message in slack_chat:
            same_messages = [msg for msg in messages if msg.id == message.id]
            if not same_messages:
                new_messages.append(message)
        return new_messages

    def _update_history(self, user: UserModel, contact: UserContact, bot: DedicatedBotModel) -> Optional[ChatMessage]:
        slack_client = SlackWebClient(bot.token, bot.cookies)
        try:
            chat_id = slack_client.im_open(contact.sender_id).get('channel', {}).get('id')
            history = slack_client.chat_history(chat_id)
        except Exception as ex:
            log.error(f'[LoadChatHistoryJob]: Failed to load chat for the contact: {contact.id}. ERROR: {str(ex)}')
            return

        if not history['ok']:
            log.error(f'[LoadChatHistoryJob]: Failed to load chat for the contact: {contact.id}. '
                      f'ERROR: {history.get("error", "")}')
            return

        messages = history.get('messages', [])
        if not messages:
            return None

        messages = [SlackMessageConvertService.from_slack_response(user.email, "slack_files",
                                                                   bot.token, m, contact.sender_id, bot.id,
                                                                   user.id, bot.cookies) for m in messages]
        new_messages = self._get_new_messages(contact, bot, messages)
        chat_history = [message.to_dic() for message in new_messages]
        self.chat_repo.upsert_messages(chat_history)
        if bot.associated_user != contact.sender_id and new_messages:
            log.info(f'[LoadChatHistoryJob]: New message. Sender id: {contact.sender_id}, bot id: {bot.id}')
            self.contacts_repo.update(contact.user_id, contact.sender_id, contact.source_id,
                                      last_message_at=datetime.now(UTC))
            return new_messages[-1]

        return None

    @staticmethod
    def _notify_about_new_messages(user: UserModel, contact: UserContact, bot: DedicatedBotModel, template_path: str):
        with open(template_path, mode='r') as template_file:
            html = template_file.read()
            chat_url = f'{portal_url}/feed?senderId={contact.sender_id}&sourceId={bot.source.source_id}'
            html = html.replace("$$USER_NAME$$", contact.name if hasattr(contact, 'name') else contact.real_name)
            html = html.replace("$$PORTAL_LINK$$", chat_url)
            html = html.replace("$$HELP_TEXT$$", get_help_text(user))
            message_data = {
                "html": html,
                "subject": 'New message(s) on Leadguru',
                "recipient": user.email,
                "images": [ImageName.LOGO, ImageName.ARROW, ImageName.MAIL]
            }

        BackgroundJobRunner.submit(SendMailJob, SendMailJobData(**message_data))
