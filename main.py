import asyncio
import os
import pathlib
import sys
from PIL import Image
from pillow_heif import register_heif_opener
from argparse import ArgumentParser, Namespace
from typing import List
from tqdm.asyncio import tqdm

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


def _get_converted_webp_image_path(
    image_path: pathlib.Path, output_dir: pathlib.Path
) -> pathlib.Path:
    image_basename = image_path.name
    image_basename_noext, _ = os.path.splitext(image_basename)
    result_path = output_dir.joinpath(f"{image_basename_noext}.webp")
    return result_path


def convert_and_strip_image_at_path_sync(
    image_path: pathlib.Path, output_dir: pathlib.Path
) -> os.stat_result:
    """given a pathlib.Path to an image in a supported format, convert to webp
    with lossless compression and save in output directory with extension .webp"""

    result_path = _get_converted_webp_image_path(image_path, output_dir)
    with Image.open(image_path) as img:
        if img.mode in UNSUPPORTED_WEBP_MODES:
            img = img.convert("RGB")
        img.save(result_path, "WEBP", lossless=True)
        # should raise if file wasn't saved successfully
        return result_path.stat()


async def convert_and_strip_image_at_path_async(
    image_path: pathlib.Path, output_dir: pathlib.Path
) -> os.stat_result:
    # run conversion task in a separate thread, otherwise we're blocking
    # event loop when pillows is saving image on same thread.
    return await asyncio.to_thread(
        convert_and_strip_image_at_path_sync, image_path, output_dir
    )


async def _logged_convert(image_path, output_dir):
    # print(f"converting {image_path} to {output_dir}")
    result = await convert_and_strip_image_at_path_async(image_path, output_dir)
    # print(f"done converting {image_path} to {output_dir}")
    return result


async def main():
    opts = parse_arguments(sys.argv[1:])
    # TODO: support calling program with path to specific image
    # instead of crawling a directory and converting everything in directory
    image_paths = find_images_in_directory(opts.input_dir)
    num_results = len(image_paths)
    print(f"found {num_results} images in {opts.input_dir}")
    # TODO: create output directory if it doesn't exist and we're allowed

    convert_tasks = [
        asyncio.create_task(_logged_convert(ip, opts.output_dir)) for ip in image_paths
    ]
    result_stats = []
    for ct in tqdm.as_completed(convert_tasks):
        convert_res = await ct
        result_stats.append(convert_res)


if __name__ == "__main__":
    asyncio.run(main())
