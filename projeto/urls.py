from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from produtividade.views import dashboard

urlpatterns = [

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "api/",
        include("produtividade.urls")
    ),

    # ---> ADICIONE ESTA LINHA ABAIXO <---
    path(
        "usuarios/",
        include("usuarios.urls")
    ),

    path(
        "", lambda request: 
        redirect("login")
    ),
]