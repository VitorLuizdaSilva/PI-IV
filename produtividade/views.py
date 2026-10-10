
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .models import RegistroProdutividade
from .serializers import RegistroProdutividadeSerializer
from .ml import prever_produtividade


class RegistroProdutividadeViewSet(viewsets.ModelViewSet):

    queryset = RegistroProdutividade.objects.all()

    serializer_class = RegistroProdutividadeSerializer


@api_view(["POST"])
def prever(request):

    dados = request.data

    resultado = prever_produtividade(
        area=float(dados["area"]),
        horas=float(dados["horas"]),
        condicao=int(dados["condicao"]),
        equipe=int(dados["equipe"]),
        servico=int(dados["servico"]),
        obra=int(dados["obra"])
    )

    return Response(resultado)