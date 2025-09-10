"""Download posts from the public Instagram account `unistays.co` and save details to an Excel file.

The script logs in using environment variables `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`. If they are not provided, anonymous access is attempted which may be rate limited.

Each post's image(s) are saved into `unistays_images/` and data (post number, date, caption, likes, image filename) are written to `unistays_posts.xlsx`.

Before running, ensure required packages are installed:
    pip install instaloader openpyxl
"""

import os
import sys
import time

try:
    import instaloader
except ModuleNotFoundError:  # pragma: no cover - import guard
    print("The 'instaloader' package is required. Install it with: pip install instaloader openpyxl")
    sys.exit(1)

try:
    from openpyxl import Workbook
except ModuleNotFoundError:  # pragma: no cover - import guard
    print("The 'openpyxl' package is required. Install it with: pip install instaloader openpyxl")
    sys.exit(1)

IMAGES_DIR = "unistays_images"
OUTPUT_FILE = "unistays_posts.xlsx"
PROFILE = "unistays.co"
MAX_POSTS = 20  # Limit number of posts to fetch for demonstration.
REQUEST_DELAY = 2  # Seconds to pause between requests to avoid throttling.

def main() -> None:
    """Fetch posts and write details to an Excel file."""
    os.makedirs(IMAGES_DIR, exist_ok=True)

    loader = instaloader.Instaloader(download_comments=False, save_metadata=False)

    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    if username and password:
        try:
            loader.login(username, password)
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"Login failed: {exc}")
            sys.exit(1)
    else:
        print("No credentials provided; attempting anonymous access (may be rate limited).")

    try:
        profile = instaloader.Profile.from_username(loader.context, PROFILE)
    except Exception as exc:  # pragma: no cover - network dependent
        print(f"Failed to load profile '{PROFILE}': {exc}")
        sys.exit(1)

    posts = profile.get_posts()

    wb = Workbook()
    ws = wb.active
    ws.title = "Posts"
    ws.append(["Post Number", "Date", "Caption", "Likes", "Image Filename"])

    for index, post in enumerate(posts, start=1):
        if MAX_POSTS and index > MAX_POSTS:
            break

        caption = post.caption or ""
        date_str = post.date_local.strftime("%Y-%m-%d")
        image_filenames = []

        try:
            if post.typename == "GraphSidecar":
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
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"Error downloading images for post {index}: {exc}")

        try:
            likes = post.likes
        except Exception:  # pragma: no cover - likes hidden or request fails
            likes = ""

        ws.append([index, date_str, caption, likes, ", ".join(image_filenames)])

        time.sleep(REQUEST_DELAY)

    wb.save(OUTPUT_FILE)
    print(f"Saved data to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
