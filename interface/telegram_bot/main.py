from aiogram.utils import executor
from create_bot import dp
from handlers import admin


async def on_startup(_):
    print('Бот вышел в онлайн')

admin.register_handlers_admin(dp=dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)