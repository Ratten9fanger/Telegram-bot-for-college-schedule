import requests
from bs4 import BeautifulSoup
from aiogram import types, Bot, Dispatcher, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
from datetime import datetime, timedelta
import pytz

def GetScheduleDict(groupId):
    scheduleUrl = f"http://schedule.ckstr.ru/cg/{groupId}.htm"
    res = requests.get(scheduleUrl)
    soup = BeautifulSoup(res.content, 'lxml')
    tbody = soup.find('table', class_='inf')
    rows = tbody.find_all('tr')

    schedule = {
        4: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        5: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        6: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        7: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        8: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        9: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        10: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}}
    }

    cells = {}
    limit = 0

    for j in rows:
        if limit <= 10:
            limit += 1
            cells[limit] = j.find_all('td', class_='ur')

    for i in cells:
        if i not in schedule:
            continue

        isMain = True
        if len(cells[i]) > 1:
            for cell in cells[i]:
                if isMain:
                    if cell.find('a', class_='z1') is not None:
                        schedule[i]['main']['name'] = cell.find('a', class_='z1').text
                    # else:
                    #     schedule[i]['main']['name'] = 'У этой подгруппы нет пары'
                    #     print('no')

                    if cell.find('a', class_='z3') is not None:
                        schedule[i]['main']['prep'] = cell.find('a', class_='z3').text
                    if cell.find('a', class_='z2') is not None:
                        schedule[i]['main']['cab'] = cell.find('a', class_='z2').text
                else:
                    if cell.find('a', class_='z1') is not None:
                        schedule[i]['add']['name'] = cell.find('a', class_='z1').text
                    # else:
                    #     schedule[i]['add']['name'] = 'У этой подгруппы нет пары'
                    #     print('no')

                    if cell.find('a', class_='z3') is not None:
                        schedule[i]['add']['prep'] = cell.find('a', class_='z3').text
                    if cell.find('a', class_='z2') is not None:
                        schedule[i]['add']['cab'] = cell.find('a', class_='z2').text
                isMain = False
        else:
            for cell in cells[i]:
                if cell.find('a', class_='z1') is not None:
                    schedule[i]['main']['name'] = cell.find('a', class_='z1').text
                if cell.find('a', class_='z3') is not None:
                    schedule[i]['main']['prep'] = cell.find('a', class_='z3').text
                if cell.find('a', class_='z2') is not None:
                    schedule[i]['main']['cab'] = cell.find('a', class_='z2').text

    return schedule

def GetScheduleText(schedule_dict):
    output_text = ""
    
    for day, subjects in schedule_dict.items():
        output_text += f"<b>📅 Пара {day - 3}:</b>\n"
        
        for key in ['main', 'add']:
            subject = subjects[key]
            subject_info = []
            
            # Составляем информацию о предмете, пропуская пустые поля
            if subject['name']:
                subject_info.append(f"\n\t\t\t\t\t\t\t\t{subject['name']}")
            if subject['prep']:
                subject_info.append(f"\t\t\t\t\t\t\t\t{subject['prep']}")
            if subject['cab']:
                subject_info.append(f"\t\t\t\t\t\t\t\t{subject['cab']}")
            
            if subject_info:
                output_text += "<b>"
                output_text += "\n".join(subject_info)
                output_text += "</b>\n"
            # else:
            #     output_text += "<b>—</b>\n"
        
        output_text += "\n"  # Добавляем пустую строку между днями
    
    return output_text.strip()

url = ''
user_id = ''
user_data = {}
schedule_time = """
I пара:
  08:30 - 09:10
  09:15 - 10:00
II пара:
  10:10 - 10:50
  10:55 - 11:40
  Обеденный перерыв 30 мин.
III пара:
  12:10 - 12:50
  12:55 - 13:40
IV пара:
  13:50 - 14:30
  14:35 - 15:20
V пара:
  15:30 - 16:50
VI пара:
  17:00 - 18:20

Среда
08:30 - 08:50 - Классный час
І пара:
  09:00 - 09:40
  09:45 - 10:30
II пара:
  10:40 - 11:20
  11:25 - 12:10
  Обеденный перерыв 20 мин.
III пара:
  12:30 - 13:10
  13:15 - 14:00
IV пара:
  14:10 - 14:50
  14:55 - 15:40
V пара:
  15:50 - 17:10
VI пара:
  17:20 - 18:40
"""

bot = Bot('token')
dp = Dispatcher(bot)

# Создаем клавиатуру
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Текущая ссылка"))
keyboard.add(KeyboardButton("Получить текущее расписание форсированно"))
keyboard.add(KeyboardButton("Расписание звонков"))

@dp.message_handler(commands='start')
async def start(message: types.Message):
    # user_id = message.from_user.id
    # user_data[user_id] = {'url': ''}  # Инициализация данных пользователя
    await message.answer(
        "Привет! Я - Бот расписания СКСиПТ\nЯ отправляю нужное вам расписание в 17:30 каждый день\nНо для начала, введите ссылку НЕДЕЛЬНОГО расписания вашей группы\nОна будет в будущем использоваться для взятия расписания и отправки вам, без передачи ссылки расписание приходить не БУДЕТ.\nУчтите, что ссылки меняются каждый семестр!\nПример: http://schedule.ckstr.ru/cg142.htm\n\n<pre>Бот может не отправить расписание, это значит что ссылка сбросилась. Каждый месяц бот нуждается в продлении хостинга</pre>",
        reply_markup=keyboard, parse_mode='html'
    )

@dp.message_handler(lambda message: message.text.startswith('http://schedule.ckstr.ru/cg/'))
async def capture_url(message: types.Message):
    user_id = message.from_user.id
    group_id = message.text[21:]
    group_id = message.text[:4]
    if user_id not in user_data:
        user_data[user_id] = group_id
    await message.reply("Ссылка сохранена! Теперь я буду отправлять вам расписание в 17:30 по будням и по ВС\nЕсли захотите поменять ее, то просто отправьте в чат новую и я автоматически сменю целевую ссылку", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text.startswith('http://46.191.196.21/cg/'))
async def capture_url(message: types.Message):
    user_id = message.from_user.id
    group_id = message.text[21:]
    group_id = message.text[:4]
    if user_id not in user_data:
        user_data[user_id] = group_id
    await message.reply("Ссылка сохранена! Теперь я буду отправлять вам расписание в 17:30 по будням и по ВС\nЕсли захотите поменять ее, то просто отправьте в чат новую и я автоматически сменю целевую ссылку", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Текущая ссылка")
async def show_current_url(message: types.Message):
    user_id = message.from_user.id 
    await message.answer("Обрабатываю запрос... Подождите")
    await asyncio.sleep(3)
    if user_id in user_data and user_data[user_id]:
        await message.answer(f"Текущая ссылка: http://schedule.ckstr.ru/cg/{user_data[user_id]}.htm")
    else:
        await message.answer("Ссылка не установлена!")

@dp.message_handler(lambda message: message.text == "Расписание звонков")
async def show_current_url(message: types.Message):
    await message.answer("Обрабатываю запрос... Подождите")
    await asyncio.sleep(2)  # Задержка 5 секунд
    await message.answer(text=schedule_time)

@dp.message_handler(lambda message: message.text == "Получить текущее расписание форсированно")
async def force_get_schedule(message: types.Message):
    user_id = message.from_user.id
    await message.answer("Обрабатываю запрос... Подождите")
    await asyncio.sleep(3)
    if user_id in user_data and user_data[user_id]:
        temp = GetScheduleDict(user_data[user_id])
        res = GetScheduleText(temp)
        await message.answer(text=res, parse_mode='html')
    else:
        await message.answer("Ссылка не установлена!")

async def on_startup(dp):
    asyncio.create_task(send_message_at_time())

async def send_message_at_time():
    ekaterinburg_tz = pytz.timezone('Asia/Yekaterinburg')

    while True:
        now = datetime.now(ekaterinburg_tz)
        target_time = now.replace(hour=17, minute=30, second=0, microsecond=0)
        
        if now > target_time:
            target_time += timedelta(days=1)
        
        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)
        
        if target_time.weekday() < 6:  # 0-4 — понедельник-пятница
            for user_id, data in user_data.items():
                if data['url']:  # Проверяем, есть ли ссылка у пользователя
                    temp = GetScheduleDict(data)
                    res = GetScheduleText(temp)
                    await bot.send_message(user_id, text=res, parse_mode='html', reply_markup=keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
