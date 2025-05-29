import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF
from PIL import Image
import math

st.title("📏 PDF Blueprint Line Measurement Tool")

uploaded_file = st.file_uploader("Upload a scaled blueprint (PDF)", type=["pdf"])
if uploaded_file:
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    page = pdf[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    st.image(img, caption="Rendered PDF Page")

    st.subheader("🎯 Set Scale")

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_image=img,
        update_streamlit=True,
        height=img.height,
        width=img.width,
        drawing_mode="line",
        key="canvas",
    )

    unit_type = st.selectbox("Choose units", ["inches", "feet"])
    real_distance = st.number_input(f"Enter real-world length of your reference line ({unit_type}):", min_value=0.01)

    if canvas_result.json_data and len(canvas_result.json_data["objects"]) >= 1:
        line = canvas_result.json_data["objects"][-1]
        (x1, y1), (x2, y2) = line["left"], line["top"], line["left"] + line["width"], line["top"] + line["height"]

        pixel_distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        scale = real_distance / pixel_distance

        st.success(f"Scale set: 1 pixel = {scale:.4f} {unit_type}")

        if len(canvas_result.json_data["objects"]) >= 2:
            mline = canvas_result.json_data["objects"][-1]
            (mx1, my1), (mx2, my2) = mline["left"], mline["top"], mline["left"] + mline["width"], mline["top"] + mline["height"]
            measure_pixels = ((mx2 - mx1) ** 2 + (my2 - my1) ** 2) ** 0.5
            real_length = measure_pixels * scale

            st.success(f"Measured line: {real_length:.2f} {unit_type}")

