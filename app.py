import streamlit as st
from ultralytics import YOLO
from PIL import Image
import os

# ==========================================================
# ตั้งค่าหน้าเว็บ
# ==========================================================

st.set_page_config(
    page_title="AI Waste Classification",
    page_icon="♻️",
    layout="centered"
)

# ==========================================================
# CSS ตกแต่งหน้าเว็บ
# ==========================================================

st.markdown("""
<style>

    /* ==============================
       พื้นหลัง
       ============================== */

    .stApp {
        background: linear-gradient(
            135deg,
            #071a13 0%,
            #0b241a 50%,
            #07110d 100%
        );
    }

    /* ==============================
       ขนาดเนื้อหา
       ============================== */

    .block-container {
        max-width: 850px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    /* ==============================
       หัวข้อ
       ============================== */

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        color: #9be7bd;
        margin-bottom: 30px;
    }

    /* ==============================
       Card
       ============================== */

    .card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 25px;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.25);
    }

    /* ==============================
       ผลลัพธ์
       ============================== */

    .result-title {
        text-align: center;
        color: #9be7bd;
        font-size: 17px;
        margin-bottom: 5px;
    }

    .result-class {
        text-align: center;
        color: #ffffff;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .confidence {
        text-align: center;
        color: #d5ffe4;
        font-size: 20px;
        font-weight: 600;
    }

    /* ==============================
       กล่องสถานะ
       ============================== */

    .warning-box {
        background: rgba(255, 193, 7, 0.12);
        border: 1px solid rgba(255, 193, 7, 0.4);
        border-radius: 12px;
        padding: 15px;
        color: #ffd666;
        text-align: center;
        margin-top: 15px;
    }

    .good-box {
        background: rgba(0, 200, 83, 0.12);
        border: 1px solid rgba(0, 200, 83, 0.3);
        border-radius: 12px;
        padding: 15px;
        color: #8ff0b5;
        text-align: center;
        margin-top: 15px;
    }

    /* ==============================
       File uploader
       ============================== */

    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px dashed rgba(155, 231, 189, 0.45);
        border-radius: 15px;
        padding: 15px;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: transparent;
        border: none;
    }

    /* ==============================
       ปุ่ม
       ============================== */

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 48px;
    }

    /* ==============================
       ซ่อนเมนู
       ============================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

</style>
""", unsafe_allow_html=True)


# ==========================================================
# Header
# ==========================================================

st.markdown(
    '<div class="main-title">♻️ AI Waste Classification</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">ระบบจำแนกประเภทขยะด้วยปัญญาประดิษฐ์</div>',
    unsafe_allow_html=True
)


# ==========================================================
# ตำแหน่งโมเดล
# ==========================================================

MODEL_PATH = "best.pt"

if not os.path.exists(MODEL_PATH):
    st.error(f"ไม่พบโมเดล: {MODEL_PATH}")
    st.stop()


# ==========================================================
# โหลดโมเดล
# ==========================================================

@st.cache_resource
def load_model():
    return YOLO(MODEL_PATH)


model = load_model()


# ==========================================================
# Upload รูป
# ==========================================================

st.markdown(
    "### 📷 เลือกรูปภาพขยะที่ต้องการวิเคราะห์"
)

uploaded_file = st.file_uploader(
    "อัปโหลดรูปภาพ",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)


# ==========================================================
# เมื่อมีรูป
# ==========================================================

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    # แสดงรูป
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.image(
        image,
        caption="รูปภาพที่เลือก",
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


    # ======================================================
    # ปุ่มวิเคราะห์
    # ======================================================

    if st.button(
        "🔍 วิเคราะห์ประเภทขยะ",
        use_container_width=True,
        type="primary"
    ):

        with st.spinner("🤖 AI กำลังวิเคราะห์รูปภาพ..."):

            results = model(image)

            result = results[0]

            # -------------------------------
            # ความน่าจะเป็นของทุก Class
            # -------------------------------

            probs = result.probs

            probabilities = probs.data.tolist()

            class_names = result.names

            # -------------------------------
            # Class ที่มั่นใจที่สุด
            # -------------------------------

            top1_index = probs.top1

            confidence = float(probs.top1conf)

            class_name = class_names[top1_index]


        # ==================================================
        # ผลลัพธ์หลัก
        # ==================================================

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(
            '<div class="result-title">📋 ผลการจำแนก</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="result-class">{class_name}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="confidence">'
            f'ความมั่นใจ {confidence * 100:.2f}%'
            f'</div>',
            unsafe_allow_html=True
        )


        # ==================================================
        # ตรวจสอบความมั่นใจ
        # ==================================================

        if confidence < 0.60:

            st.markdown(
                """
                <div class="warning-box">
                ⚠️ AI มีความมั่นใจค่อนข้างต่ำ<br>
                แนะนำให้ใช้ภาพที่เห็นวัตถุชัดเจนมากขึ้น
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="good-box">
                ✓ AI มีความมั่นใจในการจำแนกประเภท
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)


        # ==================================================
        # ความน่าจะเป็นทุกประเภท
        # ==================================================

        st.markdown("### 📊 ความน่าจะเป็นของแต่ละประเภท")


        # เรียงจากมากไปน้อย

        all_results = []

        for i, probability in enumerate(probabilities):

            all_results.append(
                (
                    class_names[i],
                    float(probability)
                )
            )

        all_results.sort(
            key=lambda x: x[1],
            reverse=True
        )


        # ==================================================
        # แสดงแต่ละ Class
        # ==================================================

        for name, probability in all_results:

            percentage = probability * 100

            col1, col2 = st.columns([3, 1])

            with col1:

                st.write(f"**{name}**")

                st.progress(
                    min(probability, 1.0)
                )

            with col2:

                st.write(
                    f"**{percentage:.2f}%**"
                )


        # ==================================================
        # Footer
        # ==================================================

        st.markdown("---")

        st.caption(
            "♻️ Waste Classification System | "
            "YOLO11 Classification"
        )