from aiogram import Router
from aiogram.types import Message, ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F

from app.get_schedule.parser.db import *
from app.get_schedule.parser.parser import html_parse

router = Router()


class AdminComands(StatesGroup):
    add_admin_id = State()
    delete_admin_id = State()


@router.message(F.content_type == ContentType.DOCUMENT)
async def cmd_start(message: Message):
    user_id = message.from_user.id
    target_user_id = select_admin()

    if user_id in target_user_id:
        await message.answer("⏳ Ой-ой-ой! Я уже начинаю! Сейчас всё обработаю, просто подожди! Это будет так круто~! 🌟")
        document = message.document
        file_id = document.file_id

        file_info = await message.bot.get_file(file_id)

        destination_file = './schedule.html'
        await message.bot.download_file(file_info.file_path, destination_file)
        
        answer = insert_data(html_parse(destination_file))
        await message.answer(answer)

    else:
        await message.reply("🚫 Ой-ой! Это не для тебя! Но я рядом, и мы что-нибудь придумаем, обещаю! 🌟")


@router.message(StateFilter(None), Command('add_admin'))
async def add_admin_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    target_user_id = select_admin()

    if user_id in target_user_id:
        await message.answer("🆔 Так, введи айди, и мы сделаем магию! Новенький добавлен в мгновение ока! 💥")
        await state.set_state(AdminComands.add_admin_id)
    else:
        await message.reply("🚫 Ой-ой! Это не для тебя! Но я рядом, и мы что-нибудь придумаем, обещаю! 🌟")
        

@router.message(StateFilter(None), Command('del_admin'))
async def add_admin_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    target_user_id = select_admin()

    if user_id in target_user_id:
        await message.answer("❌ Ах! Ты правда хочешь удалить кого-то? Ну ладно... Введи айди, и я всё сделаю... 😢")
        await state.set_state(AdminComands.delete_admin_id)
    else:
        await message.reply("🚫 Ой-ой! Это не для тебя! Но я рядом, и мы что-нибудь придумаем, обещаю! 🌟")
        
        
@router.message(StateFilter(None), Command('all_admin'))
async def all_admin_command(message: Message):
    user_id = message.from_user.id
    target_user_id = select_admin()

    if user_id in target_user_id:
        await message.answer(f"📋 Тадам! Вот список всех айди! Мы всё сделаем вместе, это будет мега круто! 💖\n{"\n".join([str(i) for i in target_user_id])}")
    else:
        await message.reply("🚫 Ой-ой! Это не для тебя! Но я рядом, и мы что-нибудь придумаем, обещаю! 🌟")

        
@router.message(AdminComands.add_admin_id)
async def add_admin(message: Message, state: FSMContext):
    try:
        insert_admin(int(message.text))
        await message.answer("🆔 Ура! У нас новый член команды)")
        await state.set_state(None)
    except:
        await message.reply("⚠️ Ааа! Это не то, что я хотела! Ладно, попробуем ещё раз и обязательно получится! 🔥")
        

@router.message(AdminComands.delete_admin_id)
async def add_admin(message: Message, state: FSMContext):
    try:
        delete_admin(int(message.text))
        await message.answer("🆔 Ура! Кажется нас стало на одного человека меньше.")
        await state.set_state(None)
    except:
        await message.reply("⚠️ Ааа! Это не то, что я хотела! Ладно, попробуем ещё раз и обязательно получится! 🔥")
        

        
    
