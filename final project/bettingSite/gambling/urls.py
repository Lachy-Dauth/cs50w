from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('', BetsListView.as_view(), name='bets_list'),
    path('bets/<int:bet_id>/', BetDetailView.as_view(), name='bet_detail'),
    path('api/bets/', BetsApiView.as_view(), name='bets_api'),
    path('api/bet-option/', BetsOptionApiView.as_view(), name='options_api'),
    path('gambling/admin/bets/', AdminBetListView.as_view(), name='admin_bet_list'),
    path('gambling/admin/bets/<int:bet_id>/', AdminBetManagementView.as_view(), name='admin_bet_management'),
    path('gambling/admin/create-bet/', CreateBetView.as_view(), name='create_bet'),
    path('profit-tracking/', ProfitTrackingView.as_view(), name='profit_tracking'),
]