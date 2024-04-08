from enum import Enum


class PPRint(Enum):

    Games       = 'Games'
    InitialBet  = 'Initial Bet'
    Payment     = 'Payment'
    Chance      = 'Chance'

    ProfitTarget= 'Profit Target'

    Profit      = "Profit"
    Wagered     = "Wagered"
    Lost        = "Lost"
    Won         = "Won"
    Streak      = "Streak"
    HighestWin  = "Highest Win"
    HighestLost = "Highest Lost"
    HighestBet  = "Highest Bet"
    MaxStreaks  = "Max Streaks"

    Change      = 'Change'
    Stop        = 'Stop'
    Reset       = 'Reset'
    Multiplier  = 'Multiplier'
    IfProfit    = 'IfProfit'
    IfLose      = 'IfLose'
    IfWin       = 'IfWin'
    NoActive    = 'No Active'
    Active      = 'Active'
