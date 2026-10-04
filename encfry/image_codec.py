from PIL import Image


# ---------------------------------------------------------
# FILE FORMAT
# ---------------------------------------------------------

MAGIC = b"ENCF"

VERSION = 4

# 4 bytes MAGIC
# 1 byte VERSION
# 3 bytes RESERVED
# 4 bytes PAYLOAD LENGTH
HEADER_SIZE = 12


# ---------------------------------------------------------
# IMAGE CAPACITY
# ---------------------------------------------------------

def get_capacity_bytes(image):
    """
    Returns approximately how many bytes can be stored
    inside the image.

    We use 1 bit from each RGB channel.
    """

    width, height = image.size

    total_bits = width * height * 3

    total_bytes = total_bits // 8

    # Reserve space for header
    return max(0, total_bytes - HEADER_SIZE)


# ---------------------------------------------------------
# BYTES -> BITS
# ---------------------------------------------------------

def bytes_to_bits(data):
    bits = []

    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    return bits


# ---------------------------------------------------------
# BITS -> BYTES
# ---------------------------------------------------------

def bits_to_bytes(bits):
    result = bytearray()

    for i in range(0, len(bits), 8):

        if i + 8 > len(bits):
            break

        byte = 0

        for bit in bits[i:i + 8]:
            byte = (byte << 1) | bit

        result.append(byte)

    return bytes(result)


# ---------------------------------------------------------
# CREATE HEADER
# ---------------------------------------------------------

def create_header(payload_length):
    """
    Creates the ENCFRY header.
    """

    if payload_length > 0xFFFFFFFF:
        raise ValueError("Payload is too large.")

    header = bytearray()

    header.extend(MAGIC)
    header.append(VERSION)

    # Reserved bytes
    header.extend(b"\x00\x00\x00")

    # 4-byte payload length
    header.extend(payload_length.to_bytes(4, "big"))

    return bytes(header)


# ---------------------------------------------------------
# HIDE DATA
# ---------------------------------------------------------

def hide_data(image, payload):
    """
    Hides encrypted payload inside RGB LSBs.

    Returns a new RGB image.
    """

    image = image.convert("RGB")

    header = create_header(len(payload))

    complete_data = header + payload

    bits = bytes_to_bits(complete_data)

    capacity = image.size[0] * image.size[1] * 3

    if len(bits) > capacity:
        capacity_bytes = get_capacity_bytes(image)

        raise ValueError(
            f"Message is too large for this image.\n"
            f"Maximum capacity: approximately {capacity_bytes} bytes.\n"
            f"Required: {len(payload)} bytes."
        )

    pixels = list(image.getdata())

    new_pixels = []

    bit_index = 0

    for pixel in pixels:

        r, g, b = pixel

        channels = [r, g, b]

        for channel_index in range(3):

            if bit_index < len(bits):

                # Clear LSB
                channels[channel_index] &= 254

                # Add our bit
                channels[channel_index] |= bits[bit_index]

                bit_index += 1

        new_pixels.append(tuple(channels))

    encoded_image = Image.new(
        "RGB",
        image.size
    )

    encoded_image.putdata(new_pixels)

    return encoded_image


# ---------------------------------------------------------
# EXTRACT DATA
# ---------------------------------------------------------

def extract_data(image):
    """
    Extracts the encrypted payload from an ENCFRY image.
    """

    image = image.convert("RGB")

    pixels = list(image.getdata())

    bits = []

    for pixel in pixels:

        r, g, b = pixel

        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)

    # Need at least the header
    if len(bits) < HEADER_SIZE * 8:
        raise ValueError(
            "This image is too small or does not contain ENCFRY data."
        )

    header_bits = bits[:HEADER_SIZE * 8]

    header = bits_to_bytes(header_bits)

    # Validate MAGIC
    if header[:4] != MAGIC:
        raise ValueError(
            "This is not a valid ENCFRY image."
        )

    # Validate version
    version = header[4]

    if version != VERSION:
        raise ValueError(
            f"Unsupported ENCFRY version: {version}"
        )

    # Extract payload length
    payload_length = int.from_bytes(
        header[8:12],
        "big"
    )

    payload_start = HEADER_SIZE * 8

    payload_end = payload_start + (payload_length * 8)

    if payload_end > len(bits):
        raise ValueError(
            "ENCFRY data appears to be corrupted or incomplete."
        )

    payload_bits = bits[
        payload_start:payload_end
    ]

    payload = bits_to_bytes(payload_bits)

    return payload