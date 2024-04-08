class Response:

    class UserBalance:

        amount: float = None
        currency: str = None
        amount_usd: float = None

        def __new__(cls, data: dict):
            for K, V in zip(data.keys(), data.values()):
                if K != 'currency':
                    setattr(Response.UserBalance, K, float(V))
                else:
                    setattr(Response.UserBalance, K, V)
            return cls
        
    class Bet:

        hash: str = None
        nonce: int = None
        currency: str = None
        amount: float = None
        profit: float = None
        multiplier: int = None
        result_value: str = None
        state: str = None
        published_at: str = None
        bet_value: str = None
        rule: str = None

        def __new__(cls, data: dict):
            for K, V in zip(data.keys(), data.values()):
                if K == 'amount':
                    setattr(Response.Bet, 'amount', float(V))
                elif K == 'profit':
                    setattr(Response.Bet, 'profit', float(V))
                else:
                    setattr(Response.Bet, K, V)
            return cls
    
    