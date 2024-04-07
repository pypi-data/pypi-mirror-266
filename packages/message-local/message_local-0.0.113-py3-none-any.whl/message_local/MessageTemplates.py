from database_mysql_local.generic_crud_ml import GenericCRUDML
from logger_local.MetaLogger import MetaLogger

from .MessageConstants import object_message
from .Recipient import Recipient

cache = {}


class MessageTemplates(GenericCRUDML, metaclass=MetaLogger, object=object_message):
    def __init__(self):
        super().__init__(default_schema_name="field", default_table_name="field_table")

    def get_potentials_recipients(self, criteria_json: dict, recipients: list[Recipient] = None) -> list[dict]:
        where = self.get_where_by_criteria_json(criteria_json)
        if recipients:
            profile_ids_str = ",".join(str(recipient.get_profile_id()) for recipient in recipients)
            where += f" AND user.profile_id IN ({profile_ids_str})"
        query_for_potentials_recipients = f"""
SELECT DISTINCT user_id, person_id, user_main_email_address, user.profile_id AS profile_id, 
   profile_phone_full_number_normalized, profile_preferred_lang_code
 FROM user.user_general_view AS user
    JOIN group_profile.group_profile_view AS group_profile on group_profile.profile_id = user.profile_id
  WHERE {where} 
"""
        columns = ("user_id, person_id, user_main_email_address, profile_id,"
                   "profile_phone_full_number_normalized, profile_preferred_lang_code")
        self.cursor.execute(query_for_potentials_recipients)
        return [self.convert_to_dict(row, columns) for row in self.cursor.fetchall()]

    def get_where_by_criteria_json(self, criteria_json: dict) -> str:
        # TODO add support to user_external_id in criteria_json
        min_age = criteria_json.get("min_age")
        max_age = criteria_json.get("max_age")
        gender_list_id = criteria_json.get("gender_list_id")
        group_list_id = criteria_json.get("group_list_id")
        self.logger.info(object={"min_age": min_age, "max_age": max_age, "gender_list_id": gender_list_id,
                                 "group_list_id": group_list_id})
        # profile_id didn't receive messages from this campaign for campaign.minimal_days
        where = "TRUE "
        if min_age is not None:
            where += f" AND TIMESTAMPDIFF(YEAR, person_birthday_date, CURDATE()) >= {min_age}"
        if max_age is not None:
            where += f" AND TIMESTAMPDIFF(YEAR, person_birthday_date, CURDATE()) <= {max_age}"

        if gender_list_id is not None:
            gender_cache_key = ("gender", gender_list_id)
            if gender_cache_key not in cache:
                profile_gender_id_list = self.sql_in_list_by_entity_list_id(
                    schema_name="gender", entity_name="gender", entity_list_id=gender_list_id)
                cache[gender_cache_key] = profile_gender_id_list
            else:
                profile_gender_id_list = cache[gender_cache_key]

            where += " AND profile_gender_id " + profile_gender_id_list

        if group_list_id is not None:
            group_cache_key = ("group", group_list_id)
            if group_cache_key not in cache:
                group_id_list = self.sql_in_list_by_entity_list_id(
                    schema_name="group", entity_name="group", entity_list_id=group_list_id)
                cache[group_cache_key] = group_id_list
            else:
                group_id_list = cache[group_cache_key]
            where += " AND group_profile.group_id " + group_id_list
        return where

    def get_critiria_json(self, message_template_id: int) -> dict:
        if message_template_id in cache:
            return cache[message_template_id]
        query = """
        SELECT DISTINCT min_age, max_age, gender_list_id, group_list_id
          FROM message_template.message_template_view
            JOIN message_template.message_template_message_template_text_block_view AS message_template_message_template_text_block
                ON message_template_message_template_text_block.message_template_id = message_template_view.message_template_id
            JOIN message_template.message_template_text_block_view AS message_template_text_block
                ON message_template_text_block.message_template_text_block_id = message_template_message_template_text_block.message_template_id
            JOIN criteria.criteria_view AS criteria
                ON criteria.criteria_id = message_template_text_block.criteria_id
          WHERE message_template_view.message_template_id = %s
          LIMIT 1  -- TODO: remove
          """  # noqa
        self.cursor.execute(query, (message_template_id,))

        columns = "min_age, max_age, gender_list_id, group_list_id"
        critiria_json = self.convert_to_dict(self.cursor.fetchone(), columns)
        cache[message_template_id] = critiria_json
        return critiria_json

    def get_textblocks_and_attributes_by_form_id(self, form_id: int) -> list[dict]:
        # TODO: get unique (field_id, question_id) from field view for a given field_id

        # TODO Can we format this query?
        # TODO query_by_form_id = ...
        query = """SELECT form_id AS formId, form_name AS formName, form_message_seq AS formMessageSeq,
        form_message_template_id AS formMessageTemplateId, message_template_id AS messageTemplateId,
        message_template_name AS messageTemplateName, message_template_text_block_seq AS messageTemplateTextBlockSeq,
        message_template_text_block_id AS messageTemplateTextBlockId, question_id AS questionId,
        question_title AS questionTitle, schema_attributes AS schemaAttributes, uischema_attributes AS uiSchemaAttributes,
        question_type_id AS questionTypeId, question_type_name AS questionTypeName, variable_name AS variableName,
        variable_ml_title AS variableMlTitle, field_name AS fieldName, possible_answer AS possibleAnswer
        FROM form.form_general_view WHERE form_id = %s"""
        columns = ("formId", "formName", "formMessageSeq", "formMessageTemplateId", "messageTemplateId",
                   "messageTemplateName", "messageTemplateTextBlockSeq", "messageTemplateTextBlockId",
                   "questionId", "questionTitle", "schemaAttributes", "uiSchemaAttributes", "questionTypeId",
                   "questionTypeName", "variableName", "variableMlTitle", "fieldName", "possibleAnswer")
        self.cursor.execute(query, (form_id,))
        return [self.convert_to_dict(row, ",".join(columns)) for row in self.cursor.fetchall()]

    def get_textblocks_and_attributes(self) -> list[dict]:
        """Returns the message template text block and attributes for the given message template id and profile id.
        The attributes are:
            - sms_body_template
            - email_subject_template
            - email_body_html_template
            - whatsapp_body_template
            ... TODO: add more attributes here

        The attributes are returned as a list of dictionaries, one dictionary
            for each text block in the message template.
        """

        if "get_textblocks_and_attributes" in cache:
            return cache["get_textblocks_and_attributes"]
        textblocks_and_attributes = []
        query = """
SELECT sms_body_template, email_subject_template, email_body_html_template, whatsapp_body_template,
        default_subject_template, default_body_template,
        question.question_id AS questionId, question.question_type_id AS questionTypeId,
        question.where_statement AS whereStatement, question.variable_id AS variableId, question.table_id AS tableId, 
        question.is_visible AS isVisible, question.is_required AS isRequired, question.label_question_id AS labelQuestionId,
        question.default_value AS defaultValue, question.answer_expiration_days AS answerExpirationDays,
        question_ml.title AS questionTitle, question_type.name AS questionTypeName,
        question_type.schema_attributes AS `schemaDefault`, question_type.uischema_attributes AS uiSchemaDefault,
        question.schema_attributes AS `schemaAttributes`, question.uischema_attributes AS uiSchemaAttributes,

        question_ml.lang_code AS langCode, question.hint AS hint,
        message_template_text_block.message_template_text_block_id AS messageTemplateTextBlockId,
        message_template_text_block_type_ml.title AS messageTemplateBlockTypeName,
        message_template_text_block_type_ml.message_template_text_block_type_id AS blockTypeId,
        message_template_message_template_text_block.message_template_id AS messageTemplateId
        -- answer_expiration_days, criteria_id, label_question_id, message_template_text_block_ml_id,

FROM message_template.message_template_text_block_view AS message_template_text_block
    JOIN message_template.message_template_text_block_ml_view AS message_template_text_block_ml
        ON message_template_text_block_ml.message_template_text_block_id = message_template_text_block.message_template_text_block_id
            -- we filter that later per recipient
            -- AND message_template_text_block_ml.lang_code = %s

    JOIN message_template.message_template_message_template_text_block_view AS message_template_message_template_text_block
        ON message_template_message_template_text_block.message_template_text_block_id = message_template_text_block.message_template_text_block_id

    JOIN message_template.message_template_text_block_type_ml_view AS message_template_text_block_type_ml
        ON message_template_text_block_type_ml.message_template_text_block_type_id = message_template_text_block.message_template_text_block_type_id
            AND message_template_text_block_type_ml.lang_code = message_template_text_block_ml.lang_code

    # TODO Change to question_view
    LEFT JOIN question.question_table AS question
        ON question.question_id = message_template_text_block.question_id

    LEFT JOIN question.question_ml_view AS question_ml
        ON question_ml.question_id = question.question_id
            AND question_ml.lang_code = message_template_text_block_ml.lang_code

    LEFT JOIN question_type.question_type_view AS question_type
        ON question_type.question_type_id = question.question_type_id
"""  # noqa

        self.cursor.execute(query)
        columns = ("sms_body_template", "email_subject_template", "email_body_html_template", "whatsapp_body_template",
                   "default_subject_template", "default_body_template",
                   "questionId", "questionTypeId", "whereStatement", "variableId", "tableId", "isVisible",
                   "isRequired", "labelQuestionId", "defaultValue", "answerExpirationDays",
                   "questionTitle", "questionTypeName",
                   "schemaDefault", "uiSchemaDefault", "schemaAttributes", "uiSchemaAttributes",
                   "langCode", "hint",
                   "messageTemplateTextBlockId", "messageTemplateBlockTypeName", "blockTypeId", "messageTemplateId")
        for inner_row in self.cursor.fetchall():
            text_block_dict = self.convert_to_dict(inner_row, ", ".join(columns))

            text_block_dict["possibleAnswers"] = self._get_possible_answers(
                question_id=text_block_dict["questionId"])
            self.logger.info(object={"text_block_dict": text_block_dict})
            textblocks_and_attributes.append(text_block_dict)
        cache["get_textblocks_and_attributes"] = textblocks_and_attributes

        return textblocks_and_attributes

    def _get_possible_answers(self, question_id: int) -> list[dict]:
        # TODO: get cities etc and insert as possible answer.
        # TODO Can we add it as a join to the previous SQL query
        query = """
        SELECT value FROM question.question_possible_answer_table
            JOIN question.question_possible_answer_ml_view AS question_possible_answer_ml
            ON question_possible_answer_ml.question_possible_answer_id = question_possible_answer_table.question_possible_answer_id
        WHERE question_id = %s
                 """
        self.cursor.execute(query, (question_id,))
        # We will change action in the future.
        return [{"answerValue": row[0], "action": None} for row in self.cursor.fetchall()]
