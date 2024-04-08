import json
from typing import Dict, NewType, Union

from .Utils import Utils

A, B, C, D = Dict[str, str], Dict[str, int], Dict[str, bool], Dict[str, float]; E = Dict[str, Union[A, B, C, D]]; DICT = NewType('DICT', Dict[str, Union[A, B, C, D, E]])

def getConfig() -> DICT:
    try:
        return json.load(open('Config.json'))
    except json.JSONDecodeError as e:
        print('Failed to load Config.json, error in line : {} column : {}'.format(str(e).split(' ')[3], str(e).split(' ')[5]))
    except FileNotFoundError as e:
        print(str(e)); exit()

config = getConfig()

def ParseCoins(coinsStr: str):
    if coinsStr == Utils.Coins.ada.name: return Utils.Coins.ada
    elif coinsStr == Utils.Coins.bch.name: return Utils.Coins.bch
    elif coinsStr == Utils.Coins.bnb.name: return Utils.Coins.bnb
    elif coinsStr == Utils.Coins.btc.name: return Utils.Coins.btc
    elif coinsStr == Utils.Coins.doge.name: return Utils.Coins.doge
    elif coinsStr == Utils.Coins.dot.name: return Utils.Coins.dot
    elif coinsStr == Utils.Coins.etc.name: return Utils.Coins.etc
    elif coinsStr == Utils.Coins.eth.name: return Utils.Coins.eth
    elif coinsStr == Utils.Coins.ltc.name: return Utils.Coins.ltc
    elif coinsStr == Utils.Coins.shib.name: return Utils.Coins.shib
    elif coinsStr == Utils.Coins.sushi.name: return Utils.Coins.sushi
    elif coinsStr == Utils.Coins.trx.name: return Utils.Coins.trx
    elif coinsStr == Utils.Coins.uni.name: return Utils.Coins.uni
    elif coinsStr == Utils.Coins.usdt.name: return Utils.Coins.usdt
    elif coinsStr == Utils.Coins.xlm.name: return Utils.Coins.xlm
    elif coinsStr == Utils.Coins.xrp.name: return Utils.Coins.xrp
    else: print('Error in Coins -> list Coins({})'.format(Utils.Coins.__dict__['_member_names_'])); exit()
