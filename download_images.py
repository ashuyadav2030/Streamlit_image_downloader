import streamlit as st
import csv
import os
import requests
import tempfile
import shutil
import random

def save_img(url, path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return f"✅ Downloaded: {os.path.basename(path)}"
        else:
            return f"❌ Failed: {url} (Status {response.status_code})"
    except Exception as e:
        return f"⚠️ Error downloading {url}: {e}"

def get_filtered_ids(csv_path, keyword):
    image_ids = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            image_id = row.get('image_id', '')
            if keyword in image_id:
                image_ids.append(image_id)
    return image_ids

def download_images(image_ids, folder_name):
    results = []

    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

    for image_id in image_ids:
        image_url = f"https://iscan.britanniaiscan.com/input_file/{image_id}"
        filepath = os.path.join(folder_name, f"{image_id}.jpg")
        result = save_img(image_url, filepath)
        results.append(result)
    return results

def zip_folder(folder_path, zip_filename):
    shutil.make_archive(zip_filename, 'zip', folder_path)
    return zip_filename + '.zip'

# Streamlit App UI
st.title("🖼️ Britannia Image Downloader")

uploaded_file = st.file_uploader("📤 Upload your CSV file", type=['csv'])

base_categories = ['WAF', 'CAK', 'CHE', 'RUS', 'BIS', 'GHE', 'DAI', 'CRO']
full_categories = [f"SOS{cat}" for cat in base_categories] + [f"SOD{cat}" for cat in base_categories]

category = st.selectbox(" Select a category to download", full_categories)


num_images = st.number_input("🔢 Number of random images to download", min_value=1, value=5, step=1)

download_button = st.button("📥 Download Images")

if uploaded_file and download_button:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    folder_name = f"{category.lower()}_images"

    with st.spinner("Filtering and downloading..."):
        all_ids = get_filtered_ids(tmp_path, category)

        if not all_ids:
            st.error(f"No images found for category: {category}")
        else:
            selected_ids = random.sample(all_ids, min(len(all_ids), num_images))
            output = download_images(selected_ids, folder_name)

            st.success(f"✅ Downloaded {len(selected_ids)} images.")
            for msg in output:
                st.write(msg)

            zip_path = zip_folder(folder_name, folder_name)
            with open(zip_path, 'rb') as f:
                st.download_button(
                    label="⬇️ Download All Images as ZIP",
                    data=f,
                    file_name=os.path.basename(zip_path),
                    mime='application/zip'
                )

            st.info(f"Images saved temporarily in: `{folder_name}/`")
