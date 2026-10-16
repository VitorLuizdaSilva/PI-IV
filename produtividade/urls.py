from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EquipamentoViewSet,
    EquipeViewSet,
    ObraViewSet,
    RegistroProdutividadeViewSet,
    RegistroTelemetriaViewSet,
    ServicoViewSet,
    prever,
    resumo,
)

router = DefaultRouter()
router.register("equipes", EquipeViewSet)
router.register("obras", ObraViewSet)
router.register("servicos", ServicoViewSet)
router.register("equipamentos", EquipamentoViewSet)
router.register("registros", RegistroProdutividadeViewSet)
router.register("telemetria", RegistroTelemetriaViewSet)

urlpatterns = [
    path("dashboard/", include(router.urls)),
    path("prever/", prever, name="prever"),
    path("resumo/", resumo, name="resumo"),
]
