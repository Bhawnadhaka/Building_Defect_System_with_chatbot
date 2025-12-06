"""
Advanced Building Defect Detection System
Flask Backend with AI Integration
"""

import os
import json
import base64
import logging
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, session, send_from_directory
import torch
from PIL import Image
import io
import gc

# Set PyTorch to use minimal memory
torch.set_num_threads(1)
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Import custom modules
from explanable_ai import ExplainableDefectDetector
from model_testing import load_trained_model

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-this')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

# Create necessary directories
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path('static/temp').mkdir(parents=True, exist_ok=True)
Path('chat_history').mkdir(exist_ok=True)

# Initialize AI models
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
detector = ExplainableDefectDetector(
    model_path='best_defect_model.pth',
    gemini_api_key=GEMINI_API_KEY
)

# Defect information database
DEFECT_INFO = {
    'algae': {
        'severity': 'Low',
        'color': '#4CAF50',
        'icon': '🦠',
        'description': 'Biological growth on surface',
        'avg_cost': '$200-500',
        'urgency': 'Low',
        'repair_time': '1-2 days'
    },
    'minor_crack': {
        'severity': 'Low',
        'color': '#FFC107',
        'icon': '⚠️',
        'description': 'Small surface cracks',
        'avg_cost': '$300-800',
        'urgency': 'Medium',
        'repair_time': '2-3 days'
    },
    'major_crack': {
        'severity': 'High',
        'color': '#F44336',
        'icon': '🚨',
        'description': 'Significant structural damage',
        'avg_cost': '$2000-5000',
        'urgency': 'High',
        'repair_time': '1-2 weeks'
    },
    'peeling': {
        'severity': 'Medium',
        'color': '#FF9800',
        'icon': '📄',
        'description': 'Paint or coating deterioration',
        'avg_cost': '$500-1500',
        'urgency': 'Medium',
        'repair_time': '3-5 days'
    },
    'spalling_aug': {
        'severity': 'High',
        'color': '#E91E63',
        'icon': '💥',
        'description': 'Concrete surface breaking away',
        'avg_cost': '$1500-4000',
        'urgency': 'High',
        'repair_time': '1-3 weeks'
    },
    'stain_aug': {
        'severity': 'Low',
        'color': '#9C27B0',
        'icon': '💧',
        'description': 'Water or chemical staining',
        'avg_cost': '$400-1000',
        'urgency': 'Low',
        'repair_time': '2-4 days'
    },
    'normal': {
        'severity': 'None',
        'color': '#2196F3',
        'icon': '✅',
        'description': 'No defects detected',
        'avg_cost': '$0',
        'urgency': 'None',
        'repair_time': 'N/A'
    }
}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_chat_history(session_id, message, role='user'):
    """Save chat message to history"""
    history_file = Path('chat_history') / f'{session_id}.json'
    
    try:
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {'session_id': session_id, 'created': datetime.now().isoformat(), 'messages': []}
        
        history['messages'].append({
            'role': role,
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")


@app.route('/')
def index():
    """Main page"""
    # Generate session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """Analyze uploaded image for defects"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, WEBP, BMP'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Analyze image using ExplainableAI
        logger.info(f"Analyzing image: {unique_filename}")
        analysis = detector.analyze_image(filepath)
        
        # Transform the response to match frontend expectations
        predicted_class = analysis.get('predicted_class', 'Unknown')
        confidence = analysis.get('confidence', 0)
        
        # Build response
        result = {
            'success': analysis.get('success', True),
            'prediction': predicted_class,
            'confidence': confidence,
            'top_predictions': analysis.get('top_predictions', []),
            'analysis_type': analysis.get('analysis_type', 'unknown')
        }
        
        # Add defect information
        defect_class = predicted_class.lower().replace(' ', '_')
        if defect_class in DEFECT_INFO:
            result['defect_info'] = DEFECT_INFO[defect_class]
        
        # Add heatmap if available
        if 'visual_explanation' in analysis and 'heatmap' in analysis['visual_explanation']:
            result['heatmap'] = analysis['visual_explanation']['heatmap']
        
        # Save only lightweight data to session (no images)
        session['last_analysis'] = {
            'prediction': predicted_class,
            'confidence': confidence,
            'defect_info': result.get('defect_info')
        }
        session['last_image'] = unique_filename
        
        # Convert image to base64 for frontend
        with open(filepath, 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            result['image_data'] = f"data:image/jpeg;base64,{img_base64}"
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chatbot interactions"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        image_context = data.get('image_context', None)
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Save user message
        session_id = session.get('session_id', 'unknown')
        save_chat_history(session_id, message, 'user')
        
        # Get last analysis if available
        last_analysis = session.get('last_analysis', {})
        
        # Build context for Gemini
        context = f"User question: {message}\n\n"
        
        if last_analysis and last_analysis.get('prediction'):
            context += f"Current image analysis:\n"
            context += f"- Defect Type: {last_analysis['prediction']}\n"
            context += f"- Confidence: {last_analysis['confidence']:.1f}%\n"
            
            if 'defect_info' in last_analysis:
                info = last_analysis['defect_info']
                context += f"- Severity: {info['severity']}\n"
                context += f"- Estimated Cost: {info['avg_cost']}\n"
                context += f"- Repair Time: {info['repair_time']}\n"
        
        # Get response from Gemini
        try:
            if detector.gemini_model:
                # Prepare image if available
                image_path = session.get('last_image')
                image_obj = None
                
                if image_path and image_context:
                    full_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
                    if os.path.exists(full_path):
                        image_obj = Image.open(full_path)
                
                # Generate response
                if image_obj:
                    response = detector.gemini_model.generate_content([context, image_obj])
                else:
                    response = detector.gemini_model.generate_content(context)
                
                bot_response = response.text
            else:
                # Fallback responses
                bot_response = generate_fallback_response(message, last_analysis)
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            bot_response = generate_fallback_response(message, last_analysis)
        
        # Save bot response
        save_chat_history(session_id, bot_response, 'assistant')
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def generate_fallback_response(message, analysis):
    """Generate fallback response when Gemini is unavailable"""
    message_lower = message.lower()
    
    # Cost-related questions
    if any(word in message_lower for word in ['cost', 'price', 'expensive', 'money']):
        if analysis.get('defect_info'):
            return f"Based on the detected {analysis['prediction']}, estimated repair cost is {analysis['defect_info']['avg_cost']}. This is an average estimate and actual costs may vary based on location, materials, and labor rates."
        return "Repair costs vary based on defect type, severity, and location. Upload an image for a specific estimate."
    
    # Severity questions
    if any(word in message_lower for word in ['serious', 'severe', 'dangerous', 'urgent', 'bad']):
        if analysis.get('defect_info'):
            severity = analysis['defect_info']['severity']
            urgency = analysis['defect_info']['urgency']
            return f"The detected {analysis['prediction']} has {severity} severity with {urgency} urgency. {analysis['defect_info']['description']}. Repair time: {analysis['defect_info']['repair_time']}."
        return "I need to analyze an image first to determine severity. Please upload a photo."
    
    # Repair questions
    if any(word in message_lower for word in ['repair', 'fix', 'solution', 'how to']):
        if analysis.get('prediction'):
            defect = analysis['prediction']
            return f"For {defect}: Professional assessment recommended. Typical repair time is {analysis.get('defect_info', {}).get('repair_time', 'varies')}. Contact a structural engineer or qualified contractor for detailed repair plan."
        return "Upload an image of the defect for specific repair recommendations."
    
    # General info
    return "I can help you understand building defects, repair costs, and severity. Please upload an image or ask specific questions about the analysis."


@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple images at once"""
    try:
        if 'images' not in request.files:
            return jsonify({'error': 'No images uploaded'}), 400
        
        files = request.files.getlist('images')
        if not files or len(files) == 0:
            return jsonify({'error': 'No files selected'}), 400
        
        results = []
        total_cost_min = 0
        total_cost_max = 0
        defect_counts = {}
        
        for file in files:
            if file and allowed_file(file.filename):
                # Save file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                # Analyze
                analysis = detector.analyze_image(filepath)
                
                # Transform response
                predicted_class = analysis.get('predicted_class', 'Unknown')
                confidence = analysis.get('confidence', 0)
                
                result = {
                    'prediction': predicted_class,
                    'confidence': confidence,
                    'filename': filename
                }
                
                # Add defect info
                defect_class = predicted_class.lower().replace(' ', '_')
                if defect_class in DEFECT_INFO:
                    result['defect_info'] = DEFECT_INFO[defect_class]
                    
                    # Parse cost range
                    cost_str = DEFECT_INFO[defect_class]['avg_cost']
                    if '$' in cost_str and '-' in cost_str:
                        costs = cost_str.replace('$', '').replace(',', '').split('-')
                        total_cost_min += int(costs[0])
                        total_cost_max += int(costs[1])
                    
                    # Count defects
                    defect_counts[defect_class] = defect_counts.get(defect_class, 0) + 1
                
                results.append(result)
        
        # Prepare summary statistics
        summary = {
            'total_images': len(results),
            'defect_distribution': defect_counts,
            'total_cost_range': f"${total_cost_min:,} - ${total_cost_max:,}",
            'high_severity_count': sum(1 for r in results if r.get('defect_info', {}).get('severity') == 'High'),
            'medium_severity_count': sum(1 for r in results if r.get('defect_info', {}).get('severity') == 'Medium'),
            'low_severity_count': sum(1 for r in results if r.get('defect_info', {}).get('severity') in ['Low', 'None']),
        }
        
        return jsonify({
            'results': results,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_chat_history():
    """Retrieve chat history for current session"""
    try:
        session_id = session.get('session_id', 'unknown')
        history_file = Path('chat_history') / f'{session_id}.json'
        
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return jsonify(history)
        
        return jsonify({'session_id': session_id, 'messages': []})
        
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all available chat sessions"""
    try:
        history_dir = Path('chat_history')
        sessions = []
        
        for file in history_dir.glob('*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        'session_id': data.get('session_id', file.stem),
                        'created': data.get('created', 'Unknown'),
                        'message_count': len(data.get('messages', []))
                    })
            except:
                continue
        
        # Sort by creation date (newest first)
        sessions.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'sessions': sessions})
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.errorhandler(413)
def file_too_large(e):
    """Handle file size exceeded error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal error: {e}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("🚀 Starting Building Defect Detection System...")
    logger.info(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"🤖 AI Model loaded: {detector.model is not None}")
    logger.info(f"🔑 Gemini API configured: {detector.gemini_model is not None}")
    
    # Get port from environment variable for deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
