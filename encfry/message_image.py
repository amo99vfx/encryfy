from PIL import Image
import struct
import math
import random


MAGIC = b"MSGI"
VERSION = b"\x01"

HEADER_SIZE = 9


def bytes_to_bits(data):

    bits = []

    for byte in data:

        for i in range(7, -1, -1):

            bits.append(
                (byte >> i) & 1
            )

    return bits


def bits_to_bytes(bits):

    result = bytearray()

    for i in range(0, len(bits), 8):

        chunk = bits[i:i + 8]

        if len(chunk) < 8:
            break

        byte = 0

        for bit in chunk:

            byte = (
                byte << 1
            ) | bit

        result.append(byte)

    return bytes(result)


def message_to_image(message):

    # Convert message to UTF-8
    message_bytes = message.encode(
        "utf-8"
    )

    # Build header
    header = (
        MAGIC
        + VERSION
        + struct.pack(
            ">I",
            len(message_bytes)
        )
    )

    data = header + message_bytes

    bits = bytes_to_bits(data)

    # Add padding so the image doesn't look too small
    minimum_pixels = 4096

    required_pixels = math.ceil(
        len(bits) / 3
    )

    pixel_count = max(
        minimum_pixels,
        required_pixels
    )

    # Make the image roughly square
    side = math.ceil(
        math.sqrt(pixel_count)
    )

    width = side
    height = side

    total_pixels = (
        width * height
    )

    # Random background
    random.seed()

    pixels = []

    for _ in range(total_pixels):

        pixels.append(
            (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
        )

    # Put the data into the least significant bits
    bit_index = 0

    for pixel_index in range(
        total_pixels
    ):

        pixel = list(
            pixels[pixel_index]
        )

        for channel in range(3):

            if bit_index < len(bits):

                pixel[channel] = (
                    pixel[channel] & 0xFE
                ) | bits[bit_index]

                bit_index += 1

        pixels[pixel_index] = tuple(
            pixel
        )

        if bit_index >= len(bits):
            break

    image = Image.new(
        "RGB",
        (width, height)
    )

    image.putdata(pixels)

    return image


def image_to_message(image):

    image = image.convert("RGB")

    pixels = list(
        image.getdata()
    )

    bits = []

    for pixel in pixels:

        for channel in range(3):

            bits.append(
                pixel[channel] & 1
            )

    # Read header
    header_bits = bits[
        :HEADER_SIZE * 8
    ]

    header = bits_to_bytes(
        header_bits
    )

    if len(header) < HEADER_SIZE:

        raise ValueError(
            "Invalid message image."
        )

    if header[:4] != MAGIC:

        raise ValueError(
            "This is not a valid ENCFRY message image."
        )

    if header[4:5] != VERSION:

        raise ValueError(
            "Unsupported message image version."
        )

    message_length = struct.unpack(
        ">I",
        header[5:9]
    )[0]

    required_bits = (
        HEADER_SIZE + message_length
    ) * 8

    if required_bits > len(bits):

        raise ValueError(
            "Message image is incomplete."
        )

    message_bits = bits[
        HEADER_SIZE * 8:
        required_bits
    ]

    message_bytes = bits_to_bytes(
        message_bits
    )

    try:

        return message_bytes.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        raise ValueError(
            "Could not decode the original message."
        )