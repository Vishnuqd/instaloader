# Install required packages before running:
# pip install instaloader pandas openpyxl

import instaloader
import os
import pandas as pd

# Create an Instaloader instance
L = instaloader.Instaloader(download_comments=False,
                            save_metadata=False,
                            download_video_thumbnails=False,
                            download_geotags=False,
                            compress_json=False,
                            post_metadata_txt_pattern="")

# Set target Instagram account (public)
profile_name = "unistays.co"

# Create folder for images
image_folder = "unistays_images"
os.makedirs(image_folder, exist_ok=True)

# Get profile
profile = instaloader.Profile.from_username(L.context, profile_name)

# Prepare list for DataFrame
data = []

# Loop through posts
for i, post in enumerate(profile.get_posts(), start=1):
    post_number = i
    date_posted = post.date_utc.strftime("%Y-%m-%d %H:%M:%S")
    caption = post.caption if post.caption else ""

    # Download image(s) into folder
    filename = f"{profile_name}_{post_number}"
    L.download_pic(os.path.join(image_folder, filename), post.url, post.date_utc)

    # Save entry in list
    data.append({
        "Post Number": post_number,
        "Date": date_posted,
        "Caption": caption,
        "Image Filename": f"{filename}.jpg"
    })

    print(f"Processed post {i}")

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to Excel
excel_file = "unistays_posts.xlsx"
df.to_excel(excel_file, index=False)

print(f"\n✅ Done! Captions + images saved.\nExcel file: {excel_file}\nImages folder: {image_folder}")
