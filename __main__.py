import asyncio
import logging

from app.tg_bot import main

# Конфигурируем логирование
logging.basicConfig(
    # filename='log_file.txt',
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s: '
    '[%(lineno)d] - [%(name)s] - %(message)s'
)

asyncio.run(main())
