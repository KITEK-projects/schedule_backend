import os
from aiogram import Router
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F

import aiohttp


from .parser import html_parse 
from .keyboards import action_selection, start_keyboard, cancel_keyboard

router = Router()

API = "http://schedule-api:8000/v1/"

document = None
file_id = ""

class fsm(StatesGroup):
    add_schedule = State()
    del_schedule = State()


async def check_admin(user_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API}users/{user_id}/", headers={
            'X-Internal-Token': os.getenv('INTERNAL_API_TOKEN')
            }) as response:
            return response.status == 200

async def check_super_admin(user_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API}users/{user_id}/", headers={
            'X-Internal-Token': os.getenv('INTERNAL_API_TOKEN')
            }) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('is_super_admin', False)
            return False


@router.message(F.content_type == ContentType.DOCUMENT)
async def add_schedule_file(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав администратора")
        return
    
    global document, file_id
    
    document = message.document
    file_id = document.file_id

    await message.answer("Выберите действие:", reply_markup=action_selection().as_markup())

@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer("Отправка отменена")

@router.callback_query(F.data.in_(["del", "add"]))
async def edit_schedule(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Обработка...")
    # Получаем информацию о файле
    file_info = await callback.message.bot.get_file(file_id)

    destination_file = './schedule.html'
    
    # Скачиваем файл
    await callback.message.bot.download_file(file_info.file_path, destination_file)

    # Чтение содержимого файла с кодировкой windows-1251
    with open(destination_file, encoding='windows-1251') as file:
        src = file.read()

    try:    
        current_state = callback.data
        print(current_state)
        user_id = callback.from_user.id
        user_name = callback.from_user.full_name

        async with aiohttp.ClientSession() as session:
            # Получаем список всех суперадминов
            async with session.get(API + "users/", headers={
                'Content-Type': 'application/json',
                'X-Internal-Token': os.getenv('INTERNAL_API_TOKEN'),
            }) as response:
                if response.status == 200:
                    admins = await response.json()
                    super_admins = [admin['user_id'] for admin in admins if admin.get('is_super_admin')]

            payload = html_parse(src)
            action_type = "добавлено" if current_state == "add" else "удалено"
            
            # Основной запрос на изменение расписания
            if current_state == "add":
                endpoint = "edit/"
                method = session.put
            else:
                endpoint = "edit/"
                method = session.delete

            async with method(API + endpoint, json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Internal-Token': os.getenv('INTERNAL_API_TOKEN'),
                }
            ) as response:
                if response.status == 200:
                    await callback.message.answer(f"Расписание {action_type} успешно")
                    
                    # Отправляем уведомление всем суперадминам, кроме инициатора
                    notification_text = f"Пользователь {user_name} (ID: {user_id}) {action_type} расписание"
                    for admin_id in super_admins:
                        if str(admin_id) != str(user_id):  # Не отправляем уведомление самому себе
                            try:
                                await callback.message.bot.send_message(admin_id, notification_text)
                                # Отправляем файл администратору
                                await callback.message.bot.send_document(
                                    admin_id, 
                                    document=file_id
                                )
                            except Exception as e:
                                print(f"Ошибка отправки уведомления админу {admin_id}: {e}")
                else: 
                    error_text = await response.text()
                    await callback.message.answer(f"[ Ошибка ] {response.status}\n\nТекст ошибки: {error_text}")

    except Exception as e:
        if "Cannot connect to host" in str(e):
            await callback.message.answer("[ Ошибка ] Не возможно подключится к серверу")
        else:
            await callback.message.answer(f"[ERROR] {e}")  

@router.message(Command('start'))
async def start_command(message: Message):
    await message.answer(
        "Добро пожаловать! Здесь вы можете просмотреть расписание.",
        reply_markup=start_keyboard().as_markup()
    )

@router.message(Command('help'))
async def help_command(message: Message):
    user_id = message.from_user.id
    
    # Проверяем является ли пользователь супер-админом
    is_super_admin = await check_super_admin(user_id)
    # Проверяем является ли пользователь обычным админом
    is_admin = await check_admin(user_id)
    
    if is_super_admin:
        help_text = (
            "🌟 Команды супер-администратора:\n"
            "Чтобы добавить расписание пришлите файл\n"
            "/adda - Добавить администратора\n"
            "/dela - Удалить администра��ора\n"
            "/lsta - Список администраторов"
        )
    elif is_admin:
        help_text = (
            "👨‍💼 Команды администратора:\n"
            "Чтобы добавить расписание пришлите файл"
        )
    else:
        help_text = "👋 Добро пожаловать! Здесь вы можете просмотреть расписание."
    
    await message.answer(help_text, reply_markup=start_keyboard().as_markup())

@router.message(Command('adda'))
async def add_admin(message: Message):
    if not await check_super_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав администратора")
        return
        
    try:
        # Получаем аргументы команды
        args = message.text.split()
        if len(args) < 3:
            await message.answer("Использование: /adda <user_id> <name> <is_super>")
            return
            
        target_user_id = int(args[1])
        name = args[2]
        is_super = True if args[3] == "1" else False

        async with aiohttp.ClientSession() as session:
            async with session.post(API + "users/", 
                json={"user_id": target_user_id, "is_admin": True, 'name': name, 'is_super_admin': is_super},
                headers={
                        'Content-Type': 'application/json',
                        'X-Internal-Token': os.getenv('INTERNAL_API_TOKEN'),
                        }
            ) as response:
                if response.status == 201:
                    await message.answer(f"Администратор (ID: {target_user_id}) успешно добавлен")
                else:
                    error_text = await response.text()
                    await message.answer(f"[ Ошибка ] {response.status}\n\nТекст ошибки: {error_text}")
    except ValueError:
        await message.answer("ID пользователя должен быть числом")
    except Exception as e:
        await message.answer(f"[ERROR] {e}")

@router.message(Command('dela'))
async def delete_admin(message: Message):
    if not await check_super_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав администратора")
        return
        
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.answer("Использование: /dela <user_id>")
            return
            
        target_user_id = int(args[1])
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(API + f"users/{target_user_id}/", 
                headers={
                        'Content-Type': 'application/json',
                        'X-Internal-Token': os.getenv('INTERNAL_API_TOKEN'),
                        }
            ) as response:
                if response.status == 204:
                    await message.answer(f"Администратор (ID: {target_user_id}) успешно удален")
                else:
                    error_text = await response.text()
                    await message.answer(f"[ Ошибка ] {response.status}\n\nТекст ошибки: {error_text}")
    except ValueError:
        await message.answer("ID пользователя должен быть числом")
    except Exception as e:
        await message.answer(f"[ERROR] {e}")

@router.message(Command('lsta'))
async def list_admins(message: Message):
    if not await check_super_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав администратора")
        return
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API + "users/", headers={
                        'Content-Type': 'application/json',
                        'X-Internal-Token': os.getenv('INTERNAL_API_TOKEN'),
                        }
            ) as response:
                if response.status == 200:
                    admins = await response.json()
                    if not admins:
                        await message.answer("Список администраторов пуст")
                        return
                        
                    admin_list = "Список администраторов:\n"
                    for admin in admins:
                        admin_info = f"• <code>{admin.get('user_id', 'Н/Д')}</code>"
                        if 'name' in admin:
                            admin_info += f" - {admin['name']}"
                        if 'is_super_admin' in admin:
                            role = "Супер админ" if admin['is_super_admin'] else "Админ"
                            admin_info += f" ({role})"
                        admin_list += admin_info + "\n"
                    await message.answer(admin_list, parse_mode="HTML")
                else:
                    error_text = await response.text()
                    await message.answer(f"[ Ошибка ] {response.status}\n\nТекст ошибки: {error_text}")
    except Exception as e:
        await message.answer(f"[ERROR] {e}")

