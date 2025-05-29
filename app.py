import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import math

st.title("📏 PDF Blueprint Line Measurement Tool")

# Upload PDF
uploaded_file = st.file_uploader("Upload a scaled blueprint (PDF)", type=["pdf"])
if uploaded_file:
    # Load first page as image
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    page = pdf[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # High-res render
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_np = np.array(img)

    st.image(img, caption="Rendered PDF Page")

    st.subheader("🎯 Set Scale")

    st.write("Draw a known-length reference line (e.g., door width, room size) and input real-world length.")

    # Draw on canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_image=img,
        update_streamlit=True,
        height=img_np.shape[0],
        width=img_np.shape[1],
        drawing_mode="line",
        key="canvas",
    )

    # Set real-world scale
    unit_type = st.selectbox("Choose units", ["inches", "feet"])
    real_distance = st.number_input(f"Enter real-world length of your reference line ({unit_type}):", min_value=0.01)

    if canvas_result.json_data and len(canvas_result.json_data["objects"]) >= 1:
        line = canvas_result.json_data["objects"][-1]  # Last drawn line
        (x1, y1), (x2, y2) = line["left"], line["top"], line["left"] + line["width"], line["top"] + line["height"]

        pixel_distance = math.hypot(x2 - x1, y2 - y1)

        if pixel_distance > 0 and real_distance > 0:
            scale = real_distance / pixel_distance  # real units per pixel
            st.success(f"Scale set: 1 pixel = {scale:.4f} {unit_type}")

            st.markdown("### 📐 Now draw a line to measure")
            st.info("Draw another line to measure it using this scale.")

            if len(canvas_result.json_data["objects"]) >= 2:
                measure_line = canvas_result.json_data["objects"][-1]
                (mx1, my1), (mx2, my2) = (
                    measure_line["left"],
                    measure_line["top"],
                    measure_line["left"] + measure_line["width"],
                    measure_line["top"] + measure_line["height"],
                )
                measure_pixel_length = math.hypot(mx2 - mx1, my2 - my1)
                measured_real_length = measure_pixel_length * scale

                st.success(f"Measured Line Length: {measured_real_length:.2f} {unit_type}")
