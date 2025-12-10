import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import requests

# --- Page Configuration ---
st.set_page_config(page_title="Hujuge Bangali News Maker", layout="wide")

st.title("📢 হুজুগে বাঙালি - ব্রেকিং নিউজ মেকার")
st.write("আপনার ছবি এবং টেক্সট দিয়ে প্রফেশনাল নিউজ কার্ড তৈরি করুন!")

# --- Helper Function: Download Font ---
def download_font():
    font_url = "https://raw.githubusercontent.com/potasiyam/Kalpurush/main/Kalpurush.ttf"
    font_path = "kalpurush.ttf"
    
    if not os.path.exists(font_path):
        with st.spinner('বাংলা ফন্ট ডাউনলোড হচ্ছে... একটু অপেক্ষা করুন'):
            try:
                response = requests.get(font_url)
                with open(font_path, "wb") as f:
                    f.write(response.content)
                st.success("ফন্ট সেটআপ সম্পন্ন হয়েছে!")
            except Exception as e:
                st.error(f"ফন্ট ডাউনলোড করা যায়নি: {e}")
                return None
    return font_path

# Load Font Automatically
font_path = download_font()

# --- Sidebar Inputs ---
st.sidebar.header("🛠 সেটিংস")

# 1. Image Upload
uploaded_image = st.sidebar.file_uploader("১. নিউজের ছবি আপলোড করুন (Main Image)", type=["jpg", "jpeg", "png"])
uploaded_logo = st.sidebar.file_uploader("২. লোগো আপলোড করুন (Optional)", type=["png", "jpg"])

# 2. Text Inputs
headline_text = st.sidebar.text_input("৩. প্রধান খবর (হলুদ লেখা)", "গুজবে কান দিয়ে দৌড়াচ্ছে জাতি!")
body_text = st.sidebar.text_area("৪. বিস্তারিত খবর (কালো লেখা)", "চাঞ্চল্যকর তথ্য: ইন্টারনেটে ছড়িয়ে পড়া খবরে লজিকের অভাব! ফলো করুন আমাদের পেজ।")
footer_text = st.sidebar.text_input("৫. ফুটার / তারিখ", "Follow us for more 'Hujug' | Date: 10/12/2025")

# --- Function to Wrap Text ---
def draw_text_wrapped(draw, text, font, max_width, start_y, text_color, align="center", image_width=800):
    lines = []
    # Approximate character width for wrapping
    avg_char_width = 25 # Adjusted for Kalpurush font size
    chars_per_line = int(max_width / avg_char_width) + 5
    
    wrapper = textwrap.TextWrapper(width=chars_per_line)
    lines = wrapper.wrap(text=text)
    
    current_y = start_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        if align == "center":
            x_pos = (image_width - text_w) / 2
        else:
            x_pos = 50
            
        draw.text((x_pos, current_y), line, font=font, fill=text_color)
        current_y += text_h + 15
    return current_y

# --- Main Logic with Generate Button ---

if st.button("📸 নিউজ কার্ড তৈরি করুন", type="primary"):
    if uploaded_image is not None and font_path is not None:
        # 1. Setup Canvas
        canvas_width = 800
        canvas_height = 900
        background_color = "white"
        
        img = Image.new('RGB', (canvas_width, canvas_height), background_color)
        draw = ImageDraw.Draw(img)

        # 2. Load Fonts
        try:
            font_headline = ImageFont.truetype(font_path, 55)
            font_body = ImageFont.truetype(font_path, 40)
            font_footer = ImageFont.truetype(font_path, 25)
            font_breaking = ImageFont.truetype(font_path, 60) # Using Bangla font for breaking news text too if needed
        except Exception as e:
            st.error(f"ফন্ট লোড এরর: {e}")
            st.stop()

        # --- DRAWING LAYOUT ---

        # A. Header (Red Background)
        header_height = 120
        draw.rectangle([(0, 0), (canvas_width, header_height)], fill="#b91c1c")
        
        # "BREAKING NEWS" Text
        draw.text((50, 25), "BREAKING NEWS", fill="white", font=font_breaking)

        # B. Logo (Top Right)
        if uploaded_logo:
            logo = Image.open(uploaded_logo).convert("RGBA")
            logo = logo.resize((100, 100))
            img.paste(logo, (680, 10), logo)

        # C. Main Image
        main_img = Image.open(uploaded_image).convert("RGB")
        target_img_width = 760
        target_img_height = 450
        main_img = main_img.resize((target_img_width, target_img_height))
        img_x = 20
        img_y = header_height + 20
        img.paste(main_img, (img_x, img_y))

        # D. Headline Strip (Black Bar + Yellow Text)
        bar_height = 90
        bar_y = img_y + target_img_height - 40
        
        draw.rectangle([(img_x, bar_y), (img_x + target_img_width, bar_y + bar_height)], fill="black")
        
        # Yellow Headline Text
        draw_text_wrapped(draw, headline_text, font_headline, 740, bar_y + 10, "#facc15", "center", canvas_width)

        # E. Body Text
        body_start_y = bar_y + bar_height + 30
        draw_text_wrapped(draw, body_text, font_body, 740, body_start_y, "black", "center", canvas_width)

        # F. Footer
        draw.line([(50, canvas_height - 60), (750, canvas_height - 60)], fill="gray", width=2)
        draw_text_wrapped(draw, footer_text, font_footer, 700, canvas_height - 50, "#555555", "center", canvas_width)

        # --- Display Result ---
        st.image(img, caption="আপনার জেনারেট করা নিউজ কার্ড", use_column_width=True)

        # --- Download Button ---
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="📥 ছবি ডাউনলোড করুন",
            data=byte_im,
            file_name="hujuge_news_card.png",
            mime="image/png"
        )
    
    elif uploaded_image is None:
        st.warning("⚠ দয়া করে প্রথমে একটি ছবি আপলোড করুন।")
    else:
        st.error("⚠ ফন্ট পাওয়া যাচ্ছে না। ইন্টারনেট কানেকশন চেক করুন।")

else:
    st.info("বামে তথ্য পূরণ করে 'নিউজ কার্ড তৈরি করুন' বাটনে ক্লিক করুন।")
