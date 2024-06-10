import math

def round_num(num):
    return math.ceil(num * 100) / 100

def get_price(reserve, total_tickets, option_tickets):
    return max(round_num(1 - 0.01 * float(reserve - option_tickets)), 0)

def get_successive_price(reserve, total_tickets, option_tickets, number):
    if number == 0:
        return 0
    current_price = get_price(reserve, total_tickets, option_tickets)
    return current_price + get_successive_price(float(reserve) + 0.99 * current_price, total_tickets + 1, option_tickets + 1, number - 1)