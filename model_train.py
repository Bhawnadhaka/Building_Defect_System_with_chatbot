import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import models, datasets, transforms
from torch.optim.lr_scheduler import StepLR
import os
import time

class EfficientNetDefectClassifier(nn.Module):
    def __init__(self, num_classes=7):
        super(EfficientNetDefectClassifier, self).__init__()
        self.backbone = models.efficientnet_b0(pretrained=True)
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

def setup_model(num_classes=7, device='cpu'):
    model = EfficientNetDefectClassifier(num_classes=num_classes)
    model = model.to(device)
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    return model

def setup_data_loaders(data_dir='Data_split', batch_size=32):
    train_transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dataset = datasets.ImageFolder(root=os.path.join(data_dir, 'train'), transform=train_transform)
    val_dataset = datasets.ImageFolder(root=os.path.join(data_dir, 'val'), transform=val_transform)
    test_dataset = datasets.ImageFolder(root=os.path.join(data_dir, 'test'), transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"Data loaders created - Classes: {train_dataset.classes}")
    print(f"Samples - Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
    
    return train_loader, val_loader, test_loader, train_dataset.classes

def setup_training(model, learning_rate=0.001, weight_decay=1e-4):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = StepLR(optimizer, step_size=7, gamma=0.1)
    return criterion, optimizer, scheduler

# MODIFIED WITH PROGRESS TRACKING
def train_epoch(model, train_loader, criterion, optimizer, device):
    model.train()
    running_loss, correct_preds, total_preds = 0.0, 0, 0
    
    print(f"  Starting epoch with {len(train_loader)} batches...")
    start_time = time.time()
    
    for batch_idx, (inputs, labels) in enumerate(train_loader):
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total_preds += labels.size(0)
        correct_preds += (predicted == labels).sum().item()
        
        # PROGRESS TRACKING - EVERY 30 BATCHES
        if batch_idx % 30 == 0:
            elapsed = time.time() - start_time
            print(f"    Batch {batch_idx:3d}/{len(train_loader)} - Loss: {loss.item():.4f} - Time: {elapsed:.1f}s")
    
    epoch_time = time.time() - start_time
    print(f"  Epoch completed in {epoch_time:.1f}s")
    
    return running_loss / len(train_loader), correct_preds / total_preds

def validate_model(model, val_loader, device):
    model.eval()
    correct, total = 0, 0
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    return correct / total

def train_model(model, train_loader, val_loader, criterion, optimizer, scheduler, 
                device, num_epochs=15, save_path='best_defect_model.pth'):
    train_losses, val_accuracies = [], []
    best_val_acc = 0.0
    class_names = train_loader.dataset.classes
    
    print(f" Starting training for {num_epochs} epochs...")
    overall_start = time.time()
    
    for epoch in range(num_epochs):
        print(f'\n Epoch {epoch+1:2d}/{num_epochs}')
        print('-' * 50)
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_acc = validate_model(model, val_loader, device)
        
        train_losses.append(train_loss)
        val_accuracies.append(val_acc)
        
        print(f' Epoch {epoch+1:2d}: Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, Val Acc: {val_acc:.4f}')
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'class_names': class_names
            }, save_path)
            print(f'NEW BEST MODEL! Val Acc: {val_acc:.4f}')
        
        scheduler.step()
        
        # Time remaining estimate
        elapsed = time.time() - overall_start
        avg_time_per_epoch = elapsed / (epoch + 1)
        remaining_epochs = num_epochs - (epoch + 1)
        eta = remaining_epochs * avg_time_per_epoch
        print(f'  ETA: {eta/60:.1f} minutes remaining')
    
    total_time = time.time() - overall_start
    print(f'\n Training completed in {total_time/60:.1f} minutes!')
    
    return train_losses, val_accuracies

def main():
    # Configuration FOR FULL DATASET TRAINING
    device = torch.device('cpu')
    num_classes = 7
    num_epochs = 10  # Reduced for reasonable time
    batch_size = 8   # Smaller for CPU
    data_dir = 'Data_split'  # FIXED: was 'Data_split'
    
    print(f" FULL DATASET TRAINING MODE")
    print(f"Using device: {device}")
    
    # Setup components
    model = setup_model(num_classes, device)
    train_loader, val_loader, test_loader, class_names = setup_data_loaders(data_dir, batch_size)
    criterion, optimizer, scheduler = setup_training(model)
    
    print(f" Training on FULL dataset: {len(train_loader.dataset)} samples")
    print(f" Validation: {len(val_loader.dataset)} samples")
    print(f"⏱  Estimated time: {len(train_loader) * num_epochs * 20 / 3600:.1f} hours")
    
    # Train model
    train_losses, val_accuracies = train_model(
        model, train_loader, val_loader, criterion, optimizer, scheduler, 
        device, num_epochs
    )
    
    print("Training completed!")
    print(f" Final model saved as 'best_defect_model.pth'")

if __name__ == "__main__":
    main()
