email_template={
	"zero_submit":"""
	Hi {username},
	<br>
	Oops! We noticed that no job applications were submitted on your behalf today and we apologize for this oversight! To make up for it, we’ll be submitting additional applications tomorrow to keep you on track. Thank you for your patience and understanding! :)
	<br><br>
	Best regards,<br>
	The Octaply Team
	""",
	"less_six":"""
	Hi {username},
	<br>
	We noticed that only a few job applications were submitted on your behalf today, which is below the daily goal of 10-12 applications. To make up for it, we’ll increase the number of applications over the next few days to ensure you reach your target. Thank you for your patience and understanding!
	<br><br>
	Best regards,<br>
	The Octaply Team
	""",
	"resume_fail":"""
	Hi {username},
	<br>
	We noticed that you experienced an issue submitting your resume. Our team has fixed the problem, and you should now be able to submit your resume without any issues. If you continue to experience problems, please reach out to our support team. Thanks for your patience!
	<br><br>
	Best regards,<br>
	The Octaply Team
	"""
}

email_sub={
	"zero_submit":"No Applications Submitted? We’re Making It Right!",
	"less_six":"We’re Working to Reach Your Daily Application Goal!",
	"resume_fail":"We’ve Fixed Your Resume Issue!"
}