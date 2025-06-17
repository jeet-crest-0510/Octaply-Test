import asyncio
from airtop import AsyncAirtop
# from Utils.get_gpt_answer import get_gpt_answer
import datetime
import math


async def radio_button(client, session, window, json_obj):
    await client.windows.click(
        session_id = session.data.id,
        window_id=window.data.window_id,
        element_description=f"Input Field of type='radio' with label='{json_obj['response']}' for question '{json_obj['name']}'" 
        # Input Field of type='radio' with label=json_obj["response"] for json_obj["name"]'
    )
 
    await asyncio.sleep(5)


async def checkbox_button(client, session, window, json_obj):
    ''' We will need different type of output format here:
        {
            "type": "checkbox_button",
            "name": "What are you preferences?",
            "response": ["Part Time", "Full Time"]
        }
    '''
    for option in json_obj["response"]:
        await client.windows.click(
            session_id = session.data.id,
            window_id=window.data.window_id,
            element_description="Input Field of type='checkbox' for label='option'" 
            # "Input Field of type='checkbox' for label='option'"
        )
 
        await asyncio.sleep(5)


async def textarea_field(client, session, window, json_obj):
    await client.windows.type(
        session_id=session.data.id,
        window_id=window.data.window_id,
        element_description=f"Input Field of type='text' for '{json_obj["name"]}'", # "Input Field for '{json_obj["name"]}'"
        text=json_obj["response"], # json_obj["response"]
        )

    await asyncio.sleep(5)


async def text_field(client, session, window, json_obj):
    await client.windows.type(
        session_id=session.data.id,
        window_id=window.data.window_id,
        element_description=f"Input Field of type='text' for '{json_obj["name"]}'", # "Input Field for '{json_obj["name"]}'"
        text=json_obj["response"], # json_obj["response"]
        )

    await asyncio.sleep(5)


async def number_field(client, session, window, json_obj):
    await client.windows.type(
        session_id=session.data.id,
        window_id=window.data.window_id,
        element_description=f"Input Field of type='number' for '{json_obj["name"]}'", 
        # "Input Field of type='number' for '{json_obj["name"]}'"
        text=json_obj["response"], # json_obj["response"]
        )

    await asyncio.sleep(5)


async def date_field(client, session, window, json_obj):
    await client.windows.type(
        session_id=session.data.id,
        window_id=window.data.window_id,
        element_description=f"Input Field of type='date' for '{json_obj["name"]}'",
        # "Input Field of type='date' for 'json_obj["name"]'"
        text=json_obj["response"], # json_obj["response"]
        )

    await asyncio.sleep(5)


async def select_field(client, session, window, json_obj):
    await client.windows.type(
        session_id=session.data.id,
        window_id=window.data.window_id,
        element_description=f"Select Field for '{json_obj["name"]}'", # "Select Field for '{json_obj["name"]}'"
        text=json_obj["response"][0], # json_obj["response"][0]
        )

    await asyncio.sleep(5)

    await client.windows.click(
        session_id = session.data.id,
        window_id=window.data.window_id,
        element_description=f"Option Field for label='{json_obj["response"]}'" # Option Field for label='json_obj["response"]'
    )
 
    await asyncio.sleep(5)


async def telephone_field(client, session, window, json_obj):
    # For Selecting Country Code
    await client.windows.type(
        session_id=session.data.id,
        window_id=window.data.window_id,
        element_description=f"Select Field with aria-label='Phone number country' for '{json_obj["name"]}'",
        # "Select Field with aria-label='Phone number country' for '{json_obj["name"]}'
        text=json_obj["response"][0], # json_obj["response"][0]
    )

    await asyncio.sleep(5)

    await client.windows.click(
        session_id = session.data.id,
        window_id=window.data.window_id,
        element_description=f"Option Field for label='{json_obj["response"]}'" # Option Field for label='json_obj["response"]'
    )
 
    await asyncio.sleep(5)

    # For Entering Phone Number
    await client.windows.type(
        session_id=session.data.id,
        window_id=window.data.window_id,
        element_description=f"Input Field of type='tel' for '{json_obj["name"]}'",
        # Input Field of type='tel' for '{json_obj["name"]}'
        text=json_obj["response"], # json_obj["response"]
    )