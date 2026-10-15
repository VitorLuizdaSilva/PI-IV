
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required


def cadastro(request):
    if request.method == "POST":
        formulario = UserCreationForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            return redirect("dashboard")
    else:
        formulario = UserCreationForm()

    return render(
        request,
        "usuarios/cadastro.html",
        {"formulario": formulario}
    )


def entrar(request):
    if request.method == "POST":
        formulario = AuthenticationForm(
            request,
            data=request.POST
        )

        if formulario.is_valid():
            usuario = formulario.get_user()
            login(request, usuario)
            return redirect("dashboard")
    else:
        formulario = AuthenticationForm()

    return render(
        request,
        "usuarios/login.html",
        {"formulario": formulario}
    )


def sair(request):
    if request.method == "POST":
        logout(request)

    return redirect("login")
