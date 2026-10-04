from PIL import Image, ImageDraw, ImageFilter
import random
import math


WIDTH = 900
HEIGHT = 900


# ---------------------------------------------------------
# RANDOM HELPERS
# ---------------------------------------------------------

def rand_color():
    palettes = [
        ((255, 225, 230), (250, 190, 205), (120, 75, 90)),
        ((225, 240, 255), (175, 210, 245), (70, 95, 125)),
        ((235, 245, 220), (185, 215, 155), (75, 100, 65)),
        ((255, 238, 200), (245, 190, 110), (120, 75, 35)),
        ((235, 220, 250), (195, 165, 230), (90, 65, 115)),
        ((245, 235, 220), (215, 185, 145), (100, 70, 45)),
    ]

    return random.choice(palettes)


def random_pastel():
    return (
        random.randint(190, 255),
        random.randint(190, 255),
        random.randint(190, 255)
    )


# ---------------------------------------------------------
# BACKGROUND
# ---------------------------------------------------------

def create_background(draw):

    bg1, bg2, _ = rand_color()

    draw.rectangle(
        (0, 0, WIDTH, HEIGHT),
        fill=bg1
    )

    # Soft circles
    for _ in range(random.randint(25, 50)):

        x = random.randint(-100, WIDTH + 100)
        y = random.randint(-100, HEIGHT + 100)

        radius = random.randint(30, 130)

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius
            ),
            fill=random_pastel()
        )

    # Decorative stars
    for _ in range(random.randint(8, 18)):

        x = random.randint(40, WIDTH - 40)
        y = random.randint(40, HEIGHT - 40)

        size = random.randint(5, 14)

        draw.line(
            (x - size, y, x + size, y),
            fill="white",
            width=3
        )

        draw.line(
            (x, y - size, x, y + size),
            fill="white",
            width=3
        )


# ---------------------------------------------------------
# EYES
# ---------------------------------------------------------

def draw_eye(draw, x, y, size, eye_style):

    if eye_style == 0:

        draw.ellipse(
            (
                x - size,
                y - size,
                x + size,
                y + size
            ),
            fill=(45, 35, 40)
        )

        draw.ellipse(
            (
                x - size // 2,
                y - size // 2,
                x + size // 2,
                y + size // 2
            ),
            fill=(95, 65, 75)
        )

    elif eye_style == 1:

        draw.ellipse(
            (
                x - size,
                y - size,
                x + size,
                y + size
            ),
            fill=(35, 35, 40)
        )

    else:

        draw.ellipse(
            (
                x - size,
                y - size,
                x + size,
                y + size
            ),
            fill=(50, 40, 45)
        )

    # Eye shine
    shine = max(5, size // 3)

    draw.ellipse(
        (
            x - shine,
            y - shine,
            x,
            y
        ),
        fill="white"
    )


# ---------------------------------------------------------
# FACE
# ---------------------------------------------------------

def draw_face(
    draw,
    animal,
    base,
    light,
    dark
):

    cx = WIDTH // 2
    cy = 380

    eye_style = random.randint(0, 2)

    # -----------------------------------------------------
    # EARS
    # -----------------------------------------------------

    ear_style = random.randint(0, 2)

    if animal in ["Cat", "Fox", "Tiger"]:

        if ear_style == 0:

            draw.polygon(
                [
                    (200, 260),
                    (150, 80),
                    (330, 205)
                ],
                fill=base,
                outline=dark
            )

            draw.polygon(
                [
                    (570, 205),
                    (750, 80),
                    (700, 260)
                ],
                fill=base,
                outline=dark
            )

        else:

            draw.ellipse(
                (130, 110, 310, 320),
                fill=base,
                outline=dark,
                width=5
            )

            draw.ellipse(
                (590, 110, 770, 320),
                fill=base,
                outline=dark,
                width=5
            )

    elif animal == "Bunny":

        draw.ellipse(
            (205, 40, 350, 320),
            fill=base,
            outline=dark,
            width=5
        )

        draw.ellipse(
            (550, 40, 695, 320),
            fill=base,
            outline=dark,
            width=5
        )

        draw.ellipse(
            (235, 80, 320, 250),
            fill=light
        )

        draw.ellipse(
            (580, 80, 665, 250),
            fill=light
        )

    elif animal == "Panda":

        draw.ellipse(
            (155, 120, 340, 300),
            fill=dark
        )

        draw.ellipse(
            (560, 120, 745, 300),
            fill=dark
        )

    elif animal == "Dog":

        # floppy ears
        draw.ellipse(
            (90, 220, 285, 500),
            fill=base,
            outline=dark,
            width=5
        )

        draw.ellipse(
            (615, 220, 810, 500),
            fill=base,
            outline=dark,
            width=5
        )

    # -----------------------------------------------------
    # HEAD
    # -----------------------------------------------------

    draw.ellipse(
        (145, 170, 755, 700),
        fill=base,
        outline=dark,
        width=6
    )

    # -----------------------------------------------------
    # PANDA EYE PATCHES
    # -----------------------------------------------------

    if animal == "Panda":

        draw.ellipse(
            (225, 310, 390, 455),
            fill=dark
        )

        draw.ellipse(
            (510, 310, 675, 455),
            fill=dark
        )

    # -----------------------------------------------------
    # EYES
    # -----------------------------------------------------

    draw_eye(
        draw,
        310,
        375,
        48,
        eye_style
    )

    draw_eye(
        draw,
        590,
        375,
        48,
        eye_style
    )

    # -----------------------------------------------------
    # MUZZLE
    # -----------------------------------------------------

    draw.ellipse(
        (275, 440, 625, 620),
        fill=light
    )

    # Nose
    draw.ellipse(
        (425, 470, 475, 510),
        fill=dark
    )

    # Smile variations
    smile = random.randint(0, 2)

    if smile == 0:

        draw.arc(
            (360, 485, 450, 570),
            10,
            160,
            fill=dark,
            width=7
        )

        draw.arc(
            (450, 485, 540, 570),
            20,
            170,
            fill=dark,
            width=7
        )

    elif smile == 1:

        draw.arc(
            (370, 485, 530, 580),
            10,
            170,
            fill=dark,
            width=8
        )

    else:

        draw.arc(
            (380, 480, 520, 550),
            20,
            160,
            fill=dark,
            width=6
        )

    # -----------------------------------------------------
    # CHEEKS
    # -----------------------------------------------------

    cheek_color = (
        random.randint(235, 255),
        random.randint(130, 190),
        random.randint(145, 200)
    )

    draw.ellipse(
        (205, 455, 280, 505),
        fill=cheek_color
    )

    draw.ellipse(
        (620, 455, 695, 505),
        fill=cheek_color
    )

    # -----------------------------------------------------
    # RANDOM MARKINGS
    # -----------------------------------------------------

    if animal in ["Tiger", "Fox", "Cat"]:

        for side in [-1, 1]:

            for _ in range(random.randint(2, 4)):

                y = random.randint(260, 520)

                if side == -1:

                    x = random.randint(180, 270)

                    draw.polygon(
                        [
                            (x, y),
                            (x + 60, y + 10),
                            (x + 10, y + 30)
                        ],
                        fill=dark
                    )

                else:

                    x = random.randint(630, 700)

                    draw.polygon(
                        [
                            (x, y),
                            (x - 60, y + 10),
                            (x - 10, y + 30)
                        ],
                        fill=dark
                    )


# ---------------------------------------------------------
# BODY
# ---------------------------------------------------------

def draw_body(draw, base, light, dark):

    draw.ellipse(
        (260, 620, 640, 850),
        fill=base,
        outline=dark,
        width=5
    )

    draw.ellipse(
        (340, 640, 560, 815),
        fill=light
    )

    # Paws

    draw.ellipse(
        (205, 745, 355, 865),
        fill=base,
        outline=dark,
        width=5
    )

    draw.ellipse(
        (545, 745, 695, 865),
        fill=base,
        outline=dark,
        width=5
    )


# ---------------------------------------------------------
# ACCESSORIES
# ---------------------------------------------------------

def add_accessory(draw, animal):

    choice = random.randint(0, 5)

    if choice == 0:

        # Bow
        cx = WIDTH // 2
        cy = 235

        draw.polygon(
            [
                (cx, cy),
                (cx - 100, cy - 55),
                (cx - 110, cy + 55)
            ],
            fill=(220, 100, 140)
        )

        draw.polygon(
            [
                (cx, cy),
                (cx + 100, cy - 55),
                (cx + 110, cy + 55)
            ],
            fill=(220, 100, 140)
        )

        draw.ellipse(
            (cx - 25, cy - 25, cx + 25, cy + 25),
            fill=(180, 65, 105)
        )

    elif choice == 1:

        # Crown
        draw.polygon(
            [
                (300, 175),
                (340, 100),
                (390, 165),
                (450, 90),
                (500, 165),
                (560, 110),
                (600, 200)
            ],
            fill=(245, 195, 65),
            outline=(150, 110, 30)
        )

    elif choice == 2:

        # Flower
        x = random.choice([220, 680])
        y = random.randint(150, 260)

        draw.ellipse(
            (x - 25, y - 60, x + 25, y),
            fill=(245, 130, 170)
        )

        draw.ellipse(
            (x - 60, y - 25, x, y + 25),
            fill=(245, 130, 170)
        )

        draw.ellipse(
            (x, y - 25, x + 60, y + 25),
            fill=(245, 130, 170)
        )

        draw.ellipse(
            (x - 15, y - 15, x + 15, y + 15),
            fill=(250, 210, 70)
        )


# ---------------------------------------------------------
# MAIN GENERATOR
# ---------------------------------------------------------

def create_animal_image():

    # Create canvas
    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT)
    )

    draw = ImageDraw.Draw(image)

    # Background
    create_background(draw)

    # Animal
    animal = random.choice(
        [
            "Cat",
            "Dog",
            "Fox",
            "Panda",
            "Bunny",
            "Tiger"
        ]
    )

    # Colours
    base, light, dark = rand_color()

    # Face
    draw_face(
        draw,
        animal,
        base,
        light,
        dark
    )

    # Body
    draw_body(
        draw,
        base,
        light,
        dark
    )

    # Accessories
    add_accessory(
        draw,
        animal
    )

    # Slight artistic softness
    image = image.filter(
        ImageFilter.GaussianBlur(
            radius=0.25
        )
    )

    return image, None, animal