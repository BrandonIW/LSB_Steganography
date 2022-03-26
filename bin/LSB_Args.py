import argparse
import os
import imghdr


def check_args(encoding=False):
    args = _build_parser(encoding)
    return args


# Argument Parsers & Verifiers---------------------------------------------

def _build_parser(encoding):
    """ Build Parser to verify and accept user-defined arguments """
    if encoding:
        parser = argparse.ArgumentParser(description="LSB Steganography App - Encoding")
        required_args = parser.add_argument_group('Required Arguments')
        required_args.add_argument('-c', '--cover', required=True, type=_validate_file, help="Please enter the "
                                                                                             "relative or "
                                                                                             "absolute file path of "
                                                                                             "image that will "
                                                                                             "function to "
                                                                                             "hide/obfuscate "
                                                                                             "the hidden image (png or "
                                                                                             "bmp)")

        required_args.add_argument('-s', '--secret', required=True, type=_validate_file, help="Please enter the "
                                                                                              "relative "
                                                                                              "or absolute path of the"
                                                                                              "image that will be "
                                                                                              "hidden "
                                                                                              "inside the cover image ("
                                                                                              "bmp or png file)")

        required_args.add_argument('-o', '--output', required=True, type=str, help="Please enter the name of the "
                                                                                   "resultant "
                                                                                   "file that will be outputted with "
                                                                                   "the "
                                                                                   "hidden data i.e. Output.bmp")
        args = parser.parse_args()
        return args if _check_size(args.cover, args.secret) else False

    parser = argparse.ArgumentParser(description="LSB Steganography App - Decoding")
    required_args = parser.add_argument_group('Required Arguments')
    required_args.add_argument('-f', '--stegofile', required=True, type=_validate_file, help="Please enter the "
                                                                                             "relative or "
                                                                                             "absolute file path of "
                                                                                             "image that contains the "
                                                                                             "hidden image that will "
                                                                                             "be extracted")

    required_args.add_argument('-o', '--output', required=True, type=str, help="Please enter the name of the "
                                                                               "resultant "
                                                                               "file that will be outputted with "
                                                                               "the extracted "
                                                                               "hidden data i.e. Output.bmp")
    args = parser.parse_args()
    return args


def _validate_file(file):
    try:
        if not os.path.isfile(file):
            raise argparse.ArgumentTypeError(f"File path of {file} cannot be found, or is not a file. "
                                             f"Please check the file path")

        if imghdr.what(file) not in ['png', 'bmp']:
            raise argparse.ArgumentTypeError(f"The file provided is not a valid image file. Image file must be a "
                                             f"png or bmp file")

        with open(file, 'rb') as test_file:
            test_file.read()
            return file

    except IOError:
        raise argparse.ArgumentTypeError(f"{file} was found, but the file is not readable. Check permissions")
    except UnicodeDecodeError:
        raise argparse.ArgumentTypeError(f"{file} was found but some characters could not be decoded with UTF8. Check"
                                         f"file type/extension.")


def _extract_meta(secretimage):
    secret_name, secret_ext = os.path.splitext(secretimage)
    metadata = "###" + secret_name + secret_ext + "###"
    metadata = metadata.encode('utf-8')
    metadata = bin(int.from_bytes(metadata, 'big'))[2:]

    if len(metadata) % 8 != 0:
        padsize = 8 - (len(metadata) % 8)
        metadata = ('0' * padsize) + metadata

    return metadata


def _check_size(coverimage, secretimage):
    metadata = _extract_meta(secretimage)
    return True if os.stat(coverimage).st_size > (os.stat(secretimage).st_size * 8) + (len(metadata) / 8) else False


if __name__ == "__main__":
    check_args()
