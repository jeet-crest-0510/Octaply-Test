import openai
import re, ast
import datetime
from Utils.constants import OPENAI_API_KEY
from Utils.automation_imports import *
from Utils.prompts import prompt_dict
from Utils.clean_user_data import clean_user_data
openai.api_key = OPENAI_API_KEY


def extract_and_convert_list(s):
    # Find the substring that looks like a list
    match = re.search(r'\[.*?\]', s)
    if match:
        list_str = match.group()
        # Safely evaluate the string to convert it into a list
        return ast.literal_eval(list_str)
    else:
        return None
    

def summarize_question(question, resume, options):
    
    if(type(options)!=list):
        options=[]
    question=question.lower()
    if("disability" in question):
        for option in options:
            if("disability" in option.lower()):
                question="Disability Status?"
                resume={
                    "disability_status": resume.get("personal_details").get("disability_status")
                }
                break
    if("veteran" in question):
        for option in options:
            if("veteran" in option.lower()):
                question="Veteran Status?"
                resume={
                    "veteran_status": resume.get("personal_details").get("veteran_status")
                }
                break
    if("gender" in question):
        for option in options:
            if("female" in option.lower()):
                question="Gender?"
                resume={
                    "gender": resume.get("personal_details").get("gender")
                }
                break
    if("sponsorship" in question and ("require" in question or "need" in question)):
        resume={
            "sponsorship_needed": resume.get("professional_preferences").get("sponsorship_needed")
        }
    if(("authorized to work" in question or "eligible to work" in question) and ("united" in question or " us" in question)):
        resume={
            "authorized_to_work_in_us": resume.get("professional_preferences").get("authorized_to_work_in_us")
        }
    if("years" in question and "experience" in question):
        resume={
            "average_experience_years": (resume.get("average_experience_years"))
        }
    if("salary" in question):
        resume={
            "salary": resume.get("professional_preferences").get("desired_salary")
        }
    if("linkedin profile" in question):
        resume={
            "linkedin_profile": resume.get("social_links").get("linkedin_link")
        }
    
    return question, resume


def handle_expected_cases(question, resume, question_type=None, options=False):
    
    question=question.lower()
    
    if(question_type=="text_question_prompt"):
        
        if("years" in question and "experience" in question):
            return str(resume.get("average_experience_years"))
        elif("full name" in question):
            return f'{resume.get("personal_details").get("name").get("first")} {resume.get("personal_details").get("name").get("last")}'
    
    if(question_type=="single_correct_mcq"):
        if("sponsorship" in question and ("require" in question or "need" in question)):
            require_sponsorship=resume.get("professional_preferences").get("sponsorship_needed")
            for option in options:
                if((require_sponsorship==True and option.lower()=="yes") or (require_sponsorship==False and option.lower()=="no")):
                    return options.index(option)    
        if(("authorized to work" in question or "eligible to work" in question) and ("united" in question or " us" in question)):
            authorized_to_work_in_us=resume.get("professional_preferences").get("authorized_to_work_in_us")
            for option in options:
                if((authorized_to_work_in_us==True and option.lower()=="yes") or (authorized_to_work_in_us==False and option.lower()=="no")):
                    return options.index(option)    
    

def get_gpt_answer(question, resume, question_type=None, options=False):

    expected_val=handle_expected_cases(question, resume, question_type)
    question, resume=summarize_question(question, resume, options)
    if(expected_val!=None):
        return expected_val
    
    prompt=f'Q-{question}\n'
    question_prompt=prompt_dict.get(question_type).replace("\n", " ").replace("  ", " ").strip()
    if(options!=False):
        for option in options:
            prompt+=f'OPTION {options.index(option)}: {option}\n'
    
    prompt+="\n"+str(clean_user_data(resume))
    if("date" in question.lower()):
        prompt+=f"\n Current date is {datetime.datetime.today().date()}."

    messages = [ {"role": "system", "content": question_prompt} ] 
    messages.append( 
        {"role": "user", "content": prompt}, 
    ) 
    chat = openai.ChatCompletion.create( 
        model="gpt-3.5-turbo", messages=messages 
    ) 
    reply = chat.choices[0].message.content 
    print(len(question_prompt+prompt)//4)
    if(question_type=="single_correct_mcq"):
        match = re.search(r'\d+', reply)
        if match:
            return int(match.group())
        else:
            return reply
    elif(question_type=="multiple_correct_mcq"):
        return extract_and_convert_list(reply)
    elif(question_type=="text_question_prompt"):
        if("NO-ANSWER" in reply):
            return '-'
    elif question_type == "numeric_question_prompt":
        print("inside numberic", reply)
        if "0" in reply:
            return '0'
        # Extract only num value 
        match = re.search(r'-?\d+(\.\d+)?', reply)
        if match:
            return int(float(match.group()))
        else:
            return 0
    return reply