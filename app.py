import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageDraw
import io

st.set_page_config(page_title="ID Card Print Studio", layout="centered")

st.title("🖨️ ID Card Print Studio (300 DPI)")
st.write("Upload your ID card PDF or Photo to generate a high-quality 4x6 print sheet instantly.")

uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"])

media_type = st.selectbox("Select Target Media", [
    "4x6 Inch Portrait (300 DPI)", 
    "4x6 Inch Landscape (300 DPI)", 
    "PVC Card Tray (130x210 mm)"
])

layout_mode = st.selectbox("Print Layout", [
    "Front + Back (Both Sides)", 
    "Front Side Only", 
    "Back Side Only"
])

if uploaded_file is not None:
    try:
        # Load PDF or Image
        if uploaded_file.name.lower().endswith(".pdf"):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(600/72, 600/72), alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            doc.close()
        else:
            img = Image.open(uploaded_file).convert("RGB")

        st.image(img, caption="Loaded Document Preview", use_container_width=True)

        if st.button("Generate Print Sheet"):
            w, h = img.size
            # Default coordinate logic for e-Aadhaar / Cards
            front_box = (int(w * 0.08), int(h * 0.71), int(w * 0.49), int(h * 0.92))
            back_box = (int(w * 0.50), int(h * 0.71), int(w * 0.91), int(h * 0.92))

            card_w_px = int((85.6 / 25.4) * 300)
            card_h_px = int((54.0 / 25.4) * 300)

            front_card = img.crop(front_box).resize((card_w_px, card_h_px), Image.Resampling.LANCZOS)
            back_card = img.crop(back_box).resize((card_w_px, card_h_px), Image.Resampling.LANCZOS)

            # Create Sheet
            if "Landscape" in media_type:
                sheet = Image.new("RGB", (1800, 1200), (255, 255, 255))
                sheet.paste(front_card, (200, 300))
                sheet.paste(back_card, (1000, 300))
            else:
                sheet = Image.new("RGB", (1200, 1800), (255, 255, 255))
                sheet.paste(front_card, (200, 200))
                sheet.paste(back_card, (200, 1000))

            st.success("Print Sheet Generated Successfully!")
            st.image(sheet, caption="Ready to Print 300 DPI Sheet", use_container_width=True)

            # Download button
            buf = io.BytesIO()
            sheet.save(buf, format="JPEG", quality=100, dpi=(300, 300))
            byte_im = buf.getvalue()

            st.download_button(
                label="📥 Download High-Res Print Sheet",
                data=byte_im,
                file_name="id_card_print_sheet.jpg",
                mime="image/jpeg"
            )

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")