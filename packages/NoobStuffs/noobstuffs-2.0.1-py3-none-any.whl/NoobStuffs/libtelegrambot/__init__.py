import asyncio
from typing import BinaryIO

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder


class TelegramLogBot:
    def __init__(self, token: str, chat_id: int, parse_mode: ParseMode):
        self.__app = ApplicationBuilder().token(token).build()
        self.__chat_id = chat_id
        self.__parse_mode = parse_mode
        self.__buttons = []
        self.__button_index = -1

    def build_button(self, text: str, link: str, newline: bool = False):
        print(self.__button_index)
        print(self.__buttons)
        button = InlineKeyboardButton(text=text, url=link)
        if newline or len(self.__buttons) == 0:
            self.__button_index += 1
            self.__buttons.append([button])
        else:
            self.__buttons[self.__button_index].append(button)

    def reset_buttons(self):
        self.__button_index = -1
        self.__buttons.clear()

    def log_msg(self, message: str, use_buttons: bool = False):
        loop = asyncio.get_event_loop()
        reply_markup = InlineKeyboardMarkup(self.__buttons) if use_buttons else None
        loop.run_until_complete(
            self.__app.bot.send_message(
                text=message,
                chat_id=self.__chat_id,
                reply_markup=reply_markup,
                parse_mode=self.__parse_mode,
            ),
        )

    def log_img(self, image: BinaryIO, caption: str, use_buttons: bool = False):
        loop = asyncio.get_event_loop()
        reply_markup = InlineKeyboardMarkup(self.__buttons) if use_buttons else None
        loop.run_until_complete(
            self.__app.bot.send_photo(
                photo=image,
                chat_id=self.__chat_id,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=self.__parse_mode,
            ),
        )
