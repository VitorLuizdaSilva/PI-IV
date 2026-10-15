from rest_framework import serializers

from .models import (
    Equipamento,
    Equipe,
    Obra,
    RegistroProdutividade,
    RegistroTelemetria,
    Servico,
)


class EquipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipe
        fields = "__all__"


class ObraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obra
        fields = "__all__"


class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = "__all__"


class EquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipamento
        fields = "__all__"


class RegistroProdutividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroProdutividade
        fields = "__all__"


class RegistroTelemetriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroTelemetria
        fields = "__all__"


class PrevisaoSerializer(serializers.Serializer):
    area = serializers.FloatField(min_value=0.01)
    horas = serializers.FloatField(min_value=0.01)
    condicao = serializers.ChoiceField(choices=(1, 2, 3))
    equipe = serializers.PrimaryKeyRelatedField(queryset=Equipe.objects.all())
    servico = serializers.PrimaryKeyRelatedField(queryset=Servico.objects.all())
    obra = serializers.PrimaryKeyRelatedField(queryset=Obra.objects.all())
    equipamento = serializers.PrimaryKeyRelatedField(
        queryset=Equipamento.objects.all(),
        required=False,
        allow_null=True,
    )
    horas_equipamento = serializers.FloatField(min_value=0, default=0)
    tempo_ocioso = serializers.FloatField(min_value=0, default=0)
