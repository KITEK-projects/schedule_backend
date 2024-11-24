import json
from aiogram import Router
from aiogram.types import Message, ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F

import aiohttp
import requests

router = Router()


class AdminComands(StatesGroup):
    add_admin_id = State()
    delete_admin_id = State()


@router.message(F.content_type == ContentType.DOCUMENT)
async def cmd_start(message: Message):
    await message.answer("Отправляю расписание")

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

    # Отправка DELETE-запроса с содержимым файла как строки
    # Отправка DELETE-запроса с данными как строки JSON
    async with aiohttp.ClientSession() as session:
        # Отправляем данные как JSON
        payload = {"data": src}  # Передаем как строку
        headers = {'Content-Type': 'application/json'}  # Указываем правильный тип контента
        async with session.delete("http://localhost:8000/v1/edit/", json=payload, headers=headers) as response:
            result = await response.json()
            await message.answer(f"Ответ от сервера: {response.status}, {result}")



@router.message(StateFilter(None), Command('add_admin'))
async def add_admin_command(message: Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer("🆔 Так, введи айди, и мы сделаем магию! Новенький добавлен в мгновение ока! 💥")
    await state.set_state(AdminComands.add_admin_id)
        

@router.message(StateFilter(None), Command('del_admin'))
async def add_admin_command(message: Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer("❌ Ах! Ты правда хочешь удалить кого-то? Ну ладно... Введи айди, и я всё сделаю... 😢")
    await state.set_state(AdminComands.delete_admin_id)
        
        
@router.message(StateFilter(None), Command('all_admin'))
async def all_admin_command(message: Message):
    user_id = message.from_user.id

    await message.answer(f"📋 Тадам! Вот список всех айди! Мы всё сделаем вместе, это будет мега круто!")


        
@router.message(AdminComands.add_admin_id)
async def add_admin(message: Message, state: FSMContext):
    try:
        await message.answer("🆔 Ура! У нас новый член команды)")
        await state.set_state(None)
    except:
        await message.reply("⚠️ Ааа! Это не то, что я хотела! Ладно, попробуем ещё раз и обязательно получится! 🔥")
        

@router.message(AdminComands.delete_admin_id)
async def add_admin(message: Message, state: FSMContext):
    try:
        await message.answer("🆔 Ура! Кажется нас стало на одного человека меньше.")
        await state.set_state(None)
    except:
        await message.reply("⚠️ Ааа! Это не то, что я хотела! Ладно, попробуем ещё раз и обязательно получится! 🔥")
        

        
    
