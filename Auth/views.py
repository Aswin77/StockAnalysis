from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm


# Create your views here.
def index(request):
    return render(request, 'base.html')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR Password is incorrect')

    context = {}
    return render(request, 'login.html', context)


def registerPage(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account created successfully!' + username)
            return redirect('login')
    context = {'form': form}
    return render(request, 'signup.html', context)


def aboutus(request):
    return render(request, 'about_us.html')


def contactus(request):
    return render(request, 'contact_us.html')


def logoutUser(request):

    logout(request)
    return redirect('login')
