from seleniumbase import Driver
from Utils.proxylist import get_proxy
from selenium.webdriver import Remote, ChromeOptions
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from dotenv import load_dotenv
# from webdriver_manager.chrome import ChromeDriverManager
# from seleniumwire import webdriver
# from seleniumbase import SB
import os

load_dotenv(override=True)

def start(page_load_strategy="none"):
    proxy = get_proxy()

    chromium_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
        "--disable-popup-blocking",
        "--force-device-scale-factor=1",
        "--ignore-certificate-errors",
        "--ignore-ssl-errors",
        "--disable-infobars",
        "--disable-extensions",
        "--disable-gpu",
        # "--headless=new",
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]

    username = "brd-customer-hl_d75b9b74-zone-scraping_browser2"
    password = "aro5qo9wvsqi"
    auth = f"{username}:{password}"
    sbr_webdriver = f"https://{auth}@brd.superproxy.io:9515"
    chrome_options = ChromeOptions()
    chrome_options.binary_location = '/Applications/Chromium.app/Contents/MacOS/Chromium'
    for arg in chromium_args:
        chrome_options.add_argument(arg)
    sbr_connection = ChromiumRemoteConnection(sbr_webdriver, "goog", "chrome")
    driver = Remote(sbr_connection, options=chrome_options)

    # proxy_options = {
    #     'proxy': {
    #         'http': f'http://{auth}@brd.superproxy.io:33335',
    #         'https': f'https://{auth}@brd.superproxy.io:33335',
    #         'no_proxy': 'localhost,127.0.0.1'
    #     }
    # }
    

    # driver = Driver(
    #     browser="chrome",
    #     # proxy='sp82ikl6vg:1Do81_eGs4miIbqoZg@us.decodo.com:10000',
    #     chromium_arg=",".join(chromium_args),
    #     uc=True,
    #     uc_subprocess=True,
    #     page_load_strategy=page_load_strategy
    # )
    
#     proxy_options = {
#         'proxy': {
#             'http': f'http://sp82ikl6vg:1Do81_eGs4miIbqoZg@gate.decodo.com:10002',
#             'https': f'https://sp82ikl6vg:1Do81_eGs4miIbqoZg@gate.decodo.com:10002',
#         }
#     }
#     service = Service(ChromeDriverManager().install())

#     driver = webdriver.Chrome(
#     service=service,
#     options=chrome_options,
#     seleniumwire_options=proxy_options
# )

    return driver
