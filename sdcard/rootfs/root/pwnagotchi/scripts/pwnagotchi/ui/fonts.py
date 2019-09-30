from PIL import ImageFont

PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono'

Bold = ImageFont.truetype("%s-Bold.ttf" % PATH, 10)
BoldSmall = ImageFont.truetype("%s-Bold.ttf" % PATH, 8)
Medium = ImageFont.truetype("%s.ttf" % PATH, 10)
Huge = ImageFont.truetype("%s-Bold.ttf" % PATH, 25)


def setup(bold, bold_small, medium, huge):
    global PATH, Bold, BoldSmall, Medium, Huge
    Bold = ImageFont.truetype("%s-Bold.ttf" % PATH, bold)
    BoldSmall = ImageFont.truetype("%s-Bold.ttf" % PATH, bold_small)
    Medium = ImageFont.truetype("%s.ttf" % PATH, medium)
    Huge = ImageFont.truetype("%s-Bold.ttf" % PATH, huge)
