from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import functions
from decimal import Decimal

class User(AbstractUser):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)

class Bet(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    reserve = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    is_active = models.BooleanField(default=True)
    tickets_sold = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    def is_bet_active(self):
        return self.is_active and timezone.now() < self.end_time

    def update_active(self):
        self.is_active = self.is_active and timezone.now() < self.end_time

    def update_tickets_sold(self):
        total_tickets = self.options.aggregate(Sum('tickets_sold'))['tickets_sold__sum'] or 0
        self.tickets_sold = total_tickets
        self.save()

    def distribute_prizes(self, winning_option_id):
        winning_option = BetOption.objects.get(id=winning_option_id)
        winning_tickets = Ticket.objects.filter(option=winning_option)
        prize_per_ticket = Decimal(1)  # Assuming the prize per winning ticket is $1

        for ticket in winning_tickets:
            if ticket.is_active:
                ticket.user.balance += prize_per_ticket
                ticket.is_active = False
                ticket.save()
                ticket.user.save()

        self.is_active = False
        self.save()

        # Calculate unused reserves
        unused_reserve = self.reserve - (prize_per_ticket * winning_tickets.count())

        # Update profit record
        profit_record = ProfitRecord.objects.last()
        cumulative_profit = profit_record.cumulative_profit + Decimal(0.01 * winning_tickets.count()) + unused_reserve
        current_reserves = profit_record.current_reserves - self.reserve

        ProfitRecord.objects.create(cumulative_profit=cumulative_profit, current_reserves=current_reserves)

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
    if created:
        profit_record = ProfitRecord.objects.last()
        cumulative_profit = profit_record.cumulative_profit + Decimal(instance.price) - Decimal(0.99) * Decimal(instance.price)
        current_reserves = profit_record.current_reserves + Decimal(0.99) * Decimal(instance.price)

        ProfitRecord.objects.create(cumulative_profit=cumulative_profit, current_reserves=current_reserves)

@receiver(post_save, sender=Bet)
def update_reserves_on_bet_creation(sender, instance, created, **kwargs):
    if created:
        # Update profit record
        profit_record = ProfitRecord.objects.last()
        if profit_record:
            cumulative_profit = profit_record.cumulative_profit - instance.reserve
            current_reserves = profit_record.current_reserves + instance.reserve
        else:
            cumulative_profit = -instance.reserve
            current_reserves = instance.reserve

        ProfitRecord.objects.create(cumulative_profit=cumulative_profit, current_reserves=current_reserves)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.transaction_type}"

class ProfitRecord(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    cumulative_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_reserves = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Profit as of {self.date}: {self.cumulative_profit}, Reserves: {self.current_reserves}"