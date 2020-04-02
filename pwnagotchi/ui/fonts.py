from PIL import ImageFont

FONT_NAME = None
FONT_NAME_FACES = 'DejaVuSansMono'

SIZE_OFFSET = 0
Bold = None
BoldSmall = None
BoldBig = None
Medium = None
Small = None
Huge = None
FaceHuge = None
FaceBold = None


def init(config):
    global FONT_NAME, SIZE_OFFSET
    FONT_NAME = config['ui']['font']['name']
    SIZE_OFFSET = config['ui']['font']['size_offset']
    setup(10, 8, 10, 25, 25, 9)


def setup(bold, bold_small, medium, huge, bold_big, small):
    global Bold, BoldSmall, Medium, Huge, BoldBig, Small, FaceHuge, FaceBold,
           FONT_NAME, SIZE_OFFSET

    Small = ImageFont.truetype("%s.ttf" % FONT_NAME, small + SIZE_OFFSET)
    Medium = ImageFont.truetype("%s.ttf" % FONT_NAME, medium, + SIZE_OFFSET)
    FaceHuge = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME_FACES, huge)
    FaceBold = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME_FACES, bold)

    try:
        BoldSmall = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME, bold_small + SIZE_OFFSET)
        Bold = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME, bold + SIZE_OFFSET)
        BoldBig = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME, bold_big + SIZE_OFFSET)
        Huge = ImageFont.truetype("%s-Bold.ttf" % FONT_NAME, huge + SIZE_OFFSET)
    except OSError:
        BoldSmall = ImageFont.truetype("%s.ttf" % FONT_NAME, bold_small + SIZE_OFFSET)
        Bold = ImageFont.truetype("%s.ttf" % FONT_NAME, bold + SIZE_OFFSET)
        BoldBig = ImageFont.truetype("%s.ttf" % FONT_NAME, bold_big + SIZE_OFFSET)
        Huge = ImageFont.truetype("%s.ttf" % FONT_NAME, huge + SIZE_OFFSET)

