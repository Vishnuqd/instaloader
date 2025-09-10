# instaloader

This repository contains a script that uses [Instaloader](https://instaloader.github.io/) to download posts from the public Instagram account `unistays.co` and export details to Excel.

## Usage

Install dependencies:

```bash
pip install instaloader openpyxl
```

Set Instagram credentials (login helps avoid rate limits):

```bash
export INSTAGRAM_USERNAME="your_instagram_username"
export INSTAGRAM_PASSWORD="your_instagram_password"
```

Run the script:

```bash
python fetch_unistays_posts.py
```

Images are saved in `unistays_images/` and post metadata in `unistays_posts.xlsx`.
