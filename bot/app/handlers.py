import json
from aiogram import Router
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F

import aiohttp
import requests

from .parser import html_parse 
from .keyboards import action_selection

router = Router()


class fsm(StatesGroup):
    add_schedule = State()
    del_schedule = State()


@router.message(StateFilter(None), Command('adds'))
async def admin_command(message: Message):
    await message.answer("Выберите действие:", reply_markup=action_selection().as_markup())


@router.callback_query(StateFilter(None), F.data == "add")
async def add_schedule(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer("Можете загрузить файл для добаления/обновления")
    await state.set_state(fsm.add_schedule)

@router.callback_query(StateFilter(None), F.data == "del")
async def del_schedule(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer("Можете загрузить файл для удаления")
    await state.set_state(fsm.del_schedule)



@router.message(F.content_type == ContentType.DOCUMENT, StateFilter(fsm.add_schedule, fsm.del_schedule))
async def add_schedule_file(message: Message, state: FSMContext):
    await message.answer("Обработка запроса...")
    
    document = message.document
    file_id = document.file_id

    # Получаем информацию о файле
    file_info = await message.bot.get_file(file_id)

    destination_file = './schedule.html'
    
    # Скачиваем файл
    await message.bot.download_file(file_info.file_path, destination_file)

    # Чтение содержимого файла с кодировкой windows-1251
    with open(destination_file, encoding='windows-1251') as file:
        src = file.read()

    try:    
        current_state = await state.get_state()

        async with aiohttp.ClientSession() as session:
            payload = html_parse(src)
            if current_state == fsm.add_schedule.state:
                async with session.put("http://localhost:8000/v1/edit/", json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.json()
                    if response.status == 200:
                        await message.answer("Расписание добавлено успешно")
                    else: 
                        await message.answer(f"[ Ошибка ]{response}\n\n {response.content}")
            else:
                async with session.delete("http://localhost:8000/v1/edit/", json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.json()
                    if response.status == 200:
                        await message.answer("Расписание удалено успешно")
                    else: 
                        await message.answer(f"[ Ошибка ]{response}, {response.content}")

    except Exception as e:
        if "Cannot connect to host" in str(e):
            await message.answer("[ Ошибка ] Не возможно подключится к серверу")
        else:
            await message.answer(f"[ERROR] {e}")
    finally:
        await state.set_state(None)