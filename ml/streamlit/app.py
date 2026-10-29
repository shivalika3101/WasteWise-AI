import streamlit as st
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

# -----------------------------
# CHANGE THIS TO YOUR FULL LIST
# -----------------------------
class_names = [
    "aerosol_cans",
    "aluminum_food_cans",
    "aluminum_soda_cans",
    "cardboard_boxes",
    "cardboard_packaging",
    "clothing",
    "coffee_grounds",
    "disposable_plastic_cutlery",
    "eggshells",
    "food_waste",
    "glass_beverage_bottles",
    "glass_cosmetic_containers",
    "glass_food_jars",
    "magazines",
    "newspaper",
    "office_paper",
    "paper_cups",
    "plastic_cup_lids",
    "plastic_detergent_bottles",
    "plastic_food_containers",
    "plastic_shopping_bags",
    "plastic_soda_bottles",
    "plastic_straws",
    "plastic_trash_bags",
    "plastic_water_bottles",
    "shoes",
    "steel_food_cans",
    "styrofoam_cups",
    "styrofoam_food_containers",
    "tea_bags"
]

# -----------------------------
# PAGE SETTINGS
# -----------------------------
st.set_page_config(
    page_title="Waste Classification",
    page_icon="♻️"
)

st.title("♻️ Waste Classification using ResNet50")

st.write(
    "Upload an image of waste and the model will predict its class."
)

# -----------------------------
# DEVICE
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# LOAD MODEL
# -----------------------------
weights = models.ResNet50_Weights.DEFAULT

model = models.resnet50(weights=weights)

model.fc = nn.Linear(
    model.fc.in_features,
    len(class_names)
)

model.load_state_dict(
    torch.load(
        "ml/models/resnet50_best.pth",
        map_location=device
    )
)

model = model.to(device)
model.eval()

# -----------------------------
# IMAGE TRANSFORM
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# -----------------------------
# FILE UPLOADER
# -----------------------------
uploaded_file = st.file_uploader(
    "Choose an image...",
    type=["jpg", "jpeg", "png"]
)

# -----------------------------
# PREDICTION
# -----------------------------
if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")

    st.image(
        image,
        caption="Uploaded Image",
        width="stretch"
    )

    img = transform(image)

    img = img.unsqueeze(0)

    img = img.to(device)

    with torch.no_grad():

        output = model(img)

        probabilities = torch.softmax(output, dim=1)

        confidence, predicted = torch.max(probabilities, 1)

    prediction = class_names[predicted.item()]

    st.success(f"Prediction: {prediction}")

    st.write(f"Confidence: {confidence.item()*100:.2f}%")