from django.urls import path
from . import views

app_name = 'bank'

urlpatterns = [
    path('cash_call/', views.CashCallListView.as_view(), name='cash_call'),
    path('refill/', views.RefillListView.as_view(), name='refill'),
    path('create_cash_call/', views.CreateCashCallView.as_view(),
         name='create_cash_call'),
    path('create_refill/', views.CreateRefillView.as_view(),
         name='create_refill'),

]
