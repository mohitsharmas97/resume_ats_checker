import docx
import PyPDF2
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(filepath):
    text = ""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs])

def clean_text(text):
    return text.replace("\t", " ").replace("\r", "").strip()

def parse_resume_with_ai(text):
    """
    Uses Gemini to structure the raw text into the exact JSON format 
    expected by the frontend.
    """
    # FIXED: Use the correct model name
    model = genai.GenerativeModel('gemini-1.5-flash-latest') 
    
    prompt = f"""
    You are a resume parser. Extract data from the text below and return ONLY valid JSON.
    Do not include Markdown formatting like ```json.
    
    The JSON structure must be exactly this:
    {{
        "personal_info": {{
            "name": "string",
            "email": "string",
            "phone": "string",
            "location": "string",
            "linkedin": "string",
            "github": "string"
        }},
        "summary": "string",
        "skills": ["string", "string"],
        "experience": [
            {{
                "title": "string",
                "company": "string",
                "duration": "string",
                "description": ["bullet point 1", "bullet point 2"]
            }}
        ],
        "education": [
            {{
                "degree": "string",
                "institution": "string",
                "year": "string",
                "gpa": "string"
            }}
        ],
        "projects": [
            {{
                "title": "string",
                "description": ["bullet point 1"]
            }}
        ],
        "certifications": [
             {{
                "name": "string",
                "issuer": "string",
                "date": "string"
            }}
        ]
    }}

    Resume Text:
    {text}
    """
    
    try:
        response = model.generate_content(prompt)
        json_str = response.text.strip()
        
        # Clean up markdown formatting if present
        if json_str.startswith("```json"):
            json_str = json_str[7:-3]
        elif json_str.startswith("```"):
            json_str = json_str[3:-3]
        
        json_str = json_str.strip()
        
        parsed_data = json.loads(json_str)
        print("✅ Successfully parsed resume with AI")
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"Response was: {response.text[:200]}...")
        return create_fallback_structure()
        
    except Exception as e:
        print(f"❌ AI Parsing Critical Error: {e}")
        return create_fallback_structure()

def create_fallback_structure():
    """Returns a valid empty structure if parsing fails"""
    return {
        "personal_info": {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": ""
        },
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": []
    }
    
def parse_resume(filepath):
    try:
        if filepath.lower().endswith(".pdf"):
            text = extract_text_from_pdf(filepath)
        else:
            text = extract_text_from_docx(filepath)
        
        text = clean_text(text)
        
        if not text or len(text) < 50:
            print("⚠️ Warning: Extracted text is too short")
            return create_fallback_structure()
        
        # We use AI here to guarantee the structure matches what the frontend expects
        parsed_data = parse_resume_with_ai(text)
        return parsed_data
        
    except Exception as e:
        print(f"❌ Error in parse_resume: {e}")
        return create_fallback_structure()