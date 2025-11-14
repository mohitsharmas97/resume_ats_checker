from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import json
from resume_parser import parse_resume
from ats_score import calculate_ats_score
from ai_enhancer import enhance_resume_content
from resume_generator import generate_resume
import traceback

# --- App Initialization ---
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/generated'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# --- Create necessary directories ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- HELPER FUNCTION (This was missing) ---
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Static Frontend Routes ---
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend_files(path):
    if "api/" not in path: 
        return send_from_directory('../frontend', path)
    return jsonify({"error": "Not Found"}), 404

# --- API Routes ---

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Resume Builder API is running"})

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # This line was causing the error because allowed_file wasn't defined
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Use PDF or DOCX"}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse resume
        parsed_data = parse_resume(filepath)
        
        # Calculate initial ATS score
        ats_result = calculate_ats_score(parsed_data)
        
        response = {
            "success": True,
            "data": parsed_data,
            "ats_score": ats_result
        }
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in upload_resume: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/manual-entry', methods=['POST'])
def manual_entry():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        ats_result = calculate_ats_score(data)
        
        response = {
            "success": True,
            "data": data,
            "ats_score": ats_result
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error in manual_entry: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/enhance', methods=['POST'])
def enhance_resume():
    try:
        data = request.get_json()
        if not data or 'resume_data' not in data:
            return jsonify({"error": "No resume data provided"}), 400
        
        resume_data = data['resume_data']
        job_description = data.get('job_description', '')
        
        enhanced_data = enhance_resume_content(resume_data, job_description)
        new_ats_result = calculate_ats_score(enhanced_data)
        
        response = {
            "success": True,
            "enhanced_data": enhanced_data,
            "ats_score": new_ats_result
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error in enhance_resume: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data or 'resume_data' not in data:
            return jsonify({"error": "No resume data provided"}), 400
        
        resume_data = data['resume_data']
        template = data.get('template', 'modern')
        
        output_files = generate_resume(resume_data, template, app.config['OUTPUT_FOLDER'])
        
        response = {
            "success": True,
            "files": output_files
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error in generate: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        print(f"Error in download_file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    templates = [
        {"id": "modern", "name": "Modern Professional", "description": "Clean, modern design with clear sections"},
        {"id": "classic", "name": "Classic ATS", "description": "Traditional format optimized for ATS"},
        {"id": "creative", "name": "Creative Professional", "description": "Eye-catching design while maintaining ATS compatibility"}
    ]
    return jsonify({"templates": templates})

if __name__ == '__main__':
    print("Starting Resume Builder API Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)