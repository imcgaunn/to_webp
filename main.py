from PIL import Image
from argparse import ArgumentParser, Namespace
import os
import pathlib
import sys
from typing import List

SUPPORTED_IMG_EXTENSIONS = {".jpg", ".jpeg", ".heic", ".heif", ".png", ".bmp"}


def parse_arguments(args) -> Namespace:
    parser = ArgumentParser(
        prog="to-webp",
        description="a program to convert images to webp and strip exif data",
    )
    parser.add_argument(
        "input_dir",
        default=str(pathlib.Path(__file__).parent),
        type=str,
        help="directory containing source images to convert",
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="directory into which webp files should be output",
    )
    return parser.parse_args(args)


def find_images_in_directory(directory: pathlib.Path) -> List[pathlib.Path]:
    dir_images = []
    for root, _, files in directory.walk():
        for name in files:
            _, f_ext = os.path.splitext(name)
            if f_ext.lower() in SUPPORTED_IMG_EXTENSIONS:
                dir_images.append(root.joinpath(name))
    return dir_images


def convert_and_strip_image_at_path(image_path):
    pass


def convert_and_strip_image():
    pass


def main():
    opts = parse_arguments(sys.argv[1:])
    print(opts)


if __name__ == "__main__":
    main()
