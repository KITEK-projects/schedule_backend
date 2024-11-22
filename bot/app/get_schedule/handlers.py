from aiogram import Router
from aiogram.types import Message, ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F

router = Router()


class AdminComands(StatesGroup):
    add_admin_id = State()
    delete_admin_id = State()


@router.message(F.content_type == ContentType.DOCUMENT)
async def cmd_start(message: Message):

    await message.answer("Отправляю расписание")
    document = message.document
    file_id = document.file_id

    file_info = await message.bot.get_file(file_id)

    destination_file = './schedule.html'
    await message.bot.download_file(file_info.file_path, destination_file)
    
    with open(destination_file, encoding='windows-1251') as file:
        src = file.read()
    
    answer = src[:500]
    await message.answer(answer)



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
        

        
    
