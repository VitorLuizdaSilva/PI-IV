
from django.db.models import Avg, Count, Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from datetime import date

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .ml import prever_produtividade
from .models import (
    Equipamento,
    Equipe,
    Obra,
    RegistroProdutividade,
    RegistroTelemetria,
    Servico,
    HistoricoPrevisao,
    FechamentoMensal,
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


@login_required
def dashboard(request):
    return render(request, "produtividade/dashboard.html")


class EquipeViewSet(viewsets.ModelViewSet):
    queryset = Equipe.objects.all().order_by("nome")
    serializer_class = EquipeSerializer
    permission_classes = [IsAuthenticated]


class ObraViewSet(viewsets.ModelViewSet):
    queryset = Obra.objects.all().order_by("nome")
    serializer_class = ObraSerializer
    permission_classes = [IsAuthenticated]


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all().order_by("nome")
    serializer_class = ServicoSerializer
    permission_classes = [IsAuthenticated]


class EquipamentoViewSet(viewsets.ModelViewSet):
    queryset = Equipamento.objects.all().order_by("identificador")
    serializer_class = EquipamentoSerializer
    permission_classes = [IsAuthenticated]


class RegistroProdutividadeViewSet(viewsets.ModelViewSet):
    queryset = RegistroProdutividade.objects.select_related(
        "obra",
        "equipe",
        "servico",
        "equipamento",
    ).order_by("-data", "-id")
    serializer_class = RegistroProdutividadeSerializer
    permission_classes = [IsAuthenticated]


class RegistroTelemetriaViewSet(viewsets.ModelViewSet):
    queryset = RegistroTelemetria.objects.select_related(
        "obra",
        "equipamento",
    ).order_by("-registrado_em")
    serializer_class = RegistroTelemetriaSerializer
    permission_classes = [IsAuthenticated]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
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

    
    produtividade = resultado.get("produtividade_prevista")
    erro_medio = resultado.get("erro_medio")

    if produtividade is None:
        return Response(
            {
                "erro": (
                    "A previsão foi calculada, mas a função "
                    "prever_produtividade não retornou "
                    "'produtividade_prevista'."
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    
    historico = HistoricoPrevisao.objects.create(
        obra=dados["obra"],
        equipe=dados["equipe"],
        servico=dados["servico"],
        equipamento=dados.get("equipamento"),
        area=dados["area"],
        horas=dados["horas"],
        condicao=dados["condicao"],
        horas_equipamento=dados["horas_equipamento"],
        tempo_ocioso=dados["tempo_ocioso"],
        produtividade_prevista=Decimal(str(produtividade)),
        erro_medio=(
            Decimal(str(erro_medio))
            if erro_medio is not None
            else None
        ),
    )

    return Response(
        {
            **resultado,
            "id": historico.id,
            "salvo": True,
            "criado_em": historico.criado_em,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumo(request):
    indicadores = RegistroProdutividade.objects.aggregate(
        total_registros=Count("id"),
        area_total=Sum("area"),
        horas_totais=Sum("horas_trabalhadas"),
        produtividade_media=Avg("produtividade"),
        tempo_ocioso_total=Sum("tempo_ocioso"),
    )

    for campo, valor in indicadores.items():
        if campo != "total_registros":
            indicadores[campo] = round(valor or 0, 2)

    indicadores["total_obras"] = Obra.objects.count()
    indicadores["total_equipes"] = Equipe.objects.count()
    indicadores["total_equipamentos"] = Equipamento.objects.count()

    return Response(indicadores)

def proximo_mes(mes):
   
    if mes.month == 12:
        return date(mes.year + 1, 1, 1)

    return date(mes.year, mes.month + 1, 1)


def calcular_totais_mensais(inicio, fim):
    
    registros = RegistroProdutividade.objects.filter(
        data__gte=inicio,
        data__lt=fim,
    )

    totais = registros.aggregate(
        total_registros=Count("id"),
        area_total=Sum("area"),
        horas_totais=Sum("horas_trabalhadas"),
        produtividade_media=Avg("produtividade"),
    )

    return {
        "total_registros": totais["total_registros"] or 0,
        "area_total": totais["area_total"] or Decimal("0"),
        "horas_totais": totais["horas_totais"] or Decimal("0"),
        "produtividade_media": (
            totais["produtividade_media"] or Decimal("0")
        ),
    }


def fechar_meses_anteriores():
    """
    Salva o resumo dos meses anteriores ao mês atual.
    Não exclui nem modifica os registros originais.
    """
    hoje = timezone.localdate()
    mes_atual = date(hoje.year, hoje.month, 1)

    primeira_data = (
        RegistroProdutividade.objects
        .order_by("data")
        .values_list("data", flat=True)
        .first()
    )

    if primeira_data is None:
        return

    mes = date(primeira_data.year, primeira_data.month, 1)

    while mes < mes_atual:
        fim = proximo_mes(mes)

        totais = calcular_totais_mensais(mes, fim)

        FechamentoMensal.objects.get_or_create(
            mes=mes,
            defaults=totais,
        )

        mes = fim


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def meses(request):
   
    fechar_meses_anteriores()

    hoje = timezone.localdate()
    inicio_atual = date(hoje.year, hoje.month, 1)
    fim_atual = proximo_mes(inicio_atual)

    fechamento_atual = calcular_totais_mensais(
        inicio_atual,
        fim_atual,
    )

    historico = list(
        FechamentoMensal.objects.all().values(
            "mes",
            "total_registros",
            "area_total",
            "horas_totais",
            "produtividade_media",
        )
    )

   
    historico.insert(
        0,
        {
            "mes": inicio_atual,
            **fechamento_atual,
            "atual": True,
        },
    )

    return Response(historico)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def detalhes_mes(request, ano, mes):
    """
    Retorna os indicadores, apontamentos reais e previsões de um mês.
    """
    if mes < 1 or mes > 12:
        return Response(
            {"erro": "Mês inválido."},
            status=400,
        )

    inicio = date(ano, mes, 1)
    fim = proximo_mes(inicio)

    totais = calcular_totais_mensais(inicio, fim)

    registros = list(
        RegistroProdutividade.objects
        .filter(data__gte=inicio, data__lt=fim)
        .select_related("obra", "servico", "equipe", "equipamento")
        .order_by("data", "id")
        .values(
            "id",
            "data",
            "obra__nome",
            "servico__nome",
            "equipe__nome",
            "equipamento__nome",
            "area",
            "horas_trabalhadas",
            "produtividade",
        )
    )

    previsoes = list(
        HistoricoPrevisao.objects
        .filter(criado_em__date__gte=inicio, criado_em__date__lt=fim)
        .select_related("obra", "servico", "equipe", "equipamento")
        .order_by("-criado_em")
        .values(
            "id",
            "criado_em",
            "obra__nome",
            "servico__nome",
            "equipe__nome",
            "equipamento__nome",
            "area",
            "horas",
            "produtividade_prevista",
            "erro_medio",
        )
    )

    return Response({
        "mes": inicio,
        "totais": totais,
        "registros": registros,
        "previsoes": previsoes,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def criar_apontamento(request):
    serializer = RegistroProdutividadeSerializer(data=request.data)

    if serializer.is_valid():
        registro = serializer.save()
        return Response(
            RegistroProdutividadeSerializer(registro).data,
            status=status.HTTP_201_CREATED,
        )
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )
