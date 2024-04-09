import os

from reportlab.lib import colors

DIR = os.path.dirname(__file__)

MM = 72 / 25.4
INCH = 72
PIXEL = 1

IN_PX = 72
IN_MM = 25.4
PX_IN = 1 / 72
PX_MM = 1 / 72 * 25.4
MM_IN = 1 / 25.4
MM_PX = 1 / 25.4 * 72

STYLES = {
    'text_color': colors.black,
    'text_transparency': None,
    'text_height': 4,
    'font_name': 'WenQuanYiMicroHeiRegular',
    'text_character_space': None,
    'text_word_space': 0,
    'text_direction': None,
    'draw_line': True,
    'line_width': 0.1,
    'line_color': colors.black,
    'line_transparency': None,
    'draw_fill': False,
    'fill_color': colors.black,
    'fill_transparency': None,
    'grid_width': 30,
    'grid_height': 30,
}

DOCUMENT_CONFIGS = {
    'title': 'PDF Document Title',
    'author': 'He Bill',
    'subject': 'PDF Document',
    'keywords': '',
    'encrypted': False,
    'encrypt_user_password': None,
    'encrypt_owner_password': None,
}

PAGE_CONFIGS = {
    'width': 210,
    'height': 297,
    'margin_top': 10,
    'margin_right': 15,
    'margin_bottom': 5,
    'margin_left': 15,
}
