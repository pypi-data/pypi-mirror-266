# TODO Please make sure every src file will have a test file i.e. CompoundMessage

import json
import random

from database_mysql_local.generic_crud import GenericCRUD
from logger_local.MetaLogger import MetaLogger
from profiles_local.profiles_local import ProfilesLocal
from user_context_remote.user_context import UserContext
from variable_local.template import ReplaceFieldsWithValues

from .MessageChannels import MessageChannel
from .MessageConstants import object_message
from .MessageTemplates import MessageTemplates
from .Recipient import Recipient

lang_code_cache = {}
JSON_VERSION = "240405"  # TODO: make it generic


class CompoundMessage(GenericCRUD, metaclass=MetaLogger, object=object_message):
    def __init__(self, campaign_id: int = None, message_template_id: int = None, body: str = None, subject: str = None,
                 recipients: list[Recipient] = None, message_id: int = None, is_test_data: bool = False, ui_schema=None,
                 schema=None, field_id=None, form_id: int = None):
        self.user_context = UserContext()
        super().__init__(default_schema_name="message", default_table_name="message_table",
                         default_view_table_name="message_sent_view", default_id_column_name="message_id",
                         is_test_data=is_test_data)

        self.campaign_id = campaign_id
        self.message_template_id = message_template_id
        self.body = body
        self.subject = subject
        self.recipients = recipients
        self.message_id = message_id
        self.form_id = form_id
        self.__compound_message = {}
        self.ui_schema = ui_schema
        self.schema = schema
        self.field_id = field_id
        self.profile_local = ProfilesLocal()
        self.message_template = MessageTemplates()
        self.set_compound_message_after_text_template()

    def _get_template_ids_by_campaign(self, campaign_id: int) -> list[int]:
        """Returns a random template id from the campaign"""

        possible_template_ids = self.select_multi_tuple_by_id(
            schema_name="campaign", view_table_name="campaign_view",
            id_column_name="campaign_id", id_column_value=campaign_id,
            select_clause_value="message_template_id")

        return [message_template_id[0] for message_template_id in possible_template_ids]

    # TODO: {
    #   "json_version": ...,
    #   "data": {
    #     "formId": ...,
    #     "formName": ...,
    #     "messageTemplates": [
    #     {
    #         "messageTemplateId": ...,
    #         "compoundMessages": [...]
    def set_compound_message_after_text_template(
            self, campaign_id: int = None, message_template_id: int = None, body: str = None, subject: str = None,
            recipients: list[Recipient] = None, message_id: int = None, form_id: int = None) -> None:
        """ Sets the compound message in the instance and in the database using the following structure:"""

        #     {
        #         # "compoundMessageId": ...,
        #         "DEFAULT": {
        #             "bodyBlocks": [
        #                 {
        #                     "messageTemplateTextBlockId": ...,
        #                     "blockTypeId": ...,
        #                     "messageTemplateId": ...,
        #                     "messageTemplateBlockTypeName": ...,
        #                     "questionTitle": ...,
        #                     "questionTypeName": ...,
        #                     "questionId": ...,
        #                     "questionTypeId": ...,
        #                     "answerExpirationDays": ...,
        #                     "tableId": ...,
        #                     "variableId": ...,
        #                     "whereStatement": ...,
        #                     "isVisible": ...,
        #                     "isRequired": ...,
        #                     "defaultValue": ...,
        #                     "labelQuestionId": ...,
        #                     "template": ...,
        #                     "hint": ...,
        #                     "profileBlocks": [
        #                         {"profileId": ..., "processedTemplate": ...},
        #                         {"profileId": ..., "processedTemplate": ...},
        #                     ]
        #                 },
        #                 {"messageTemplateTextBlockId": ...}
        #             ],
        #             "subjectBlock": {"messageTemplateTextBlockId": ...}  # same structure as one bodyBlock
        #         },
        #         "EMAIL": {"bodyBlocks": [...], "subjectBlock": {...}},  # same structure as DEFAULT
        #         "SMS": {},
        #         "WHATSAPP": {},
        #         ...
        #     }

        # Allow overiding instance vars
        campaign_id = campaign_id or self.campaign_id
        message_template_id = message_template_id or self.message_template_id
        body = body or self.body
        subject = subject or self.subject
        recipients = recipients or self.recipients or []
        message_id = message_id or self.message_id
        form_id = form_id or self.form_id

        data = {"DEFAULT": {"bodyBlocks": [], "subjectBlock": {}, "formId": form_id}}

        channels_mapping = {
            MessageChannel.EMAIL.name: {"body": "email_body_html_template", "subject": "email_subject_template"},
            "DEFAULT": {"body": "default_body_template", "subject": "default_subject_template"},
        }
        for channel in MessageChannel:
            data[channel.name] = {"bodyBlocks": [], "subjectBlock": {}, "formId": form_id}
            if channel.name not in channels_mapping:
                channels_mapping[channel.name] = {"body": f"{channel.name.lower()}_body_template",
                                                  "subject": f"{channel.name.lower()}_subject_template"}

        if body:
            textblocks_and_attributes = [{}]  # one textblock
            for message_channel, template_header in channels_mapping.items():
                textblocks_and_attributes[0][template_header["body"]] = body
                textblocks_and_attributes[0][template_header["subject"]] = subject

        else:  # If body is not given, get it from the database
            # if form_id:
            #     textblocks_and_attributes = self.message_template.get_textblocks_and_attributes_by_form_id(form_id=form_id)
            # else:
            textblocks_and_attributes = self.message_template.get_textblocks_and_attributes()

        if campaign_id and not message_template_id:
            possible_template_ids = self._get_template_ids_by_campaign(campaign_id=campaign_id)
            message_template_id = random.choice(possible_template_ids)
            self.logger.info(object={"message_template_id": message_template_id})

        criteria_json = self.message_template.get_critiria_json(message_template_id=message_template_id)
        potentials_recipients = self.message_template.get_potentials_recipients(
            criteria_json, recipients)
        self.logger.info(object={"textblocks_and_attributes": textblocks_and_attributes,
                                 "criteria_json": criteria_json})

        for message_template_textblock_and_attributes in textblocks_and_attributes:
            for message_channel, template_header in channels_mapping.items():
                for part in ("body", "subject"):
                    templates = [x for x in (message_template_textblock_and_attributes.get(template_header[part]),
                                             message_template_textblock_and_attributes.get("questionTitle"))
                                 if x]

                    message_template = " ".join(templates)
                    if not message_template:
                        self.logger.warning("message_template is empty", object={
                            "message_template_textblock_and_attributes": message_template_textblock_and_attributes})
                        continue

                    block = {
                        "messageTemplateTextBlockId": message_template_textblock_and_attributes.get("messageTemplateTextBlockId"),
                        "blockTypeId": message_template_textblock_and_attributes.get("blockTypeId"),
                        "messageTemplateId": message_template_textblock_and_attributes.get("messageTemplateId"),
                        "messageTemplateBlockTypeName": message_template_textblock_and_attributes.get(
                            "messageTemplateBlockTypeName"),
                        "template": message_template,
                        "questionTitle": message_template_textblock_and_attributes.get("questionTitle"),
                        "questionTypeName": message_template_textblock_and_attributes.get("questionTypeName"),
                        "schemaDefault": message_template_textblock_and_attributes.get("schemaDefault"),
                        "uiSchemaDefault": message_template_textblock_and_attributes.get("uiSchemaDefault"),
                        "schemaAttributes": message_template_textblock_and_attributes.get("schemaAttributes"),
                        "uiSchemaAttributes": message_template_textblock_and_attributes.get("uiSchemaAttributes"),
                        "messageTemplateName": message_template_textblock_and_attributes.get("messageTemplateName"),
                        "messageTemplateTextBlockSeq": message_template_textblock_and_attributes.get(
                            "messageTemplateTextBlockSeq"),
                        "variableName": message_template_textblock_and_attributes.get("variableName"),
                        "variableMlTitle": message_template_textblock_and_attributes.get("variableMlTitle"),
                        "fieldName": message_template_textblock_and_attributes.get("fieldName"),

                        # from question_view:
                        "questionId": message_template_textblock_and_attributes.get("questionId"),
                        "questionTypeId": message_template_textblock_and_attributes.get("questionTypeId"),
                        "possibleAnswers": message_template_textblock_and_attributes.get("possibleAnswers"),
                        "answerExpirationDays": message_template_textblock_and_attributes.get("answerExpirationDays"),
                        "tableId": message_template_textblock_and_attributes.get("tableId"),
                        "variableId": message_template_textblock_and_attributes.get("variableId"),
                        "whereStatement": message_template_textblock_and_attributes.get("whereStatement"),
                        "isVisible": message_template_textblock_and_attributes.get("isVisible"),
                        "isRequired": message_template_textblock_and_attributes.get("isRequired"),
                        "defaultValue": message_template_textblock_and_attributes.get("defaultValue"),
                        "labelQuestionId": message_template_textblock_and_attributes.get("labelQuestionId"),
                        "hint": message_template_textblock_and_attributes.get("hint"),
                        "profileBlocks": []
                    }

                    for recipient in recipients:
                        if recipient.get_profile_id() not in lang_code_cache:
                            lang_code_cache[
                                recipient.get_profile_id()] = self.profile_local.get_preferred_lang_code_by_profile_id(
                                recipient.get_profile_id()).value
                        # TODO: The test critiria doesn't match the recipient
                        if 1 or (any(recipient.get_profile_id() == potential_recipient["profile_id"]
                                     for potential_recipient in potentials_recipients)
                                 # TODO recipient_preferred_lang_code_str
                                 and (lang_code_cache[recipient.get_profile_id()] ==
                                      message_template_textblock_and_attributes.get("langCode"))):
                            block["profileBlocks"].append(
                                # each profile has its own template, because of the language
                                {"profileId": recipient.get_profile_id(),
                                 "processedTemplate": self._process_text_block(message_template, recipient=recipient),
                                 })
                    if part == "subject":
                        # ignore if already set
                        data[message_channel]["subjectBlock"] = data[message_channel]["subjectBlock"] or block
                    else:
                        data[message_channel][f"{part}Blocks"].append(block)

        # remove empty channels:
        data = {k: v for k, v in data.items() if v["bodyBlocks"] or v["subjectBlock"]}

        compound_message = {"json_version": JSON_VERSION, "data": data}
        # save in message table
        if message_id:
            self.update_by_id(id_column_value=message_id,
                              data_json={"compound_message_json": json.dumps(compound_message),
                                         "compound_message": json.dumps(compound_message),
                                         "compound_message_json_version": JSON_VERSION})
        else:
            self.message_id = self.insert(data_json={"compound_message_json": json.dumps(compound_message),
                                                     "compound_message": json.dumps(compound_message),
                                                     "compound_message_json_version": JSON_VERSION})

        self.__compound_message = compound_message
        self.logger.debug(object=locals())

    def _process_text_block(self, text_block_body: str, recipient: Recipient) -> str:
        template = ReplaceFieldsWithValues(message=text_block_body,
                                           # TODO language -> lang_code_str ?
                                           language=recipient.get_preferred_lang_code_str(),
                                           variable=recipient.get_profile_variables())
        processed_text_block = template.get_variable_values_and_chosen_option(
            profile_id=self.user_context.get_effective_profile_id(),
            # TODO profile_id -> effective_profile_id
            kwargs={"recipient.first_name": recipient.get_first_name(),
                    # TODO: effective -> real in user_context
                    "sender.first_name": self.user_context.get_real_first_name(),
                    "message_id": self.message_id
                    })
        return processed_text_block

    def get_compound_message_dict(self, channel: MessageChannel = None) -> dict:
        if channel is None:
            return self.__compound_message["data"]
        else:
            return {"DEFAULT": self.__compound_message["data"]["DEFAULT"],
                    channel.name: self.__compound_message["data"].get(channel.name, {})}

    def get_compound_message_str(self, channel: MessageChannel = None) -> str:
        return json.dumps(self.get_compound_message_dict(channel=channel))

    def get_profile_block(self, profile_id: int, channel: MessageChannel, part: str = "body") -> dict:
        """Returns a dict with the following keys:
        profileId, template, processedTemplate, messageTemplateTextBlockId, blockTypeId, messageTemplateBlockTypeName, questionId,
            questionTypeId, questionTitle, questionTypeName
        """

        assert part in ("body", "subject")
        if part == "body":
            blocks = self.__compound_message["data"].get(channel.name, {}).get("bodyBlocks", [])
        else:
            blocks = [self.__compound_message["data"].get(channel.name, {}).get("subjectBlock", {})]
        for block in blocks:
            for _profile_block in block.get("profileBlocks", []):
                if _profile_block.get("profileId") == profile_id:
                    return {**_profile_block, **{k: v for k, v in block.items() if k != "profileBlocks"}}
        return {}

    def get_message_fields(self) -> dict:
        if self.recipients:
            recipients_mapping = {recipient.get_profile_id(): recipient.to_json() for recipient in self.recipients}
        else:
            recipients_mapping = {}
        return {
            "campaign_id": self.campaign_id,
            "body": self.body,
            "subject": self.subject,
            "message_id": self.message_id,
            "ui_schema": self.ui_schema,
            "schema": self.schema,
            "field_id": self.field_id,
            "recipients": recipients_mapping,
            "json_version": JSON_VERSION,
        }
