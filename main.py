from ApiAdmin import httpx_api
from ApiAdmin import aiohtttp_api
from html2image import Html2Image
import config
import asyncio


USERNAME = config.USERNAME
PASSWORD = config.PASSWORD
SCHOOL_ID = config.SCHOOL_ID


async def save_to_img(html_page, css_file, type: str):
    if type == "marks":
        resize_params = (1100, 480)
        name = 'Marks.jpeg'
    if type == "totals":
        resize_params = (800, 3200)
        name = 'Totals.jpeg'
    hti = Html2Image(custom_flags=['--no-sandbox'])
    hti.screenshot(html_str=html_page, css_str=css_file, save_as=name, size=resize_params)


async def main_httpx():
    session = httpx_api.API("https://region.zabedu.ru")
    await session.login(username=USERNAME, password=PASSWORD, school_id=SCHOOL_ID)

    html_page, css_file = await session.get_report_teacher_average_mark()
    await save_to_img(html_page=html_page, css_file=css_file, type="marks")

    html_page, css_file = await session.get_report_class_subject_totals()
    await save_to_img(html_page=html_page, css_file=css_file, type="totals")

async def main_aiohttp():
    session = aiohtttp_api.API("https://region.zabedu.ru")
    await session.login(username=USERNAME, password=PASSWORD, school_id=SCHOOL_ID)

    html_page, css_file = await session.get_report_teacher_average_mark()
    await save_to_img(html_page=html_page, css_file=css_file, type="marks")

    html_page, css_file = await session.get_report_class_subject_totals()
    await save_to_img(html_page=html_page, css_file=css_file, type="totals")

    await session.logout()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    #asyncio.run(main_httpx())
    asyncio.run(main_aiohttp())