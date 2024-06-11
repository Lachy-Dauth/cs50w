from decimal import Decimal
import math

def round_num(num):
    return Decimal(math.ceil(num * Decimal(100)) / 100)
    
def r(num):
    return Decimal(round(num, 2))

def get_price(reserve, total_tickets, option_tickets):
    return round_num(max(Decimal(10) - Decimal(0.02/(math.log10(int(total_tickets)+100))) * Decimal(reserve - 10 * option_tickets), 0))

def get_successive_price(reserve, total_tickets, option_tickets, number):
    return r(get_successive_price_inner(reserve, total_tickets, option_tickets, number))

def get_successive_price_inner(reserve, total_tickets, option_tickets, number):
    if number == 0:
        return 0
    current_price = Decimal(get_price(reserve, total_tickets, option_tickets))
    return current_price + get_successive_price(reserve + current_price - Decimal(0.2), total_tickets + 1, option_tickets + 1, number - 1)