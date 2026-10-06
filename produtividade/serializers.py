from rest_framework import serializers
from .models import RegistroProdutividade


class RegistroProdutividadeSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = RegistroProdutividade
        fields = "__all__"