from PIL import ImageFont

FONT_NAME = None
Bold = None
BoldSmall = None
BoldBig = None
Medium = None
Small = None
Huge = None


def init(config):
    global FONT_NAME
    FONT_NAME = config['ui']['font']
    setup(10, 8, 10, 25, 25, 9)


def setup(bold, bold_small, medium, huge, bold_big, small):
    global Bold, BoldSmall, Medium, Huge, BoldBig, Small, FONT_NAME

    Small = ImageFont.truetype("%s.ttf" % FONT_NAME, small)
    Medium = ImageFont.truetype("%s.ttf" % FONT_NAME, medium)

    try:
        BoldSmall = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME, bold_small)
        Bold = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME, bold)
        BoldBig = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME, bold_big)
        Huge = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME, huge)
    except OSError:
        BoldSmall = ImageFont.truetype("%s.ttf" % FONT_NAME, bold_small)
        Bold = ImageFont.truetype("%s.ttf" % FONT_NAME, bold)
        BoldBig = ImageFont.truetype("%s.ttf" % FONT_NAME, bold_big)
        Huge = ImageFont.truetype("%s.ttf" % FONT_NAME, huge)

