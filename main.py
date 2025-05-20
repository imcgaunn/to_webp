import asyncio
import dataclasses
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


@dataclasses.dataclass(frozen=True)
class ConvertResult:
    filepath: str
    fstat: os.stat_result


def parse_arguments(args) -> Namespace:
    parser = ArgumentParser(
        prog="to-webp",
        description="a program to convert images to webp and strip exif data",
    )
    parser.add_argument(
        "input_dir",
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
    """Get list of paths for images of supported formats in a directory.

    Args:
        directory: the directory to search for images.

    Returns:
        The list of pathlib.Path objects for images under `directory`

    """
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
) -> ConvertResult:
    """Convert an image and strip it of exif data.

    Given a pathlib.Path to an image in a supported format, convert to webp
    with lossless compression and save in output directory with extension `.webp`.

    Args:
        image_path: The path to image that should be converted and stripped of exif
            data.
        output_dir: The path to directory where .webp should be output.

    Returns:
        ConvertResult: The result of image conversion.
    """

    result_path = _get_converted_webp_image_path(image_path, output_dir)
    with Image.open(image_path) as img:
        if img.mode in UNSUPPORTED_WEBP_MODES:
            img = img.convert("RGB")
        img.save(result_path, "WEBP", lossless=True)
        # should raise if file wasn't saved successfully
        return ConvertResult(filepath=str(result_path), fstat=result_path.stat())


async def convert_and_strip_image_at_path_async(
    image_path: pathlib.Path, output_dir: pathlib.Path
) -> ConvertResult:
    """Async wrapper for convert_and_strip_image_at_path_sync.

    Runs `convert_and_strip_image_at_path_sync` in separate executor to avoid
    blocking event loop when saving images.

    Args:
        image_path: The path to image that should be converted and stripped of exif
            data.
        output_dir: The path to directory where .webp should be output.

    Returns:
        ConvertResult: The result of image conversion.
    """
    return await asyncio.to_thread(
        convert_and_strip_image_at_path_sync, image_path, output_dir
    )


async def main():
    opts = parse_arguments(sys.argv[1:])
    # TODO: support calling program with path to specific image
    # instead of crawling a directory and converting everything in directory
    image_paths = find_images_in_directory(opts.input_dir)
    print(f"converting images in {opts.input_dir}")
    print(f"saving converted .webp images to {opts.output_dir} ")
    # TODO: create output directory if it doesn't exist and we're allowed

    convert_tasks = [
        asyncio.create_task(convert_and_strip_image_at_path_async(ip, opts.output_dir))
        for ip in image_paths
    ]
    result_stats = [
        await ct for ct in tqdm.as_completed(convert_tasks, desc="Converting")
    ]
    print(f"successfully converted {len(result_stats)} images")


if __name__ == "__main__":
    asyncio.run(main())
