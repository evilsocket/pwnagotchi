from PIL import ImageFont

# should not be changed
FONT_NAME = 'DejaVuSansMono'

# can be changed
STATUS_FONT_NAME = None
SIZE_OFFSET = 0

Bold = None
BoldSmall = None
BoldBig = None
Medium = None
Small = None
Huge = None


def init(config):
    global STATUS_FONT_NAME, SIZE_OFFSET
    STATUS_FONT_NAME = config['ui']['font']['name']
    SIZE_OFFSET = config['ui']['font']['size_offset']
    setup(10, 8, 10, 25, 25, 9)


def status_font(old_font):
    global STATUS_FONT_NAME, SIZE_OFFSET
    return ImageFont.truetype(STATUS_FONT_NAME, size=old_font.size + SIZE_OFFSET)


def setup(bold, bold_small, medium, huge, bold_big, small):
    global Bold, BoldSmall, Medium, Huge, BoldBig, Small, FONT_NAME

    Small = ImageFont.truetype(FONT_NAME, small)
    Medium = ImageFont.truetype(FONT_NAME, medium)
    BoldSmall = ImageFont.truetype("%s-Bold" % FONT_NAME, bold_small)
    Bold = ImageFont.truetype("%s-Bold" % FONT_NAME, bold)
    BoldBig = ImageFont.truetype("%s-Bold" % FONT_NAME, bold_big)
    Huge = ImageFont.truetype("%s-Bold" % FONT_NAME, huge)
