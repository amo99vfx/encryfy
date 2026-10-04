from PIL import Image
import struct


MAGIC = b"ENCF"
VERSION = b"\x02"

# Header:
# MAGIC      = 4 bytes
# VERSION    = 1 byte
# PAYLOAD SIZE = 4 bytes

HEADER_SIZE = 9


def bytes_to_bits(data):
    bits = []

    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    return bits


def bits_to_bytes(bits):
    result = bytearray()

    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]

        if len(chunk) < 8:
            break

        byte = 0

        for bit in chunk:
            byte = (byte << 1) | bit

        result.append(byte)

    return bytes(result)


def hide_data(input_image, output_image, payload):

    image = Image.open(input_image).convert("RGB")

    width, height = image.size

    header = (
        MAGIC
        + VERSION
        + struct.pack(">I", len(payload))
    )

    complete_data = header + payload

    bits = bytes_to_bits(complete_data)

    capacity = width * height * 3

    if len(bits) > capacity:
        raise ValueError(
            f"Data is too large for this image.\n\n"
            f"Required: {len(bits)} bits\n"
            f"Available: {capacity} bits\n\n"
            f"Please choose a larger carrier image."
        )

    pixels = list(image.getdata())

    bit_index = 0
    new_pixels = []

    for pixel in pixels:

        new_pixel = list(pixel)

        for channel in range(3):

            if bit_index < len(bits):

                new_pixel[channel] = (
                    new_pixel[channel] & 0xFE
                ) | bits[bit_index]

                bit_index += 1

        new_pixels.append(tuple(new_pixel))

    output = Image.new(
        "RGB",
        image.size
    )

    output.putdata(new_pixels)

    output.save(
        output_image,
        "PNG"
    )


def extract_data(input_image):

    image = Image.open(input_image).convert("RGB")

    pixels = list(image.getdata())

    bits = []

    for pixel in pixels:

        for channel in range(3):

            bits.append(
                pixel[channel] & 1
            )

    # Extract header
    header_bits = bits[:HEADER_SIZE * 8]

    header = bits_to_bytes(
        header_bits
    )

    if len(header) < HEADER_SIZE:

        raise ValueError(
            "Image does not contain a valid ENCFRY payload."
        )

    magic = header[:4]

    if magic != MAGIC:

        raise ValueError(
            "No ENCFRY hidden data was found."
        )

    version = header[4:5]

    if version != VERSION:

        raise ValueError(
            "Unsupported ENCFRY data version."
        )

    payload_length = struct.unpack(
        ">I",
        header[5:9]
    )[0]

    total_bits = (
        HEADER_SIZE + payload_length
    ) * 8

    if total_bits > len(bits):

        raise ValueError(
            "Hidden data is incomplete or corrupted."
        )

    payload_bits = bits[
        HEADER_SIZE * 8:
        total_bits
    ]

    return bits_to_bytes(
        payload_bits
    )