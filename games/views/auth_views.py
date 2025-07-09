from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from ..handlers import ResponseHelper


def registrar_usuario(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("game_search")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def home(request):
    return ResponseHelper.simple_render(request, "home.html")


@login_required
def graphs_home(request):
    return ResponseHelper.simple_render(request, "graphs_home.html")
