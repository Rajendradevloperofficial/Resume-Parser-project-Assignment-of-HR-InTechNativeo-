from django.shortcuts import render
from django.http import JsonResponse
import PyPDF2
import docx
from .forms import ResumeUploadForm
import re
from .education import study
from .skills import skill


def extract_info_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_info_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def parse_resume(text):
    data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "contact_number": extract_contact_number(text),
        "location": extract_location(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "skills": extract_skills(text),
    }
    return data

def extract_name(text):
    lines = text.splitlines()
    for line in lines[:10]:
        if re.match(r"^[A-Z][A-Z\s]+$", line.strip()):
            return line.strip()
        if re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)*$", line.strip()):
            return line.strip()
    return "Name not found"


def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(email_pattern, text)
    return match.group(0) if match else "Email not found"


def extract_contact_number(text):
    phone_pattern = r"\+?\d[\d -]{8,12}\d"
    match = re.search(phone_pattern, text)
    return match.group(0) if match else "Contact number not found"


def extract_location(text):
    location_pattern = r"\b(?:[A-Z][a-z]+(?: [A-Z][a-z]+)?) (?:Street|Avenue|City|Town|State|Country|Sector|sector)\b|\b(?:[A-Za-z0-9\s]+Sector|sector [0-9]+ [A-Za-z]+)\b"
    match = re.search(location_pattern, text, re.IGNORECASE)
    return match.group(0) if match else "Location not found"


def extract_education(text):
    education_keywords = study

    matches = [
        keyword for keyword in education_keywords if keyword.lower() in text.lower()
    ]
    return ",".join(matches) if matches else "Education not found"


def extract_experience(text):
    experience_pattern = r"\b\d{1-5}years|year|exprieance? of experience\b"
    match = re.search(experience_pattern, text, re.IGNORECASE)
    if match:
        return match.group(0)
    if "internship" in text.lower():
        return "Internship experience found"
    return "Experience not found"


def extract_skills(text):
    skill_keywords = skill
    return [skill for skill in skill_keywords if skill.lower() in text.lower()]


def upload_resume(request):
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES["resume"]
            if resume_file.size > 5 * 1024 * 1024:
                return render(
                    request,
                    "upload.html",
                    {"form": form, "error": "File size exceeds 5MB."},
                )

            if resume_file.name.endswith(".pdf"):
                text = extract_info_from_pdf(resume_file)
            elif resume_file.name.endswith(".docx"):
                text = extract_info_from_docx(resume_file)

            else:
                return render(
                    request,
                    "upload.html",
                    {"form": form, "error": "Invalid file type."},
                )

            extracted_data = parse_resume(text)
            
            return render(request, "edit_form.html", {"data": extracted_data})

    else:
        form = ResumeUploadForm()
    return render(request, "upload.html", {"form": form})


def save_data(request):
    if request.method == "POST":

        name = request.POST.get("name", "Name not found")
        email = request.POST.get("email", "Email not found")
        contact_number = request.POST.get("contact_number", "Contact number not found")
        location = request.POST.get("location", "Location not found")
        education = request.POST.get("education", "Education not found")
        experience = request.POST.get("experience", "Experience not found")
        skills = request.POST.get("skills", "Skills not found")

        updated_data = {
            "name": name,
            "email": email,
            "contact_number": contact_number,
            "location": location,
            "education": education,
            "experience": experience,
            "skills": skills,
        }

        return render(request, "confirmation.html", {"data": updated_data})

    return JsonResponse({"error": "Invalid request"}, status=400)
