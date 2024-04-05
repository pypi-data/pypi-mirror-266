import json
from datetime import datetime
from typing import List

from email_message_aws_ses_local.ses_email import EmailMessageAwsSesLocal
from label_message_local.LabelConstants import MESSAGE_OUTBOX_LABEL_ID
from label_message_local.LabelMessage import LabelsMessageLocal
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.MetaLogger import MetaLogger
from message_local.ChannelProviderConstants import (
    AWS_SES_EMAIL_MESSAGE_PROVIDER_ID, AWS_SNS_SMS_MESSAGE_PROVIDER_ID,
    INFORU_MESSAGE_PROVIDER_ID, VONAGE_MESSAGE_PROVIDER_ID)
from message_local.MessageChannels import MessageChannel
from message_local.MessageImportance import MessageImportance
from message_local.MessageLocal import MessageLocal
from message_local.Recipient import Recipient
from queue_worker_local.queue_worker import QueueWorker
from sms_message_aws_sns_local.sms_message_aws_sns import SmsMessageAwsSnsLocal
from whataspp_inforu_local.WhatsAppMessageInforuLocal import WhatsAppMessageInforuLocal
from whatsapp_message_vonage_local.vonage_whatsapp_message_local import WhatsAppMessageVonageLocal

# Relative imports makes the worker confused, so we are not using constants.py
# TODO Replace Magic Number with enum in a separate file in this repo which will be created by Sql2Code in the future
MESSAGES_API_TYPE_ID = 5
MESSAGE_LOCAL_PYTHON_COMPONENT_ID = 259
MESSAGE_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME = 'messages-local-python-package'
DEVELOPER_EMAIL = 'akiva.s@circ.zone'

logger_object_message = {
    'component_id': MESSAGE_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': MESSAGE_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}


class MessagesLocal(metaclass=MetaLogger, object=logger_object_message):
    # no classes type, so the worker can init it with json.
    def __init__(self, default_original_body: str = None, default_subject: str = None,
                 default_importance: int = MessageImportance.MEDIUM.value, recipients: List[dict] = None):
        self.recipients = recipients

        self.default_original_body = default_original_body
        self.default_subject = default_subject
        self.default_importance = default_importance
        self.label_crud = LabelsMessageLocal()
        self.queue_worker = QueueWorker(schema_name="message", table_name="message_table",
                                        view_name="message_outbox_view", id_column_name="message_id")

    # This method should be used by Queue Worker
    # Make sure send_sync has all the parameters in the function_parameters_json below
    def send_sync(self, message_id: int, campaign_id: int,
                  recipients: List[dict] = None,
                  cc_recipients: List[dict] = None,
                  bcc_recipients: List[dict] = None,
                  request_datetime: str = None,
                  # TODO What is exactly the operational meaning of start_timestamp?
                  #  There is start_timestamp, when the message can be sent?
                  start_timestamp: datetime = datetime.now(),
                  importance: int = None,
                  requested_message_type: int = None,
                  sender_profile_id: int = None) -> None:
        """send method"""
        details = {
            "message_id": message_id,
            "campaign_id": campaign_id,
            "recipients": recipients,
            "request_datetime": request_datetime,
            "importance": importance,
            "requested_message_type": requested_message_type
        }

        recipients = Recipient.recipients_from_json(recipients or self.recipients)
        importance = MessageImportance(importance or self.default_importance)
        message_local = MessageLocal(message_id=message_id,
                                     original_body=self.default_original_body,
                                     original_subject=self.default_subject,
                                     campaign_id=campaign_id,
                                     recipients=recipients,
                                     importance=importance,
                                     api_type_id=MESSAGES_API_TYPE_ID,
                                     sender_profile_id=sender_profile_id)
        for recipient in recipients:
            init_kwargs = {}
            send_kwargs = {}

            message_recipient_channel = message_local.get_message_channel(recipient)
            message_recipient_provider_id = message_local.get_message_provider_id(message_recipient_channel, recipient)
            # profile_body_block = message_local.get_profile_block( recipient.get_profile_id(), message_recipient_channel, part="body")
            body = message_local.get_body_after_text_template(recipient, message_recipient_channel)
            if (message_recipient_channel == MessageChannel.SMS and
                    message_recipient_provider_id == AWS_SNS_SMS_MESSAGE_PROVIDER_ID):
                message_local.__class__ = SmsMessageAwsSnsLocal

            elif message_recipient_channel == MessageChannel.WHATSAPP:
                if message_recipient_provider_id == INFORU_MESSAGE_PROVIDER_ID:
                    message_local.__class__ = WhatsAppMessageInforuLocal
                elif message_recipient_provider_id == VONAGE_MESSAGE_PROVIDER_ID:
                    message_local.__class__ = WhatsAppMessageVonageLocal
                else:
                    raise Exception("Don't know which WhatsAppMessageLocal class to use "
                                    f"(provider_id: {message_recipient_provider_id})")
            elif (message_recipient_channel == MessageChannel.EMAIL and
                  message_recipient_provider_id == AWS_SES_EMAIL_MESSAGE_PROVIDER_ID):
                # Parameters to the function we call???
                init_kwargs = {"subject": message_local.get_profile_block(
                    recipient.get_profile_id(), message_recipient_channel, part="subject").get("processedTemplate")}
                message_local.__class__ = EmailMessageAwsSesLocal

            else:
                # TODO We need to add to the message Recipient country, message plain text length after template,
                #  message HTML length after template, number of attachments, attachments' types and sizes.
                compound_message_dict = message_local.get_compound_message_dict()
                data_json = {"channel_id": message_recipient_channel,
                             "provider_id": message_recipient_provider_id,
                             "recipient": recipient,
                             "compound_message_dict": compound_message_dict,
                             "compound_message_length": len(compound_message_dict),
                             "importance": importance,
                             "campaign_id": campaign_id
                             }
                error_message = "Don't know which MessageLocal class to use." + " Data: " + str(data_json)
                # data_json will be printed anyway, as the meta logger prints the object & local variables
                raise Exception(error_message)

            message_local.__init__(**init_kwargs)  # noqa, calling the son's init
            # TODO: should we send multiple recipients outside this loop?
            message_local.send(
                body=body,
                recipients=[recipient],
                compound_message_dict=message_local.get_compound_message_dict(message_recipient_channel),
                **send_kwargs)

    # This method will push the messages to the queue in message_outbox_table
    def send_scheduled(self, campaign_id: int, action_id: int,
                       recipients: List[Recipient] = None,
                       cc_recipients: List[Recipient] = None,
                       bcc_recipients: List[Recipient] = None,
                       request_datetime: datetime = None,
                       importance: MessageImportance = None,
                       requested_message_type: MessageChannel = None,
                       start_timestamp: datetime = datetime.now(),
                       sender_profile_id: int = None) -> list[int]:
        """The message will be sent any time between start_timestamp and end_timestamp
        For every bcc_recipient, a message will be pushed to the queue with the same parameters
        (message_id per bcc_recipient, or one if none provided)
        """
        importance = importance or MessageImportance(self.default_importance)
        message_ids = []
        for bcc_recipient in bcc_recipients or [None]:
            function_parameters_json = {
                # Make sure send_sync accepts all these parameters + message_id
                "campaign_id": campaign_id,
                "recipients": Recipient.recipients_to_json(recipients),
                "cc_recipients": Recipient.recipients_to_json(cc_recipients),
                "bcc_recipients": bcc_recipient.to_json() if bcc_recipient else None,
                "request_datetime": str(request_datetime),
                "importance": importance.value,
                "requested_message_type": requested_message_type.value if requested_message_type else None,
                "start_timestamp": str(start_timestamp),
                "sender_profile_id": sender_profile_id
            }

            # Make sure MessagesLocal.__init__ accepts all these parameters
            class_parameters_json = {"default_original_body": self.default_original_body,
                                     "default_subject": self.default_subject,
                                     "default_importance": self.default_importance,
                                     "recipients": self.recipients
                                     }

            message_id = self.queue_worker.push({"function_parameters_json": function_parameters_json,
                                                 "class_parameters_json": class_parameters_json,
                                                 "action_id": action_id})
            function_parameters_json["message_id"] = message_id
            # update function_parameters_json in the queue
            self.queue_worker.update_by_id(id_column_value=message_id,
                                           data_json={"function_parameters_json": json.dumps(function_parameters_json)})
            try:
                self.label_crud.add_label_message(label_id=MESSAGE_OUTBOX_LABEL_ID, message_id=message_id)
            except Exception as e:
                self.logger.exception("Failed to add label to message", object=e)
            self.logger.info("Message pushed to the queue successfully", object={"message_id": message_id})
            message_ids.append(message_id)
        return message_ids
