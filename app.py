import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import requests
import io

# --- Page Configuration ---
st.set_page_config(page_title="Hujuge Bangali News Maker", layout="wide")
st.title("📢 হুজুগে বাঙালি - ব্রেকিং নিউজ মেকার")

# --- Helper Function: Download Font ---
def get_font_path(use_manual, uploaded_font_file):
    font_path = "HindSiliguri-Bold.ttf"
    
    if use_manual and uploaded_font_file is not None:
        return uploaded_font_file
    
    if not os.path.exists(font_path):
        # Hind Siliguri ফন্ট বাংলা যুক্তাক্ষরের জন্য সেরা
        url = "https://github.com/google/fonts/raw/main/ofl/hindsiliguri/HindSiliguri-Bold.ttf"
        try:
            with st.spinner('ফন্ট ডাউনলোড হচ্ছে...'):
                response = requests.get(url)
                if response.status_code == 200:
                    with open(font_path, "wb") as f:
                        f.write(response.content)
                else:
                    return None
        except:
            return None
    return font_path

# --- Sidebar Inputs ---
st.sidebar.header("🛠 সেটিংস")
uploaded_image = st.sidebar.file_uploader("১. ছবি আপলোড (বাধ্যতামূলক)", type=["jpg", "jpeg", "png"])
uploaded_logo = st.sidebar.file_uploader("২. লোগো আপলোড (অপশনাল)", type=["png", "jpg"])
font_choice = st.sidebar.radio("৩. ফন্ট সোর্স:", ("অটোমেটিক (Hind Siliguri)", "ম্যানুয়াল আপলোড"))

manual_font = None
if font_choice == "ম্যানুয়াল আপলোড":
    manual_font = st.sidebar.file_uploader("আপনার .ttf ফন্ট ফাইল দিন", type=["ttf"])

headline_text = st.sidebar.text_input("৪. প্রধান খবর", "গুজবে কান দিয়ে দৌড়াচ্ছে জাতি!")
body_text = st.sidebar.text_area("৫. বিস্তারিত খবর", "চাঞ্চল্যকর তথ্য: ইন্টারনেটে ছড়িয়ে পড়া খবরে লজিকের অভাব! ফলো করুন আমাদের পেজ।")
footer_text = st.sidebar.text_input("৬. ফুটার", "Follow us for more 'Hujug' | Date: 10/12/2025")

# --- Optimized Text Wrapper Function ---
def draw_text_wrapped(draw, text, font, max_width, start_y, text_color, align="center", image_width=800):
    lines = []
    avg_char_width = 20
    chars_per_line = int(max_width / avg_char_width)
    wrapper = textwrap.TextWrapper(width=chars_per_line)
    lines = wrapper.wrap(text=text)
    
    current_y = start_y
    for line in lines:
        # language='bn' প্যারামিটারটি যুক্তাক্ষর ঠিক রাখে
        bbox = draw.textbbox((0, 0), line, font=font, language='bn')
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        if align == "center":
            x_pos = (image_width - text_w) / 2
        else:
            x_pos = 50
            
        # এখানে language='bn' ব্যবহার করা হয়েছে
        draw.text((x_pos, current_y), line, font=font, fill=text_color, language='bn')
        current_y += text_h + 15
    return current_y

# --- Main Logic ---
if st.button("📸 নিউজ কার্ড তৈরি করুন", type="primary"):
    if uploaded_image is None:
        st.warning("⚠ ছবি আপলোড করুন।")
        st.stop()

    font_source = get_font_path(font_choice == "ম্যানুয়াল আপলোড", manual_font)
    if font_source is None:
        st.error("⚠ ফন্ট পাওয়া যায়নি।")
        st.stop()

    try:
        canvas_width = 800
        canvas_height = 900
        img = Image.new('RGB', (canvas_width, canvas_height), "white")
        draw = ImageDraw.Draw(img)

        # Fonts
        font_headline = ImageFont.truetype(font_source, 45) 
        font_body = ImageFont.truetype(font_source, 35)
        font_footer = ImageFont.truetype(font_source, 22)
        font_breaking = ImageFont.truetype(font_source, 55)

        # Layout Drawing
        draw.rectangle([(0, 0), (canvas_width, 120)], fill="#b91c1c")
        draw.text((50, 25), "BREAKING NEWS", fill="white", font=font_breaking)

        if uploaded_logo:
            logo = Image.open(uploaded_logo).convert("RGBA").resize((100, 100))
            img.paste(logo, (680, 10), logo)

        main_img = Image.open(uploaded_image).convert("RGB").resize((760, 450))
        img.paste(main_img, (20, 140))

        # Headline
        draw.rectangle([(20, 550), (780, 650)], fill="black")
        draw_text_wrapped(draw, headline_text, font_headline, 740, 565, "#facc15", "center", canvas_width)

        # Body
        draw_text_wrapped(draw, body_text, font_body, 740, 680, "black", "center", canvas_width)

        # Footer
        draw.line([(50, 840), (750, 840)], fill="gray", width=2)
        draw_text_wrapped(draw, footer_text, font_footer, 700, 850, "#555555", "center", canvas_width)

        st.image(img, caption="ফাইনাল আউটপুট")
        
        # Download
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("📥 ডাউনলোড", buf.getvalue(), "news.png", "image/png")

    except Exception as e:
        st.error(f"এরর: {e}")
