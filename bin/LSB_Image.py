import logging
import os.path
import re

from collections import deque
from itertools import islice, product, zip_longest
from logging.handlers import RotatingFileHandler
from PIL import Image


# Classes ----------------------------

class StegImage:
    def __init__(self, height, width, cover, outfile):
        self.height = height
        self.width = width
        self.cover = cover
        self.outfile = outfile
        self.pixels = deque()

    def add_pixels(self, pixels):
        for pixel in pixels:
            self.pixels.append(pixel)

    def write_image(self):
        img = Image.open(self.cover)
        rgb_cover = img.convert('RGB')
        pixel_object = rgb_cover.load()

        for y in range(self.height):
            for x in range(self.width):
                if self.pixels:
                    pixel_object[x, y] = self.pixels.popleft()
                    continue
                rgb_cover.save(self.outfile, "bmp")
                return


class HiddenImage:
    def __init__(self, pixels, height, width, output):
        self.height = height
        self.width = width
        self.output = output
        self.pixels = deque(pixels)

    def write_image(self):
        new_img = Image.new('RGB', (self.width, self.height))
        pixel_object = new_img.load()

        for y in range(self.height):
            for x in range(self.width):
                pixel_object[x, y] = self.pixels.popleft()

        new_img.save(self.output, "bmp")
        return


# Encoding---------------------------------------------

def encoder(coverimage, secretimage, outfile):
    logger = _build_logger_encode()

    with Image.open(coverimage) as cover:
        rgb_cover = cover.convert('RGB')
        cover_width, cover_height = rgb_cover.size
        cover_object = rgb_cover.load()

    with Image.open(secretimage) as secret:
        rgb_secret = secret.convert('RGB')
        secret_width, secret_height = rgb_secret.size
        secret_object = rgb_secret.load()
    logger.info(f"Successfully opened files {coverimage} & {secretimage}")

    metadata = _extract_meta(secretimage, logger, secret_width, secret_height)
    logger.info(f"Final Metadata Extracted: {metadata}")

    cover_pixel_generator = _cover_pixel_generator(cover_width, cover_height, cover_object)
    steg_image = StegImage(cover_height, cover_width, coverimage, outfile)
    logger.info(f"Successfully Created Stego Object")

    for y in range(secret_height):                        # Pull out a single hidden pixel and 8 cover bytes for each
        for x in range(secret_width):                     # Pixel coordinate of the hidden photo. Replace LSB and write
            red, green, blue = secret_object[x, y]
            secret_pixel = [bin(channel)[2:].zfill(8) for channel in [red, green, blue]]
            cover_pixels = next(cover_pixel_generator)
            new_pixels = _lsb_replace(secret_pixel, cover_pixels)
            steg_image.add_pixels(new_pixels)

    for bit_set in metadata:
        cover_pixels = next(cover_pixel_generator)        # Similar to above. This treats metadata in chunks of 3 bytes
        new_pixels = _lsb_replace(bit_set, cover_pixels)  # We can reuse lsbreplace and generator if we treat metadata
        steg_image.add_pixels(new_pixels)                 # in chunks of 3

    steg_image.write_image()
    logger.info(f"Successfully Wrote New Image to {outfile}")


def _extract_meta(secretimage, logger, secret_width, secret_height):
    secret_name, secret_ext = os.path.splitext(secretimage)
    logger.info(f"Extracting metadata {secret_name}, {secret_ext}")

    metadata = "###" + secret_name + secret_ext + "###" + str(secret_width) + "x" + str(secret_height) + "###" + "END"
    logger.info(f"Added Delimiters: {metadata}")

    metadata = metadata.encode('utf-8')
    metadata = bin(int.from_bytes(metadata, 'big'))[2:]
    logger.info(f"Convert to Binary: {metadata}")

    if len(metadata) % 8 != 0:
        padsize = 8 - (len(metadata) % 8)
        metadata = ('0' * padsize) + metadata
        logger.info(f"Adding Padding: {metadata}")

    metadata = [metadata[idex:idex + 8] for idex in range(0, len(metadata), 8)]  # Split into chunks of 8 to match
    metadata = [metadata[idex:idex + 3] for idex in range(0, len(metadata), 3)]  # generator's 8 byte output. Split
    return list(filter(lambda bit_set: bit_set, metadata))                       # again into chunks of 3 to replicate
                                                                                 # a single pixel


def _lsb_replace(secret_pixel, cover_pixels):
    data = []
    cover_bin_list = [[bin(channel)[2:].zfill(8) for channel in tup] for tup in cover_pixels]
    cover_bin_flat = [item for sublist in cover_bin_list for item in sublist]
    secret_bin = "".join(list(secret_pixel))

    for byte_cover, bit_secret in zip_longest(cover_bin_flat, secret_bin):  # Ziplongest to compensate for secret_pixels
        if bit_secret:                                                      # that are not a full chunk of 3 bytes
            byte_cover = byte_cover[:-1] + bit_secret                       # If not 3 bytes, just fill with the
        data.append(byte_cover)                                             # original pixel from cover image, unedited

    return [tuple(int(num, 2) for num in data)[idex:idex + 3] for idex in range(0, 24, 3)]


def _cover_pixel_generator(cover_width, cover_height, cover_object):
    width = range(cover_width)
    height = range(cover_height)
    pixels = (cover_object[x, y] for y, x in product(height, width))
    while True:
        chunk = list(islice(pixels, 8))
        if not chunk:
            break
        yield chunk


# Decoding---------------------------------------------

def decoder(stegofile, outfile):
    logger = _build_logger_decode()
    delim = False
    extracted_data = []

    with Image.open(stegofile) as cover:
        rgb_cover = cover.convert('RGB')
        stego_width, stego_height = rgb_cover.size
        stego_object = rgb_cover.load()
    logger.info(f"Opened Stegofile: {stegofile}")

    stego_pixel_generator = _stego_pixel_generator(stego_width, stego_height, stego_object)  # Pulls 24 pixels each call

    while not delim:
        pixels = next(stego_pixel_generator)                                                 # Pull 24 pixels of stego.
        cover_bin_list = [[bin(channel)[2:].zfill(8) for channel in tup] for tup in pixels]  # Convert to bits
        cover_bin_flat = [item for sublist in cover_bin_list for item in sublist]            # Flatten the list

        for pixel in _hidden_data_extraction(cover_bin_flat):   # Begin appending hidden data in RGB form
            extracted_data.append(pixel)                        # i.e. (255,241,13)

        delim = True if _check_meta(extracted_data) else False  # Checks if delimiter is met. In which case, we
                                                                # have all the hidden data

    (image_data, filename, file_ext, height, width) = _extract_metadata(extracted_data, logger)
    restored_image = HiddenImage(image_data, height, width, outfile)
    restored_image.write_image()

    logger.info(f"Successfully created restored Image: {outfile}")
    print(f"Completed. Restored Hidden image: {outfile} | Original filename: {filename} | Original Ext: {file_ext}")


def _hidden_data_extraction(pixels):
    """This function extracts the hidden data and returns it in the form of RGB Code Tuples i.e. (255, 123, 92)"""
    data = []

    for byte in pixels:
        data.append(byte[-1])

    hidden_pixels_bytes = ["".join(data[idex:idex + 8]) for idex in range(0, len(data), 8)]
    return [tuple(int(byte, 2) for byte in hidden_pixels_bytes)[idex:idex + 3] \
            for idex in range(0, len(hidden_pixels_bytes), 3)]


def _extract_metadata(extracted_pixels, logger):
    """This functions extracts the filename, extension, pixels, width and height from the hidden data"""
    regex_ext = re.compile(r'\.\w{3,}$')
    regex_name = re.compile(r'(?<=\\)[\w\s]+(?=\.)')

    # Isolates the data related to the hidden image itself
    meta_idex_start = extracted_pixels.index((35, 35, 35))
    image_data = extracted_pixels[:meta_idex_start]

    # Isolates data relating to the filename, extension and size
    metadata = [str(num) for subtuble in extracted_pixels[meta_idex_start + 1:] for num in subtuble]
    metadata = " ".join(metadata).split("35 35 35")
    meta_filename_ext, meta_size = metadata[0].strip(" ").split(" "), metadata[1].strip(" ").split(" ")

    # Logic to pull out file name and extension via regex
    filename_ext_data = "".join([chr(int(num)) for num in meta_filename_ext])
    file_extension = regex_ext.search(filename_ext_data).group()
    file_name = regex_name.search(filename_ext_data).group()

    # Logic to pull out file size
    filesize_data = "".join([chr(int(num)) for num in meta_size])
    height, width = filesize_data.split("x")

    logger.info(f"Filename: {file_name} | Extension: {file_extension} | Width: {width} | Height: {height}")
    return image_data, file_name, file_extension, int(width), int(height)


def _stego_pixel_generator(stego_width, stego_height, stego_object):
    width = range(stego_width)
    height = range(stego_height)
    pixels = (stego_object[x, y] for y, x in product(height, width))
    while True:
        chunk = list(islice(pixels, 24))
        if not chunk:
            break
        yield chunk


def _check_meta(extracted_pixels):
    """Checks to see if we have collected data beyond the hidden metadata. The hidden metadata is the last aspect
    of the hidden file that we embed. So once we have the metadata, there is no need to continue extracting pixels
    as we'd be extracting pixels belonging to the cover image at this point"""
    rgb_flattened = "".join([str(num) for subtuple in extracted_pixels for num in subtuple])
    detect_delim = rgb_flattened.split("353535")
    if len(detect_delim) >= 4:
        return True
    return False


# Cryptography---------------------------------------------

def encryption():
    pass


def decryption():
    pass


# Loggers---------------------------------------------

def _build_logger_encode():
    directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(directory)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler_info = RotatingFileHandler('../logs/Encoder.log', maxBytes=1048576)
    file_handler_info.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s || %(levelname)s || %(message)s || %(name)s')
    file_handler_info.setFormatter(formatter)
    logger.addHandler(file_handler_info)

    return logger


def _build_logger_decode():
    directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(directory)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler_info = RotatingFileHandler('../logs/Decoder.log', maxBytes=1048576)
    file_handler_info.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s || %(levelname)s || %(message)s || %(name)s')
    file_handler_info.setFormatter(formatter)
    logger.addHandler(file_handler_info)

    return logger
