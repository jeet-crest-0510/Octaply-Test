from airtop import Airtop
from selenium import webdriver
from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from Utils.database_conn import mydatabase
from seleniumbase import Driver
import re

import os
import json
import asyncio
import subprocess
import requests
import webbrowser
from datetime import datetime
from pymongo import MongoClient
from airtop import AsyncAirtop
from airtop import SessionConfigV1
from airtop.core.api_error import ApiError
from shutil import which
import nest_asyncio

from selenium import webdriver
from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Utils.database_queries import fetch_resume_data
from airtop_module.Utils.form_filler import *
from functools import wraps
from airtop_module.Utils.handle_pop_ups import *
from airtop_module.Utils.verification_code import *


def timeout_handler(timeout_seconds):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                print(f"❌ Operation timed out after {timeout_seconds} seconds")
                return False
        return wrapper
    return decorator

def create_airtop_selenium_connection(airtop_api_key, airtop_session_data, *args, **kwargs):
    class AirtopRemoteConnection(ChromeRemoteConnection):
        @classmethod
        def get_remote_connection_headers(cls, *args, **kwargs):
            headers = super().get_remote_connection_headers(*args, **kwargs)
            headers['Authorization'] = f'Bearer {airtop_api_key}'
            return headers
    return AirtopRemoteConnection(remote_server_addr=airtop_session_data.chromedriver_url, *args, **kwargs)

def inject_new_tab_blocker(browser):
    """
    Injects JavaScript to block new tabs and popups, storing intercepted URLs in DOM elements
    """
    js_block_script = """
    (function() {
        // Create a hidden container to store intercepted URLs
        function createUrlStorage() {
            let storage = document.getElementById('airtop-url-storage');
            if (!storage) {
                storage = document.createElement('div');
                storage.id = 'airtop-url-storage';
                storage.style.display = 'none';
                storage.setAttribute('data-airtop-storage', 'true');
                document.body.appendChild(storage);
            }
            return storage;
        }

        // Function to store URL in DOM element
        function storeUrl(url, action = 'blocked') {
            const storage = createUrlStorage();
            const urlElement = document.createElement('div');
            urlElement.className = 'airtop-intercepted-url';
            urlElement.setAttribute('data-url', url);
            urlElement.setAttribute('data-action', action);
            urlElement.setAttribute('data-timestamp', Date.now());
            urlElement.textContent = url; // Also store as text content for easy access
            storage.appendChild(urlElement);
            
            console.log(`📋 Stored ${action} URL:`, url);
            
            // Keep only last 10 URLs to prevent memory issues
            const urlElements = storage.querySelectorAll('.airtop-intercepted-url');
            if (urlElements.length > 10) {
                urlElements[0].remove();
            }
        }

        // Override window.open
        const originalOpen = window.open;
        window.open = function(url, name, features) {
            console.log('🚫 Blocked window.open:', url);
            if (url && url !== 'about:blank') {
                storeUrl(url, 'window.open-blocked');
                // Store the URL but don't navigate automatically
                // Let Airtop decide what to do with it
            }
            return window; // Return current window
        };

        // Override location methods
        const originalAssign = window.location.assign;
        const originalReplace = window.location.replace;
        
        window.location.assign = function(url) {
            console.log('🔄 Intercepted location.assign:', url);
            storeUrl(url, 'location.assign-intercepted');
            // Don't execute the original assign, just store the URL
        };
        
        window.location.replace = function(url) {
            console.log('🔄 Intercepted location.replace:', url);
            storeUrl(url, 'location.replace-intercepted');
            // Don't execute the original replace, just store the URL
        };

        // Monitor all click events
        document.addEventListener('click', function(e) {
            const element = e.target.closest('a, button, [onclick]');
            if (element) {
                // Check for links that would open in new tabs
                if (element.tagName === 'A' && element.href && 
                    (element.target === '_blank' || element.getAttribute('target') === '_blank')) {
                    e.preventDefault(); // Prevent the link from opening
                    storeUrl(element.href, 'link-blocked');
                    console.log('🚫 Blocked link click:', element.href);
                }
                
                // Remove target attributes
                if (element.target) {
                    element.target = '_self';
                }
                
                // Check for JavaScript that might open new windows
                const onclick = element.getAttribute('onclick');
                if (onclick && onclick.includes('window.open')) {
                    console.log('🚫 Detected window.open in onclick, will be blocked');
                }
            }
        }, true);

        // Periodic cleanup of new elements and monitoring
        setInterval(() => {
            // Convert target="_blank" to target="_self"
            document.querySelectorAll('a[target="_blank"], form[target="_blank"]').forEach(el => {
                if (el.tagName === 'A' && el.href) {
                    storeUrl(el.href, 'target-blank-converted');
                }
                el.target = '_self';
            });
        }, 1000);

        // Block postMessage attempts that might open new windows
        const originalPostMessage = window.postMessage;
        window.postMessage = function(message, targetOrigin) {
            if (typeof message === 'string' && message.includes('window.open')) {
                console.log('🚫 Blocked postMessage that might open new window');
                storeUrl(message, 'postMessage-blocked');
                return;
            }
            return originalPostMessage.apply(this, arguments);
        };

        // Add helper function to get stored URLs (accessible from Python)
        window.getStoredUrls = function() {
            const storage = document.getElementById('airtop-url-storage');
            if (!storage) return [];
            
            const urlElements = storage.querySelectorAll('.airtop-intercepted-url');
            return Array.from(urlElements).map(el => ({
                url: el.getAttribute('data-url'),
                action: el.getAttribute('data-action'),
                timestamp: el.getAttribute('data-timestamp'),
                text: el.textContent
            }));
        };

        // Add helper function to get latest URL
        window.getLatestStoredUrl = function() {
            const urls = window.getStoredUrls();
            return urls.length > 0 ? urls[urls.length - 1] : null;
        };

        // Add helper function to clear stored URLs
        window.clearStoredUrls = function() {
            const storage = document.getElementById('airtop-url-storage');
            if (storage) {
                storage.innerHTML = '';
            }
        };

        console.log('🛡️ Maximum new tab blocking with URL storage activated!');
        
        // Return success indicator
        return true;
    })();
    """
    
    try:
        result = browser.execute_script(js_block_script)
        print("✅ New tab blocker with URL storage injected successfully")
        return result
    except Exception as e:
        print(f"❌ Failed to inject new tab blocker: {e}")
        return False

def get_intercepted_urls(browser):
    """
    Retrieve all intercepted URLs from the DOM storage
    """
    try:
        urls = browser.execute_script("return window.getStoredUrls();")
        return urls if urls else []
    except Exception as e:
        print(f"❌ Failed to get stored URLs: {e}")
        return []

def get_latest_intercepted_url(browser):
    """
    Get the most recently intercepted URL
    """
    try:
        latest_url = browser.execute_script("return window.getLatestStoredUrl();")
        return latest_url
    except Exception as e:
        print(f"❌ Failed to get latest URL: {e}")
        return None

def clear_intercepted_urls(browser):
    """
    Clear all stored URLs from DOM storage
    """
    try:
        browser.execute_script("window.clearStoredUrls();")
        print("✅ Cleared stored URLs")
        return True
    except Exception as e:
        print(f"❌ Failed to clear stored URLs: {e}")
        return False

def find_url_storage_element(browser):
    """
    Find the URL storage element using Selenium
    """
    try:
        storage_element = browser.find_element("id", "airtop-url-storage")
        return storage_element
    except Exception as e:
        print(f"❌ URL storage element not found: {e}")
        return None

def get_urls_from_storage_element(browser):
    """
    Get URLs directly from DOM elements using Selenium
    """
    try:
        storage_element = find_url_storage_element(browser)
        if not storage_element:
            return []
        
        url_elements = storage_element.find_elements("class name", "airtop-intercepted-url")
        urls = []
        
        for element in url_elements:
            url_data = {
                'url': element.get_attribute('data-url'),
                'action': element.get_attribute('data-action'),
                'timestamp': element.get_attribute('data-timestamp'),
                'text': element.text
            }
            urls.append(url_data)
        
        return urls
    except Exception as e:
        print(f"❌ Failed to get URLs from storage element: {e}")
        return []

def setup_persistent_blocking(browser):
    """
    Set up navigation listener to re-inject script on page changes
    """
    navigation_listener = """
    // Store the original pushState and replaceState
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;
    
    // Override history methods to detect navigation
    history.pushState = function() {
        originalPushState.apply(history, arguments);
        setTimeout(() => {
            if (typeof window.newTabBlockerInjected === 'undefined') {
                // Re-inject the blocker if not present
                console.log('🔄 Re-injecting new tab blocker after navigation');
            }
        }, 100);
    };
    
    history.replaceState = function() {
        originalReplaceState.apply(history, arguments);
        setTimeout(() => {
            if (typeof window.newTabBlockerInjected === 'undefined') {
                console.log('🔄 Re-injecting new tab blocker after navigation');
            }
        }, 100);
    };
    
    // Listen for hashchange events
    window.addEventListener('hashchange', function() {
        setTimeout(() => {
            if (typeof window.newTabBlockerInjected === 'undefined') {
                console.log('🔄 Re-injecting new tab blocker after hash change');
            }
        }, 100);
    });
    """
    
    browser.execute_script(navigation_listener)


nest_asyncio.apply()
# ---------------------- Configuration and Constants ----------------------
RESUME_API = 'http://ec2-3-18-99-76.us-east-2.compute.amazonaws.com/api/build-resume'
RESUME_PATH = "resume.pdf"
TS_SCRIPT_PATH = os.path.join(os.getcwd(), "airtop_module/resume_upload.ts")
AIRTOP_API_KEY = os.getenv("airtop_key", "6e7b2f5ff7f57523.dSrLf2UTxQImFch3qBiK71Eo1FTXQtqw99hQymCcDg")

# ---------------------- MongoDB and Resume Utility ----------------------

def get_mongo_collections():
    db = mydatabase
    return db["job_listings"], db["users"]

def fetch_job_and_user(email, limit=1):
    job_collection, user_collection = get_mongo_collections()
    job = job_collection.find_one({"jobLink": {"$exists": True}, "jobListingId": {"$exists": True}})
    if not job:
        raise ValueError("❌ No job found.")
    
    user = user_collection.find_one({"email": email})
    if not user:
        raise ValueError("❌ No user found.")

    skills = job_collection.find_one({"jobListingId": int(job["jobListingId"])}).get("skills", [])
    try:
        name_parts = user["name"].split(" ", 1)
        return {
            "jobListingId": job["jobListingId"],
            "jobLink": job["jobLink"],
            "email": user["glassdoorEmail"],
            "password": user["glassdoorPwd"],
            "first_name": name_parts[0],
            "last_name": name_parts[1] if len(name_parts) > 1 else "",
            "skills": skills
        }
    except KeyError as e:
        raise ValueError(f"❌ Missing required user or job field: {e}")
    except Exception as e:
        raise RuntimeError(f"❌ An unexpected error occurred: {str(e)}")
    
def fetch_skills_by_joblisting_id(job_listing_id):
    """
    Fetch skills associated with a job listing ID from the database.
    """
    job_collection, _ = get_mongo_collections()
    job = job_collection.find_one({"jobListingId": job_listing_id})
    if not job or "skills" not in job:
        raise ValueError(f"❌ No skills found for jobListingId: {job_listing_id}")
    return job["skills"]

def fetch_job_link_by_id(job_listing_id):
    job_collection, _ = get_mongo_collections()
    job = job_collection.find_one({"jobListingId": job_listing_id})
    if not job or "jobLink" not in job:
        raise ValueError(f"❌ No job found with jobListingId: {job_listing_id}")
    return job["jobLink"]

def generate_resume(skills, file_path, email):
    # email = 'chriswagner@octa-jobs.com'
    # email = 'archish.p@crestinfosystems.com'
    payload = json.dumps({"email": email, "skills": skills})
    headers = {'Content-Type': 'application/json'}
    res = requests.post(RESUME_API, headers=headers, data=payload)

    print("Request Payload:", payload)
    print("Response:", res.text)

    env = os.environ.copy() 
    env.update({
        "RESUME_FILE_PATH": file_path
    })

    if res.ok:
        with open(file_path, "wb+") as f:
            f.write(res.content)
        print(f"✅ Resume saved: {file_path}")
        return True
    else:
        print(skills, email)
        error_message = f"❌ Resume generation failed with status code {res.status_code} and response: {res.text}"
        print(error_message)
        raise RuntimeError(error_message)

def upload_resume_subprocess(session_id, window_id):
    env = os.environ.copy() 
    env.update({
        "AIRTOP_SESSION_ID": session_id,
        "AIRTOP_WINDOW_ID": window_id,
        "AIRTOP_API_KEY": AIRTOP_API_KEY
    })

    npx_path = which("npx")
    if not npx_path:
        raise EnvironmentError("❌ Could not find 'npx'. Ensure Node.js is installed.")

    print("🚀 Launching TS upload subprocess...")
    try:
        result = subprocess.run(
            [npx_path, "ts-node", TS_SCRIPT_PATH],
            check=True,
            capture_output=True,
            text=True,
            env=env,
            timeout=20
        )
        print("🔁 TS Output:\n" + result.stdout)
        if result.stderr:
            print("⚠️ TS Warnings/Errors:\n" + result.stderr)
    except subprocess.CalledProcessError as e:
        print("❌ TS Script Failed:\n" + e.stderr)
    except Exception as e:
        print(f"Exception: {e}")

# ---------------------- Airtop Automation Class ----------------------

class JobApplicationAutomation:

    def __init__(self):
        self.client = AsyncAirtop(api_key=AIRTOP_API_KEY, follow_redirects=True)

    @timeout_handler(1200)
    async def execute(self, user_data):

        # generate_resume(user_data["skills"], RESUME_PATH, user_data['email'])
        completed = False
        file_name=f"{user_data['first_name']}_{user_data['last_name']}_Resume.pdf"

        success = generate_resume(user_data["skills"], os.path.join(os.getcwd(), file_name), user_data['user_email'])

        if not success:
            return False, "Resume Generation Failure"

        session_id = None
        try:
            session = await self.client.sessions.create(
                configuration=SessionConfigV1(
                    timeout_minutes=15, 
                    solveCaptcha=True, 
                    proxy={
                        "country": 'AE'
                        # "country": "global",   # or use a specific country code like "US"
                    }
                )
            )
            session_id = session.data.id
            print("🚀 Airtop session started")

            window = await self.client.windows.create(session_id, url=user_data["jobLink"])
            window_id = window.data.window_id

            # options = Options()

            # browser = webdriver.Remote(
            #     command_executor=create_airtop_selenium_connection(AIRTOP_API_KEY, session.data),
            #     options=options
            # )

            # print(browser.capabilities)

            # await asyncio.sleep(5)
            # live_view_url = (await self.client.windows.get_window_info(session_id, window_id)).data.live_view_url
            # print(f"🔴 Live View: {live_view_url}")
            # webbrowser.open(live_view_url)

            # Set up persistent blocking for navigation events
            # inject_new_tab_blocker(browser)
            # setup_persistent_blocking(browser)
            
            # Get the window info and scrape the page content
            # window_info = await self.client.windows.get_window_info_for_selenium_driver(
            #     session.data,
            #     browser,
            # )
            # window_id = window_info.data.window_id
            # print(f"Window ID: {window_info.data.window_id}")

            # print(f"Live view url: {window_info.data.live_view_url}")
            # print("🌐 Successfully connected to Airtop browser and injected new tab blocker. Waiting..........")

            # is_active = browser.execute_script("return typeof window.open !== 'function' || window.open.toString().includes('Blocked window.open');")
            # print(f"✅ Blocking active: {is_active}")

            await asyncio.sleep(5)
            live_view_url = (await self.client.windows.get_window_info(session_id, window_id)).data.live_view_url
            print(f"🔴 Live View: {live_view_url}")
            print(f"Initial Window Id: {window_id}")
            # webbrowser.open(live_view_url)


            # Attach SeleniumBase to live browser
            driver = Driver(uc=True, headless=False)
            # driver = Driver(uc=True, headless=True)
            driver.open(live_view_url)
            print("🧭 Driver opened Live View")

            await asyncio.sleep(10)  # Wait for page to fully load

            # Step 5: Store original tabs
            original_tabs = driver.window_handles

            print(f"original_tabs: {original_tabs}")

            await asyncio.sleep(5)

            # -------------------- 👇 Login + Easy Apply Flow --------------------

            employer_site = await self.client.windows.page_query(
                session_id=session_id,
                window_id=window_id,
                prompt="Do you see a Button or heading on the page that says 'Apply on employer site?' Answer only Y/N."
            )
 
            print(f"Apply on employer site button?: {employer_site}")
 
            if employer_site.data.model_response == 'Y':
                return False, "Employer Site URL"
 
            # await self.client.windows.click(
            #     session_id=session_id,
            #     window_id=window_id,
            #     element_description='button or link with text "Sign In"',
            # )
            # print("✅ Clicked on 'Sign In' button")
            # await asyncio.sleep(2)
 
            # Click the Easy Apply button
            await self.client.windows.click(
                session_id=session_id,
                window_id=window_id,
                element_description="A button element with class button_Button__MlD2g and data-test='easyApply', nested inside a container with class JobDetails_applyButtonContainer__L36Bs. It contains a unique SVG lightning bolt icon and text 'Easy Apply', indicating a special one-click job application action."
            )
            print("✅ Clicked on Easy Apply")
 
            await asyncio.sleep(5)

            await self.client.windows.type(
                session_id=session_id,
                window_id=window_id,
                element_description="input field of type='email' with inputmode = text",
                text=user_data["email"],
                press_enter_key=True
            )
            print("✅ Entered Email")
            await asyncio.sleep(5)

            # inject_new_tab_blocker(browser)
            # setup_persistent_blocking(browser)

            await self.client.windows.type(
                session_id=session_id,
                window_id=window_id,
                element_description="input field of type='password' with inputmode = text",
                text=user_data["password"],
                press_enter_key=True
            )
            print("✅ Entered Password")
            await asyncio.sleep(5)

            # inject_new_tab_blocker(browser)
            # setup_persistent_blocking(browser)

            print("✅ Logged into Glassdoor.")

            # await handle_popups(self.client, session_id, window_id, user_data["email"])

            # intercepted_urls = get_intercepted_urls(browser)
            # print("📋 Intercepted URLs:", intercepted_urls)
            
            # Method 2: Get URLs directly from DOM elements
            # urls_from_dom = get_urls_from_storage_element(browser)
            # print("📋 URLs from DOM elements:", urls_from_dom)
            
            # Method 3: Get just the latest URL
            # latest_url = get_latest_intercepted_url(browser)
            # if latest_url:
            #     print(f"🔗 Latest intercepted URL: {latest_url['url']} (Action: {latest_url['action']})")


            # await asyncio.sleep(5)  # Wait for redirection or new tab

            await asyncio.sleep(15)

            # Detect new tab and fetch URL

            retry = 3

            while retry:

                current_tabs = driver.window_handles

                if len(current_tabs) > len(original_tabs):
                    new_tab = list(set(current_tabs) - set(original_tabs))[0]
                    driver.switch_to.window(new_tab)
                    new_url = driver.current_url
                    print(f"🌐 Redirected to new tab: {new_url}")

                    # 🔍 Extract windowId from the URL
                    match = re.search(r"windowId=([a-f0-9\-]+)", new_url)
                    if match:
                        window_id = match.group(1)
                        print(f"✅ Extracted new Airtop window_id: {window_id}")
                        break
                    else:
                        print("⚠️ No windowId found in the redirected URL.")
                        retry -= 1
                        
                else:

                    new_url = driver.current_url
                    print(f"🌐 Current Tab URL: {new_url}")

                    if new_url != live_view_url:
                        # 🔍 Extract windowId from the URL
                        match = re.search(r"windowId=([a-f0-9\-]+)", new_url)
                        if match:
                            window_id = match.group(1)
                            print(f"✅ Extracted new Airtop window_id: {window_id}")
                            break
                        else:
                            print("⚠️ No New windowId found in the URL.")

                    retry -= 1
                    if retry:
                        await asyncio.sleep(10)
                        continue
                    else:
                        return False, "New URL Not Detected"

                    # If no new tab, maybe same tab redirected
                    # current_url = driver.current_url
                    # print(f"🔁 Same tab redirect URL: {current_url}")

                    # # Attempt extraction from same-tab URL too
                    # match = re.search(r"windowId=([a-f0-9\-]+)", current_url)
                    # if match:
                    #     window_id = match.group(1)
                    #     print(f"✅ Extracted window_id from same tab: {window_id}")

            print(f"New Tab Window Id: {window_id}")

            # -------------------- Job Application Filling --------------------
 
            # Fill in First Name
            await self.client.windows.type(
                session_id=session_id,
                window_id=window_id,
                element_description="input[name='firstName']",
                text=user_data["first_name"]
            )
            print("✅ Entered First Name")
   
            await asyncio.sleep(4)
   
            # Fill in Last Name
            await self.client.windows.type(
                session_id=session_id,
                window_id=window_id,
                element_description="input[name='lastName']",
                text=user_data["last_name"]
            )
            print("✅ Entered Last Name")
 
            await asyncio.sleep(4)
 
            available_phone = await self.client.windows.page_query(
                session_id=session_id,
                window_id=window_id,
                prompt= "Do you see a text 'Phone number'  on the page? Answer only Y/N."
                # prompt="Do you see a label[for='input-phoneNumber'] or span[class='dd-privacy-allow css-bev4h3 e37uo190'] on the page? Answer only Y/N."
            )
 
            print(f"Phone Number Field Availabel? {available_phone}")  
 
            await asyncio.sleep(2)
 
            if available_phone.data.model_response == 'Y' :
 
                if user_data['resume'].get("personal_details").get("contact").get("phone_number_country"):
                    phone_code = user_data['resume'].get("personal_details").get("contact").get("phone_number_country")
                else:
                    phone_code = 'United States'
 
                if user_data['resume'].get("personal_details").get("contact").get("phone"):
                    phone  = user_data['resume'].get("personal_details").get("contact").get("phone")
                else:
                    phone = '212-456-7890'
 
                print(f"code: {phone_code}, phone: {phone}")
 
                await self.client.windows.type(
                    session_id=session.data.id,
                    window_id=window.data.window_id,
                    element_description=f"Select Field with aria-label='Phone number country' for 'Phone number'",
                    # "Select Field with aria-label='Phone number country' for '{json_obj["name"]}'
                    text=phone_code[0], # json_obj["response"][0]
                )
 
                await asyncio.sleep(5)
 
                await self.client.windows.click(
                    session_id = session.data.id,
                    window_id=window.data.window_id,
                    element_description=f"Option Field for label='{phone_code}'" # Option Field for label='json_obj["response"]'
                )
           
                await asyncio.sleep(5)
 
                # For Entering Phone Number
                await self.client.windows.type(
                    session_id=session.data.id,
                    window_id=window.data.window_id,
                    element_description=f"Input Field of type='tel' for 'Phone Number'",
                    # Input Field of type='tel' for '{json_obj["name"]}'
                    text=phone, # json_obj["response"]
                )
   
                print("✅ Entered Phone Number")
   
                await asyncio.sleep(4)
 
            available_email = await self.client.windows.page_query(
                session_id=session_id,
                window_id=window_id,
                prompt = "Do you see an input field for 'email' on the page? Answer only Y/N."
                # prompt= "Do you see a input[id='input-email'] or any field for the email on the page? Answer only Y/N."
                # prompt="Do you see a label[for='input-phoneNumber'] or span[class='dd-privacy-allow css-bev4h3 e37uo190'] on the page? Answer only Y/N."
            )

            print(f"available email: {available_email}")
 
            await asyncio.sleep(2)
 
            if available_email.data.model_response == 'Y' :
                # For Entering Email
                await self.client.windows.type(
                    session_id=session.data.id,
                    window_id=window.data.window_id,
                    element_description=f"Input Field of type='email' for 'Email'",
                    # Input Field of type='tel' for '{json_obj["name"]}'
                    text=user_data["email"], # json_obj["response"]
                )
   
                print("✅ Entered Email")
   
                await asyncio.sleep(4)
   
            # Click "Continue" on the job listing
            await self.client.windows.click(
                session_id=session_id,
                window_id=window_id,
                element_description="button:has-text('Continue')"
            )
            print("✅ Clicked on Continue")
   
            await asyncio.sleep(4)
 
            verification_section = await self.client.windows.page_query(
                    session_id=session_id,
                    window_id=window_id,
                    prompt="Do you see a heading like 'Verify your email' or a text saying 'Enter verification code'? Answer only Y/N."
            )
           
            await asyncio.sleep(2)
 
            print(f"Verifying Email")
 
            if verification_section.data.model_response == 'Y':
 
                # Split the code into digits
                code = await get_verification_code(target_email=user_data["email"])
                print(f"Verification Code: {code}")

                if not code:
                    return False, "Verification code is None"
                await asyncio.sleep(5)
 
                # Try to enter the full code in one field
                await self.client.windows.type(
                    session_id=session_id,
                    window_id=window_id,
                    element_description="input[type='number],input[id='input-passcode']",
                    text=code
                )
 
                print("✅ Entered Verification Code")
 
                # Optional: Small wait before clicking
                await asyncio.sleep(4)
 
                # Click the "Verify" button
                await self.client.windows.click(
                    session_id=session_id,
                    window_id=window_id,
                    element_description="button[data-testid='continue-button'] with text 'Verify'"
                )
 
                print("✅ Clicked on Verify")
 
                await asyncio.sleep(4)
 
            await asyncio.to_thread(upload_resume_subprocess, session_id, window_id)
 
            await asyncio.sleep(4)
            await self.client.windows.click(
                session_id=session_id,
                window_id=window_id,
                element_description="button:has-text('Continue')"
            )
 
            await asyncio.sleep(5)
 
            print("✅ Clicked on Continue\n🎉 Resume submitted!")

            # -------------------- Questions based on the Resume --------------------
    
            await asyncio.sleep(4)

            available = await self.client.windows.page_query(
                session_id=session_id,
                window_id=window_id,
                prompt="Do you see a button or link labeled 'Continue' on the page? Answer only Y/N."
            )   

            print(available)

            await asyncio.sleep(4)

            while(available.data.model_response == 'Y'):
                await parse_and_answer_all_questions_airtop(self.client, session, window, user_data["resume"], driver)

                await asyncio.sleep(4)

                # Click "Continue"
                await self.client.windows.click(
                    session_id=session_id,
                    window_id=window_id,
                    element_description="button:has-text('Continue')"
                )
                print("✅ Clicked on Continue")

                await asyncio.sleep(5)

                available = await self.client.windows.page_query(
                    session_id=session_id,
                    window_id=window_id,
                    prompt="Do you see a button or link labeled 'Continue' on the page? Answer only Y/N."
                )   
                
                print(available)

                await asyncio.sleep(4)

            print("🎉 Reached Employer Questions.")

            await asyncio.sleep(5)

            submit = await self.client.windows.page_query(
                session_id=session_id,
                window_id=window_id,
                prompt="Answer only Y/N if you see any 'Submit your application' button"
            )

            print(f"submit: {submit}")

            if(submit.data.model_response == 'Y'):

                await asyncio.sleep(2)

                recaptcha = await self.client.windows.paginated_extraction(
                    session_id=session_id,
                    window_id=window_id,
                    prompt="Answer only Y/N if you find any I'm not a robot Recaptcha"
                )

                if (recaptcha.data.model_response == 'Y'):
                    await asyncio.sleep(2)

                    # Click "Recatcha"
                    await self.client.windows.click(
                        session_id=session_id,
                        window_id=window_id,
                        element_description="click checkbox or button which is labeled in I'm not a robot Recaptcha"
                    )

                await asyncio.sleep(10)

                # Click "Submit"
                await self.client.windows.click(
                    session_id=session_id,
                    window_id=window_id,
                    element_description="button:has-text('Submit your application')"
                )
                print("✅ Clicked on Submit")

            await asyncio.sleep(15)

            print("🎉 Job application completed successfully!")

            # Check if the final page contains the text "Your application has been submitted"
            final_page_check = await self.client.windows.page_query(
                session_id=session_id,
                window_id=window_id,
                prompt="Do you see the text 'Your application has been submitted' on the page? Answer only Y/N."
            )

            print(f"Final page check: {final_page_check.data.model_response}")

            if final_page_check.data.model_response == 'Y':
                completed = True
                # return True
            else:
                return False, "Final Submission Pending"
            # -------------------- Questions based on the Resume --------------------

            # await parse_and_answer_all_questions_airtop(self.client, session, window, "")

        except ApiError as e:
            print(f"❌ API Error: {e.status_code} - {e.body}")
            return False, f"API Error: {e.status_code} - {e.body}"
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
            return False, f"Unexpected Error: {str(e)}"
        finally:
            if session_id:
                await self.client.sessions.terminate(session_id)
                print("🔚 Session terminated.")
            return completed

async def run_airtop_automation(joblisting_id, user_email, email, password, first_name, last_name, resume):
    automation = JobApplicationAutomation()
    
    data = {
        # "jobLink" : fetch_job_link_by_id(joblisting_id),
        "jobLink" : "https://www.glassdoor.co.in/job-listing/medicaid-claims-analyst-aston-carter-JV_KO0,23_KE24,36.htm?jl=1009775431938&src=GD_JOB_AD&ao=1110586&jrtk=5-yul1-0-1ithbn5tvjn36800-2c0d9f8572bf0527---6NYlbfkN0ChYVx_I3yfZ_JDY3EFoivtqvi_stwnZ_kRt8Dowt_l_T08GzZ4dLfgqREKn0Au9KYbuF1A35levFasuhGfbo505S7hznP6pnfeWzrTqZEEmSuqOGfb2AxRyxRerMLgLAUqPhKRtTzmOCb4U7H9xGS9gbYotSJ45ozk_hYLz7s-x0mlb_8UDRrykQ5z4QwhR5V5IGQgi7PKbscIsceXJ-KJeWbPrzPIxautvkP85-hFVQRD_nuifTn1hixu7DXa8pxgkPnHv9p3_XpcVjpPeKM7lLihINWLwX4r9ykGgdlcI57tbVWZLNG5eI0YK1iarLQlaYEFDxu9jGeWko7aUCTu_j-dE8xd6v0zD97RpoTWNVzLT4Vsm3RARiBmYjssFpDSUBz4jl3cREEh48Acz8y89S-_KhvtJu-ZmPslkNlD8bmR8_hXtD4Zx3TjM_h2c22hnvrpB3Gt3paLq3215Zw_MWvfiQUKknHlQYeRnCOSjMAgH27XPcky3ycSt7b6PYWHcDC3h9dv01vbd8hTetpBdOcmj0gdQskBCBtAwzAWes_ai4aU7jtk--KJsfua0yXTwd__vQUncytFiYOHxS9QzD3N_PU0C2ch9teFjxYxaHSf3m9HHO7C68pLWril7pshwLTLEUzy7RYYGJo4zJZkyBMSpBkVCfzAWn1fU79d5PJB9zInBKL42O7_VAOk1KQG4bxRQsc4CPALSX6S5CdTb6oi9rGvtcouVxHY3Uieb2QSoZczEPSj1FET4JxoDqHrOvIsjk0TQofNhER4_sc7Tk4l9qxdN9UK84cxSE3Q5359NxSVTew7x_DvwgUo_QWUID_giNGdVTq23JwdowYvXk80nvMlowLX6ULHaAL6rDevH-yQ2kDMxHNYNiCbvOhxuAMwM_2WYQZi2F3fX8gMItNv4MhasFBsneyVrayUTTFumVvtGXsNlwTnjfbTxT8kOqt1eu86B3N7qUk8ylPvbeEyC9jeFKBRWE6kvtiUgaxisqAWHVE5iHG_2iSbt3kDt6qjMuOfNQ8g7uOO21gsGRokKt4rWj417Yvoh9aTLJKvTre6iylc2jE5jrx_DiBwghXsrUt5Sv9qNZo5rO6vOUY7iyYwNV_WRwJhPWhLtFZldvY_Q93j1J_-F_O_CjybVXwjvO9GLCbKT4TsVtX_WRCH1_2u7S7XZZy3Yyz7QNxaYVSQIaxw9TjVCbPLohboN3bfNLzAvXkMT91LcBcS6Jx7QtCVQSVx5H7DAtpkFQ%253D%253D&cs=1_eb987dca&s=58&t=SR&pos=114&cpc=3BA4CE39D5B5DEF5&guid=0000019762bb9771baae64f109910230&jobListingId=1009775431938&ea=1&vt=w&cb=1749708151507&ctt=1749729276401",
        # "jobLink" : "https://www.glassdoor.co.in/job-listing/medicaid-claims-analyst-aston-carter-JV_KO0,23_KE24,36.htm?jl=1009775431938&src=GD_JOB_AD&ao=1110586&jrtk=5-yul1-0-1ithbn5tvjn36800-2c0d9f8572bf0527---6NYlbfkN0ChYVx_I3yfZ_JDY3EFoivtqvi_stwnZ_kRt8Dowt_l_T08GzZ4dLfgqREKn0Au9KYbuF1A35levFasuhGfbo505S7hznP6pnfeWzrTqZEEmSuqOGfb2AxRyxRerMLgLAUqPhKRtTzmOCb4U7H9xGS9gbYotSJ45ozk_hYLz7s-x0mlb_8UDRrykQ5z4QwhR5V5IGQgi7PKbscIsceXJ-KJeWbPrzPIxautvkP85-hFVQRD_nuifTn1hixu7DXa8pxgkPnHv9p3_XpcVjpPeKM7lLihINWLwX4r9ykGgdlcI57tbVWZLNG5eI0YK1iarLQlaYEFDxu9jGeWko7aUCTu_j-dE8xd6v0zD97RpoTWNVzLT4Vsm3RARiBmYjssFpDSUBz4jl3cREEh48Acz8y89S-_KhvtJu-ZmPslkNlD8bmR8_hXtD4Zx3TjM_h2c22hnvrpB3Gt3paLq3215Zw_MWvfiQUKknHlQYeRnCOSjMAgH27XPcky3ycSt7b6PYWHcDC3h9dv01vbd8hTetpBdOcmj0gdQskBCBtAwzAWes_ai4aU7jtk--KJsfua0yXTwd__vQUncytFiYOHxS9QzD3N_PU0C2ch9teFjxYxaHSf3m9HHO7C68pLWril7pshwLTLEUzy7RYYGJo4zJZkyBMSpBkVCfzAWn1fU79d5PJB9zInBKL42O7_VAOk1KQG4bxRQsc4CPALSX6S5CdTb6oi9rGvtcouVxHY3Uieb2QSoZczEPSj1FET4JxoDqHrOvIsjk0TQofNhER4_sc7Tk4l9qxdN9UK84cxSE3Q5359NxSVTew7x_DvwgUo_QWUID_giNGdVTq23JwdowYvXk80nvMlowLX6ULHaAL6rDevH-yQ2kDMxHNYNiCbvOhxuAMwM_2WYQZi2F3fX8gMItNv4MhasFBsneyVrayUTTFumVvtGXsNlwTnjfbTxT8kOqt1eu86B3N7qUk8ylPvbeEyC9jeFKBRWE6kvtiUgaxisqAWHVE5iHG_2iSbt3kDt6qjMuOfNQ8g7uOO21gsGRokKt4rWj417Yvoh9aTLJKvTre6iylc2jE5jrx_DiBwghXsrUt5Sv9qNZo5rO6vOUY7iyYwNV_WRwJhPWhLtFZldvY_Q93j1J_-F_O_CjybVXwjvO9GLCbKT4TsVtX_WRCH1_2u7S7XZZy3Yyz7QNxaYVSQIaxw9TjVCbPLohboN3bfNLzAvXkMT91LcBcS6Jx7QtCVQSVx5H7DAtpkFQ%253D%253D&cs=1_eb987dca&s=58&t=SR&pos=114&cpc=3BA4CE39D5B5DEF5&guid=0000019762bb9771baae64f109910230&jobListingId=1009775431938&ea=1&vt=w&cb=1749708151507&ctt=1749724666940",
        "user_email" : user_email,
        "email" : email,
        "password" : password,
        "first_name" : first_name,
        "last_name" : last_name,
        "skills" : fetch_skills_by_joblisting_id(joblisting_id),
        "resume": resume
    }
    return await automation.execute(data)

# if __name__ == "__main__":

#     resume_id=os.getenv('resume_id')
#     jobListingId=int(os.getenv('jobListingId'))
#     if(resume_id==None):
#         logger.info(f'Resume_id not passed')
#         exit()

#     logger.info(f'Resume_id is: {resume_id}')
#     logger.info(f'jobListingId is: {jobListingId}')

#     resume=fetch_resume_data(resume_id)

#     data = {
#         "user_email" : "archish.p@crestinfosystems.com",
#         "email" : "lecenab522@3dboxer.com",
#         "password" : "lecenab@522",
#         "first_name" : "test",
#         "last_name" : "test",
#     }
    
#     application_success = run_airtop_automation(jobListingId, data['user_email'], data['email'], data['password'], data['first_name'], data['last_name'], resume)
#     if application_success:
#         logger.info(f"Application submitted successfully via Airtop for jobListingId: {jobListingId}")
#     else:
#         logger.info(f"Application failed via Airtop for jobListingId: {jobListingId}")
