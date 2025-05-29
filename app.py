import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF
from PIL import Image
import math

st.set_page_config(page_title="Blueprint Measurement Tool", layout="wide")
st.title("📏 PDF Blueprint Line Measurement Tool")

uploaded_file = st.file_uploader("Upload a PDF blueprint", type=["pdf"])

if uploaded_file:
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    page = pdf[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # High-res rendering
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    st.image(img, caption="Rendered PDF Page")

    st.subheader("🖊️ Draw a reference line to set the scale")

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

    unit_type = st.selectbox("Select units", ["inches", "feet"])
    real_distance = st.number_input(f"Enter the real-world length of your drawn line ({unit_type}):", min_value=0.01)

    if canvas_result.json_data and len(canvas_result.json_data["objects"]) >= 1:
        last_line = canvas_result.json_data["objects"][-1]
        (x1, y1), (x2, y2) = last_line["left"], last_line["top"], last_line["left"] + last_line["width"], last_line["top"] + last_line["height"]
        pixel_dist = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
        scale = real_distance / pixel_dist
        st.success(f"Scale set: 1 pixel = {scale:.4f} {unit_type}")

        st.write("🎯 Draw another line to measure:")
        if len(canvas_result.json_data["objects"]) >= 2:
            second_line = canvas_result.json_data["objects"][-1]
            (mx1, my1), (mx2, my2) = second_line["left"], second_line["top"], second_line["left"] + second_line["width"], second_line["top"] + second_line["height"]
            measured_pixels = ((mx2 - mx1)**2 + (my2 - my1)**2) ** 0.5
            measured_real = measured_pixels * scale
            st.success(f"Measured line: {measured_real:.2f} {unit_type}")
