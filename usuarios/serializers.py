from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UsuarioSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    grupo = serializers.ChoiceField(
        choices=["Gerente", "Funcionario"],
        write_only=True,
        default="Funcionario"
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "grupo",
        ]

    def validate_grupo(self, value):

        usuario = self.context["request"].user

        if value == "Gerente" and not usuario.is_superuser:
            raise serializers.ValidationError(
                "Somente o superusuário pode cadastrar gerentes."
            )

        return value

    def create(self, validated_data):

        grupo_nome = validated_data.pop("grupo")

        senha = validated_data.pop("password")

        usuario = User.objects.create_user(
            password=senha,
            **validated_data
        )

        grupo = Group.objects.get(name=grupo_nome)

        usuario.groups.add(grupo)

        return usuario