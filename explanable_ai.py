

import torch
import torch.nn.functional as F
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import io
import base64
import google.generativeai as genai
import os
from typing import Dict, List, Tuple, Optional
import logging

# Import your existing model
from model_testing import load_trained_model, EfficientNetDefectClassifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExplainableDefectDetector:
    """Advanced AI system combining custom model + Gemini API"""
    
    def __init__(self, model_path='best_defect_model.pth', gemini_api_key=None):
        """Initialize the explainable AI system"""
        # Load your trained model
        try:
            self.model, self.class_names = load_trained_model(model_path)
            self.model.eval()
            logger.info("✅ Custom model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self.model, self.class_names = None, []
        
        # Configure Gemini API
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✅ Gemini API configured")
        else:
            self.gemini_model = None
            logger.warning("⚠️ Gemini API not configured - using fallback explanations")
        
        # Confidence thresholds
        self.HIGH_CONFIDENCE = 0.65
        self.LOW_CONFIDENCE = 0.35
        
        # Defect severity mapping
        self.severity_mapping = {
            'normal': {'severity': 'none', 'color': '#28a745', 'priority': 0},
            'minor_crack': {'severity': 'low', 'color': '#ffc107', 'priority': 2},
            'stain_aug': {'severity': 'low', 'color': '#ffc107', 'priority': 1},
            'algae': {'severity': 'medium', 'color': '#fd7e14', 'priority': 3},
            'peeling': {'severity': 'medium', 'color': '#fd7e14', 'priority': 4},
            'major_crack': {'severity': 'high', 'color': '#dc3545', 'priority': 6},
            'spalling_aug': {'severity': 'high', 'color': '#dc3545', 'priority': 5}
        }

    def analyze_image(self, image_path: str, building_context: Dict = None, language: str = 'english') -> Dict:
        """
        Main analysis function - intelligently routes between custom model and Gemini
        """
        try:
            # Step 1: Get prediction from your custom model
            if self.model is None:
                return self._gemini_fallback_analysis(image_path, building_context, language)
            
            prediction_result = self._get_model_prediction(image_path)
            
            # Step 2: Intelligent routing based on confidence
            if prediction_result['confidence'] >= self.HIGH_CONFIDENCE:
                # High confidence - use custom model with explanations
                return self._generate_high_confidence_analysis(
                    image_path, prediction_result, building_context, language
                )
            elif prediction_result['confidence'] >= self.LOW_CONFIDENCE:
                # Medium confidence - hybrid analysis
                return self._generate_hybrid_analysis(
                    image_path, prediction_result, building_context, language
                )
            else:
                # Low confidence - use Gemini API
                return self._gemini_comprehensive_analysis(
                    image_path, prediction_result, building_context, language
                )
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {
                'error': f'Analysis failed: {str(e)}',
                'success': False
            }

    def _get_model_prediction(self, image_path: str) -> Dict:
        """Get prediction from your trained model"""
        from torchvision import transforms
        
        # Prepare image
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0)
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
        # Get top 3 predictions
        top_probs, top_indices = torch.topk(probabilities, 3)
        
        top_predictions = []
        for i in range(3):
            class_name = self.class_names[top_indices[0][i]]
            prob = top_probs[0][i].item()
            top_predictions.append({
                'class': class_name,
                'probability': prob,
                'severity': self.severity_mapping.get(class_name, {}).get('severity', 'unknown')
            })
        
        return {
            'predicted_class': self.class_names[predicted.item()],
            'confidence': confidence.item(),
            'top_predictions': top_predictions,
            'raw_outputs': outputs,
            'input_tensor': input_tensor
        }

    def _generate_high_confidence_analysis(self, image_path: str, prediction: Dict, 
                                         building_context: Dict, language: str) -> Dict:
        """Generate analysis for high-confidence predictions"""
        
        predicted_class = prediction['predicted_class']
        confidence = prediction['confidence']
        
        # Generate heatmap
        heatmap_b64 = self._generate_gradcam_heatmap(
            image_path, prediction['input_tensor'], prediction['raw_outputs']
        )
        
        # Get defect information
        defect_info = self.severity_mapping.get(predicted_class, {})
        
        # Generate recommendations
        recommendations = self._get_defect_recommendations(predicted_class, building_context, language)
        
        return {
            'success': True,
            'analysis_type': 'high_confidence_custom_model',
            'predicted_class': predicted_class,
            'confidence': round(confidence * 100, 2),
            'severity': defect_info.get('severity', 'unknown'),
            'severity_color': defect_info.get('color', '#6c757d'),
            'priority': defect_info.get('priority', 0),
            'top_predictions': prediction['top_predictions'],
            'visual_explanation': {
                'heatmap': heatmap_b64,
                'explanation': self._get_visual_explanation(predicted_class, language)
            },
            'recommendations': recommendations,
            'technical_details': {
                'model_confidence': confidence,
                'analysis_method': 'Custom EfficientNet-B0 + GradCAM',
                'trained_classes': len(self.class_names)
            }
        }

    def _generate_hybrid_analysis(self, image_path: str, prediction: Dict, 
                                building_context: Dict, language: str) -> Dict:
        """Combine custom model with Gemini insights"""
        
        # Get base analysis from custom model
        base_analysis = self._generate_high_confidence_analysis(
            image_path, prediction, building_context, language
        )
        
        # Add Gemini insights if available
        if self.gemini_model:
            gemini_insights = self._get_gemini_insights(image_path, prediction['predicted_class'], language)
            base_analysis['gemini_insights'] = gemini_insights
            base_analysis['analysis_type'] = 'hybrid_custom_model_gemini'
        
        return base_analysis

    def _gemini_comprehensive_analysis(self, image_path: str, prediction: Dict, 
                                     building_context: Dict, language: str) -> Dict:
        """Use Gemini for comprehensive analysis of uncertain predictions"""
        
        if not self.gemini_model:
            return self._fallback_low_confidence_analysis(prediction, language)
        
        try:
            # Prepare image for Gemini
            image = Image.open(image_path)
            
            # Create comprehensive prompt
            prompt = self._create_gemini_prompt(prediction, building_context, language)
            
            # Get Gemini analysis
            response = self.gemini_model.generate_content([prompt, image])
            
            return {
                'success': True,
                'analysis_type': 'gemini_comprehensive',
                'confidence': round(prediction['confidence'] * 100, 2),
                'gemini_analysis': response.text,
                'custom_model_suggestion': prediction['predicted_class'],
                'note': 'Low confidence from custom model - using AI comprehensive analysis',
                'recommendations': self._extract_recommendations_from_gemini(response.text, language),
                'visual_explanation': {
                    'explanation': 'AI-powered comprehensive visual analysis provided'
                }
            }
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return self._fallback_low_confidence_analysis(prediction, language)

    def _gemini_fallback_analysis(self, image_path: str, building_context: Dict, language: str) -> Dict:
        """Fallback when custom model is not available"""
        
        if not self.gemini_model:
            return {
                'error': 'Both custom model and Gemini API unavailable',
                'success': False
            }
        
        try:
            image = Image.open(image_path)
            prompt = self._create_fallback_gemini_prompt(building_context, language)
            
            response = self.gemini_model.generate_content([prompt, image])
            
            return {
                'success': True,
                'analysis_type': 'gemini_only',
                'gemini_analysis': response.text,
                'note': 'Custom model unavailable - using Gemini AI only',
                'recommendations': self._extract_recommendations_from_gemini(response.text, language)
            }
            
        except Exception as e:
            logger.error(f"Gemini fallback error: {e}")
            return {
                'error': 'All analysis methods failed',
                'success': False
            }

    def _generate_gradcam_heatmap(self, image_path: str, input_tensor: torch.Tensor, 
                                outputs: torch.Tensor) -> str:
        """Generate GradCAM heatmap for visual explanation"""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            # Get the last convolutional layer
            target_layer = self.model.backbone.features[-1]
            
            # Register hook
            gradients = []
            activations = []
            
            def backward_hook(module, grad_input, grad_output):
                gradients.append(grad_output[0])
                
            def forward_hook(module, input, output):
                activations.append(output)
            
            backward_handle = target_layer.register_backward_hook(backward_hook)
            forward_handle = target_layer.register_forward_hook(forward_hook)
            
            # Forward pass
            self.model.zero_grad()
            outputs = self.model(input_tensor)
            class_idx = outputs.argmax(dim=1)
            
            # Backward pass
            outputs[0, class_idx].backward()
            
            # Generate heatmap
            gradients_val = gradients[0][0].cpu().data.numpy()
            activations_val = activations[0][0].cpu().data.numpy()
            
            weights = np.mean(gradients_val, axis=(1, 2))
            heatmap = np.zeros(activations_val.shape[1:], dtype=np.float32)
            
            for i, w in enumerate(weights):
                heatmap += w * activations_val[i, :, :]
            
            heatmap = np.maximum(heatmap, 0)
            heatmap = cv2.resize(heatmap, (224, 224))
            heatmap = heatmap / np.max(heatmap)
            
            # Overlay on original image
            original_image = cv2.imread(image_path)
            original_image = cv2.resize(original_image, (224, 224))
            
            heatmap_colored = cm.jet(heatmap)[:, :, :3]
            overlaid = 0.6 * original_image/255.0 + 0.4 * heatmap_colored
            
            # Convert to base64
            plt.figure(figsize=(8, 6))
            plt.imshow(overlaid)
            plt.axis('off')
            plt.title('Defect Detection Heatmap')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            
            heatmap_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Clean up
            backward_handle.remove()
            forward_handle.remove()
            plt.close()
            
            return heatmap_b64
            
        except Exception as e:
            logger.error(f"Heatmap generation error: {e}")
            return None

    def _create_gemini_prompt(self, prediction: Dict, building_context: Dict, language: str) -> str:
        """Create comprehensive prompt for Gemini analysis"""
        
        if language == 'hindi':
            base_prompt = """
            इस भवन की छवि का विस्तृत विश्लेषण करें। मैं एक AI मॉडल का उपयोग कर रहा हूँ लेकिन इसका विश्वास स्तर कम है।
            
            मेरे AI मॉडल का सुझाव: {predicted_class} (विश्वास: {confidence}%)
            
            कृपया बताएं:
            1. यह छवि भवन से संबंधित है या नहीं
            2. कोई भी दोष या समस्याएं जो दिखाई दे रही हैं
            3. समस्या की गंभीरता (कम/मध्यम/उच्च)
            4. सुधार के सुझाव और अनुमानित लागत
            5. सुरक्षा चेतावनियां यदि कोई हों
            
            भवन की जानकारी: {building_context}
            """
        else:
            base_prompt = """
            Please provide a comprehensive analysis of this building image. I'm using an AI model but its confidence is low.
            
            My AI model suggests: {predicted_class} (Confidence: {confidence}%)
            
            Please analyze:
            1. Whether this image is building-related or not
            2. Any defects or issues visible in the image
            3. Severity level (low/medium/high)
            4. Repair recommendations and estimated costs
            5. Safety warnings if any
            6. If this shows defects beyond typical categories (cracks, stains, algae, peeling, spalling)
            
            Building context: {building_context}
            """
        
        return base_prompt.format(
            predicted_class=prediction['predicted_class'],
            confidence=round(prediction['confidence'] * 100, 1),
            building_context=building_context or "Not provided"
        )

    def _create_fallback_gemini_prompt(self, building_context: Dict, language: str) -> str:
        """Create prompt when custom model is unavailable"""
        
        if language == 'hindi':
            return """
            इस छवि में भवन की समस्याओं का पूर्ण विश्लेषण करें:
            
            1. यह भवन की छवि है या नहीं
            2. कोई भी दोष दिखाई दे रहे हैं (दरारें, दाग, काई, छिलना, आदि)
            3. समस्या की गंभीरता
            4. सुधार के सुझाव
            5. अनुमानित लागत
            6. सुरक्षा सावधानियां
            
            भवन की जानकारी: {building_context}
            """.format(building_context=building_context or "उपलब्ध नहीं")
        else:
            return """
            Please provide a complete building defect analysis of this image:
            
            1. Is this a building-related image?
            2. What defects are visible (cracks, stains, algae, peeling, spalling, etc.)?
            3. Severity assessment
            4. Repair recommendations
            5. Estimated costs
            6. Safety precautions
            
            Building context: {building_context}
            """.format(building_context=building_context or "Not provided")

    def _get_defect_recommendations(self, defect_class: str, building_context: Dict, language: str) -> Dict:
        """Get specific recommendations for detected defects"""
        
        recommendations = {
            'english': {
                'algae': {
                    'immediate': 'Clean with anti-fungal solution',
                    'longterm': 'Improve ventilation, apply waterproof coating',
                    'cost': '$100-300',
                    'urgency': 'Medium'
                },
                'major_crack': {
                    'immediate': 'Structural inspection required immediately',
                    'longterm': 'Professional repair with concrete filling/steel reinforcement',
                    'cost': '$500-2000',
                    'urgency': 'High'
                },
                'minor_crack': {
                    'immediate': 'Monitor crack progression',
                    'longterm': 'Seal with appropriate filler, repaint',
                    'cost': '$50-150',
                    'urgency': 'Low'
                },
                'peeling': {
                    'immediate': 'Remove loose paint',
                    'longterm': 'Surface preparation and repainting',
                    'cost': '$200-500',
                    'urgency': 'Medium'
                },
                'spalling_aug': {
                    'immediate': 'Safety barriers if concrete falling',
                    'longterm': 'Professional concrete repair/replacement',
                    'cost': '$800-3000',
                    'urgency': 'High'
                },
                'stain_aug': {
                    'immediate': 'Identify stain source',
                    'longterm': 'Clean and seal, address moisture issues',
                    'cost': '$100-400',
                    'urgency': 'Low'
                },
                'normal': {
                    'immediate': 'No immediate action required',
                    'longterm': 'Regular maintenance schedule',
                    'cost': '$0',
                    'urgency': 'None'
                }
            },
            'hindi': {
                'algae': {
                    'immediate': '[translate:एंटी-फंगल समाधान से सफाई करें]',
                    'longterm': '[translate:वेंटिलेशन सुधारें, वाटरप्रूफ कोटिंग लगाएं]',
                    'cost': '₹8,000-25,000',
                    'urgency': '[translate:मध्यम]'
                },
                'major_crack': {
                    'immediate': '[translate:तुरंत संरचनात्मक निरीक्षण आवश्यक]',
                    'longterm': '[translate:कंक्रीट भराव/स्टील सुदृढीकरण के साथ पेशेवर मरम्मत]',
                    'cost': '₹40,000-1,60,000',
                    'urgency': '[translate:उच्च]'
                },
                'minor_crack': {
                    'immediate': '[translate:दरार की प्रगति पर नजर रखें]',
                    'longterm': '[translate:उपयुक्त फिलर से सील करें, पुनः पेंट करें]',
                    'cost': '₹4,000-12,000',
                    'urgency': '[translate:कम]'
                },
                'peeling': {
                    'immediate': '[translate:ढीला पेंट हटाएं]',
                    'longterm': '[translate:सतह की तैयारी और पुनः पेंटिंग]',
                    'cost': '₹16,000-40,000',
                    'urgency': '[translate:मध्यम]'
                },
                'spalling_aug': {
                    'immediate': '[translate:यदि कंक्रीट गिर रहा है तो सुरक्षा बाधाएं]',
                    'longterm': '[translate:पेशेवर कंक्रीट मरम्मत/प्रतिस्थापन]',
                    'cost': '₹65,000-2,40,000',
                    'urgency': '[translate:उच्च]'
                },
                'stain_aug': {
                    'immediate': '[translate:दाग का स्रोत पहचानें]',
                    'longterm': '[translate:सफाई और सील, नमी की समस्याओं का समाधान]',
                    'cost': '₹8,000-32,000',
                    'urgency': '[translate:कम]'
                },
                'normal': {
                    'immediate': '[translate:कोई तत्काल कार्रवाई आवश्यक नहीं]',
                    'longterm': '[translate:नियमित रखरखाव कार्यक्रम]',
                    'cost': '₹0',
                    'urgency': '[translate:कोई नहीं]'
                }
            }
        }
        
        return recommendations.get(language, recommendations['english']).get(defect_class, {
            'immediate': 'Consult building professional',
            'longterm': 'Professional assessment required',
            'cost': 'Varies',
            'urgency': 'Medium'
        })

    def _get_visual_explanation(self, predicted_class: str, language: str) -> str:
        """Get visual explanation for the prediction"""
        
        explanations = {
            'english': {
                'algae': 'Green/dark patches indicate moisture and biological growth',
                'major_crack': 'Significant structural crack requiring immediate attention',
                'minor_crack': 'Small surface crack, monitor for progression',
                'peeling': 'Paint/coating separation from surface',
                'spalling_aug': 'Concrete deterioration with material loss',
                'stain_aug': 'Discoloration indicating moisture or chemical damage',
                'normal': 'No significant defects detected in this area'
            },
            'hindi': {
                'algae': '[translate:हरे/काले धब्बे नमी और जैविक वृद्धि दर्शाते हैं]',
                'major_crack': '[translate:महत्वपूर्ण संरचनात्मक दरार जिसमें तत्काल ध्यान चाहिए]',
                'minor_crack': '[translate:छोटी सतही दरार, प्रगति पर नजर रखें]',
                'peeling': '[translate:सतह से पेंट/कोटिंग का अलग होना]',
                'spalling_aug': '[translate:सामग्री हानि के साथ कंक्रीट का क्षरण]',
                'stain_aug': '[translate:नमी या रासायनिक क्षति दर्शाने वाला रंग परिवर्तन]',
                'normal': '[translate:इस क्षेत्र में कोई महत्वपूर्ण दोष नहीं मिला]'
            }
        }
        
        return explanations.get(language, explanations['english']).get(predicted_class, 
            'Analysis available through comprehensive AI assessment')

    def _extract_recommendations_from_gemini(self, gemini_text: str, language: str) -> Dict:
        """Extract structured recommendations from Gemini response"""
        # This is a simplified extraction - you can make it more sophisticated
        return {
            'immediate': 'See AI analysis for immediate actions',
            'longterm': 'See AI analysis for long-term solutions',
            'cost': 'Cost estimation provided in AI analysis',
            'urgency': 'Priority level mentioned in AI analysis'
        }

    def _fallback_low_confidence_analysis(self, prediction: Dict, language: str) -> Dict:
        """Fallback when both model confidence is low and Gemini is unavailable"""
        return {
            'success': True,
            'analysis_type': 'low_confidence_fallback',
            'predicted_class': prediction['predicted_class'],
            'confidence': round(prediction['confidence'] * 100, 2),
            'note': 'Low confidence prediction - professional inspection recommended',
            'recommendations': {
                'immediate': 'Consult a building professional for accurate assessment',
                'longterm': 'Professional inspection recommended',
                'cost': 'Varies based on professional assessment',
                'urgency': 'Medium - seek expert opinion'
            },
            'visual_explanation': {
                'explanation': 'Model confidence too low for reliable visual explanation'
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the explainable detector
    detector = ExplainableDefectDetector(
        model_path='best_defect_model.pth',
        gemini_api_key=None  # Add your Gemini API key here
    )
    
    # Test with a sample image
    test_image = "sample_defect_image.jpg"  # Replace with actual image path
    building_context = {
        'age': 15,
        'type': 'residential',
        'location': 'Mumbai',
        'climate': 'humid'
    }
    
    # Analyze image
    result = detector.analyze_image(test_image, building_context, 'english')
    
    # Print results
    print("🔍 Analysis Results:")
    print(f"Analysis Type: {result.get('analysis_type', 'N/A')}")
    print(f"Success: {result.get('success', False)}")
    
    if result.get('success'):
        print(f"Predicted Class: {result.get('predicted_class', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 0)}%")
        print(f"Severity: {result.get('severity', 'N/A')}")
