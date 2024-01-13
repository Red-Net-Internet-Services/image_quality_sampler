import os
import random
import mimetypes
import magic
# import pyexiv2
from PIL import Image


def is_jp2(file_path):
    try:
        with open(file_path, 'rb') as file:
            header = file.read(12)
            # JP2 files start with 0x0000000C, followed by 'jP  ' (0x6A502020), and then 0x0D0A870A
            if header.startswith(b'\x00\x00\x00\x0CjP \x20\x0D\x0A\x87\x0A'):
                return True
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

    return False


def check_image(file):
    mime_type, _ = mimetypes.guess_type(file)

    if not mime_type or not mime_type.startswith("image"):
        mime_type = magic.from_file(file, mime=True)

    if mime_type and mime_type.startswith("image"):
        return 1

    # Check for JP2 files specifically
    if is_jp2(file):
        return 1

    return 0


def select_random_images(folder_path, sample_size):
    subfolder_images = {}
    all_images = []

    # Walk through all subdirectories and collect images
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            try:
                # mime_type = magic.from_file(full_path, mime=True)
                if check_image(full_path):
                    if dirpath not in subfolder_images:
                        subfolder_images[dirpath] = []
                    subfolder_images[dirpath].append(full_path)
                    all_images.append(full_path)
            except Exception as e:
                print(e)

    # Ensure there are enough images to sample
    if len(all_images) < sample_size:
        raise ValueError(
            f"Only {len(all_images)} images found, but sample size is {sample_size}."
        )

    selected_images = []

    # Select one image from each subfolder
    for images in subfolder_images.values():
        if images:  # Check if there are images in the subfolder
            selected_images.append(random.choice(images))

    # If more images are needed, select randomly from all images
    if len(selected_images) < sample_size:
        remaining_sample_size = sample_size - len(selected_images)
        remaining_images = list(set(all_images) - set(selected_images))
        selected_images.extend(random.sample(remaining_images, remaining_sample_size))

    return selected_images


def extract_readable_metadata(img_path):
    metadata = {}
    with Image.open(img_path) as img:
        bits_per_channel = img.info.get("bit", 8)
        depth = len(img.getbands()) * bits_per_channel
        dpi = img.info.get("dpi", (None, None))
        # File size
        file_size = round(os.path.getsize(img_path) / (1024 * 1024), 2)
        file_name = os.path.basename(img_path)

        basic_data = {
            "File Name": file_name,
            "File Size": f"{file_size} MB",
            "Width": img.width,
            "Height": img.height,
            "Format": img.format,
            "Mode": img.mode,
            "Depth": f"{depth}bit {img.mode}",
            "DPI": dpi,  # Added this line for DPI
        }

        metadata["Basic"] = basic_data

    # with pyexiv2.Image(img_path) as exiv_img:
    #     # Extracting EXIF data
    #     exif_data = exiv_img.read_exif()
    #     human_readable_tags = [
    #         "Exif.Image.Make",
    #         "Exif.Image.Model",
    #         "Exif.Image.Software",
    #         "Exif.Photo.DateTimeOriginal",
    #         "Exif.Photo.DateTimeDigitized",
    #         "Exif.Photo.ShutterSpeedValue",
    #         "Exif.Photo.ApertureValue",
    #         "Exif.Photo.ExposureBiasValue",
    #         "Exif.Photo.MeteringMode",
    #         "Exif.Photo.Flash",
    #         "Exif.Photo.FocalLength",
    #         "Exif.Photo.ISOSpeedRatings",
    #         "Exif.Photo.ExposureTime",
    #         "Exif.Photo.FNumber",
    #         "Exif.Photo.ExposureProgram",
    #         "Exif.Photo.WhiteBalance",
    #         "Exif.Photo.LensModel",
    #     ]

    #     filtered_exif_data = {
    #         k.split(".")[-1]: v
    #         for k, v in exif_data.items()
    #         if k in human_readable_tags
    #     }
    #     if filtered_exif_data:
    #         metadata["EXIF"] = filtered_exif_data

    return metadata


class SamplingPlan:
    def __init__(self):
        self.lotSizeArray = [
            {
                "levels": {
                    "I": "A",
                    "II": "A",
                    "III": "B",
                    "S1": "A",
                    "S2": "A",
                    "S3": "A",
                    "S4": "A",
                },
                "min": 2,
                "max": 8,
            },
            {
                "levels": {
                    "I": "A",
                    "II": "B",
                    "III": "C",
                    "S1": "A",
                    "S2": "A",
                    "S3": "A",
                    "S4": "A",
                },
                "min": 9,
                "max": 15,
            },
            {
                "levels": {
                    "I": "B",
                    "II": "C",
                    "III": "D",
                    "S1": "A",
                    "S2": "A",
                    "S3": "B",
                    "S4": "B",
                },
                "min": 16,
                "max": 25,
            },
            {
                "levels": {
                    "I": "C",
                    "II": "D",
                    "III": "E",
                    "S1": "A",
                    "S2": "B",
                    "S3": "B",
                    "S4": "C",
                },
                "min": 26,
                "max": 50,
            },
            {
                "levels": {
                    "I": "C",
                    "II": "E",
                    "III": "F",
                    "S1": "B",
                    "S2": "B",
                    "S3": "C",
                    "S4": "C",
                },
                "min": 51,
                "max": 90,
            },
            {
                "levels": {
                    "I": "D",
                    "II": "F",
                    "III": "G",
                    "S1": "B",
                    "S2": "B",
                    "S3": "C",
                    "S4": "D",
                },
                "min": 91,
                "max": 150,
            },
            {
                "levels": {
                    "I": "E",
                    "II": "G",
                    "III": "H",
                    "S1": "B",
                    "S2": "C",
                    "S3": "D",
                    "S4": "E",
                },
                "min": 151,
                "max": 280,
            },
            {
                "levels": {
                    "I": "F",
                    "II": "H",
                    "III": "J",
                    "S1": "B",
                    "S2": "C",
                    "S3": "D",
                    "S4": "E",
                },
                "min": 281,
                "max": 500,
            },
            {
                "levels": {
                    "I": "G",
                    "II": "J",
                    "III": "K",
                    "S1": "C",
                    "S2": "C",
                    "S3": "E",
                    "S4": "F",
                },
                "min": 501,
                "max": 1200,
            },
            {
                "levels": {
                    "I": "H",
                    "II": "K",
                    "III": "L",
                    "S1": "C",
                    "S2": "D",
                    "S3": "E",
                    "S4": "G",
                },
                "min": 1201,
                "max": 3200,
            },
            {
                "levels": {
                    "I": "J",
                    "II": "L",
                    "III": "M",
                    "S1": "C",
                    "S2": "D",
                    "S3": "F",
                    "S4": "G",
                },
                "min": 3201,
                "max": 10000,
            },
            {
                "levels": {
                    "I": "K",
                    "II": "M",
                    "III": "N",
                    "S1": "C",
                    "S2": "D",
                    "S3": "F",
                    "S4": "H",
                },
                "min": 10001,
                "max": 35000,
            },
            {
                "levels": {
                    "I": "L",
                    "II": "N",
                    "III": "P",
                    "S1": "D",
                    "S2": "E",
                    "S3": "G",
                    "S4": "J",
                },
                "min": 35001,
                "max": 150000,
            },
            {
                "levels": {
                    "I": "M",
                    "II": "P",
                    "III": "Q",
                    "S1": "D",
                    "S2": "E",
                    "S3": "G",
                    "S4": "J",
                },
                "min": 150001,
                "max": 500000,
            },
            {
                "levels": {
                    "I": "N",
                    "II": "Q",
                    "III": "R",
                    "S1": "D",
                    "S2": "E",
                    "S3": "H",
                    "S4": "K",
                },
                "min": 500001,
                "max": -1,
            },
        ]
        self.sampleSizes = {
            "A": 2,
            "B": 3,
            "C": 5,
            "D": 8,
            "E": 13,
            "F": 20,
            "G": 32,
            "H": 50,
            "J": 80,
            "K": 125,
            "L": 200,
            "M": 315,
            "N": 500,
            "P": 800,
            "Q": 1250,
            "R": 2000,
        }
        self.AQLnumbers = [
            {
                "lotSize": 2,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 0, "reject": 1, "ss": 50},
                    "0.40": {"accept": 0, "reject": 1, "ss": 32},
                    "0.65": {"accept": 0, "reject": 1, "ss": 20},
                    "1.0": {"accept": 0, "reject": 1, "ss": 13},
                    "1.5": {"accept": 0, "reject": 1, "ss": 8},
                    "2.5": {"accept": 0, "reject": 1, "ss": 5},
                    "4.0": {"accept": 0, "reject": 1, "ss": 3},
                    "6.5": {"accept": 0, "reject": 1},
                },
            },
            {
                "lotSize": 3,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 0, "reject": 1, "ss": 50},
                    "0.40": {"accept": 0, "reject": 1, "ss": 32},
                    "0.65": {"accept": 0, "reject": 1, "ss": 20},
                    "1.0": {"accept": 0, "reject": 1, "ss": 13},
                    "1.5": {"accept": 0, "reject": 1, "ss": 8},
                    "2.5": {"accept": 0, "reject": 1, "ss": 5},
                    "4.0": {"accept": 0, "reject": 1},
                    "6.5": {"accept": 0, "reject": 1, "ss": 2},
                },
            },
            {
                "lotSize": 5,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 0, "reject": 1, "ss": 50},
                    "0.40": {"accept": 0, "reject": 1, "ss": 32},
                    "0.65": {"accept": 0, "reject": 1, "ss": 20},
                    "1.0": {"accept": 0, "reject": 1, "ss": 13},
                    "1.5": {"accept": 0, "reject": 1, "ss": 8},
                    "2.5": {"accept": 0, "reject": 1},
                    "4.0": {"accept": 0, "reject": 1, "ss": 3},
                    "6.5": {"accept": 1, "reject": 2, "ss": 8},
                },
            },
            {
                "lotSize": 8,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 0, "reject": 1, "ss": 50},
                    "0.40": {"accept": 0, "reject": 1, "ss": 32},
                    "0.65": {"accept": 0, "reject": 1, "ss": 20},
                    "1.0": {"accept": 0, "reject": 1, "ss": 13},
                    "1.5": {"accept": 0, "reject": 1},
                    "2.5": {"accept": 0, "reject": 1, "ss": 5},
                    "4.0": {"accept": 1, "reject": 2, "ss": 13},
                    "6.5": {"accept": 1, "reject": 2},
                },
            },
            {
                "lotSize": 13,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 0, "reject": 1, "ss": 50},
                    "0.40": {"accept": 0, "reject": 1, "ss": 32},
                    "0.65": {"accept": 0, "reject": 1, "ss": 20},
                    "1.0": {"accept": 0, "reject": 1},
                    "1.5": {"accept": 0, "reject": 1, "ss": 8},
                    "2.5": {"accept": 1, "reject": 2, "ss": 20},
                    "4.0": {"accept": 1, "reject": 2},
                    "6.5": {"accept": 2, "reject": 3},
                },
            },
            {
                "lotSize": 20,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 0, "reject": 1, "ss": 50},
                    "0.40": {"accept": 0, "reject": 1, "ss": 32},
                    "0.65": {"accept": 0, "reject": 1},
                    "1.0": {"accept": 0, "reject": 1, "ss": 13},
                    "1.5": {"accept": 1, "reject": 2, "ss": 32},
                    "2.5": {"accept": 1, "reject": 2},
                    "4.0": {"accept": 2, "reject": 3},
                    "6.5": {"accept": 3, "reject": 4},
                },
            },
            {
                "lotSize": 32,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 0, "reject": 1, "ss": 50},
                    "0.40": {"accept": 0, "reject": 1},
                    "0.65": {"accept": 0, "reject": 1, "ss": 20},
                    "1.0": {"accept": 1, "reject": 2, "ss": 50},
                    "1.5": {"accept": 1, "reject": 2},
                    "2.5": {"accept": 2, "reject": 3},
                    "4.0": {"accept": 3, "reject": 4},
                    "6.5": {"accept": 5, "reject": 6},
                },
            },
            {
                "lotSize": 50,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 0, "reject": 1},
                    "0.40": {"accept": 0, "reject": 1, "ss": 32},
                    "0.65": {"accept": 1, "reject": 2, "ss": 80},
                    "1.0": {"accept": 1, "reject": 2},
                    "1.5": {"accept": 2, "reject": 3},
                    "2.5": {"accept": 3, "reject": 4},
                    "4.0": {"accept": 5, "reject": 6},
                    "6.5": {"accept": 7, "reject": 8},
                },
            },
            {
                "lotSize": 80,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 0, "reject": 1},
                    "0.25": {"accept": 0, "reject": 1, "ss": 50},
                    "0.40": {"accept": 1, "reject": 2, "ss": 125},
                    "0.65": {"accept": 1, "reject": 2},
                    "1.0": {"accept": 2, "reject": 3},
                    "1.5": {"accept": 3, "reject": 4},
                    "2.5": {"accept": 5, "reject": 6},
                    "4.0": {"accept": 7, "reject": 8},
                    "6.5": {"accept": 10, "reject": 11},
                },
            },
            {
                "lotSize": 125,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 0, "reject": 1},
                    "0.15": {"accept": 0, "reject": 1, "ss": 80},
                    "0.25": {"accept": 1, "reject": 2, "ss": 200},
                    "0.40": {"accept": 1, "reject": 2},
                    "0.65": {"accept": 2, "reject": 3},
                    "1.0": {"accept": 3, "reject": 4},
                    "1.5": {"accept": 5, "reject": 6},
                    "2.5": {"accept": 7, "reject": 8},
                    "4.0": {"accept": 10, "reject": 11},
                    "6.5": {"accept": 14, "reject": 15},
                },
            },
            {
                "lotSize": 200,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1},
                    "0.10": {"accept": 0, "reject": 1, "ss": 125},
                    "0.15": {"accept": 1, "reject": 2, "ss": 315},
                    "0.25": {"accept": 1, "reject": 2},
                    "0.40": {"accept": 2, "reject": 3},
                    "0.65": {"accept": 3, "reject": 4},
                    "1.0": {"accept": 5, "reject": 6},
                    "1.5": {"accept": 7, "reject": 8},
                    "2.5": {"accept": 10, "reject": 11},
                    "4.0": {"accept": 14, "reject": 15},
                    "6.5": {"accept": 21, "reject": 22},
                },
            },
            {
                "lotSize": 315,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 0, "reject": 1, "ss": 200},
                    "0.10": {"accept": 1, "reject": 2, "ss": 500},
                    "0.15": {"accept": 1, "reject": 2},
                    "0.25": {"accept": 2, "reject": 3},
                    "0.40": {"accept": 3, "reject": 4},
                    "0.65": {"accept": 5, "reject": 6},
                    "1.0": {"accept": 7, "reject": 8},
                    "1.5": {"accept": 10, "reject": 11},
                    "2.5": {"accept": 14, "reject": 15},
                    "4.0": {"accept": 21, "reject": 22},
                    "6.5": {"accept": 21, "reject": 22, "ss": 200},
                },
            },
            {
                "lotSize": 500,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 1, "reject": 2, "ss": 800},
                    "0.10": {"accept": 1, "reject": 2},
                    "0.15": {"accept": 2, "reject": 3},
                    "0.25": {"accept": 3, "reject": 4},
                    "0.40": {"accept": 5, "reject": 6},
                    "0.65": {"accept": 7, "reject": 8},
                    "1.0": {"accept": 10, "reject": 11},
                    "1.5": {"accept": 14, "reject": 15},
                    "2.5": {"accept": 21, "reject": 22},
                    "4.0": {"accept": 21, "reject": 22, "ss": 315},
                    "6.5": {"accept": 21, "reject": 22, "ss": 200},
                },
            },
            {
                "lotSize": 800,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 1, "reject": 2},
                    "0.10": {"accept": 2, "reject": 3},
                    "0.15": {"accept": 3, "reject": 4},
                    "0.25": {"accept": 5, "reject": 6},
                    "0.40": {"accept": 7, "reject": 8},
                    "0.65": {"accept": 10, "reject": 11},
                    "1.0": {"accept": 14, "reject": 15},
                    "1.5": {"accept": 21, "reject": 22},
                    "2.5": {"accept": 21, "reject": 22, "ss": 500},
                    "4.0": {"accept": 21, "reject": 22, "ss": 315},
                    "6.5": {"accept": 21, "reject": 22, "ss": 200},
                },
            },
            {
                "lotSize": 1250,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 2, "reject": 3},
                    "0.10": {"accept": 3, "reject": 4},
                    "0.15": {"accept": 5, "reject": 6},
                    "0.25": {"accept": 7, "reject": 8},
                    "0.40": {"accept": 10, "reject": 11},
                    "0.65": {"accept": 14},
                    "1.0": {"accept": 21, "reject": 22},
                    "1.5": {"accept": 21, "reject": 22, "ss": 800},
                    "2.5": {"accept": 21, "reject": 22, "ss": 500},
                    "4.0": {"accept": 21, "reject": 22, "ss": 315},
                    "6.5": {"accept": 21, "reject": 22, "ss": 200},
                },
            },
            {
                "lotSize": 2000,
                "numbers": {
                    "0": {"accept": 0, "reject": 0},
                    "0.065": {"accept": 3, "reject": 4},
                    "0.10": {"accept": 5, "reject": 6},
                    "0.15": {"accept": 7, "reject": 8},
                    "0.25": {"accept": 10, "reject": 11},
                    "0.40": {"accept": 14, "reject": 15},
                    "0.65": {"accept": 21, "reject": 22},
                    "1.0": {"accept": 21, "reject": 22, "ss": 1250},
                    "1.5": {"accept": 21, "reject": 22, "ss": 800},
                    "2.5": {"accept": 21, "reject": 22, "ss": 500},
                    "4.0": {"accept": 21, "reject": 22, "ss": 315},
                    "6.5": {"accept": 21, "reject": 22, "ss": 200},
                },
            },
        ]

    def get_sample_size_and_acceptance(self, lot_size, inspection_level, AQL):
        # Iterate through the lotSizeArray
        for lot in self.lotSizeArray:
            if lot["min"] <= lot_size and (
                lot["max"] >= lot_size or lot["max"] == -1
            ):
                sample_size_letter = lot["levels"][inspection_level]
                default_sample_size = self.sampleSizes[sample_size_letter]

                # Iterate through the AQLnumbers
                for aql in self.AQLnumbers:
                    if aql["lotSize"] == default_sample_size:
                        if AQL in aql["numbers"]:
                            accept = aql["numbers"][AQL]["accept"]
                            reject = aql["numbers"][AQL]["reject"]
                            try:
                                sample_size = aql["numbers"][AQL]["ss"]
                            except KeyError:
                                sample_size = default_sample_size
                            if sample_size > lot_size:
                                sample_size = lot_size
                            return sample_size, accept, reject
                        else:
                            return None, None, None
        return None, None, None
