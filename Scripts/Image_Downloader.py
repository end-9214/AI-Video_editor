from bing_image_downloader import downloader
import os

def download_images(keywords, limit=1):
    image_paths = {}

    for keyword in keywords:
        downloader.download(keyword, limit=limit, output_dir="images", adult_filter_off=True, force_replace=False, timeout=60)
        image_paths[keyword] = f"images/{keyword}"

    return image_paths