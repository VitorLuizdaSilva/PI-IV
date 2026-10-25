from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views
from django.http import HttpResponse
from .views import (
    EquipamentoViewSet,
    EquipeViewSet,
    ObraViewSet,
    RegistroProdutividadeViewSet,
    RegistroTelemetriaViewSet,
    ServicoViewSet,
    prever,
    resumo,
    criar_apontamento,
)

router = DefaultRouter()
router.register("equipes", EquipeViewSet)
router.register("obras", ObraViewSet)
router.register("servicos", ServicoViewSet)
router.register("equipamentos", EquipamentoViewSet)
router.register("registros", RegistroProdutividadeViewSet)
router.register("telemetria", RegistroTelemetriaViewSet)

urlpatterns = [
    path("teste/", lambda request: HttpResponse("Servidor OK")),
    path("meses/", views.meses, name="meses"),
    path("meses/<int:ano>/<int:mes>/",views.detalhes_mes,name="detalhes_mes",),
    path("", include(router.urls)),
    path("prever/", prever, name="prever"),
    path("resumo/", resumo, name="resumo"),
    path("apontamentos/criar/",criar_apontamento,name="criar_apontamento",),
]
