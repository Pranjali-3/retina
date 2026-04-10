import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os

CLASS_NAMES = ['Mild', 'Moderate', 'No_DR', 'Proliferative_DR', 'Severe']
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@torch.no_grad()
def load_model():
    model = models.resnet50()
    model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))

    if os.path.exists("model.pth"):
        model.load_state_dict(torch.load("model.pth", map_location=device))

    model.to(device).eval()
    return model

model = load_model()

def predict(image_path):
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)

    outputs = model(image)
    probs = torch.nn.functional.softmax(outputs, dim=1)
    confidence, predicted = torch.max(probs, 1)

    return CLASS_NAMES[predicted.item()], confidence.item()