class Constant:

    class BaseBet:
        
        Amount: float   = 0.0

        def __new__(cls, amount: float):
            setattr(Constant.BaseBet, 'Amount', amount)
            return cls
    
    class Payment:
        
        Amount: float   = 0.0

        def __new__(cls, amount: float):
            setattr(Constant.Payment, 'Amount', amount)
            return cls
    
    class Chance:
        
        Value: int   = 0

        def __new__(cls, value: int):
            setattr(Constant.Chance, 'Value', value)
            return cls
    
    class IfWin:
        
        EveryChange: int= 1
        EveryStop: int  = 1
        EveryReset: int = 1
        Multiplier: float = 0
        isStop: bool    = True
        isChange: bool  = False
        isReset: bool   = False

        def __new__(cls, **kwargs):
            for K, V in zip(kwargs.keys(), kwargs.values()):
                setattr(Constant.IfWin, K, V)
            return cls
    
    class IfLose:
        
        EveryChange: int= 1
        EveryStop: int  = 1
        EveryReset: int = 1
        Multiplier: float = 0
        isStop: bool    = False
        isChange: bool  = False
        isReset: bool   = False

        def __new__(cls, **kwargs):
            for K, V in zip(kwargs.keys(), kwargs.values()):
                setattr(Constant.IfLose, K, V)
            return cls
    
    class IfProfit:

        isStop: bool    = False
        isReset: bool   = False
        Profit: float   = 0.0

        def __new__(cls, **kwargs):
            for K, V in zip(kwargs.keys(), kwargs.values()):
                setattr(Constant.IfProfit, K, V)
            return cls

    class Rule:

        under: str = 'under'
        over: str = 'over'
        Change_HI_LO: bool  = False
        Change_HI_LO_Every: int = 1

        def __new__(cls, **kwargs):
            for K, V in zip(kwargs.keys(), kwargs.values()):
                setattr(Constant.Rule, K, V)
            return cls
