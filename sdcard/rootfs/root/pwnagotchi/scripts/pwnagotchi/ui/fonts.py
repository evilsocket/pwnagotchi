from PIL import ImageFont

PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono'

Bold = ImageFont.truetype("%s-Bold.ttf" % PATH, 10)
BoldSmall = ImageFont.truetype("%s-Bold.ttf" % PATH, 9)
Medium = ImageFont.truetype("%s.ttf" % PATH, 10)
Huge = ImageFont.truetype("%s-Bold.ttf" % PATH, 30)
