import torch
import torch.nn as nn
from torchvision import models, datasets, transforms
from torch.utils.data import DataLoader
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import numpy as np
import os

# 1. Define model architecture (same as training)
class EfficientNetDefectClassifier(nn.Module):
    def __init__(self, num_classes=7):
        super(EfficientNetDefectClassifier, self).__init__()
        self.backbone = models.efficientnet_b0(weights='DEFAULT')
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)

# 2. Load trained model
def load_trained_model(model_path='best_defect_model.pth'):
    print("Loading trained model...")
    checkpoint = torch.load(model_path, map_location='cpu',weights_only=False)
    
    model = EfficientNetDefectClassifier(num_classes=7)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    class_names = checkpoint['class_names']
    val_acc = checkpoint['val_acc']
    epoch = checkpoint['epoch']
    
    print(f" Model loaded successfully!")
    print(f" Best validation accuracy: {val_acc:.4f} (from epoch {epoch})")
    print(f"  Classes: {class_names}")
    
    return model, class_names

# 3. Test model on test set
def evaluate_on_test_set():
    print("\n TESTING MODEL ON TEST SET...")
    
    # Load model
    model, class_names = load_trained_model()
    
    # Create test data loader
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    test_dataset = datasets.ImageFolder('Data_split/test', transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)
    
    print(f" Test set size: {len(test_dataset)} images")
    
    # Evaluate
    model.eval()
    all_predictions = []
    all_labels = []
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    test_accuracy = correct / total
    
    print(f"\n FINAL TEST RESULTS:")
    print(f" Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    print("\n Detailed Classification Report:")
    print("=" * 60)
    print(classification_report(all_labels, all_predictions, target_names=class_names))
    
    return test_accuracy, all_predictions, all_labels, class_names

# 4. Single image prediction function
def predict_single_image(image_path, model_path='best_defect_model.pth'):
    print(f"\n PREDICTING: {image_path}")
    
    # Load model
    model, class_names = load_trained_model(model_path)
    
    # Prepare image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    try:
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0)
        
        # Predict
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_class = class_names[predicted.item()]
        confidence_score = confidence.item()
        
        print(f" Prediction: {predicted_class}")
        print(f" Confidence: {confidence_score:.4f} ({confidence_score*100:.2f}%)")
        
        # Show top 3 predictions
        top_probs, top_indices = torch.topk(probabilities, 3)
        print(f"\n Top 3 Predictions:")
        for i in range(3):
            class_name = class_names[top_indices[0][i]]
            prob = top_probs[0][i].item()
            print(f"  {i+1}. {class_name}: {prob:.4f} ({prob*100:.2f}%)")
        
        return predicted_class, confidence_score
        
    except Exception as e:
        print(f" Error processing image: {e}")
        return None, None

# 5. Main testing function
def main():
    print(" STEP 3F: MODEL TESTING & EVALUATION")
    print("=" * 50)
    
    # Test 1: Evaluate on test set
    test_acc, predictions, labels, class_names = evaluate_on_test_set()
    
    # Test 2: Single image prediction example
    print("\n" + "="*50)
    print(" SINGLE IMAGE PREDICTION TEST")
    
    # Try to predict on a sample from test set
    test_images_dir = "Data_split/test"
    
    # Get first image from each class for testing
    for class_name in class_names:
        class_dir = os.path.join(test_images_dir, class_name)
        if os.path.exists(class_dir):
            images = os.listdir(class_dir)
            if images:
                sample_image = os.path.join(class_dir, images[0])
                print(f"\n--- Testing {class_name} sample ---")
                predict_single_image(sample_image)
                break  # Test just one for now
    
    print(f"\n STEP 3 COMPLETED!")
    print(f" Final Model Performance: {test_acc:.4f} ({test_acc*100:.2f}%)")
    print(f" Model saved as: best_defect_model.pth")
    print(f" Ready for Step 4: User Interface Development!")

if __name__ == "__main__":
    main()
