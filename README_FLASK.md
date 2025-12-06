# 🏗️ Building Defect Detection System

An advanced AI-powered web application for automated detection and analysis of building defects using deep learning, computer vision, and explainable AI techniques.

## 🌟 Features

### Core Functionality
- **🔍 Real-time Defect Detection**: Upload images for instant AI-powered analysis
- **🎯 91.45% Accuracy**: EfficientNet-B0 model trained on 7 defect categories
- **🔥 GradCAM Visualizations**: See exactly where the AI detected defects
- **🤖 AI Chatbot**: Interactive Gemini-powered assistant for defect queries
- **📊 Batch Processing**: Analyze multiple images simultaneously
- **📈 Analytics Dashboard**: Comprehensive statistics and defect distribution charts
- **💾 Chat History**: Persistent conversation storage with session management

### Defect Categories
1. **Algae** - Biological growth (Low severity)
2. **Minor Crack** - Small surface cracks (Low severity)
3. **Major Crack** - Significant structural damage (High severity)
4. **Peeling** - Paint/coating deterioration (Medium severity)
5. **Spalling** - Concrete surface breaking (High severity)
6. **Staining** - Water/chemical stains (Low severity)
7. **Normal** - No defects detected

### Advanced Features
- **Explainable AI**: GradCAM heatmaps show decision reasoning
- **Confidence Scoring**: Intelligent routing based on prediction certainty
- **Cost Estimation**: Automatic repair cost calculations
- **Severity Assessment**: Priority-based defect categorization
- **Multi-language Support**: English and Hindi translations
- **Responsive Design**: Modern UI with animations and gradients
- **Dark Theme**: Toggle between light and dark modes

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0** - Web framework
- **PyTorch 2.5.0** - Deep learning
- **EfficientNet-B0** - CNN architecture
- **Google Gemini AI** - Chatbot integration
- **OpenCV** - Image processing
- **Matplotlib** - Visualization

### Frontend
- **HTML5** - Structure
- **CSS3** - Advanced styling with gradients and animations
- **JavaScript (ES6+)** - Dynamic interactions
- **Chart.js** - Data visualization
- **Font Awesome** - Icons
- **Google Fonts** - Typography (Inter)

### DevOps
- **python-dotenv** - Environment management
- **Werkzeug** - WSGI utilities

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone or Navigate to Project
```powershell
cd C:\Users\SUN\OneDrive\Desktop\Building_Defects
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
The `.env` file is already configured with:
```
GEMINI_API_KEY=AIzaSyD2ssTYntdiqTxDZjwy3-q4JG3SSxFmMO4
FLASK_SECRET_KEY=your-secret-key-here-change-in-production
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

**Note**: Change `FLASK_SECRET_KEY` in production!

### Step 5: Verify Model File
Ensure `best_defect_model.pth` is in the project root directory.

## 🚀 Running the Application

### Method 1: Direct Flask Run
```powershell
python flask_app.py
```

### Method 2: Flask CLI
```powershell
$env:FLASK_APP="flask_app.py"
flask run --host=0.0.0.0 --port=5000
```

### Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

## 📖 Usage Guide

### Single Image Analysis
1. Click **"Start Analysis"** in the hero section
2. Upload an image (JPG, PNG, WEBP, BMP - max 16MB)
3. Wait for AI analysis (typically < 2 seconds)
4. View results:
   - Original image
   - GradCAM heatmap
   - Defect classification
   - Confidence score
   - Severity level
   - Estimated repair cost
   - Repair timeline

### Batch Processing
1. Navigate to **"Batch Process"** section
2. Select multiple images
3. View comprehensive dashboard:
   - Total images analyzed
   - High severity count
   - Total estimated costs
   - Defect distribution chart
   - Individual results for each image

### AI Chat Assistant
1. Go to **"Chat"** section
2. Ask questions about:
   - Defect types and severity
   - Repair costs and timelines
   - Maintenance recommendations
   - Building safety concerns
3. Use quick action buttons for common queries
4. Toggle image context to include/exclude last analyzed image

### Chat History
- Sessions are automatically saved to `chat_history/` folder
- View past conversations in the sidebar
- Create new sessions anytime
- Clear current chat when needed

## 📁 Project Structure

```
Building_Defects/
├── flask_app.py              # Main Flask application
├── explanable_ai.py          # ExplainableAI with GradCAM
├── model_testing.py          # Model loading utilities
├── model_train.py            # Training script
├── gemini_config.py          # Gemini API configuration
├── best_defect_model.pth     # Trained model (91.45% accuracy)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── README.md                 # This file
│
├── templates/
│   └── index.html            # Main HTML template
│
├── static/
│   ├── css/
│   │   └── style.css         # Advanced CSS styling
│   └── js/
│       └── script.js         # JavaScript functionality
│
├── uploads/                  # Uploaded images
├── chat_history/             # Saved chat sessions
└── Data_split/              # Training/validation/test data
    ├── train/
    ├── val/
    └── test/
```

## 🎨 UI Features

### Design Elements
- **Modern Gradient Backgrounds**: Purple, blue, and multi-color gradients
- **Smooth Animations**: Fade-in, slide-in, float effects
- **Hover Effects**: Scale transforms, color transitions
- **Glass Morphism**: Backdrop blur effects
- **Responsive Layout**: Grid-based design for all screen sizes
- **Custom Shadows**: Multi-level depth perception

### Color Palette
- **Primary**: #2563eb (Blue)
- **Secondary**: #0891b2 (Cyan)
- **Accent**: #8b5cf6 (Purple)
- **Success**: #10b981 (Green)
- **Warning**: #f59e0b (Orange)
- **Danger**: #ef4444 (Red)

## 🔒 Security Considerations

### Production Checklist
- [ ] Change `FLASK_SECRET_KEY` in `.env`
- [ ] Set `debug=False` in `flask_app.py`
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Enable HTTPS/SSL
- [ ] Secure Gemini API key
- [ ] Implement user authentication (if needed)
- [ ] Sanitize file uploads
- [ ] Add input validation

## 📊 Model Information

### Architecture
- **Base Model**: EfficientNet-B0 (pretrained on ImageNet)
- **Custom Classifier**: 256-neuron hidden layer + Dropout(0.3)
- **Input Size**: 224x224 RGB
- **Training**: Transfer learning with frozen early layers

### Performance Metrics
- **Validation Accuracy**: 91.45%
- **Classes**: 7 defect types
- **Inference Time**: < 2 seconds per image
- **Batch Processing**: Parallel analysis supported

### Training Data
- Located in `Data_split/` directory
- Organized by class (train/val/test split)
- Augmented dataset for better generalization

## 🤝 API Endpoints

### Image Analysis
```
POST /api/analyze
Content-Type: multipart/form-data
Body: { image: File }
Response: { prediction, confidence, heatmap, defect_info, top_predictions }
```

### Batch Analysis
```
POST /api/batch-analyze
Content-Type: multipart/form-data
Body: { images: File[] }
Response: { results[], summary }
```

### Chat
```
POST /api/chat
Content-Type: application/json
Body: { message: string, image_context: boolean }
Response: { response: string, timestamp: string }
```

### Chat History
```
GET /api/history
Response: { session_id, messages[] }
```

### Sessions List
```
GET /api/sessions
Response: { sessions[] }
```

## 🐛 Troubleshooting

### Common Issues

**1. Module Import Errors**
```powershell
pip install -r requirements.txt --upgrade
```

**2. Model Not Found**
Ensure `best_defect_model.pth` is in the project root.

**3. Gemini API Errors**
Check your API key in `.env` and verify quota limits.

**4. Port Already in Use**
```powershell
# Change port in flask_app.py or use:
flask run --port=5001
```

**5. Upload Folder Permissions**
```powershell
mkdir uploads
mkdir chat_history
```

## 📝 Future Enhancements

### Planned Features
- [ ] Before/After comparison mode
- [ ] Advanced XAI Suite (SHAP, LIME)
- [ ] Building database with risk scoring
- [ ] Trend analysis and predictions
- [ ] PDF report generation
- [ ] Multi-user authentication
- [ ] Mobile app version
- [ ] Real-time video analysis
- [ ] Integration with building management systems

## 👨‍💻 Development

### Running in Development Mode
```powershell
$env:FLASK_ENV="development"
python flask_app.py
```

### Logging
Logs are printed to console with levels:
- INFO: General operations
- WARNING: Potential issues
- ERROR: Failures requiring attention

## 📄 License

This project is created for academic/educational purposes.

## 🙏 Acknowledgments

- **PyTorch Team** - Deep learning framework
- **Google** - Gemini AI API
- **EfficientNet Authors** - Model architecture
- **Flask Community** - Web framework
- **Chart.js** - Data visualization library

## 📞 Contact

For questions or issues:
- Email: info@defectai.com
- Website: www.defectai.com

---

**Built with ❤️ for Advanced Building Analysis**

Last Updated: December 6, 2025
