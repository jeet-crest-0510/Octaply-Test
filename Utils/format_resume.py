
import phonenumbers
from phonenumbers import geocoder
def get_base_phone_number(international_phone_number):
    try:
        phone_number = phonenumbers.parse(international_phone_number, 'US') # set default country if a phone number is not recognized
        base_phone_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        clean_phone_number = ''.join([char for char in base_phone_number if char.isnumeric()])
        country=geocoder.country_name_for_number(phone_number, "en")
        return clean_phone_number, country
    except phonenumbers.NumberParseException as e:
        return str(e)
def format_resume(resume):
    EDFields=resume.get("EDFields")
    if(type(EDFields)!=list):
        EDFields=[]
    WEFields=resume.get("WEFields")
    if(type(WEFields)!=list):
        WEFields=[]
    certificationsFields=resume.get("certificationsFields")
    if(type(certificationsFields)!=list):
        certificationsFields=[]

    clean_phone_number, phone_number_country=get_base_phone_number(resume.get("mobile"))
    print(f"Phone number: {clean_phone_number}")
    print(f"Phone number country: {phone_number_country}")
    education=[]
    for x in EDFields:
        education.append({
            "institute_name": x.get("instName"),
            "degree": x.get("degree"),
            "gpa": x.get("gpa"),
            "start_date": x.get("startDate"),
            "end_date": x.get("endDate"),
            "field_of_study": x.get("major")
        })

    work_experience=[]
    for x in WEFields[:1]:
        work_experience.append({
        "employer": x.get("company"),
        "location": x.get("location"),
        "role": x.get("position"),
        "type": x.get("expType"),
        "status": x.get("employmentStatus"),
        "start_date": x.get("startDate"),
        "end_date": x.get("endDate")
        # "description": x.get("descp")
        })


    certifications=[]
    for x in certificationsFields:
        certifications.append({
            "title": x.get("title"),
            "url": x.get("link"),
        })



    location={
        "city": resume.get("city"),
        "state": resume.get("state"),
        "country": resume.get("country")
    }
    personal_details={
        "name": {
            "first": resume.get("fname"),
            "last": resume.get("lname")
        },
        "contact": {
            "email": resume.get("key"),
            "phone": clean_phone_number,
            "phone_number_country": phone_number_country
        },
        "gender": resume.get("gender"),
        "ethnicity": resume.get("ethnicity"),
        "disability_status": resume.get("disability"),
        "veteran_status": resume.get("veteran"),
        "lgbtq_plus_status": resume.get("lgbtqPlus")
    }
    professional_preferences={
        "desired_role": resume.get("jobToSearch"),
        "employment_type": resume.get("jobType"),
        "work_setting": resume.get("remoteOrHybrid"),
        "sponsorship_needed": resume.get("requireSponsorship"),
        "desired_salary": resume.get("salary"),
        "seniority_level": resume.get("seniorityLevel"),
        "company_rating": resume.get("companyRating"),
        "company_size": resume.get("companySize"),
        "authorized_to_work_in_us": resume.get("authToWorkInUS"),
        "job_type": resume.get("jobType")
    }
    social_links={
        "github_link": resume.get("githubLink"),
        "linkedin_link": resume.get("linkedInLink")
    }
    skills=resume.get("skillsFields")
    average_experience_years=resume.get("avgExp")
    bio=resume.get("descp")


    new_resume={
        "education": education,
        "work_experience": work_experience,
        "certifications": certifications,
        "location": location,
        "personal_details": personal_details,
        "professional_preferences": professional_preferences,
        "social_links": social_links,
        "skills": skills,
        "average_experience_years": average_experience_years,
        # "bio": bio,
        "key": resume.get("key")
    }
    
    return new_resume