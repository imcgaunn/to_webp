from PIL import Image
from pillow_heif import register_heif_opener
from argparse import ArgumentParser, Namespace
import os
import pathlib
import sys
from typing import List

register_heif_opener()

SUPPORTED_IMG_EXTENSIONS = {".jpg", ".jpeg", ".heic", ".heif", ".png", ".bmp"}
UNSUPPORTED_WEBP_MODES = {"RGBA", "P"}


def parse_arguments(args) -> Namespace:
    parser = ArgumentParser(
        prog="to-webp",
        description="a program to convert images to webp and strip exif data",
    )
    parser.add_argument(
        "input_dir",
        default=pathlib.Path(__file__).parent,
        type=pathlib.Path,
        help="directory containing source images to convert",
    )
    parser.add_argument(
        "output_dir",
        type=pathlib.Path,
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


def get_converted_webp_image_path(
    image_path: pathlib.Path, output_dir: pathlib.Path
) -> pathlib.Path:
    image_basename = image_path.name
    image_basename_noext, _ = os.path.splitext(image_basename)
    result_path = output_dir.joinpath(f"{image_basename_noext}.webp")
    return result_path


def convert_and_strip_image_at_path(
    image_path: pathlib.Path, output_dir: pathlib.Path
) -> os.stat_result:
    """given a pathlib.Path to an image in a supported format, convert to webp
    with lossless compression and save in output directory with extension .webp"""

    result_path = get_converted_webp_image_path(image_path, output_dir)
    with Image.open(image_path) as img:
        if img.mode in UNSUPPORTED_WEBP_MODES:
            img = img.convert("RGB")
        img.save(result_path, "WEBP", lossless=True)
        # should raise if file wasn't saved successfully
        return result_path.stat()


def main():
    opts = parse_arguments(sys.argv[1:])
    print(f"finding images in {opts.input_dir}")
    # TODO: support calling program with path to specific image
    # instead of crawling a directory and converting everything in directory
    image_paths = find_images_in_directory(opts.input_dir)

    num_results = len(image_paths)
    print(f"found {num_results} images in {opts.input_dir}")
    if num_results > 20:
        print("only printing first 20 results")
    for ip in image_paths[0:20]:
        print(str(ip))

    print("result paths:")
    result_paths = [
        get_converted_webp_image_path(ip, opts.output_dir) for ip in image_paths
    ]
    for rp in result_paths[0:20]:
        print(str(rp))


if __name__ == "__main__":
    main()
