import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import plotly.express as px
import tempfile
import pandas as pd
from database.database import save_prediction
from utils.prediction import predict_disease
from utils.report import generate_report
from utils.disease_info import DISEASE_INFO
from database.database import get_predictions, clear_predictions

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="AI Crop Disease Prediction",
    page_icon="🌿",
    layout="wide"
)
st.markdown("""
<style>

.main {
    background-color: #f6fff8;
}

h1 {
    color: #2E7D32;
    text-align: center;
}

h2,h3 {
    color: #388E3C;
}

.stButton>button{
    background:#2E7D32;
    color:white;
    border-radius:10px;
    height:50px;
    width:100%;
    font-size:18px;
    border:none;
}

.stButton>button:hover{
    background:#1B5E20;
}

[data-testid="stMetric"]{
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.15);
}

</style>
""", unsafe_allow_html=True)
# -----------------------------
# Sidebar

# -----------------------------
st.sidebar.image(
    "https://img.icons8.com/color/480/plant-under-sun.png",
    width=120
)
st.sidebar.title("🌿 Project Information")

st.sidebar.markdown("### Model")
st.sidebar.write("EfficientNetB0")

st.sidebar.markdown("### Validation Accuracy")
st.sidebar.success("95.52%")

st.sidebar.markdown("### Classes")
st.sidebar.write("15 Crop Disease Classes")

st.sidebar.markdown("---")

st.sidebar.info(
    "Upload a crop leaf image to predict disease and view treatment recommendations."
)
history = get_predictions()

st.sidebar.markdown("### Total Predictions")
st.sidebar.success(len(history))

# ---------------------------------
# Title
page = st.sidebar.radio(
    "Navigation",
    ["Prediction", "Prediction History","Dashboard"]
)
st.markdown("---")
# ---------------------------------
st.markdown("""
# 🌿 AI Crop Disease Prediction

### AI-Based Crop Disease Prediction System
Upload a crop leaf image and get instant disease prediction, confidence score, treatment and prevention recommendations.
""")

# ---------------------------------
# Disease Display Names
# ---------------------------------
DISPLAY_NAMES = {
    "Tomato_Late_blight": "🍅 Tomato Late Blight",
    "Tomato_Early_blight": "🍅 Tomato Early Blight",
    "Tomato_healthy": "🍅 Healthy Tomato",
    "Tomato_Bacterial_spot": "🍅 Tomato Bacterial Spot",
    "Tomato_Leaf_Mold": "🍅 Tomato Leaf Mold",
    "Tomato_Septoria_leaf_spot": "🍅 Tomato Septoria Leaf Spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "🍅 Tomato Spider Mites",
    "Tomato__Target_Spot": "🍅 Tomato Target Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "🍅 Tomato Yellow Leaf Curl Virus",
    "Tomato__Tomato_mosaic_virus": "🍅 Tomato Mosaic Virus",
    "Potato___Early_blight": "🥔 Potato Early Blight",
    "Potato___Late_blight": "🥔 Potato Late Blight",
    "Potato___healthy": "🥔 Healthy Potato",
    "Pepper__bell___healthy": "🫑 Healthy Bell Pepper",
    "Pepper__bell___Bacterial_spot": "🫑 Bell Pepper Bacterial Spot"
}

# ---------------------------------
# File Upload
# ---------------------------------
# ---------------------------------
# Prediction Page
# ---------------------------------
if page == "Prediction":

    st.subheader("Upload or Capture Leaf")

    tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Camera"])

    uploaded_file = None
    camera_image = None

    with tab1:
        uploaded_file = st.file_uploader(
            "Choose a Leaf Image",
           type=["jpg", "jpeg", "png"]
        )

    with tab2:

        if "camera_open" not in st.session_state:
            st.session_state.camera_open = False

        if not st.session_state.camera_open:
            if st.button("📷 Open Camera"):
                st.session_state.camera_open = True
                st.rerun()

        else:
            camera_image = st.camera_input("Capture Leaf")

            if camera_image is not None:
                st.session_state.camera_open = False

    if uploaded_file is not None or camera_image is not None:

        if st.button("🔍 Predict Disease"):

            # Save uploaded image temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                if uploaded_file is not None:
                    tmp.write(uploaded_file.read())
                else:
                    tmp.write(camera_image.read())
                temp_path = tmp.name

            # Predict
            disease, confidence = predict_disease(temp_path)

            display_name = DISPLAY_NAMES.get(
                disease,
                disease.replace("_", " ")
            )

            save_prediction(display_name, confidence)

            info = DISEASE_INFO.get(disease)
            pdf = generate_report(
                display_name,
                confidence,
                info
            )

            col1, col2 = st.columns([1, 2])

            with col1:
                if uploaded_file is not None:
                    st.image(uploaded_file, caption="Uploaded Leaf")
                else:
                    st.image(camera_image, caption="Captured Leaf")

            with col2:

                if "healthy" in disease.lower():
                    st.success("🌱 Plant is Healthy")
                else:
                    st.error("⚠️ Disease Detected")

                st.success(display_name)
                st.info(f"Confidence : {confidence:.2f}%")
                st.progress(confidence / 100)
                st.caption(f"Prediction Confidence : {confidence:.2f}%")

            if info:

                with st.expander("🦠 Disease Information", expanded=True):

                    st.markdown("## 🌿 Disease Name")
                    st.write(info["name"])

                    st.markdown("## 🩺 Symptoms")
                    for item in info["symptoms"]:
                        st.write("•", item)

                    st.markdown("## 💊 Treatment")
                    for item in info["treatment"]:
                        st.write("•", item)

                    st.markdown("## 🛡 Prevention")
                    for item in info["prevention"]:
                        st.write("•", item)
                    st.download_button(
                        "📥 Download PDF Report",
                        data=pdf,
                        file_name="crop_report.pdf",
                        mime="application/pdf"
                    )

elif page == "Prediction History":
    

    st.title("Prediction History")

    history = get_predictions()

    if history:


        df = pd.DataFrame(
                 history,
                 columns=[
                    "ID",
                    "Disease",
                    "Confidence",
                     "Prediction Time"
                ]
        )

        df["Confidence"] = df["Confidence"].round(2)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No prediction history available.")

elif page == "Dashboard":

    st.title("AI Crop Disease Dashboard")

    history = get_predictions()

    if history:

        df = pd.DataFrame(
            history,
            columns=[
                "ID",
                "Disease",
                "Confidence",
                "Prediction Time"
            ]
        )

        total = len(df)

        healthy = df["Disease"].str.contains(
            "Healthy",
            case=False
        ).sum()

        diseased = total - healthy

        common = df["Disease"].mode()[0]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("📄 Total", total)
        col2.metric("🌱 Healthy", healthy)
        col3.metric("⚠️ Diseased", diseased)
        col4.metric("🏆 Common", common)

        st.markdown("---")

        st.subheader("Disease Distribution")

        chart = df["Disease"].value_counts()

        st.bar_chart(chart)
        st.markdown("---")

        st.subheader("🕒 Recent Predictions")

        st.dataframe(
            df.head(5),
            use_container_width=True,
            hide_index=True
        )
        st.markdown("---")
        

        st.subheader("🥧 Healthy vs Diseased")
        st.write("Healthy Count:", healthy)
        st.write("Diseased Count:", diseased)

        pie_df = pd.DataFrame({
            "Category": ["Healthy", "Diseased"],
            "Count": [healthy, diseased]
        })

        fig = px.pie(
            pie_df,
            names="Category",
            values="Count",
            title="Healthy vs Diseased Plants",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
        label="📥 Download Prediction History (CSV)",
        data=csv,
        file_name="prediction_history.csv",
        mime="text/csv"
        )
        st.markdown("---")

        if st.button("🗑️ Clear Prediction History"):

            clear_predictions()

            st.success("Prediction history cleared successfully!")

            st.rerun()

    else:
        st.info("No prediction history available.")
        st.markdown("---")

        st.markdown(
        """
        <div style='text-align:center;color:gray;'>

        Made with using Streamlit & TensorFlow

        © 2026 AI Crop Disease Prediction System

        </div>
        """,
        unsafe_allow_html=True
        )



