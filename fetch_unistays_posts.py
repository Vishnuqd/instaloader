"""Download posts from the public Instagram account `unistays.co` and
save details to an Excel file.

The script uses Instaloader without logging in, so it only works for
public accounts. It downloads each post's image(s) into `unistays_images/`
and records the post date, caption and image filename(s) in
`unistays_posts.xlsx`.

Before running, ensure required packages are installed:
    pip install instaloader openpyxl
"""

import os
import sys

# Attempt to import third-party libraries and print a helpful message if missing.
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

# Configuration constants.
IMAGES_DIR = "unistays_images"
OUTPUT_FILE = "unistays_posts.xlsx"
PROFILE = "unistays.co"
MAX_POSTS = 20  # Limit number of posts to fetch for demonstration.


def main() -> None:
    """Fetch posts and write details to an Excel file."""
    # Ensure the image output directory exists.
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Create an Instaloader instance. No login is required for public profiles.
    loader = instaloader.Instaloader(download_comments=False, save_metadata=False)

    try:
        profile = instaloader.Profile.from_username(loader.context, PROFILE)
    except Exception as exc:  # pragma: no cover - network dependent
        print(f"Failed to load profile '{PROFILE}': {exc}")
        sys.exit(1)

    posts = profile.get_posts()

    # Prepare the Excel workbook and header row.
    wb = Workbook()
    ws = wb.active
    ws.title = "Posts"
    ws.append(["Post Number", "Date", "Caption", "Image Filename"])

    for index, post in enumerate(posts, start=1):
        if MAX_POSTS and index > MAX_POSTS:
            break

        # Some posts might not have captions; use empty string in that case.
        caption = post.caption or ""
        date_str = post.date_local.strftime("%Y-%m-%d")
        image_filenames = []

        try:
            # Handle carousel posts with multiple images.
            if post.typename == "GraphSidecar":
                for i, node in enumerate(post.get_sidecar_nodes(), start=1):
                    url = node.display_url
                    filename = f"{post.shortcode}_{i}.jpg"
                    filepath = os.path.join(IMAGES_DIR, filename)
                    loader.download_pic(filepath, url, post.date_utc)
                    image_filenames.append(filename)
            else:
                # Single image or video (thumbnail) post.
                url = post.url
                filename = f"{post.shortcode}.jpg"
                filepath = os.path.join(IMAGES_DIR, filename)
                loader.download_pic(filepath, url, post.date_utc)
                image_filenames.append(filename)
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"Error downloading images for post {index}: {exc}")

        # Record the collected information in the Excel sheet.
        ws.append([index, date_str, caption, ", ".join(image_filenames)])

    wb.save(OUTPUT_FILE)
    print(f"Saved data to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
