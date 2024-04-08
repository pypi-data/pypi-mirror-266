from enum import Enum

from .type import config, ParseCoins
from .Utils import Utils

class Config:

    class Proxy(Enum):

        HOST: str        = config.get('Proxy').get('HOST', None)
        PORT: str        = config.get('Proxy').get('PORT', None)
        USERNAME: str    = config.get('Proxy').get('USERNAME', None)
        PASSWORD: str    = config.get('Proxy').get('PASSWORD', None)

    class API(Enum):

        Authorization: str  = config.get('API').get('Authorization', None)
        Log: bool           = config.get('API').get('Log', False)

    class Limbo(Enum):

        #Coins   = Coins.shib # Coins Name in list @Coins
        Coins: Utils.Coins  = ParseCoins(config.get('API').get('Coins', Utils.Coins.trx.name).lower())
        BaseBet: float      = config.get('Limbo').get('BaseBet', 0.00000001)
        Payment: int        = config.get('Limbo').get('Payment', 100)

    #class Plinko(Enum):

        #Coins   = Coins.shib # Coins Name in list @Coins
    #    Coins: Utils.Coins  = ParseCoins(config.get('API').get('Coins', Utils.Coins.trx.name).lower())
    #    BaseBet: float      = config.get('Plinko').get('BaseBet', 0.00000001)
    #    Payment: int        = config.get('Plinko').get('Payment', 100)

    class Dice(Enum): # not Implement

        #Coins   = Coins.xlm # Coins Name in list @Coins
        Coins: Utils.Coins  = ParseCoins(config.get('API').get('Coins', Utils.Coins.trx.name).lower())
        BaseBet: float      = config.get('Dice').get('BaseBet', 0.00000001)
        Chance: int         = config.get('Dice').get('Chance', 100)

        HI: bool                = config.get('Dice').get('HI', False)
        LO: bool                = config.get('Dice').get('LO', True)
        RANDOM: bool            = config.get('Dice').get('RANDOM', False)
        Change_HI_LO: bool      = config.get('Dice').get('Change_HI_LO', False)
        Change_HI_LO_Every: int = config.get('Dice').get('Change_HI_LO_Every', 5)

    class ResetSeed:

        class inStart:
            
            Active: bool    = config.get('ResetSeed').get('inStart').get('Active', True)
        
        class inCounter:
            
            Count: int      = config.get('ResetSeed').get('inCounter').get('Count', 100000)
            Active: bool    = config.get('ResetSeed').get('inCounter').get('Active', False)
        
        class inLoser:
            
            Count: int      = config.get('ResetSeed').get('inLoser').get('Count', 50000)
            Active: bool    = config.get('ResetSeed').get('inLoser').get('Active', True)
        
        class inWinner:
            
            Count: int      = config.get('ResetSeed').get('inWinner').get('Count', 50000)
            Active: bool    = config.get('ResetSeed').get('inWinner').get('Active', False)

    class IfLose:
        
        class inStop:

            Count: int      = config.get('IfLose').get('inStop').get('Count', 1)
            Active: bool    = config.get('IfLose').get('inStop').get('Active', False)
        
        class inReset:

            Count: int      = config.get('IfLose').get('inReset').get('Count', 1)
            Active: bool    = config.get('IfLose').get('inReset').get('Active', False)
        
        class inChange:

            Count: int      = config.get('IfLose').get('inChange').get('Count', 10)
            Active: bool    = config.get('IfLose').get('inChange').get('Active', True)
            Multiplier: int = config.get('IfLose').get('inChange').get('Multiplier', 10)

    class IfWin:
        
        class inStop:

            Count: int      = config.get('IfWin').get('inStop').get('Count', 1)
            Active: bool    = config.get('IfWin').get('inStop').get('Active', False)
        
        class inReset:

            Count: int      = config.get('IfWin').get('inReset').get('Count', 1)
            Active: bool    = config.get('IfWin').get('inReset').get('Active', True)
        
        class inChange:

            Count: int      = config.get('IfWin').get('inChange').get('Count', 1)
            Active: bool    = config.get('IfWin').get('inChange').get('Active', False)
            Multiplier: int = config.get('IfWin').get('inChange').get('Multiplier', 1)

    class IfProfit:

        Profit: int         = config.get('IfProfit').get('TargetProfit', 1)

        class inReset:
            
            Active: bool    = config.get('IfProfit').get('inReset').get('Active', False)
        
        class inStop:

            Active: bool    = config.get('IfProfit').get('inStop').get('Active', True)
   
    class Display(Enum):

        Table: bool   = config.get('Display').get('Table', False)
        List: bool    = config.get('Display').get('List', True)

