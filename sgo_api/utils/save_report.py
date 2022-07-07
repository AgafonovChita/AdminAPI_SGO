from html2image import Html2Image
from typing import Tuple


async def save_report_to_img(html_page: str, css_file: str, name_img: str, size_img: Tuple):
    hti = Html2Image(custom_flags=['--no-sandbox'])
    hti.screenshot(html_str=html_page, css_str=css_file, save_as=name_img, size=size_img)
