from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from .. import keyboards
from interface.telegram_bot.create_bot import bot
from menu_maker.menu_compilation import main as get_menu
# from keyboards import kb_client, kb_yn, answers_keyboards

# class FSMLoadInfo(StatesGroup):
#     states = {i: State() for i in states}
#     for i in states:
#         locals()[i] = states[i]


async def echo_send(message: types.Message):
    await message.answer(message.text)


# # Генератор хэндлеров по структуре из базы данных
# def points_handlers(q):
#     async def _(message: types.Message, state=FSMContext):
#         async with state.proxy() as data:
#             data[_] = message.text
#         await FSMLoadInfo.states[q].set()
#         await message.answer(db.get_messages(q + 1))
#     return _

def format_message(week_menu: list[dict]) -> str:
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    string_menu = ''
    for day, menu in zip(days, week_menu):
        string_menu += f'{day}\n'
        for eating in menu:
            string_menu += f'{eating}: {menu[eating].dish_name}\n{menu[eating].href}\n\n'
    return string_menu



async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет! Я могу помочь составить меню на неделю.\n'
                                                 'для начала нажми на "start"')
    await message.delete()
    menu = get_menu()
    message_menu = format_message(menu)
    await message.answer(message_menu)


# Список хэндлеров для пунктов меню
# points_list = {point_number: points_handlers(point_number) for point_number in states}


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    # for q in states.items():
    #     dp.register_message_handler(points_list[q[0]], state=FSMLoadInfo.states[q[0] - 1])
    dp.register_message_handler(echo_send)
