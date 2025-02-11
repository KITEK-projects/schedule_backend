from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def action_selection():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="➕ Добавить(обновить)", callback_data="add"),
    )
    builder.row(
        types.InlineKeyboardButton(text="🗑 Удалить", callback_data="del"),
    )
    builder.row(
        types.InlineKeyboardButton(text="✖️ Отмена", callback_data="cancel"),
    )
    return builder

def start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(.0.0.1:8000/
Quit the server with CONTROL-C.

            text="Открыть расписание", 
            web_app=types.WebAppInfo(url="https://schedule.omsktec-playgrounds.ru/")
        ),
    )
    return builder

def cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Отмена", callback_data="cancel"),
    )
    return builder