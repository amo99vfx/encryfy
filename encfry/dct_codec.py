import cv2
import numpy as np
import struct

MAGIC = b"ENCF"
VERSION = 6

# Header:
# 4 bytes MAGIC
# 1 byte VERSION
# 1 byte METHOD
# 2 bytes RESERVED
# 4 bytes PAYLOAD LENGTH
HEADER_SIZE = 12

METHOD_DCT = 2

# DCT parameters
BLOCK_SIZE = 8

# Two mid-frequency coefficients.
# Using a pair makes detection more resistant to brightness changes.
COEFF_A = (3, 2)
COEFF_B = (2, 3)

# Strength of coefficient separation.
STRENGTH = 18.0


# ---------------------------------------------------------
# BASIC BIT CONVERSION
# ---------------------------------------------------------

def bytes_to_bits(data):
    bits = []

    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    return bits


def bits_to_bytes(bits):
    if len(bits) % 8 != 0:
        raise ValueError("Bit count is not divisible by 8")

    output = bytearray()

    for i in range(0, len(bits), 8):
        value = 0

        for bit in bits[i:i + 8]:
            value = (value << 1) | bit

        output.append(value)

    return bytes(output)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

def create_header(payload_length):
    return (
        MAGIC +
        bytes([VERSION]) +
        bytes([METHOD_DCT]) +
        b"\x00\x00" +
        struct.pack(">I", payload_length)
    )


# ---------------------------------------------------------
# CAPACITY
# ---------------------------------------------------------

def get_capacity_bytes(image):
    """
    Returns approximate maximum payload size in bytes.

    One bit is stored in each 8x8 block.
    We use 3 colour channels.
    """

    if image is None:
        return 0

    height, width = image.shape[:2]

    blocks_x = width // BLOCK_SIZE
    blocks_y = height // BLOCK_SIZE

    total_bits = blocks_x * blocks_y * 3

    total_bytes = total_bits // 8

    return max(0, total_bytes - HEADER_SIZE)


# ---------------------------------------------------------
# ERROR CORRECTION
# ---------------------------------------------------------

def add_repetition_coding(bits, repetitions=3):
    """
    Each bit is repeated several times.

    Example:

    1 -> 111
    0 -> 000

    During extraction majority voting reconstructs the bit.
    """

    encoded = []

    for bit in bits:
        encoded.extend([bit] * repetitions)

    return encoded


def repetition_decode(bits, repetitions=3):
    """
    Majority-vote decoder.
    """

    usable = len(bits) - (len(bits) % repetitions)

    decoded = []

    for i in range(0, usable, repetitions):
        group = bits[i:i + repetitions]

        ones = sum(group)

        decoded.append(
            1 if ones >= (repetitions / 2) else 0
        )

    return decoded


# ---------------------------------------------------------
# DCT HELPERS
# ---------------------------------------------------------

def _prepare_channel(channel):
    return channel.astype(np.float32)


def _embed_bit(block, bit):
    """
    Embed one bit by forcing a difference between
    two mid-frequency DCT coefficients.
    """

    dct = cv2.dct(block)

    a_pos = COEFF_A
    b_pos = COEFF_B

    a = dct[a_pos]
    b = dct[b_pos]

    if bit == 1:
        target = max(a, b)

        dct[a_pos] = target + STRENGTH / 2
        dct[b_pos] = target - STRENGTH / 2

    else:
        target = max(a, b)

        dct[a_pos] = target - STRENGTH / 2
        dct[b_pos] = target + STRENGTH / 2

    return cv2.idct(dct)


def _extract_raw_bit(block):
    """
    Extract one bit based on coefficient comparison.
    """

    dct = cv2.dct(block)

    a = dct[COEFF_A]
    b = dct[COEFF_B]

    return 1 if a > b else 0


# ---------------------------------------------------------
# EMBEDDING
# ---------------------------------------------------------

def hide_data(image, payload):
    """
    Hide encrypted payload inside an image using
    robust DCT + repetition coding.
    """

    if image is None:
        raise ValueError("Invalid image")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Image must be RGB/BGR colour image")

    height, width = image.shape[:2]

    blocks_x = width // BLOCK_SIZE
    blocks_y = height // BLOCK_SIZE

    if blocks_x < 4 or blocks_y < 4:
        raise ValueError("Image is too small")

    header = create_header(len(payload))

    raw_bits = bytes_to_bits(header + payload)

    # Error correction
    encoded_bits = add_repetition_coding(raw_bits, 3)

    capacity_bits = blocks_x * blocks_y * 3

    if len(encoded_bits) > capacity_bits:
        raise ValueError(
            f"Payload too large. "
            f"Need {len(encoded_bits)} bits, "
            f"but only {capacity_bits} bits are available."
        )

    result = image.astype(np.float32).copy()

    bit_index = 0

    # Process every colour channel.
    for channel in range(3):

        for by in range(blocks_y):

            for bx in range(blocks_x):

                if bit_index >= len(encoded_bits):
                    break

                y = by * BLOCK_SIZE
                x = bx * BLOCK_SIZE

                block = result[
                    y:y + BLOCK_SIZE,
                    x:x + BLOCK_SIZE,
                    channel
                ]

                bit = encoded_bits[bit_index]

                modified = _embed_bit(block, bit)

                result[
                    y:y + BLOCK_SIZE,
                    x:x + BLOCK_SIZE,
                    channel
                ] = modified

                bit_index += 1

            if bit_index >= len(encoded_bits):
                break

        if bit_index >= len(encoded_bits):
            break

    result = np.clip(result, 0, 255).astype(np.uint8)

    return result


# ---------------------------------------------------------
# EXTRACTION
# ---------------------------------------------------------

def extract_data(image):
    """
    Extract and error-correct an ENCFRY DCT payload.
    """

    if image is None:
        raise ValueError("Invalid image")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Image must be RGB/BGR colour image")

    height, width = image.shape[:2]

    blocks_x = width // BLOCK_SIZE
    blocks_y = height // BLOCK_SIZE

    if blocks_x < 4 or blocks_y < 4:
        raise ValueError("Image too small")

    raw_bits = []

    # Extract all available bits.
    for channel in range(3):

        for by in range(blocks_y):

            for bx in range(blocks_x):

                y = by * BLOCK_SIZE
                x = bx * BLOCK_SIZE

                block = image[
                    y:y + BLOCK_SIZE,
                    x:x + BLOCK_SIZE,
                    channel
                ].astype(np.float32)

                bit = _extract_raw_bit(block)

                raw_bits.append(bit)

    # First decode enough bits to recover the header.
    encoded_header_bits = HEADER_SIZE * 8 * 3

    if len(raw_bits) < encoded_header_bits:
        raise ValueError("Not enough data")

    header_encoded = raw_bits[:encoded_header_bits]

    header_bits = repetition_decode(
        header_encoded,
        repetitions=3
    )

    header = bits_to_bytes(header_bits[:HEADER_SIZE * 8])

    if len(header) != HEADER_SIZE:
        raise ValueError("Invalid header")

    # Validate magic.
    if header[:4] != MAGIC:
        raise ValueError("Not an ENCFRY DCT image")

    # Validate version.
    if header[4] != VERSION:
        raise ValueError("Unsupported ENCFRY version")

    # Validate method.
    if header[5] != METHOD_DCT:
        raise ValueError("Not DCT method")

    payload_length = struct.unpack(
        ">I",
        header[8:12]
    )[0]

    # Total raw bytes required.
    total_bytes = HEADER_SIZE + payload_length

    total_raw_bits = total_bytes * 8

    total_encoded_bits = total_raw_bits * 3

    if total_encoded_bits > len(raw_bits):
        raise ValueError("Incomplete payload")

    encoded_payload = raw_bits[:total_encoded_bits]

    decoded_bits = repetition_decode(
        encoded_payload,
        repetitions=3
    )

    decoded_bytes = bits_to_bytes(decoded_bits)

    header_check = decoded_bytes[:HEADER_SIZE]

    if header_check[:4] != MAGIC:
        raise ValueError("Header corruption")

    payload = decoded_bytes[
        HEADER_SIZE:
        HEADER_SIZE + payload_length
    ]

    if len(payload) != payload_length:
        raise ValueError("Payload length mismatch")

    return payload