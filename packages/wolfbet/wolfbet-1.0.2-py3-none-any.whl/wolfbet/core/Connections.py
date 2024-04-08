import random
import secrets
from typing import Dict, List
from http_injector import HTTPInjector, ProxyParams, ProxyType, TypeInjector

class Connection:

    __connection__: HTTPInjector = None

    def __new__(cls, Authorization: str, HOST: str = None, PORT: int = None, USERNAME: str = None, PASSWORD: str = None):
        if HOST is not None and PORT is not None:
            Proxy = ProxyParams (
                type    = ProxyType.http,
                IP      = HOST,
                PORT    = PORT,
                USERNAME= USERNAME,
                PASSWORD= PASSWORD
            )
        else: Proxy = None
        setattr(Connection, '__connection__', HTTPInjector(
            typeInjector    = TypeInjector.httpx,
            timeout         = 15,
            headers         = {
                'Authorization' : f'Bearer {Authorization}'
            },
            proxyParams     = Proxy
        ))
        return cls
        
    @classmethod
    def Balance(self) -> Dict[str, List[Dict[str, str]]]:
        return self.__connection__.get('https://wolf.bet/api/v1/user/balances').json()
        
    @classmethod
    def limbo(self, json: dict) -> dict:
        return self.__connection__.post('https://wolf.bet/api/v2/limbo/manual/play', json=json).json()
        
    @classmethod
    def dice(self, json: dict) -> dict:
        return self.__connection__.post('https://wolf.bet/api/v1/dice/manual/play', json=json).json()
        return self.__connection__.post('https://wolf.bet/api/v1/bet/place', json=json).json()
    
    @classmethod
    def seedClient(self) -> dict:
        return self.__connection__.post('https://wolf.bet/api/v1/user/seed/refresh', json=dict(client_seed = secrets.token_hex(random.choice([8, 16, 32])))).json()
        
    @classmethod
    def seedServer(self) -> dict:
        return self.__connection__.get('https://wolf.bet/api/v1/game/seed/refresh').json()
        
    @classmethod
    def stats(self) -> dict:
        return self.__connection__.get('https://wolf.bet/api/v1/user/stats/bets').json()
    
    