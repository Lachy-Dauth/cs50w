from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import functions
from decimal import Decimal

class User(AbstractUser):
    gifted_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    last_daily_bonus = models.DateField(default=timezone.now)

    def update_user_stats(self):
        tickets = Ticket.objects.filter(user=self, is_active=True)
        money_spent = tickets.aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
        profit = Decimal(self.balance) + Decimal(money_spent) - Decimal(self.gifted_balance) 
        UserStat.objects.create(
            user=self,
            balance=self.balance,
            money_spent_on_tickets=money_spent,
            profit=profit,
            total_money=Decimal(self.balance)+Decimal(money_spent),
        )

@receiver(post_save, sender=User)
def update_profit_on_new_user(sender, instance, created, **kwargs):
    if created:
        instance.update_user_stats()

class UserStat(models.Model):
    user = models.ForeignKey(User, related_name='stats', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    money_spent_on_tickets = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    total_money = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp} - Balance: {self.balance} - Spent: {self.money_spent_on_tickets} - Profit: {self.profit}"

class Bet(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    reserve = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    is_active = models.BooleanField(default=True)
    can_buy = models.BooleanField(default=True)
    tickets_sold = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def update_active(self):
        self.can_buy = self.can_buy and self.is_active and timezone.now() < self.end_time
        self.save()

    def update_tickets_sold(self):
        total_tickets = self.options.aggregate(Sum('tickets_sold'))['tickets_sold__sum'] or 0
        self.tickets_sold = total_tickets
        self.save()

    def distribute_prizes(self, winning_option_id):
        winning_option = BetOption.objects.get(id=winning_option_id)
        all_tickets = Ticket.objects.filter(option__bet=self)
        winning_tickets = all_tickets.filter(option=winning_option)
        prize_per_ticket = Decimal(10)  # Assuming the prize per winning ticket is $10

        for ticket in winning_tickets:
            if ticket.is_active:
                ticket.user.balance += prize_per_ticket
                ticket.user.save()

        for ticket in all_tickets:
            ticket.is_active = False
            ticket.save()

        self.is_active = False
        self.save()
        ticket.user.update_user_stats()

        # Calculate unused reserves
        unused_reserve = self.reserve - (prize_per_ticket * winning_tickets.count())

        # Update profit record
        profit_record = ProfitRecord.objects.last()
        cumulative_profit = profit_record.cumulative_profit + unused_reserve
        current_reserves = profit_record.current_reserves - self.reserve

        ProfitRecord.objects.create(cumulative_profit=cumulative_profit, current_reserves=current_reserves)

    def handle_ticket_purchase(self, user, option, ticket_quantity):
        total_cost = functions.get_successive_price(self.reserve, self.tickets_sold, option.tickets_sold, ticket_quantity)
        if total_cost <= user.balance:
            new_reserves = Decimal(0)
            for i in range(ticket_quantity):
                option.update_sold()
                price = option.current_price
                ticket = Ticket(
                    user=user,
                    option=option,
                    price=price,
                )
                new_reserves += Decimal(price) - Decimal(0.2)
                self.reserve += Decimal(price) - Decimal(0.2)
                ticket.save()
                user.balance -= Decimal(price)

            profit_record = ProfitRecord.objects.last()
            cumulative_profit = profit_record.cumulative_profit + Decimal(0.2) * Decimal(ticket_quantity)
            current_reserves = profit_record.current_reserves + new_reserves

            ProfitRecord.objects.create(cumulative_profit=cumulative_profit, current_reserves=current_reserves)

            option.update_sold()
            user.update_user_stats()
            user.save()

class BetOption(models.Model):
    bet = models.ForeignKey(Bet, related_name='options', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    tickets_sold = models.IntegerField(default=0)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.5)

    def __str__(self):
        return f"{self.bet.name} - {self.name}"
    
    def update_price(self):
        self.bet.update_tickets_sold()
        self.current_price = functions.get_price(self.bet.reserve, self.bet.tickets_sold, self.tickets_sold)
        self.save()

    def update_sold(self):
        self.tickets_sold = self.sold_tickets.count()
        self.update_price()
        self.save()

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    option = models.ForeignKey(BetOption, on_delete=models.CASCADE, related_name='sold_tickets')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.option.bet.name} - {self.option.name}"
        
@receiver(post_save, sender=Ticket)
def update_profit_on_ticket_purchase(sender, instance, created, **kwargs):
    pass

@receiver(post_save, sender=Bet)
def update_reserves_on_bet_creation(sender, instance, created, **kwargs):
    if created:
        profit_record = ProfitRecord.objects.last()
        reserve_decimal = Decimal(instance.reserve)
        if profit_record:
            cumulative_profit = profit_record.cumulative_profit - reserve_decimal
            current_reserves = profit_record.current_reserves + reserve_decimal
        else:
            cumulative_profit = -reserve_decimal
            current_reserves = reserve_decimal

        ProfitRecord.objects.create(cumulative_profit=cumulative_profit, current_reserves=current_reserves)

class ProfitRecord(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    cumulative_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_reserves = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Profit as of {self.date}: {self.cumulative_profit}, Reserves: {self.current_reserves}"
