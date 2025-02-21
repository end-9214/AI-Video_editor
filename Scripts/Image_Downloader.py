from bing_image_downloader import downloader

def download_images(keywords, limit=1):
    """Downloads images for keywords."""
    image_paths = {}
    for keyword in keywords:
        downloader.download(keyword, limit=limit, output_dir="images", adult_filter_off=True, force_replace=False)
        image_paths[keyword] = f"images/{keyword}"
    return image_paths
