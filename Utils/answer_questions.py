from Utils.automation_imports import *
from Utils.get_gpt_answer import get_gpt_answer
import logging, traceback
import math
import re
logger = logging.getLogger(__name__)
def radio_button(resume, element, question_text):
    options_element=element.find_elements(by=By.XPATH, value=xpaths.get("radio_button_option"))
    option_text_list=[]
    for option in options_element:
        option_text_list.append(option.text)
    if(len(options_element)==1):
        options_element[0].click()
        return True
    correct_option=get_gpt_answer(question_text, resume, "singe_correct_mcq", option_text_list)
    options_element[int(correct_option)].click()
    return True

def checkbox_button(resume, element, question_text):
    
    options_element=element.find_elements(by=By.XPATH, value=xpaths.get("checkbox_button_option1"))
    if(len(options_element)==0):
        options_element=element.find_elements(by=By.XPATH, value=xpaths.get("checkbox_button_option2"))
    option_text_list=[]
    for option in options_element:
        option_text_list.append(option.text)
    if(len(options_element)==1):
        options_element[0].click()
        return True
    correct_options=get_gpt_answer(question_text, resume, "multiple_correct_mcq", option_text_list)
    for correct_option in correct_options:
        options_element[correct_option].click()
    return True
def textarea_field(resume, element, question_text):
    
    correct_answer=get_gpt_answer(question_text, resume, "text_question_prompt", False)
    input_field=element.find_element(by=By.TAG_NAME, value=tag_names.get("textarea"))
    type_string(input_field, correct_answer)
    return True

def text_field(resume, element, question_text):
    
    correct_answer=get_gpt_answer(question_text, resume, "text_question_prompt", False)
    input_field=element.find_element(by=By.XPATH, value=xpaths.get("text_input"))
    type_string(input_field, correct_answer)
    return True

def date_field(resume, element, question_text):
    
    correct_answer=str((datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%d%m%Y'))
    input_field=element.find_element(by=By.XPATH, value=xpaths.get("date_input"))
    type_string(input_field, correct_answer)
    return True

def number_field(resume, element, question_text):
    
    correct_answer=get_gpt_answer(question_text, resume, "numeric_question_prompt", False)
    print("Answer", correct_answer)
    correct_answer = str(math.ceil(float(correct_answer)))
    print("correct_answer", correct_answer)
    element.find_element(by=By.XPATH, value=xpaths.get("numerical_input")).click()
    input_field=element.find_element(by=By.XPATH, value=xpaths.get("numerical_input"))
    type_string(input_field, correct_answer)
    return True

def select_field(resume, element, question_text, flag=True):
    old_val=len(element.find_elements(by=By.XPATH, value=".//div[@class='css-1blujpy e1ttgm5y0']"))
    
    options_element=element.find_elements(by=By.XPATH, value=xpaths.get("select_option"))
    option_text_list=[]
    for option in options_element:
        if("Afghanistan" in option.text and "Afghani " not in option.text):
            element.find_element(by=By.TAG_NAME, value="select").click()
            sleep(1.5)
            element.find_element(by=By.TAG_NAME, value="select").send_keys(resume.get("location").get("country").replace('USA', 'United States'))
            flag=False
        option_text_list.append(option.text)
    if(flag):
        correct_option=int(get_gpt_answer(question_text, resume, "singe_correct_mcq", option_text_list))
        logger.info(correct_option)
        logger.info(option_text_list[correct_option])
        logger.info('-------')
        select = Select(element.find_element(by=By.TAG_NAME, value=tag_names.get('select')))
        element.find_element(by=By.TAG_NAME, value=tag_names.get('select')).click()
        sleep(1)
        select.select_by_index(correct_option)
    
    if(len(element.find_elements(by=By.XPATH, value=".//div[@role='group']"))):
        print("group")
        sleep(2)
        if(len(element.find_elements(by=By.XPATH, value=".//div[@class='css-1blujpy e1ttgm5y0']"))!=old_val):
            print("new val is ", len(element.find_elements(by=By.XPATH, value=".//div[@class='css-1blujpy e1ttgm5y0']")))
            temp=element.find_elements(by=By.XPATH, value=".//div[@class='css-1blujpy e1ttgm5y0']")[-1]
            return select_field(resume, temp, question_text)
    return True

def telephone_field(resume, element, question_text):
    
    correct_answer=get_gpt_answer(question_text, resume, "text_question_prompt", False)
    input_field=element.find_element(by=By.XPATH, value=xpaths.get("telephonic_input"))
    type_string(input_field, correct_answer)
    return True

def resume_field(driver, pdfpath):
    resume_element=driver.find_elements(by=By.XPATH, value='//input[@data-testid="FileResumeCard-file-input"]')
    if(len(resume_element)==0):
        return False
    for error_count in range(3):
        try:
            resume_element[0].send_keys(pdfpath)
            driver.execute_script("window.scrollTo(0, 350);")
            try: driver.find_element(by=By.XPATH, value=xpaths.get("accept_cookie_button")).click()
            except: pass
            return True
        except Exception as e:
            sleep(1)
    return False
    
def work_expierence_field(resume, driver):
    work_experience=resume.get("work_experience")
    if(type(work_experience)==list and len(work_experience)>0):
        past_role=work_experience[0].get("role")
        past_employer=work_experience[0].get("employer")
    else:
        return False
    try:
        job_title_element=driver.find_element(by=By.XPATH, value=xpaths.get("job_title_input"))
        company_title_element=driver.find_element(by=By.XPATH, value=xpaths.get("company_title_input"))

    
        type_string(job_title_element, past_role)
        job_title_element.send_keys(Keys.TAB)
        type_string(company_title_element, past_employer)
        company_title_element.send_keys(Keys.TAB)
        return True
    except:
        return False
    
def write_cover_letter(driver, resume, cover_letter,job_record):
    try:
        cover_letter = cover_letter.replace("<ROLE NAME>", job_record.get('jobTitleText','-').strip())
        cover_letter=html2text.html2text(cover_letter)
        while ('\n\n' in cover_letter):
            cover_letter=cover_letter.replace('\n\n', '\n').strip()

        cover_letter = cover_letter.replace("[INSERT COMPANY NAME]", job_record.get('employerNameFromSearch','-')) \
        .replace("[where you found the job posting]", 'Glassdoor') \
        .replace("[position title]", job_record.get('jobTitleText','-').strip()) \
        .replace("[Company Name]", job_record.get('employerNameFromSearch','-').strip()) \
        .replace("[company name]", job_record.get('employerNameFromSearch','-').strip()) \
        .replace("[Company Address]", job_record.get('locationName','-').strip()) \
        .replace("[City, State, ZIP Code]", job_record.get('locationName','-').strip()) \
        .replace("[Employer's Name]", job_record.get('employerNameFromSearch','-').strip())

        driver.find_element(by=By.XPATH, value=xpaths.get("cover_letter_input")).send_keys(cover_letter)
        return True
    except: 
        return False
    
def date_field_1(resume, element, question_text):
    input_field=element.find_element(by=By.TAG_NAME, value="input")
    input_field.click()
    input_field.send_keys(Keys.CONTROL + "a")
    input_field.send_keys(Keys.DELETE)
    input_field.clear()
    try:
        correct_answer=str(input_field.get_attribute("placeholder"))
        if(len(correct_answer)<5):
            correct_answer=str((datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%m/%d/%Y'))
    except:
        correct_answer=str((datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%m/%d/%Y'))
    type_string(input_field, correct_answer)
    return True

def handle_unexpected_cases(resume, element, question_text):
    try:
        correct_answer=str(get_gpt_answer(question_text, resume, "text_question_prompt", False))

        if('SELF-IDENTIFICATION OF DISABILITY' in question_text):
            #xpaths.get("radio_button_option")
            input_field=element.find_element(by=By.TAG_NAME, value=xpaths.get("radio_button_option"))
        else:
            input_field=element.find_element(by=By.TAG_NAME, value="input")
        type_string(input_field, correct_answer)
        return True
    except: pass

def answer_question(resume, element, question_list):
    try:
        question_id=None
        daughter_tags = element.find_elements(By.XPATH, ".//*[@*[starts-with(., 'input-')]]")
        if(type(daughter_tags)==list and len(daughter_tags)>=1):
            for attr in daughter_tags[0].get_property('attributes'):
                if attr['value'].startswith('input-'):
                    question_id = attr['value']
                    break
        else:
            question_id = element.find_element(by=By.XPATH, value=xpaths.get("question_text")).get_attribute("id")
        if(question_id==None or question_id in question_list):
            return True, question_id

        question_text=element.find_element(by=By.XPATH, value=xpaths.get("question_text")).text.encode('utf-8').decode('utf-8')
        question_text=remove_non_printable_utf8_chars(question_text)
        
        if("(optional)" in question_text and "LinkedIn Profile" not in question_text):
            logger.info(f'Optional Question Skipped: {question_text}')
            return True, question_text
        else:
            logger.info(f'Question: {question_text}')
        
        # if(f'{index} {question_text}' in question_list or f'{index+1} {question_text}' in question_list):
        #     return True, question_id
        if(len(element.find_elements(by=By.XPATH, value=xpaths.get("radio_button_option")))):
            return radio_button(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.XPATH, value=xpaths.get("checkbox_button_option1")))):
            return checkbox_button(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.XPATH, value=xpaths.get("checkbox_button_option2")))):
            return checkbox_button(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.TAG_NAME, value=tag_names.get("textarea")))):
            return textarea_field(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.XPATH, value=xpaths.get("text_input")))):
            return text_field(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.XPATH, value=xpaths.get("date_input")))):
            return date_field(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.XPATH, value=xpaths.get("numerical_input")))):
            
            return number_field(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.XPATH, value=xpaths.get("select_option")))):
            return select_field(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.XPATH, value=xpaths.get("telephonic_input")))):
            return telephone_field(resume, element, question_text), question_id
        elif(len(element.find_elements(by=By.XPATH, value=xpaths.get("date_input_1")))):
            return date_field_1(resume, element, question_text), question_id
        else:
            return handle_unexpected_cases(resume, element, question_text), question_id
        
    except Exception as e:
        logger.error("Task failed while answering question.")        
        logger.error(e)
        logger.error(traceback.print_exc())
        return False, None

def fix_invalid_int_cast(resume: dict, fallback_value: int = 1) -> int:
    """
    Safely retrieve 'average_experience_years' from resume and cast to int.
    If the value is missing or invalid, return the fallback_value.
    """
    raw_value = resume.get("average_experience_years", "").strip()
    if re.fullmatch(r"\d+", raw_value):
        return int(raw_value)
    return fallback_value