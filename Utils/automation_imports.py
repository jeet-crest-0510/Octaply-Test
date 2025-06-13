from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import datetime
import gc
import re
from random import randint, uniform
import html2text
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from Utils.xpaths import xpaths, tag_names
def type_string(input_field, input_string):
    input_string=str(input_string)
    input_field.click()
    input_field.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
    
    input_field.clear()
    if(len(input_string)>30):
        input_field.send_keys(input_string)
        return True
    for char in str(input_string):
        sleep(uniform(0.03, 0.07))
        input_field.send_keys(char)

def remove_non_printable_utf8_chars(text):
    printable_utf8_pattern = (
        r'['
        u'\u0020-\u007E'  # Basic Latin (printable ASCII)
        u'\u00A0-\u00FF'  # Latin-1 Supplement (mostly printable characters)
        u'\u0100-\u017F'  # Latin Extended-A
        u'\u0180-\u024F'  # Latin Extended-B and more
        # Add more ranges as needed
        r']+'
    )
    return ''.join(re.findall(printable_utf8_pattern, text))


