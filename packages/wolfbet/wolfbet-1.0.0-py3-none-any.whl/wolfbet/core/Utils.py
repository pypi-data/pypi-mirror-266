from enum import Enum, auto
import os
import platform
import shutil
from typing import Union

from colorama import Fore


class Utils:

    class Games(Enum):

        limbo = auto()
        dice = auto()
        plinko = auto()

    class Coins(Enum):
        ada     = auto() # Min Bet 0.00000001
        bch     = auto() # Min Bet 0.00000001
        bnb     = auto() # Min Bet 0.00000001
        btc     = auto() # Min Bet 0.00000001
        doge    = auto() # Min Bet 0.00000001
        dot     = auto() # Min Bet 0.00000001
        etc     = auto() # Min Bet 0.00000001
        eth     = auto() # Min Bet 0.00000001
        ltc     = auto() # Min Bet 0.00000001
        shib    = auto() # Min Bet 1
        sushi   = auto() # Min Bet 0.00000001
        trx     = auto() # Min Bet 0.00000001
        uni     = auto() # Min Bet 0.00000001
        usdt    = auto() # Min Bet 0.00000001
        xlm     = auto() # Min Bet 0.00000001
        xrp     = auto() # Min Bet 0.00000001

    class Color:
    
        BLACK       = Fore.LIGHTBLACK_EX
        RED         = Fore.LIGHTRED_EX
        GREEN       = Fore.LIGHTGREEN_EX
        YELLOW      = Fore.LIGHTYELLOW_EX
        BLUE        = Fore.LIGHTBLUE_EX
        MAGENTA     = Fore.LIGHTMAGENTA_EX
        CYAN        = Fore.LIGHTCYAN_EX
        WHITE       = Fore.LIGHTWHITE_EX
        RESET       = Fore.RESET

    class Line:
        
        @staticmethod
        def Normal():
            try: Size = os.get_terminal_size()
            except: Size = shutil.get_terminal_size(fallback=(120, 50))
            Length = int((Size.columns))
            print('-' * Length)
            
        @staticmethod
        def Bold():
            try: Size = os.get_terminal_size()
            except: Size = shutil.get_terminal_size(fallback=(120, 50))
            Length = int((Size.columns))
            print('=' * Length)
            
        @staticmethod
        def Clear():
            try: Size = os.get_terminal_size()
            except: Size = shutil.get_terminal_size(fallback=(120, 50))
            Length = int((Size.columns))
            print((' ' * Length), end='\r')

    class Reset:

        def __init__(self) -> None:
            if platform.system().lower() == "windows":
                os.system('color')
                os.system('cls')
            else:os.system('clear')

    class FloatToString:

        def __init__(self, amount: float, ndigits: int = 8) -> None:
            self.__amount__     = amount
            self.__ndigits__    = ndigits
        
        def __str__(self) -> str:
            res = str("%.{}f".format(self.__ndigits__) % round(self.__amount__, self.__ndigits__)).rstrip('0').rstrip('.')
            try:
                r = res.split('.')[1]
                if len(r) < self.__ndigits__:
                    length = self.__ndigits__ - len(r)
                    res = res + '{}'.format('0' * length)
            except IndexError:
                res = '{}.{}'.format(res, '0' * self.__ndigits__)
            return res
    
    class PaymentToChance:
        
        def __init__(self, Payment: Union[float, int]) -> None:
            if Payment >= 1000000: Payment = 1000000
            elif Payment <= 1.01:  Payment = 1.01
            self.Chance     = 99 / Payment
            self.Payment    = Payment

        def __str__(self) -> str:
            return str(Utils.FloatToString(self.Chance, 2))
    
    class ChanceToPayment:
        
        def __init__(self, Chance: Union[float, int]) -> None:
            if Chance >= 98: Chance = 98
            elif Chance <= 0.01:  Chance = 0.01
            self.Payment    = round(99 / Chance, 4)
            self.Chance     = Chance

        def __str__(self) -> str:
            return str(self.Payment)