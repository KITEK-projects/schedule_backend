from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def action_selection():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Добавить|Обновить", callback_data="add"),
    )
    builder.row(
        types.InlineKeyboardButton(text="Удалить", callback_data="del"),
    )
    return builder