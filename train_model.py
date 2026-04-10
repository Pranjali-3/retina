import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from collections import Counter
import os

def train():

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # -------------------------------
    # 1. Image Transformations
    # -------------------------------
    transform = transforms.Compose([
        transforms.Resize((256,256)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485,0.456,0.406],
            std=[0.229,0.224,0.225]
        )
    ])

    # -------------------------------
    # 2. Dataset Path
    # -------------------------------
    data_path = "dataset/archive/gaussian_filtered_images/gaussian_filtered_images"

    if not os.path.exists(data_path):
        print("❌ Dataset folder not found.")
        return

    dataset = datasets.ImageFolder(data_path, transform=transform)

    print("\n✅ Classes:", dataset.classes)
    print("📊 Total Images:", len(dataset))

    # -------------------------------
    # 3. Class Distribution
    # -------------------------------
    labels = [label for _, label in dataset]
    print("📊 Class Distribution:", Counter(labels))

    # -------------------------------
    # 4. Train / Validation Split
    # -------------------------------
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size

    train_dataset, val_dataset = random_split(dataset,[train_size,val_size])

    print("\nTrain Images:", len(train_dataset))
    print("Validation Images:", len(val_dataset))

    train_loader = DataLoader(train_dataset,batch_size=16,shuffle=True)
    val_loader = DataLoader(val_dataset,batch_size=16)

    # -------------------------------
    # 5. Load Pretrained Model
    # -------------------------------
    model = models.resnet50(weights="DEFAULT")

    # Freeze early layers
    for param in model.parameters():
        param.requires_grad = False

    # Unfreeze deeper layers
    for param in model.layer3.parameters():
        param.requires_grad = True

    for param in model.layer4.parameters():
        param.requires_grad = True

    model.fc = nn.Linear(model.fc.in_features,len(dataset.classes))

    model = model.to(device)

    # -------------------------------
    # 6. Loss Function (class weights)
    # -------------------------------
    class_counts = Counter(labels)

    weights = []
    total = len(dataset)

    for i in range(len(dataset.classes)):
        weights.append(total/class_counts[i])

    weights = torch.tensor(weights,dtype=torch.float).to(device)

    criterion = nn.CrossEntropyLoss(weight=weights)

    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=0.0001
    )

    epochs = 20

    print(f"\n🚀 Training for {epochs} epochs...\n")

    # -------------------------------
    # 7. Training Loop
    # -------------------------------
    for epoch in range(epochs):

        model.train()
        train_loss = 0

        for images,labels in train_loader:

            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(outputs,labels)

            loss.backward()

            optimizer.step()

            train_loss += loss.item()

        train_loss /= len(train_loader)

        # -------------------------------
        # 8. Validation
        # -------------------------------
        model.eval()

        correct = 0
        total = 0

        with torch.no_grad():

            for images,labels in val_loader:

                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)

                _,predicted = torch.max(outputs,1)

                total += labels.size(0)

                correct += (predicted == labels).sum().item()

        accuracy = 100*correct/total if total>0 else 0

        print(f"Epoch {epoch+1}/{epochs} | Loss: {train_loss:.6f} | Val Accuracy: {accuracy:.2f}%")

    # -------------------------------
    # 9. Save Model
    # -------------------------------
    torch.save(model.state_dict(),"model.pth")

    print("\n✅ Model saved as model.pth")


if __name__ == "__main__":
    train()