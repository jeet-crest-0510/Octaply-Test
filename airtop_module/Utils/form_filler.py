import asyncio
import logging
import json
from airtop_module.Utils.answer_questions import *
from airtop_module.Utils.fill_answers import *
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

# def get_visible_field_labels(driver):
#     labels = driver.find_elements(By.TAG_NAME, "label")
#     inputs = driver.find_elements(By.TAG_NAME, "input")
#     selects = driver.find_elements(By.TAG_NAME, "select")
#     textareas = driver.find_elements(By.TAG_NAME, "textarea")

#     visible_labels = set()

#     for el in labels + inputs + selects + textareas:
#         if el.is_displayed():
#             try:
#                 text = el.get_attribute("placeholder") or el.text or el.get_attribute("aria-label")
#                 if text:
#                     visible_labels.add(text.strip())
#             except:
#                 continue

#     return visible_labels

# def filter_airtop_fields(airtop_response, valid_labels):
#     filtered = []
#     for field in airtop_response.get("input", []):
#         if field["name"].strip() in valid_labels:
#             filtered.append(field)
#     return {"input": filtered}


async def parse_and_answer_all_questions_airtop(client, session, window, resume, driver):
    """
    Uses Airtop API to find all form questions on the page and answer them intelligently.
    """

     # Prompt to detect all relevant form fields
    form_field_prompt = """
    if you find any fields like [radio_button, checkbox_button, textarea_field, text_field, date_field, number_field, select_field, telephone_field, date_field_1, etc..] that should be selected or filled in the page then provide only it's type and text in the following format:
    {
    "input" : [{
            "type": "select_field",
            "name": "Country",
        },
        {
            "type": "text_field",
            "name": "city",
        },
        {
            "type": "radio_button",
            "name": "Are you above 18 years?",
        }]
    }.
    Ignore the continue button.
    and return {"input" : []} if the page doesn't contain any of the fields.
    """


     # Prompt to detect all relevant form fields
    # form_field_prompt = """
    # if you find any fields like [input, radio_button, checkbox_button, textarea_field, text_field, date_field, number_field, select_field, telephone_field, date_field_1, etc..] that should be selected or filled in the page then provide only it's type and text in the following format:
    # {
    # "input" : [{
    #         "type": "select_field",
    #         "name": "Country",
    #     },
    #     {
    #         "type": "text_field",
    #         "name": "city",
    #     },
    #     {
    #         "type": "radio_button",
    #         "name": "Are you above 18 years?",
    #     },
    #     {
    #         "type": "input",
    #         "name": "Company",
    #     }]
    # }.
    # Ignore the continue button and the optional Fields.
    # and return {"input" : []} if the page doesn't contain any of the fields.
    # """

    # Run paginated extraction on a form-heavy page
    response = await client.windows.paginated_extraction(
        session_id=session.data.id,
        window_id=window.data.window_id,
        prompt=form_field_prompt
    )

    await asyncio.sleep(4)

    print(f"Response for Page Query: {response}")

    # valid_labels = get_visible_field_labels(driver)
    # final_result = filter_airtop_fields(response, valid_labels)
    # print(final_result)

    json_format = {}
    if response.data != '{"input" : []}':
        json_str = (str)(response.data.model_response).replace('\n', '').replace(' ', '')
        json_format = json.loads(json_str)

    print(json_format)

    answers = await get_response_from_prompt(json_format, resume)
    answers = json.loads(answers)

    for json_obj in answers["output"]:    # needs a proper prompt that can generate output containing all the fields
    # for json_obj in json_format["input"]:   # currently we are not getting all the fields in output so using input
        if json_obj["type"] == "select_field":
            await select_field(client, session, window, json_obj)
        elif json_obj["type"] == "radio_button":
            await radio_button(client, session, window, json_obj)
        elif json_obj["type"] == "checkbox_button":
            await checkbox_button(client, session, window, json_obj)
        elif json_obj["type"] == "textarea_field":
            await textarea_field(client, session, window, json_obj)
        elif json_obj["type"] == "text_field":
            await text_field(client, session, window, json_obj)
        elif json_obj["type"] == "number_field":
            await number_field(client, session, window, json_obj)
        elif json_obj["type"] == "telephone_field":
            await telephone_field(client, session, window, json_obj)
        elif json_obj["type"] == "date_field":
            await date_field(client, session, window, json_obj)