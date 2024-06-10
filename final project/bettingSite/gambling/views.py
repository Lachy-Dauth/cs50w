from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import *
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Sum
import decimal
from .decorators import *
from django.utils.decorators import method_decorator
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import *
from . import functions

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.balance = 50.00  # Set the balance to $50
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'gambling/register.html', {'form': form, 'initial_balance': 50.00})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'gambling/login.html', {'error': 'Invalid credentials'})
    return render(request, 'gambling/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required()
def dashboard_view(request):
    return render(request, 'gambling/dashboard.html')

class BetsListView(View):
    def get(self, request):
        return render(request, 'gambling/bets_list.html')


class BetDetailView(LoginRequiredMixin, View):
    def get(self, request, bet_id):
        bet = Bet.objects.get(id=bet_id)
        bet.update_active()
        for option in bet.options.all():
            option.update_price()
        return render(request, 'gambling/bet_detail.html', {
            'bet': bet,
            'options': bet.options.all(),
        })
    
    def post(self, request, bet_id):
        ticket_quantity = int(request.POST['ticket-quantity'])
        option_id = request.POST['option-id']

        bet = Bet.objects.get(id=bet_id)
        option = bet.options.get(id=option_id)

        if ticket_quantity < 1:
            return
        
        total_cost = functions.get_successive_price(bet.reserve, bet.tickets_sold, option.tickets_sold, ticket_quantity)
        if total_cost <= request.user.balance:
            for i in range(ticket_quantity):
                option.update_sold()
                price = option.current_price
                ticket = Ticket(
                    user = request.user,
                    option = option,
                    price = price,
                )
                bet.reserve += decimal.Decimal(0.99) * decimal.Decimal(price)
                ticket.save()
                request.user.balance -= decimal.Decimal(price)
            option.update_sold()
            request.user.save()
        return HttpResponseRedirect(reverse('dashboard'))

class BetsOptionApiView(View):
    def get(self, request):
        bet_id = request.GET.get('bet_id', 1)
        option_id = request.GET.get('option_id', 1)

        bet = Bet.objects.get(id=bet_id)
        option = bet.options.get(id=option_id)
        
        reserve = bet.reserve
        total_tickets = bet.tickets_sold
        option_tickets = option.tickets_sold
        
        return JsonResponse({
            'reserve' : reserve,
            'total_tickets' : total_tickets,
            'option_tickets' : option_tickets,
            'option_name' : option.name,
        })

class BetsApiView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by', 'created_at')
        page = request.GET.get('page', 1)
        
        if sort_by == 'created_at':
            bets = Bet.objects.filter(is_active=True).order_by('-created_at')
        elif sort_by == 'ending_at':
            bets = Bet.objects.filter(is_active=True).order_by('end_time')
        elif sort_by == 'tickets_sold':
            bets = Bet.objects.filter(is_active=True).order_by('-tickets_sold')

        paginator = Paginator(bets, 10)  # 10 bets per page
        bets_page = paginator.get_page(page)

        bets_data = [
            {
                'id': bet.id,
                'name': bet.name,
                'description': bet.description,
                'created_at': bet.created_at,
                'ending_at': bet.end_time,
                'tickets_sold': bet.tickets_sold,
            } for bet in bets_page
        ]

        return JsonResponse({'bets': bets_data, 'has_next': bets_page.has_next()})

@method_decorator(admin_required, name='dispatch')
class AdminBetManagementView(View):
    def get(self, request, bet_id):
        bet = Bet.objects.get(id=bet_id)
        options = bet.options.all()
        return render(request, 'gambling/admin_bet_management.html', {'bet': bet, 'options': options})

    def post(self, request, bet_id):
        bet = Bet.objects.get(id=bet_id)
        if not bet.is_active:
            raise PermissionDenied("This bet is no longer active. A winner has already been selected.")
        
        winning_option_id = request.POST.get('winning_option')
        
        # Distribute prizes and deactivate the bet
        bet.distribute_prizes(winning_option_id)
        
        return redirect('admin_bet_list')

@method_decorator(admin_required, name='dispatch')
class AdminBetListView(View):
    def get(self, request):
        bets = Bet.objects.all()
        return render(request, 'gambling/admin_bet_list.html', {'bets': bets})
    
@method_decorator(admin_required, name='dispatch')
class CreateBetView(View):
    def get(self, request):
        bet_form = BetForm()
        BetOptionFormSet = formset_factory(BetOptionForm)
        formset = BetOptionFormSet()
        return render(request, 'gambling/create_bet.html', {'bet_form': bet_form, 'formset': formset})

    def post(self, request):
        bet_form = BetForm(request.POST)
        BetOptionFormSet = formset_factory(BetOptionForm)
        formset = BetOptionFormSet(request.POST)

        if bet_form.is_valid() and formset.is_valid():
            bet = bet_form.save(commit=False)
            bet.save()

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    option_name = form.cleaned_data['name']
                    BetOption.objects.create(bet=bet, name=option_name, tickets_sold=0)

            return redirect('admin_bet_list')

        return render(request, 'gambling/create_bet.html', {'bet_form': bet_form, 'formset': formset})
    
@method_decorator(admin_required, name='dispatch')
class ProfitTrackingView(View):
    def get(self, request):
        records = ProfitRecord.objects.all().order_by('date')
        return render(request, 'gambling/profit_tracking.html', {'records': records})