from PIL import Image, ImageDraw
import random, base64
from io import BytesIO


def random_color():
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )


def captcha_base64():
    chars = 'ABDEFGHLMNQRTabdefghimnrt12345678'
    code = ''
    for i in range(4):
        code += random.choice(chars)
    f = BytesIO()
    img = Image.new(mode='RGB', size=(120, 40), color=random_color())
    draw = ImageDraw.Draw(img)
    for i in range(random.randint(100, 200)):
        draw.point((random.randint(0, 120), random.randint(0, 40)), fill=random_color())
    char_width = 10
    x = 2
    for char in code:
        draw.text((x, 2), char, font=None, fill=random_color(),font_size=26)
        x += char_width + random.randint(10, 25)
    img.save(f, 'png')
    base64_str = base64.b64encode(f.getvalue()).decode()
    return code, base64_str

