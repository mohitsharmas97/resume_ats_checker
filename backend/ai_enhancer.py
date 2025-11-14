import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def enhance_resume_content(resume_data, job_description=""):
    # FIXED: Use the correct model name
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    # Convert resume data to string for the prompt
    resume_json = json.dumps(resume_data, indent=2)
    
    prompt = f"""
    You are an expert Resume Writer and ATS Optimization Specialist.
    
    Task: Enhance the following resume JSON data. 
    1. Improve grammar, clarity, and impact of bullet points. Use strong action verbs.
    2. Optimize for ATS keywords based on the provided Job Description (if any).
    3. Return the output as valid JSON matching the exact structure of the input.
    4. Do not add Markdown formatting like ```json.
    5. Keep all existing fields, just improve the content.
    
    Job Description:
    {job_description if job_description else "General Professional Software/Tech Role"}
    
    Input Resume JSON:
    {resume_json}
    
    Return ONLY the enhanced JSON, no explanations.
    """
    
    try:
        response = model.generate_content(prompt)
        enhanced_text = response.text.strip()
        
        # Clean up markdown formatting
        if enhanced_text.startswith("```json"):
            enhanced_text = enhanced_text[7:-3]
        elif enhanced_text.startswith("```"):
            enhanced_text = enhanced_text[3:-3]
            
        enhanced_text = enhanced_text.strip()
        
        enhanced_json = json.loads(enhanced_text)
        print("✅ Successfully enhanced resume with AI")
        return enhanced_json
        
    except json.JSONDecodeError as e:
        print(f"❌ Enhancement JSON Error: {e}")
        print(f"Response was: {response.text[:200]}...")
        return resume_data
        
    except Exception as e:
        print(f"❌ Enhancement Error: {e}")
        return resume_data  # Return original if AI fails