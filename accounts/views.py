# from django.shortcuts import render
from . import forms
from .models import UserBalance
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
# Create accounts your views here.
User = get_user_model()


class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        response = super().form_valid(form)
        form.save()
        balance = UserBalance.objects.create(user=self.object)
        balance.save()
        return response


class CreateAddressView(LoginRequiredMixin, CreateView):
    user = User
    form_class = forms.UserAddress
    template_name = 'accounts/address_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        response = super().form_valid(form)
        form.save()
        return response
