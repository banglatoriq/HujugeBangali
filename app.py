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
# আমরা এখানে Google Fonts ব্যবহার করছি যা অনেক বেশি Reliable
def get_font_path(use_manual, uploaded_font_file):
    font_path = "HindSiliguri-Bold.ttf"
    
    # অপশন ১: ব্যবহারকারী যদি ম্যানুয়ালি আপলোড করেন
    if use_manual and uploaded_font_file is not None:
        return uploaded_font_file
    
    # অপশন ২: অটোমেটিক ডাউনলোড (Google Fonts থেকে)
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/hindsiliguri/HindSiliguri-Bold.ttf"
        try:
            with st.spinner('ইন্টারনেট থেকে ফন্ট ডাউনলোড হচ্ছে...'):
                response = requests.get(url)
                if response.status_code == 200:
                    with open(font_path, "wb") as f:
                        f.write(response.content)
                else:
                    st.error("ফন্ট ডাউনলোড ব্যর্থ হয়েছে। ম্যানুয়াল আপলোড অপশন ব্যবহার করুন।")
                    return None
        except Exception as e:
            st.error(f"ইন্টারনেট এরর: {e}")
            return None
    
    return font_path

# --- Sidebar Inputs ---
st.sidebar.header("🛠 সেটিংস")

# 1. Image Upload
uploaded_image = st.sidebar.file_uploader("১. ছবি আপলোড (বাধ্যতামূলক)", type=["jpg", "jpeg", "png"])
uploaded_logo = st.sidebar.file_uploader("২. লোগো আপলোড (অপশনাল)", type=["png", "jpg"])

# 2. Font Selection
font_choice = st.sidebar.radio("৩. ফন্ট নির্বাচন করুন:", ("অটোমেটিক (Hind Siliguri)", "ম্যানুয়াল আপলোড"))

manual_font = None
if font_choice == "ম্যানুয়াল আপলোড":
    manual_font = st.sidebar.file_uploader("আপনার .ttf ফন্ট ফাইল দিন", type=["ttf"])

# 3. Text Inputs
headline_text = st.sidebar.text_input("৪. প্রধান খবর (হলুদ লেখা)", "গুজবে কান দিয়ে দৌড়াচ্ছে জাতি!")
body_text = st.sidebar.text_area("৫. বিস্তারিত খবর (কালো লেখা)", "চাঞ্চল্যকর তথ্য: ইন্টারনেটে ছড়িয়ে পড়া খবরে লজিকের অভাব! ফলো করুন আমাদের পেজ।")
footer_text = st.sidebar.text_input("৬. ফুটার / তারিখ", "Follow us for more 'Hujug' | Date: 10/12/2025")

# --- Function to Wrap Text ---
def draw_text_wrapped(draw, text, font, max_width, start_y, text_color, align="center", image_width=800):
    lines = []
    # Dynamic character width approximation
    # Hind Siliguri is a bit wider, so we adjust char width estimate
    avg_char_width = 20 
    chars_per_line = int(max_width / avg_char_width)
    
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

# --- Main Logic ---

if st.button("📸 নিউজ কার্ড তৈরি করুন", type="primary"):
    
    if uploaded_image is None:
        st.warning("⚠ দয়া করে প্রথমে একটি ছবি (Main Image) আপলোড করুন।")
        st.stop()

    # ফন্ট লোড করার চেষ্টা
    font_source = get_font_path(font_choice == "ম্যানুয়াল আপলোড", manual_font)
    
    if font_source is None:
        st.error("⚠ ফন্ট পাওয়া যায়নি। দয়া করে 'ম্যানুয়াল আপলোড' সিলেক্ট করে আপনার কম্পিউটার থেকে একটি .ttf ফন্ট ফাইল দিন।")
        st.stop()

    try:
        # 1. Setup Canvas
        canvas_width = 800
        canvas_height = 900
        background_color = "white"
        
        img = Image.new('RGB', (canvas_width, canvas_height), background_color)
        draw = ImageDraw.Draw(img)

        # 2. Load Fonts
        # ফন্ট সাইজ একটু এডজাসট করা হয়েছে নতুন ফন্টের জন্য
        font_headline = ImageFont.truetype(font_source, 45) 
        font_body = ImageFont.truetype(font_source, 35)
        font_footer = ImageFont.truetype(font_source, 22)
        font_breaking = ImageFont.truetype(font_source, 55)

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

        # D. Headline Strip (Black Bar)
        bar_height = 100 # একটু বাড়ালাম যাতে বাংলা লেখা না কাটে
        bar_y = img_y + target_img_height - 40
        
        draw.rectangle([(img_x, bar_y), (img_x + target_img_width, bar_y + bar_height)], fill="black")
        
        # Yellow Headline Text
        draw_text_wrapped(draw, headline_text, font_headline, 740, bar_y + 15, "#facc15", "center", canvas_width)

        # E. Body Text
        body_start_y = bar_y + bar_height + 30
        draw_text_wrapped(draw, body_text, font_body, 740, body_start_y, "black", "center", canvas_width)

        # F. Footer
        draw.line([(50, canvas_height - 60), (750, canvas_height - 60)], fill="gray", width=2)
        draw_text_wrapped(draw, footer_text, font_footer, 700, canvas_height - 50, "#555555", "center", canvas_width)

        # --- Display Result ---
        st.success("✅ কার্ড তৈরি সম্পন্ন!")
        st.image(img, caption="আপনার জেনারেট করা নিউজ কার্ড", use_column_width=True)

        # --- Download Button ---
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="📥 হাই-কোয়ালিটি ডাউনলোড",
            data=byte_im,
            file_name="hujuge_news_card.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"ছবি তৈরি করার সময় সমস্যা হয়েছে: {e}")
        st.info("টিপস: 'ম্যানুয়াল আপলোড' অপশন ব্যবহার করে একটি সাধারণ ফন্ট (যেমন SolaimanLipi) দিয়ে চেষ্টা করুন।")

else:
    st.info("বাম পাশের প্যানেল থেকে ছবি আপলোড করে 'নিউজ কার্ড তৈরি করুন' বাটনে চাপ দিন।")
