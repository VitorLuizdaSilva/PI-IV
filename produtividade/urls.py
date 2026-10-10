from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    RegistroProdutividadeViewSet,
    prever
)


router = DefaultRouter()

router.register(
    "registros",
    RegistroProdutividadeViewSet
)


urlpatterns = [

    path(
        "",
        include(router.urls)
    ),

    path(
        "prever/",
        prever
    ),
]