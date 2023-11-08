import logging
import json

logger = logging.getLogger(__name__)


def quantity_keys_get():
    """_summary_

    Returns:
        _type_: _description_
    """
    with open(file='app/infrastructure/substance_data/combustible_gas.json', mode='r', encoding='utf-8') as file_r_gas:
        db_gas = json.load(file_r_gas)
    with open(file='app/infrastructure/substance_data/combustible_liquid.json', mode='r', encoding='utf-8') as file_r_liquid:
        db_liquid = json.load(file_r_liquid)
    with open(file='app/infrastructure/substance_data/combustible_dust.json', mode='r', encoding='utf-8') as file_r_dust:
        db_dust = json.load(file_r_dust)

    list_sub = list(db_gas.keys())+list(db_liquid.keys())+list(db_dust.keys())
    quantity_keys = len(list_sub)
    return quantity_keys
