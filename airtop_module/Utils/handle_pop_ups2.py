import asyncio

from airtop_module.Utils.verification_code1 import get_verification_code

async def handle_popups(client, session_id, window_id, email):
    print("🔍 Checking for popups...")

    popup_patterns = [
        {
            "description": "Employment status",
            "selector": '[id="NOT_EMPLOYED"] button:contains("Not currently"), button:contains("Not currently")'
        },
        {
            "description": "Close button",
            "selector": ', '.join([
                'button[data-test="user-registration-modal-close-button"]',
                'button[aria-label="Close"]',
                'button[aria-label="close"]',
                'button[title="Close"]',
                'button[title="close"]',
                'button:contains("×")',
                'button:contains("✕")',
                'button:contains("Skip")',
                'button:contains("Dismiss")',
                'button:contains("No thanks")',
                'button:contains("Maybe later")',
                'button element that contains close in any attribute values'
            ])
        },
        {
            "description": "Job preferences",
            "selector": '[data-test="preferences-next"], button:contains("Next")'
        }
    ]

    try:
        for pattern in popup_patterns:
            try:

                # if (available.data.model_response == 'Y'):
                if pattern['description'] == "Employment status":

                    available = await client.windows.page_query(
                        session_id=session_id,
                        window_id=window_id,
                        prompt="Do you see a button or link labeled 'Not currently' on the page? Answer only Y/N."
                    )
                    await asyncio.sleep(2)

                    print(f"Popup Available? - Not Currently button: {available}")

                    if (available.data.model_response == 'Y'):
                        response = await client.windows.click(
                            session_id=session_id,
                            window_id=window_id,
                            element_description=pattern["selector"],
                            # time_threshold_seconds = 3
                            # timeout=3000
                        )
                        print(f"Response: {response}")

                        await asyncio.sleep(4)

                    available = await client.windows.page_query(
                        session_id=session_id,
                        window_id=window_id,
                        prompt="Do you see a field or label related to 'Current university or college*' on the page? Answer only Y/N."
                    )
                    await asyncio.sleep(2)

                    print(f"Popup Available? - Current University or College: {available}")

                    if (available.data.model_response == 'Y'):
                        response = await client.windows.type(
                            session_id=session_id,
                            window_id=window_id,
                            text="Stanford University",
                            element_description='input[data-test="university-autocomplete"]',
                            press_enter_key=True
                            # time_threshold_seconds = 3
                            # timeout=3000
                        )
                        print(f"✅ Entered University")

                        await asyncio.sleep(4)

                    available = await client.windows.page_query(
                        session_id=session_id,
                        window_id=window_id,
                        prompt="Do you see a field or label related to 'Current degree type*' on the page? Answer only Y/N."
                    )
                    await asyncio.sleep(2)

                    print(f"Popup Available? - Current Degree Type: {available}")

                    if (available.data.model_response == 'Y'):
                        response = await client.windows.type(
                            session_id=session_id,
                            window_id=window_id,
                            text="Bachelor's",
                            element_description='Button for current degree type',
                            press_enter_key=True
                            # time_threshold_seconds = 3
                            # timeout=3000
                        )
                        print(f"✅ Entered Current Degree")

                        await asyncio.sleep(4)

                    available = await client.windows.page_query(
                        session_id=session_id,
                        window_id=window_id,
                        prompt="Do you see a field or label related to 'Desired job title' or 'What are you looking for?' on the page? Answer only Y/N."
                    )
                    await asyncio.sleep(2)

                    print(f"Popup Available? - Desired Job Title: {available}")

                    # if pattern['description'] == "Employment status":
                    if (available.data.model_response == 'Y'):
                        await asyncio.sleep(4)
        
                        # Fill in Job Title
                        await client.windows.type(
                            session_id=session_id,
                            window_id=window_id,
                            element_description="input element with [data-test='job-title-autocomplete']",
                            text="Software Engineer",
                            press_enter_key=True
                        )
                        print("✅ Entered Job Title")

                        await asyncio.sleep(4)

                        # Fill in Job Location (step 1: type it)
                        await client.windows.type(
                            session_id=session_id,
                            window_id=window_id,
                            element_description="input element with [data-test='location-autocomplete']",
                            text="Surat",
                            press_enter_key=True
                        )
                        print("✅ Typed Location")

                        await asyncio.sleep(4)  # Give time for suggestions to appear

                        await client.windows.click(
                            session_id=session_id,
                            window_id=window_id,
                            element_description="button:has-text('Next')"
                        )
                        print("✅ Clicked on Next")

                        await asyncio.sleep(4)

                    industry_section = await client.windows.page_query(
                        session_id=session_id,
                        window_id=window_id,
                        prompt="Do you see a question or heading on the page that says 'What's your industry?' or a label 'Industry*'? Answer only Y/N."
                    )
                    await asyncio.sleep(2)

                    print(f"Popup Available? - Industry: {industry_section}")

                    # if pattern['description'] == "Employment status":
                    if (industry_section.data.model_response == 'Y'):

                       
                        await client.windows.type(
                            session_id=session_id,
                            window_id=window_id,
                            element_description='button[data-test="industry-select-button"]',
                            text="Other",
                            press_enter_key=True
                        )
                       
                        print("✅ Selected 'Other' from dropdown")

                        await asyncio.sleep(4)

                        await client.windows.click(
                            session_id=session_id,
                            window_id=window_id,
                            element_description="button:has-text('Next')"
                        )
                        print("✅ Clicked on Next")

                        await asyncio.sleep(4)

                    verification_section = await client.windows.page_query(
                        session_id=session_id,
                        window_id=window_id,
                        prompt="Do you see a heading like 'Check your email' or a message saying 'We sent a verification code to'? Answer only Y/N."
                    )
                    await asyncio.sleep(2)

                    print(f"Popup Available? - Verification: {verification_section}")

                    if verification_section.data.model_response == 'Y':

                        # Split the code into digits
                        code = await get_verification_code(target_email=email)
                        await asyncio.sleep(5)

                        # Try to enter the full code in one field
                        await client.windows.click(
                            session_id=session_id,
                            window_id=window_id,
                            element_description='[data-test="pinInput-0"]'
                        )

                        await asyncio.sleep(0.5)

                        await client.windows.type(
                            session_id=session_id,
                            window_id=window_id,
                            element_description='[data-test="pinInput-0"]',
                            text=code
                        )

                        print("✅ Entered full code in pinInput-0")

                        # Optional: Small wait before clicking
                        await asyncio.sleep(4)

                        # Click the "Verify" button
                        await client.windows.click(
                            session_id=session_id,
                            window_id=window_id,
                            element_description="button[data-test='button-primary'] with text 'verify'"
                        )

                        print("✅ Clicked on Verify")

                    await asyncio.sleep(4)

                else:
                    response = await client.windows.click(
                        session_id=session_id,
                        window_id=window_id,
                        element_description=pattern["selector"],
                        # time_threshold_seconds = 3
                        # timeout=3000
                    )

                    await asyncio.sleep(4)

            except Exception as e:
                print(f"Exception: {e}")
                continue

    except Exception as error:
        print("ℹ️ Popup handling completed with status:", str(error))
