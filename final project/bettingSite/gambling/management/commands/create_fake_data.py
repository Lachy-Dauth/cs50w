from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from gambling.models import User, Bet, BetOption, Ticket
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Generate fake data for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()
        game_names = [
            "Football Championship", "Basketball Showdown", "Tennis Grand Slam",
            "Soccer World Cup", "Cricket Test Series", "Hockey Finals",
            "Rugby Cup", "Baseball Playoffs", "Golf Masters", "Boxing Title Match"
        ]

        # Create fake users
        for _ in range(10):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                balance=Decimal(1000)
            )
            user.save()

            # Create fake bets and options
            for _ in range(5):
                game_name = random.choice(game_names)
                bet = Bet.objects.create(
                    name=f"{game_name} game {random.randint(1, 100)}",
                    description=fake.text(),
                    end_time=timezone.now() + timezone.timedelta(days=random.randint(1, 30)),
                    reserve=Decimal(666),
                    is_active=True
                )

                options = []
                for _ in range(3):
                    option = BetOption.objects.create(
                        bet=bet,
                        name=fake.word(),
                        tickets_sold=random.randint(0, 20),
                        current_price=Decimal(0.5)
                    )
                    options.append(option)

                # Create fake tickets for the user using handle_ticket_purchase
                for option in options:
                    ticket_quantity = random.randint(1, 5)
                    bet.handle_ticket_purchase(user, option, ticket_quantity)

        self.stdout.write(self.style.SUCCESS('Successfully created fake data.'))
