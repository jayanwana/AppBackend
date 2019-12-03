# from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CashCall, Refill
from . import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.http import Http404, request
# Create your views here.
User = get_user_model()


class ContentMixin(generic.base.ContextMixin):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of the user balance
        user = self.request.user
        context['user_balance'] = user.user_balance.get().balance
        return context


class CashCallListView(LoginRequiredMixin, generic.ListView, ContentMixin):
    model = CashCall
    template_name = 'bank/cash_call_list.html'
    context_object_name = 'cash_call_list'

    def get_queryset(self):
        return CashCall.objects.filter(user=self.request.user)


class RefillListView(LoginRequiredMixin, generic.ListView, ContentMixin):
    model = Refill
    select_related = ('user', 'user_balance')
    context_object_name = 'refill_list'
    template_name = 'bank/refill_list.html'

    def get_queryset(self):
        return Refill.objects.filter(user=self.request.user)


class CreateRefillView(LoginRequiredMixin, generic.CreateView, ContentMixin):
    form_class = forms.RefillForm
    template_name = 'bank/refill_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        response = super().form_valid(form)
        messages.success(request=self.request, message='You Have deposited {}'.format(self.object.amount))
        return response


class CreateCashCallView(LoginRequiredMixin, generic.CreateView, ContentMixin):
    form_class = forms.CashCallForm
    template_name = 'bank/cash_call_form.html'

    def get_initial(self):
        self.initial.update({'user': self.request.user})
        return self.initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        response = super().form_valid(form)
        messages.success(request=self.request, message='You Have withdrawn {}'.format(self.object.amount))
        return response
