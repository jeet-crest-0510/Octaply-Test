def get_resume_json(user_id, data):

    education=[
        {
        "institute_name": data.get("Education_school"),
        "degree": data.get("Education_degree"),
        "gpa": data.get("Education_gpa"),
        "start_date": data.get("Education_start_date"),
        "end_date": data.get("Education_end_date"),
        "field_of_study": data.get("Education_field_of_study")
        }
    ]
    work_experience=[
        {
        "employer": data.get("Experience_company"),
        "location": data.get("Experience_location"),
        "role": data.get("Experience_title"),
        "type": data.get("Experience_type"),
        "status": data.get("Experience_status"),
        "start_date": data.get("Experience_start"),
        "end_date": data.get("Experience_end"),
        "description": data.get("Experience_description")
        }
    ]
    certifications=[
        {
        "title": data.get("Certification_title"),
        "url": data.get("Certification_issuer"),
        }
    ]
    location={
        "city": data.get("Contact_city"),
        "state": data.get("state"),
        "country": data.get("Contact_country")
    }
    personal_details={
        "name": {
            "first": data.get("Contact_first_name"),
            "last": data.get("Contact_last_name")
        },
        "contact": {
            "email": data.get("Contact_email"),
            "phone": data.get("Contact_phone")
        },
        "gender": data.get("gender"),
        "ethnicity": data.get("ethnicity"),
        "disability_status": data.get("disability_status"),
        "veteran_status": data.get("veteran_status"),
        "lgbtq_plus_status": data.get("lgbtq_plus_status")
    }
    professional_preferences={
        "desired_role": data.get("relevant_role"),
        "employment_type": data.get("employment_type"),
        "work_setting": data.get("work_setting"),
        "sponsorship_needed": data.get("visa_status"),
        "desired_salary": data.get("desired_salary"),
        "seniority_level": data.get("seniority_level"),
        "authorized_to_work_in_us": data.get("authorized_in_us")
    }
    social_links={
        "linkedin_link": data.get("Contact_linkedin")
    }
    skills=data.get("Main_Resume_tools")
    average_experience_years=data.get("average_experience_years")
    if(average_experience_years==None):
        average_experience_years=0
    temp={
        "user_id": str(user_id),
        "education": education,
        "work_experience": work_experience,
        "certifications": certifications,
        "location": location,
        "personal_details": personal_details,
        "professional_preferences": professional_preferences,
        "social_links": social_links,
        "skills": skills,
        "average_experience_years": average_experience_years
    }
    return temp
