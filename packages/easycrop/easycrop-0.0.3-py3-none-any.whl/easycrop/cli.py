import os
import argparse
from .crop import ImageCropper
from PIL.Image import registered_extensions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument(
        "--set_4k",
        "-4k",
        "-2160p",
        default=False,
        help="Sets crop to 3840x2160.",
        action="store_true",
    )
    parser.add_argument(
        "--set_720p",
        "-720p",
        default=False,
        help="Sets crop to 1280x720.",
        action="store_true",
    )

    parser.add_argument(
        "-width",
        default=False,
        help="Sets custom width.",
    )

    parser.add_argument(
        "-height",
        default=False,
        help="Sets custom height.",
    )

    parser.add_argument(
        "-r",
        default=False,
        help="Sets recursiveness.",
        action="store_true",
    )
    parser.add_argument("-ratio", default=False, help="Sets ratio.")
    parser.add_argument(
        "-resize",
        default=False,
        help="Will resize image if too big to best fit for resolution.",
        action="store_true",
    )

    args = parser.parse_known_args()[0]
    if args.set_4k:
        width = 3840
        height = 2160
    elif args.set_720p:
        width = 1280
        height = 720
    elif args.width or args.height:
        if not (args.width and args.height):
            raise Exception("You need to provide both width and height.")
        width = int(args.width)
        height = int(args.height)
    else:
        width = 1920
        height = 1080

    ratio = None
    if args.ratio:
        ratio = args.ratio

    resize = None
    if args.resize:
        resize = args.resize
    cropper = ImageCropper(width, height, ratio, resize)
    if not args.r:
        cropper.crop_image(args.filename)
    else:
        files_cropped = 0
        acceptable_extensions = [x[1:] for x in list(registered_extensions().keys())]
        for root, dirs, files in os.walk(args.filename):
            path = root.split(os.sep)
            for file in files:
                if file.split(".")[-1] in acceptable_extensions:
                    filepath = ""
                    for subpath in path:
                        filepath += subpath
                        filepath += "/"
                    filepath += file
                    print(
                        f"files_cropped: {files_cropped}\tCropping {filepath}", end="\r"
                    )
                    cropper.crop_image(filepath, path)
                    files_cropped += 1
