"""Fetch posts from Instagram account 'unistays.co' using Instaloader and save metadata to an Excel file.

Before running, ensure required packages are installed:
    pip install instaloader openpyxl

Provide login credentials via environment variables:
    export INSTAGRAM_USERNAME="your_username"
    export INSTAGRAM_PASSWORD="your_password"
"""

import os
import sys

try:
    import instaloader
except ModuleNotFoundError:
    print("The 'instaloader' package is required. Install it with: pip install instaloader openpyxl")
    sys.exit(1)

try:
    from openpyxl import Workbook
except ModuleNotFoundError:
    print("The 'openpyxl' package is required. Install it with: pip install instaloader openpyxl")
    sys.exit(1)

IMAGES_DIR = 'unistays_images'
OUTPUT_FILE = 'unistays_posts.xlsx'
MAX_POSTS = 20

def main():
    """Main execution."""
    os.makedirs(IMAGES_DIR, exist_ok=True)

    loader = instaloader.Instaloader(download_comments=False,
                                     save_metadata=False,
                                     filename_pattern='{shortcode}_{index}')

    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    if not username or not password:
        print("Instagram credentials not found. Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables.")
        sys.exit(1)
    try:
        loader.login(username, password)
    except Exception as exc:
        print(f"Login failed: {exc}")
        sys.exit(1)

    profile_name = 'unistays.co'
    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
    except Exception as exc:
        print(f"Failed to load profile '{profile_name}': {exc}")
        sys.exit(1)

    posts = profile.get_posts()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Posts'
    ws.append(['Post Number', 'Date', 'Caption', 'Likes', 'Image Filename'])

    for index, post in enumerate(posts, start=1):
        if MAX_POSTS and index > MAX_POSTS:
            break

        caption = post.caption or ''
        date_str = post.date_local.strftime('%Y-%m-%d')

        try:
            likes = post.likes
        except Exception:
            likes = None

        image_filenames = []
        try:
            if post.typename == 'GraphSidecar':
                for i, node in enumerate(post.get_sidecar_nodes(), start=1):
                    url = node.display_url
                    filename = f"{post.shortcode}_{i}.jpg"
                    filepath = os.path.join(IMAGES_DIR, filename)
                    loader.download_pic(filepath, url, post.date_utc)
                    image_filenames.append(filename)
            else:
                url = post.url
                filename = f"{post.shortcode}.jpg"
                filepath = os.path.join(IMAGES_DIR, filename)
                loader.download_pic(filepath, url, post.date_utc)
                image_filenames.append(filename)
        except Exception as exc:
            print(f"Error downloading images for post {index}: {exc}")

        ws.append([
            index,
            date_str,
            caption,
            likes if likes is not None else '',
            ', '.join(image_filenames)
        ])

    wb.save(OUTPUT_FILE)
    print(f'Saved data to {OUTPUT_FILE}')

if __name__ == '__main__':
    main()
