
from aiogram.filters import BaseFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import TelegramObject

from app.tg_bot.states.fsm_state_data import FSMFireAccidentForm


class SFilter_fire_pool(BaseFilter):
    async def __call__(self, obj: TelegramObject, state: FSMContext) -> bool:

        user_state = await state.get_state()

        return user_state in [FSMFireAccidentForm.edit_fire_pool_area_state,
                              FSMFireAccidentForm.edit_fire_pool_distance_state,
                              FSMFireAccidentForm.edit_fire_pool_wind_state]
