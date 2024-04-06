import os.path
from io import BytesIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def get_display_width(text: str, font, height, char_space=0, word_space=0):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', font + '.ttf')
    pdfmetrics.registerFont(TTFont(font, file))
    pdf.setFont(font, height)
    w = pdf.stringWidth(text, font, height)
    if word_space > 0:
        w += text.count(' ') * word_space
    if char_space > 0:
        w += len(text) * char_space
    return w
