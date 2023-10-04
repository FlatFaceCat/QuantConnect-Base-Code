"""
This file contains QuantConnect order codes for easy conversion and more 
intuitive custom order handling

References:
    https://github.com/QuantConnect/Lean/blob/master/Common/Orders/OrderTypes.cs
    https://github.com/QuantConnect/Lean/blob/master/Common/Orders/OrderRequestStatus.cs
"""

OrderTypeKeys = [
    'Market', 'Limit', 'StopMarket', 'StopLimit', 'MarketOnOpen',
    'MarketOnClose', 'OptionExercise',
]

OrderTypeCodes = dict(zip(range(len(OrderTypeKeys)), OrderTypeKeys))

OrderDirectionKeys = ['Buy', 'Sell', 'Hold']
OrderDirectionCodes = dict(zip(range(len(OrderDirectionKeys)), OrderDirectionKeys))

## NOTE ORDERSTATUS IS NOT IN SIMPLE NUMERICAL ORDER

OrderStatusCodes = {
    0:'New', # new order pre-submission to the order processor
    1:'Submitted', # order submitted to the market
    2:'PartiallyFilled', # partially filled, in market order
    3:'Filled', # completed, filled, in market order
    5:'Canceled', # order cancelled before filled
    6:'None', # no order state yet
    7:'Invalid', # order invalidated before it hit the market (e.g. insufficient capital)
    8:'CancelPending', # order waiting for confirmation of cancellation
}