import random

from django.core.management.base import BaseCommand

from produtividade.models import (
    Equipamento,
    Equipe,
    Obra,
    RegistroProdutividade,
    RegistroTelemetria,
    Servico,
)


class Command(BaseCommand):
    help = "Cria uma base simples de demonstração para a API e o modelo preditivo."

    def handle(self, *args, **options):
        gerador = random.Random(42)
        obra, _ = Obra.objects.get_or_create(
            nome="Obra de demonstração",
            defaults={"local": "Araras - SP"},
        )
        equipe, _ = Equipe.objects.get_or_create(
            nome="Equipe de terraplenagem",
            defaults={"quantidade_funcionarios": 6},
        )
        servico, _ = Servico.objects.get_or_create(
            nome="Terraplenagem",
            defaults={"unidade": "m²"},
        )
        equipamento, _ = Equipamento.objects.get_or_create(
            identificador="ESC-001",
            defaults={
                "nome": "Escavadeira de demonstração",
                "tipo": "Escavadeira hidráulica",
            },
        )

        if RegistroProdutividade.objects.filter(obra=obra).exists():
            self.stdout.write(
                self.style.WARNING("Os dados de demonstração já foram criados.")
            )
            return

        registros = []
        for indice in range(20):
            horas = gerador.uniform(6, 10)
            area = gerador.uniform(70, 180)
            condicao = gerador.choice([1, 2, 3])
            horas_equipamento = gerador.uniform(4, horas)
            tempo_ocioso = gerador.uniform(0, 2)
            fator_condicao = {1: 0.8, 2: 1.0, 3: 1.15}[condicao]
            produtividade = (area / horas) * fator_condicao

            registros.append(
                RegistroProdutividade(
                    obra=obra,
                    equipe=equipe,
                    servico=servico,
                    equipamento=equipamento,
                    area=round(area, 2),
                    horas_trabalhadas=round(horas, 2),
                    horas_equipamento=round(horas_equipamento, 2),
                    tempo_ocioso=round(tempo_ocioso, 2),
                    condicao_trabalho=condicao,
                    produtividade=round(produtividade, 2),
                    origem=(
                        RegistroProdutividade.Origem.IOT
                        if indice % 2
                        else RegistroProdutividade.Origem.MANUAL
                    ),
                )
            )

        RegistroProdutividade.objects.bulk_create(registros)
        RegistroTelemetria.objects.create(
            equipamento=equipamento,
            obra=obra,
            horas_operacao=7.5,
            tempo_ocioso=0.8,
            producao=125,
        )

        self.stdout.write(
            self.style.SUCCESS("Base de demonstração criada com 20 registros.")
        )
