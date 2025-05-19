# to_webp

`to_webp` is a command line utility that can be used to quickly convert a
directory containing image files of various formats to webp with lossless
compression.

the program relies on the venerable [pillow](https://pillow.readthedocs.io/en/stable/) library and
the [pillow-heif](https://pillow-heif.readthedocs.io/en/latest/) extension,
to convert photos from my apple devices. It also relies on
[tqdm](https://github.com/tqdm/tqdm) for progress reporting

## Usage

Make sure you have [uv](https://github.com/astral-sh/uv) installed and
`python>=3.13`. `uv` _might_ be able to install python for you, but i'm not a
doctor, and this isn't medical advice.

### example usage - get help

```bash
to_webp on  main [!] is 📦 v0.1.0 via 🐍 v3.13.2
❯ uv run python3 main.py --help
usage: to-webp [-h] input_dir output_dir

a program to convert images to webp and strip exif data

positional arguments:
  input_dir   directory containing source images to convert
  output_dir  directory into which webp files should be output

options:
  -h, --help  show this help message and exit

tv run python3 main.py --help
```

`to_webp` will output files into output_dir ignoring any structure they had in the
parent folder, with their original extensions replaced with `.webp`
