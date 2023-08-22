import datetime
import os

import exifread
from PIL import Image


def extract_image_metadata(img_path):
    metadata = {}

    # Using PIL for basic metadata
    with Image.open(img_path) as img:
        metadata["DPI"] = img.info.get("dpi", (None, None))
        channels = len(img.getbands())
        metadata["Color depth"] = f"{img.bits * channels}bit {img.mode}"
        metadata["File type"] = img.format
        metadata["Size"] = round(
            os.path.getsize(img_path) / (1024 * 1024), 2
        )  # in MB
        metadata["Filename"] = os.path.basename(img_path)

    # Using exifread for more detailed metadata
    with open(img_path, "rb") as f:
        exif_data = exifread.process_file(f)

        # If EXIF DateTimeOriginal is not available, use file creation date
        exif_date = exif_data.get("EXIF DateTimeOriginal", None)
        if exif_date:
            metadata["Date Created"] = str(exif_date)
        else:
            creation_timestamp = os.path.getctime(img_path)
            creation_date = datetime.datetime.fromtimestamp(creation_timestamp)
            metadata["Date Created"] = creation_date.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        metadata["Creation method"] = str(
            exif_data.get("Image Make", None)
        ) or str(exif_data.get("Image Software", None))

    return metadata
