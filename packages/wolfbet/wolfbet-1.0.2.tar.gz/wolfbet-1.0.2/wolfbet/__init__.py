import argparse
import random
import sys
import time
from typing import Tuple, Union

from .core import Utils, PPRint, Config, Connection, Response, Constant

parser = argparse.ArgumentParser(description='Wolf Bet by DesKaOne')

parser.add_argument('--limbo', action='store_true', help='Start Limbo')
parser.add_argument('--dice', action='store_true', help='Start Dice')

args = parser.parse_args()

class WolfBet:

    class Starter:

        def __utils__(self, v: bool):
            if v:
                return f'{Utils.Color.GREEN}{PPRint.Active.value}'
            return f'{Utils.Color.RED}{PPRint.NoActive.value}'

        def Info(self, InitialBet: float, Coins: Utils.Coins, Payment: Union[float, int, Utils.ChanceToPayment], Chance: Union[float, int, Utils.PaymentToChance]):
            Utils.Line.Bold()
            print(f'{Utils.Color.WHITE}{PPRint.Games.value}\t\t{Utils.Color.YELLOW}: {Utils.Color.GREEN}{self.Game.name.capitalize()}{Utils.Color.WHITE}')
            print(f'{Utils.Color.WHITE}{PPRint.InitialBet.value}\t{Utils.Color.YELLOW}: {Utils.Color.GREEN}{Utils.FloatToString(InitialBet, 8)}{Utils.Color.WHITE} {Coins.name.upper()}')
            print(f'{Utils.Color.WHITE}{PPRint.Payment.value}\t\t{Utils.Color.YELLOW}: {Utils.Color.GREEN}{Payment}{Utils.Color.WHITE}x')
            print(f'{Utils.Color.WHITE}{PPRint.Chance.value}\t\t{Utils.Color.YELLOW}: {Utils.Color.GREEN}{Chance}{Utils.Color.WHITE}%')

            Utils.Line.Normal()

            # If Profit
            print(f'{Utils.Color.WHITE}{PPRint.IfProfit.value}')
            print(f'{Utils.Color.WHITE}{PPRint.ProfitTarget.value}\t{Utils.Color.YELLOW}: {Utils.Color.GREEN}{Utils.FloatToString(Config.IfProfit.Profit, 8)}{Utils.Color.WHITE} {Coins.name.upper()}')
            print(f'{Utils.Color.WHITE}{PPRint.Reset.value}\t\t{Utils.Color.YELLOW}: {self.__utils__(Config.IfProfit.inReset.Active)}{Utils.Color.WHITE}')
            print(f'{Utils.Color.WHITE}{PPRint.Stop.value}\t\t{Utils.Color.YELLOW}: {self.__utils__(Config.IfProfit.inStop.Active)}{Utils.Color.WHITE}')

            Utils.Line.Normal()

            # If Lose
            print(f'{Utils.Color.WHITE}{PPRint.IfLose.value}')
            print(f'{Utils.Color.WHITE}{PPRint.Multiplier.value}\t{Utils.Color.YELLOW}: {Utils.Color.GREEN}{Config.IfLose.inChange.Multiplier}{Utils.Color.WHITE}x')
            print(f'{Utils.Color.WHITE}{PPRint.Change.value}\t\t{Utils.Color.YELLOW}: {self.__utils__(Config.IfLose.inChange.Active)}{Utils.Color.WHITE}')
            print(f'{Utils.Color.WHITE}{PPRint.Reset.value}\t\t{Utils.Color.YELLOW}: {self.__utils__(Config.IfLose.inReset.Active)}{Utils.Color.WHITE}')
            print(f'{Utils.Color.WHITE}{PPRint.Stop.value}\t\t{Utils.Color.YELLOW}: {self.__utils__(Config.IfLose.inStop.Active)}{Utils.Color.WHITE}')

            Utils.Line.Normal()

            # If Lose
            print(f'{Utils.Color.WHITE}{PPRint.IfWin.value}')
            print(f'{Utils.Color.WHITE}{PPRint.Multiplier.value}\t{Utils.Color.YELLOW}: {Utils.Color.GREEN}{Config.IfWin.inChange.Multiplier}{Utils.Color.WHITE}x')
            print(f'{Utils.Color.WHITE}{PPRint.Change.value}\t\t{Utils.Color.YELLOW}: {self.__utils__(Config.IfWin.inChange.Active)}{Utils.Color.WHITE}')
            print(f'{Utils.Color.WHITE}{PPRint.Reset.value}\t\t{Utils.Color.YELLOW}: {self.__utils__(Config.IfWin.inReset.Active)}{Utils.Color.WHITE}')
            print(f'{Utils.Color.WHITE}{PPRint.Stop.value}\t\t{Utils.Color.YELLOW}: {self.__utils__(Config.IfWin.inStop.Active)}{Utils.Color.WHITE}')

            Utils.Line.Normal()
            if input('Enter to continue or N/n to stop : ').upper() == 'N': exit()
            Utils.Line.Normal()
        
        def Transaction(self, isWin: bool, Balance: float, Bet: float, Profit: float, Payment: float, Result: float, HI_LO = '', Rule = ''):
            Utils.Line.Clear()
            if self.Game == Utils.Games.dice:
                sys.stdout.write(f'{Utils.Color.BLUE}[{Utils.Color.YELLOW}{HI_LO}{Utils.Color.BLUE}]{Utils.Color.WHITE} ')
            sys.stdout.write(f'{Utils.Color.GREEN}{Utils.FloatToString(Balance, 8)}{Utils.Color.WHITE} ')
            if isWin:
                sys.stdout.write(f'{Utils.Color.GREEN}{Utils.FloatToString(Bet, 8)}{Utils.Color.WHITE} ')
            else:
                sys.stdout.write(f'{Utils.Color.YELLOW}{Utils.FloatToString(Bet, 8)}{Utils.Color.WHITE} ')
            if Profit < float(-0):
                sys.stdout.write(f'{Utils.Color.RED}{Utils.FloatToString(Profit, 8)}{Utils.Color.WHITE} ')
            else:
                sys.stdout.write(f'{Utils.Color.GREEN}{Utils.FloatToString(Profit, 8)}{Utils.Color.WHITE} ')
            if not isWin:
                if self.Game == Utils.Games.dice:
                    if Rule == 'under':
                        sys.stdout.write(f'{Utils.Color.CYAN}{Utils.FloatToString(Payment, 2)}{Utils.Color.WHITE} >= ')
                        sys.stdout.write(f'{Utils.Color.CYAN}{Utils.FloatToString(Result, 2)}{Utils.Color.WHITE}\n')
                    else:
                        sys.stdout.write(f'{Utils.Color.CYAN}{Utils.FloatToString(Payment, 2)}{Utils.Color.WHITE} <= ')
                        sys.stdout.write(f'{Utils.Color.CYAN}{Utils.FloatToString(Result, 2)}{Utils.Color.WHITE}\n')
                else:
                    sys.stdout.write(f'{Utils.Color.CYAN}{Utils.FloatToString(Payment, 2)}{Utils.Color.WHITE} >= ')
                    sys.stdout.write(f'{Utils.Color.CYAN}{Utils.FloatToString(Result, 2)}{Utils.Color.WHITE}\n')
            else:
                if self.Game == Utils.Games.dice:
                    if Rule == 'under':
                        sys.stdout.write(f'{Utils.Color.YELLOW}{Utils.FloatToString(Payment, 2)}{Utils.Color.WHITE} >= ')
                        sys.stdout.write(f'{Utils.Color.YELLOW}{Utils.FloatToString(Result, 2)}{Utils.Color.WHITE}\n')
                    else:
                        sys.stdout.write(f'{Utils.Color.YELLOW}{Utils.FloatToString(Payment, 2)}{Utils.Color.WHITE} <= ')
                        sys.stdout.write(f'{Utils.Color.YELLOW}{Utils.FloatToString(Result, 2)}{Utils.Color.WHITE}\n')
                else:
                    sys.stdout.write(f'{Utils.Color.YELLOW}{Utils.FloatToString(Payment, 2)}{Utils.Color.WHITE} >= ')
                    sys.stdout.write(f'{Utils.Color.YELLOW}{Utils.FloatToString(Result, 2)}{Utils.Color.WHITE}\n')
            
        def Footer(self, Lost: int, Won: int, Count: int, StreakWon: int, StreakLost: int, MaxWon: int, MaxLost: int, end = '\r'):
            sys.stdout.write(f'{Utils.Color.WHITE}Count {Utils.Color.YELLOW}{Count}{Utils.Color.WHITE} ')
            #sys.stdout.write(f'{Utils.Color.WHITE}Lost {Utils.Color.RED}{Lost}{Utils.Color.WHITE} ')
            sys.stdout.write(f'{Utils.Color.WHITE}SLost {Utils.Color.RED}{StreakLost}{Utils.Color.WHITE} ')
            sys.stdout.write(f'{Utils.Color.WHITE}MLost {Utils.Color.RED}{MaxLost}{Utils.Color.WHITE} ')
            #sys.stdout.write(f'{Utils.Color.WHITE}Won {Utils.Color.GREEN}{Won}{Utils.Color.WHITE} ')
            sys.stdout.write(f'{Utils.Color.WHITE}SWon {Utils.Color.GREEN}{StreakWon}{Utils.Color.WHITE} ')
            sys.stdout.write(f'{Utils.Color.WHITE}MWon {Utils.Color.GREEN}{MaxWon}{Utils.Color.WHITE}{end}')
        
        @property
        def Connection(self):
            return Connection(Config.API.Authorization.value, Config.Proxy.HOST.value, Config.Proxy.PORT.value, Config.Proxy.USERNAME.value, Config.Proxy.PASSWORD.value)
        
        @property
        def InfoBalance(self):
            Utils.Line.Bold()
            while True:
                try:
                    balances = self.Connec.Balance()
                    for balance in balances.get('balances'):
                        for K, V in zip(balance.keys(), balance.values()):
                            userBalance = Response.UserBalance(balance)
                            if userBalance.amount > float(0):
                                print('{}{}{} {}{} {}'.format(Utils.Color.WHITE, 'Balance', Utils.Color.GREEN, Utils.FloatToString(userBalance.amount, 8), Utils.Color.WHITE, userBalance.currency.upper()))
                                break
                    break
                except Exception: pass
                except KeyboardInterrupt: raise KeyboardInterrupt()
        
        @property
        def __reset_seed__(self):
            try:
                self.Connec.seedClient(); self.Connec.seedServer()
            except Exception: pass

        def __init__(self, Game: Utils.Games) -> None:
            self.Game = Game
            self.Connec = self.Connection

            self.InfoBalance
            
            if self.Game == Utils.Games.limbo:
                self.BaseBet    = Config.Limbo.BaseBet.value
                self.Coins      = Config.Limbo.Coins.value
                self.Payment    = Config.Limbo.Payment.value
                self.Chance     = Utils.PaymentToChance(Config.Limbo.Payment.value)
            elif self.Game == Utils.Games.dice:
                self.BaseBet    = Config.Dice.BaseBet.value
                self.Coins      = Config.Dice.Coins.value
                self.Payment    = Utils.ChanceToPayment(Config.Dice.Chance.value)
                self.Chance     = Config.Dice.Chance.value
                self.DiceChange = Constant.Rule(
                    Change_HI_LO        = Config.Dice.Change_HI_LO.value,
                    Change_HI_LO_Every  = Config.Dice.Change_HI_LO_Every.value,
                )
            
            
            self.IfWin      = Constant.IfWin(
                EveryChange = Config.IfWin.inChange.Count,
                EveryStop   = Config.IfWin.inStop.Count,
                EveryReset  = Config.IfWin.inReset.Count,
                isChange    = Config.IfWin.inChange.Active,
                isReset     = Config.IfWin.inReset.Active,
                isStop      = Config.IfWin.inStop.Active,
                Multiplier  = Config.IfWin.inChange.Multiplier / 100,
            )
            self.IfLose      = Constant.IfLose(
                EveryChange = Config.IfLose.inChange.Count,
                EveryStop   = Config.IfLose.inStop.Count,
                EveryReset  = Config.IfLose.inReset.Count,
                isChange    = Config.IfLose.inChange.Active,
                isReset     = Config.IfLose.inReset.Active,
                isStop      = Config.IfLose.inStop.Active,
                Multiplier  = Config.IfLose.inChange.Multiplier / 100,
            )
            #elif self.Game == Utils.Games.plinko:
            #    BaseBet = Config.Plinko.BaseBet.value
            #    Coins   = Config.Limbo.Coins.value

            self.Info(self.BaseBet, self.Coins, self.Payment, self.Chance)

            if Config.ResetSeed.inStart.Active: self.__reset_seed__

            self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.Profit = 0, 0, 0, 0, 0, 0.0
            self.MaxLost, self.MaxWon, self.CLost, self.CWon = 0, 0, 0, 0
            self.IsLose, self.IsWon = False, False
            self.RCounter, self.RCounterLose, self.RCounterWin = 0, 0, 0

            self.AmountBetting = round(self.BaseBet, 10)     
    
        def Configuration(self, AmountBetting: float, IsWon: bool, IsLose: bool, Lost: int, Won: int, Count: int, StreakWon: int, StreakLost: int, CLost: int, CWon: int):
            if IsWon:
                CWon        += 1
                Won         += 1
                Count       += 1
                StreakWon   += 1
                StreakLost  = 0
                if self.IfWin.isChange and self.IfWin.EveryChange == StreakWon:
                    AmountBetting += round(AmountBetting * self.IfWin.Multiplier, 10)
                elif self.IfWin.isReset and self.IfWin.EveryReset == StreakWon:
                    AmountBetting = round(self.BaseBet, 10)
                elif self.IfWin.isStop and self.IfWin.EveryStop == StreakWon:
                    raise StopIteration(f'If Win Stop Every {StreakWon}')
            elif IsLose:
                CLost       += 1
                Lost        += 1
                Count       += 1
                StreakWon    = 0
                StreakLost  += 1
                if self.IfLose.isChange and self.IfLose.EveryChange == CLost:
                    CLost = 0
                    AmountBetting += round(self.AmountBetting * self.IfLose.Multiplier, 10)
                elif self.IfLose.isReset and self.IfLose.EveryReset == CLost:
                    CLost = 0
                    AmountBetting = round(self.BaseBet, 10)
                elif self.IfLose.isStop and self.IfLose.EveryStop == StreakLost:
                    raise StopIteration(f'If Lose Stop Every {StreakLost}')
            else:
                AmountBetting = round(self.BaseBet, 10)
            return AmountBetting, IsWon, IsLose, Lost, Won, Count, StreakWon, StreakLost, CLost, CWon

        @property
        def Limbo(self):
            Try = 0
            while True:
                Try += 1
                try:
                    Result =  self.Connec.limbo(dict(
                        currency    = self.Coins.name.lower(),
                        game        = 'limbo',
                        amount      = str(Utils.FloatToString(self.AmountBetting, 8)),
                        multiplier  = self.Payment, # Pembayaran
                    ))
                    Try = 0
                    return Response.Bet(Result['bet']),Response.UserBalance(Result['userBalance'])
                except KeyboardInterrupt: raise KeyboardInterrupt()
                except Exception as e:
                    print(Utils.Color.RED, e, Utils.Color.WHITE, end='\r')
                    time.sleep(5)
                    if Try > 5:
                        if input('Try Again y/n : ').upper() == 'N':
                            exit()
                    else:
                        self.Connec = self.Connection
        
        def Dice(self, Rule: str, Multiplier: str, BetValue: str):
            Try = 0
            while True:
                Try += 1
                try:
                    Result = self.Connec.dice(dict(
                        currency    = self.Coins.name.lower(),
                        game        = 'dice',
                        auto        = 1,
                        amount      = str(Utils.FloatToString(self.AmountBetting, 8)),
                        rule        = Rule,
                        multiplier  = Multiplier, # Pembayaran
                        bet_value   = BetValue # ROLL
                    ))
                    return Response.Bet(Result['bet']),Response.UserBalance(Result['userBalance'])
                except KeyboardInterrupt: raise KeyboardInterrupt()
                except Exception as e:
                    print(Utils.Color.RED, e, Utils.Color.WHITE, end='\r')
                    time.sleep(5)
                    if Try > 5:
                        if input('Try Again y/n : ').upper() == 'N':
                            exit()
                    else:
                        self.Connec = self.Connection

    class Limbo(Starter):

        def __init__(self) -> None:
            super().__init__(Utils.Games.limbo)
            Try = 0
            while True:
                try:
                    self.RCounter += 1
                    self.Result_Bet, self.Result_Balance = self.Limbo

                    if self.Result_Bet.state == 'loss':
                        self.IsLose = True; self.IsWon = False
                        self.RCounterLose   += 1
                    else:
                        self.IsLose = False; self.IsWon = True
                        self.RCounterWin    += 1

                    self.Profit += self.Result_Bet.profit
                    if self.IsWon:
                        self.Transaction(self.IsWon, self.Result_Balance.amount, self.Result_Bet.profit, self.Profit, self.Payment, float(self.Result_Bet.result_value))
                    else:
                        self.Transaction(self.IsWon, self.Result_Balance.amount, self.Result_Bet.amount, self.Profit, self.Payment, float(self.Result_Bet.result_value))

                    self.AmountBetting, self.IsWon, self.IsLose, self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.CLost, self.CWon = self.Configuration(self.AmountBetting, self.IsWon, self.IsLose, self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.CLost, self.CWon)
                    
                    if self.MaxWon < self.StreakWon: self.MaxWon = self.StreakWon
                    if self.MaxLost < self.StreakLost: self.MaxLost = self.StreakLost

                    self.Footer(self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.MaxWon, self.MaxLost)

                    try:
                        if Config.ResetSeed.inCounter.Active and self.RCounter >= Config.ResetSeed.inCounter.Count: self.__reset_seed__; self.RCounter = 0
                        elif Config.ResetSeed.inLoser.Active and self.RCounterLose >= Config.ResetSeed.inLoser.Count: self.__reset_seed__; self.RCounterLose = 0
                        elif Config.ResetSeed.inWinner.Active and self.RCounterWin >= Config.ResetSeed.inWinner.Count: self.__reset_seed__; self.RCounterWin = 0
                    except Exception: pass
                    
                    if self.Profit >= float(Config.IfProfit.Profit): 
                        raise StopIteration('Profit Mencapai Target')

                    Try = 0
                except KeyboardInterrupt: 
                    self.Footer(self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.MaxWon, self.MaxLost, '\n')
                    if input('Anda yakin untuk berhenti y/n : ').upper() == 'Y': exit()
                    self.Connec = self.Connection
                except StopIteration as e:
                    self.Footer(self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.MaxWon, self.MaxLost, '\n')
                    print(Utils.Color.RED, e, Utils.Color.WHITE)
                    if input('Anda yakin untuk berhenti y/n : ').upper() == 'Y': exit()
                except Exception as e:
                    Try += 1
                    print(Utils.Color.RED, e, Utils.Color.WHITE)
                    if Try > 5:
                        if input('Try Again y/n : ').upper() == 'N': exit()
                    else:
                        time.sleep(random.randint(5, 10))

    class Dice(Starter):

        def BetValues(self) -> Tuple[str, str]:
            ChanceToPayment = Utils.ChanceToPayment(self.Chance)
            if self.Rule == 'over':
                Multiplier  = str(ChanceToPayment.Payment)
                Roll        = str(round((100 - (0.01 + ChanceToPayment.Chance)), 2))
            else:
                Multiplier  = str(ChanceToPayment.Payment)
                Roll        = str(ChanceToPayment.Chance)
            return Multiplier, Roll
        
        @property
        def ChangeHiLo(self):
            if self.DiceChange.Change_HI_LO:
                if self.Rule == self.DiceChange.under:
                    if self.DiceChange.Change_HI_LO_Every == self.HILOCHANGE:
                        self.Rule = self.DiceChange.over
                        self.HILOCHANGE = 0
                elif self.Rule == self.DiceChange.over:
                    if self.DiceChange.Change_HI_LO_Every == self.HILOCHANGE:
                        self.Rule = self.DiceChange.under
                        self.HILOCHANGE = 0

        def __init__(self) -> None:
            super().__init__(Utils.Games.dice)
            Try = 0
            self.HILOCHANGE = 0
            while True:
                try:

                    if Config.Dice.LO.value: self.Rule      = self.DiceChange.under
                    elif Config.Dice.HI.value: self.Rule    = self.DiceChange.over
                    elif Config.Dice.RANDOM: self.Rule      = random.choice([self.DiceChange.under, self.DiceChange.over])
                    else: self.Rule                         = self.DiceChange.under
                    if self.DiceChange.Change_HI_LO:
                        self.HILOCHANGE += 1
                        self.ChangeHiLo

                    self.Payment, BetValue = self.BetValues()

                    self.RCounter += 1
                    self.Result_Bet, self.Result_Balance = self.Dice(self.Rule, self.Payment, BetValue)
                    HI_LO      = 'LO' if self.Result_Bet.rule == 'under' else 'HI'

                    if self.Result_Bet.state == 'loss':
                        self.IsLose = True; self.IsWon = False
                        self.RCounterLose   += 1
                    else:
                        self.IsLose = False; self.IsWon = True
                        self.RCounterWin    += 1

                    self.Profit += self.Result_Bet.profit
                    if self.IsWon:
                        self.Transaction(self.IsWon, self.Result_Balance.amount, self.Result_Bet.profit, self.Profit, float(BetValue), float(self.Result_Bet.result_value), HI_LO)
                    else:
                        self.Transaction(self.IsWon, self.Result_Balance.amount, self.Result_Bet.amount, self.Profit, float(BetValue), float(self.Result_Bet.result_value), HI_LO)

                    self.AmountBetting, self.IsWon, self.IsLose, self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.CLost, self.CWon = self.Configuration(self.AmountBetting, self.IsWon, self.IsLose, self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.CLost, self.CWon)
                    
                    if self.MaxWon < self.StreakWon: self.MaxWon = self.StreakWon
                    if self.MaxLost < self.StreakLost: self.MaxLost = self.StreakLost

                    self.Footer(self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.MaxWon, self.MaxLost)

                    try:
                        if Config.ResetSeed.inCounter.Active and self.RCounter >= Config.ResetSeed.inCounter.Count: self.__reset_seed__; self.RCounter = 0
                        elif Config.ResetSeed.inLoser.Active and self.RCounterLose >= Config.ResetSeed.inLoser.Count: self.__reset_seed__; self.RCounterLose = 0
                        elif Config.ResetSeed.inWinner.Active and self.RCounterWin >= Config.ResetSeed.inWinner.Count: self.__reset_seed__; self.RCounterWin = 0
                    except Exception: pass
                    
                    if self.Profit >= float(Config.IfProfit.Profit): 
                        raise StopIteration('Profit Mencapai Target')

                    Try = 0
                except KeyboardInterrupt: 
                    self.Footer(self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.MaxWon, self.MaxLost, '\n')
                    if input('Anda yakin untuk berhenti y/n : ').upper() == 'Y': exit()
                    self.Connec = self.Connection
                except StopIteration as e:
                    self.Footer(self.Lost, self.Won, self.Count, self.StreakWon, self.StreakLost, self.MaxWon, self.MaxLost, '\n')
                    print(Utils.Color.RED, e, Utils.Color.WHITE)
                    if input('Anda yakin untuk berhenti y/n : ').upper() == 'Y': exit()
                #except Exception as e:
                    Try += 1
                    print(Utils.Color.RED, e, Utils.Color.WHITE)
                    if Try > 5:
                        if input('Try Again y/n : ').upper() == 'N': exit()
                    else:
                        time.sleep(random.randint(5, 10))

    def __new__(cls) -> 'WolfBet':

        Utils.Reset()
        if args.limbo:
            cls.Limbo()
        elif args.dice:
            cls.Dice()
        else:
            parser.print_help()
        return cls

if __name__ == '__main___':
    WolfBet()
