from django.db.models import Avg, Count, Sum
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .ml import prever_produtividade
from .models import (
    Equipamento,
    Equipe,
    Obra,
    RegistroProdutividade,
    RegistroTelemetria,
    Servico,
)
from .serializers import (
    EquipamentoSerializer,
    EquipeSerializer,
    ObraSerializer,
    PrevisaoSerializer,
    RegistroProdutividadeSerializer,
    RegistroTelemetriaSerializer,
    ServicoSerializer,
)


def dashboard(request):
    return render(request, "produtividade/dashboard.html")


class EquipeViewSet(viewsets.ModelViewSet):
    queryset = Equipe.objects.all().order_by("nome")
    serializer_class = EquipeSerializer


class ObraViewSet(viewsets.ModelViewSet):
    queryset = Obra.objects.all().order_by("nome")
    serializer_class = ObraSerializer


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all().order_by("nome")
    serializer_class = ServicoSerializer


class EquipamentoViewSet(viewsets.ModelViewSet):
    queryset = Equipamento.objects.all().order_by("identificador")
    serializer_class = EquipamentoSerializer


class RegistroProdutividadeViewSet(viewsets.ModelViewSet):
    queryset = RegistroProdutividade.objects.select_related(
        "obra",
        "equipe",
        "servico",
        "equipamento",
    ).order_by("-data", "-id")
    serializer_class = RegistroProdutividadeSerializer


class RegistroTelemetriaViewSet(viewsets.ModelViewSet):
    queryset = RegistroTelemetria.objects.select_related(
        "obra",
        "equipamento",
    ).order_by("-registrado_em")
    serializer_class = RegistroTelemetriaSerializer


@api_view(["POST"])
def prever(request):
    serializer = PrevisaoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dados = serializer.validated_data

    try:
        resultado = prever_produtividade(
            area=dados["area"],
            horas=dados["horas"],
            condicao=dados["condicao"],
            equipe=dados["equipe"],
            servico=dados["servico"],
            obra=dados["obra"],
            equipamento=dados.get("equipamento"),
            horas_equipamento=dados["horas_equipamento"],
            tempo_ocioso=dados["tempo_ocioso"],
        )
    except ValueError as erro:
        return Response(
            {"erro": str(erro)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(resultado)


@api_view(["GET"])
def resumo(request):
    indicadores = RegistroProdutividade.objects.aggregate(
        total_registros=Count("id"),
        area_total=Sum("area"),
        horas_totais=Sum("horas_trabalhadas"),
        produtividade_media=Avg("produtividade"),
        tempo_ocioso_total=Sum("tempo_ocioso"),
    )

    for campo, valor in indicadores.items():
        if campo == "total_registros":
            indicadores[campo] = valor
        else:
            indicadores[campo] = round(valor or 0, 2)

    indicadores["total_obras"] = Obra.objects.count()
    indicadores["total_equipes"] = Equipe.objects.count()
    indicadores["total_equipamentos"] = Equipamento.objects.count()

    return Response(indicadores)
