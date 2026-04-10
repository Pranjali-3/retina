import streamlit as st
from fastai.vision.all import *
import os
from PIL import Image
import fastai.layers

# --- 1. Version Patch ---
# This fixes internal naming conflicts between different FastAI versions
if not hasattr(fastai.layers, 'FlattenedLoss'):
    try:
        fastai.layers.FlattenedLoss = BaseLoss
    except:
        pass

# --- 2. Page Configuration ---
st.set_page_config(page_title="Retino.ai", page_icon="👁️", layout="centered")

st.title("👁️ AI Detection of Diabetic Retinopathy")
st.write("Upload a retinal fundus image for AI-based diagnostic analysis.")

# --- 3. Model Loading ---
# Since export.pkl is right next to app.py, we find it like this:
MODEL_FILENAME = "export.pkl"
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, MODEL_FILENAME)

@st.cache_resource
def load_retino_model():
    if not os.path.exists(model_path):
        return None
    try:
        # load_learner is the ONLY way to open .pkl files
        return load_learner(model_path)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

learn = load_retino_model()

# --- 4. Sidebar ---
with st.sidebar:
    st.header("Project Info")
    st.info("Retino.ai uses a Deep Learning model to classify the severity of Diabetic Retinopathy.")
    st.warning("⚠️ **Disclaimer:** Research prototype only. Consult a doctor for medical advice.")

# --- 5. Main UI Logic ---
if learn is None:
    st.error(f"❌ **File Not Found:** Please ensure '{MODEL_FILENAME}' is in: `{current_dir}`")
else:
    uploaded_file = st.file_uploader("Upload Retinal Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(img, caption="Uploaded Scan", use_container_width=True)
        
        with col2:
            if st.button("🚀 Analyze Image"):
                with st.spinner("Analyzing..."):
                    # FastAI prediction step
                    img_fastai = PILImage.create(uploaded_file)
                    pred, pred_idx, probs = learn.predict(img_fastai)

                    st.subheader("Analysis Result")
                    
                    # Clean the label (No_DR -> No DR)
                    clean_pred = str(pred).replace("_", " ")
                    
                    # Show result with color coding
                    if "No" in clean_pred:
                        st.success(f"**Stage: {clean_pred}**")
                    else:
                        st.error(f"**Stage: {clean_pred}**")

                    st.metric("Confidence Score", f"{probs[pred_idx]*100:.2f}%")

                    # Show all category percentages
                    st.write("---")
                    st.write("**Full Breakdown:**")
                    for i, label in enumerate(learn.dls.vocab):
                        label_name = label.replace("_", " ")
                        st.write(f"{label_name}: {probs[i]*100:.1f}%")
                        st.progress(float(probs[i]))

# --- Footer ---
st.markdown("---")
st.caption("Developed with Streamlit and FastAI.")