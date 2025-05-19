# to_webp

this is a little command line utility that can be used to
quickly convert a directory containing image files of various
formats to webp with losless compression.

the program relies on the venerable `pillows` library and its
heif extension, convert photos from my apple devices

## Usage

make sure you have `uv` installed and `python>=3.13`

```
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
parent folder, with their extensions replaced with `.webp`
