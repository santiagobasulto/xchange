from decimal import Decimal

from xchange import exceptions
from xchange.constants import exchanges
from xchange.decorators import is_valid_argument


@is_valid_argument('action', arg_position=0)
@is_valid_argument('amount', arg_position=2)
def volume_weighted_average_price(action, order_book, amount):
    """
    Calculates the weighted average price of an operation (sell/buy)
    for a given `amount` and `order_book`.

    @params:
        * action: exchanges.ACTIONS choice
        * order_book: models.base.OrderBook instance or subclass
        * amount: Decimal or valid numeric argument representing volume to operate.

    @returns:
        a Decimal object representing the weighted average price.
    """
    order_list = order_book.asks if action == exchanges.BUY else order_book.bids

    total_market_depth = sum([t[1] for t in order_list])
    if amount > total_market_depth:
        raise exceptions.InsufficientMarketDepth(
            'Not enough depth in OrderBook to {} {} volume'.format(action, amount))

    if action == exchanges.BUY:
        # when checking the "asks" list, we want to
        # iterate orders from cheapest to highest
        order_list = list(reversed(order_list))
    accum = Decimal(0.0)

    # most of the times last used order in the orderbook
    # is partially used. we need to know which was the portion
    # used from that order to calculate the weighted average
    rest = amount

    for index, price_tuple in enumerate(order_list):
        volume = price_tuple[1]
        accum += volume
        if accum >= amount:
            break
        rest -= volume

    # get the sub list representing only the necessary
    # orders to fulfill the amount amount
    sub_list = order_list[:index + 1]

    # change the last used order in the list, to just
    # the needed rest amount
    sub_list[-1] = (sub_list[-1][0], Decimal(rest))

    sub_list_amounts = [t[1] for t in sub_list]
    return sum(x * y for x, y in sub_list) / sum(sub_list_amounts)
