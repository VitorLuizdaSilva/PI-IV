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
    help = "Cria uma base de demonstração com os equipamentos de EQ001 a EQ007 e serviços vinculados."

    def handle(self, *args, **options):
        gerador = random.Random(42)

        obra, _ = Obra.objects.get_or_create(
            nome="Obra de demonstração",
            defaults={"local": "Araras - SP"},
        )

        if RegistroProdutividade.objects.filter(obra=obra).exists():
            self.stdout.write(
                self.style.WARNING("Os dados de demonstração já foram criados.")
            )
            return

        # 1. Criação das Equipes e Serviços específicos e pareados
        equipe_terraplenagem, _ = Equipe.objects.get_or_create(
            nome="Equipe de terraplenagem",
            defaults={"quantidade_funcionarios": 6},
        )
        servico_terraplenagem, _ = Servico.objects.get_or_create(
            nome="Terraplenagem",
            defaults={"unidade": "m²"},
        )

        equipe_drenagem, _ = Equipe.objects.get_or_create(
            nome="Equipe de drenagem",
            defaults={"quantidade_funcionarios": 5},
        )
        servico_drenagem, _ = Servico.objects.get_or_create(
            nome="Drenagem",
            defaults={"unidade": "m"},
        )

        equipe_pavimentacao, _ = Equipe.objects.get_or_create(
            nome="Equipe de pavimentação",
            defaults={"quantidade_funcionarios": 8},
        )
        servico_pavimentacao, _ = Servico.objects.get_or_create(
            nome="Pavimentação",
            defaults={"unidade": "m²"},
        )

        pares_servico_equipe = [
            (servico_terraplenagem, equipe_terraplenagem),
            (servico_drenagem, equipe_drenagem),
            (servico_pavimentacao, equipe_pavimentacao),
        ]

        # 2. Lista exata com os 7 equipamentos da imagem
        dados_equipamentos = [
            {"identificador": "EQ001", "nome": "Retroescavadeira", "tipo": "Terraplenagem e Valas"},
            {"identificador": "EQ002", "nome": "Escavadeira hidráulica", "tipo": "Escavação pesada"},
            {"identificador": "EQ003", "nome": "Pá-carregadeira", "tipo": "Movimentação de carga"},
            {"identificador": "EQ004", "nome": "Motoniveladora", "tipo": "Nivelamento"},
            {"identificador": "EQ005", "nome": "Rolo compactador", "tipo": "Compactação"},
            {"identificador": "EQ006", "nome": "Caminhão basculante", "tipo": "Transporte"},
            {"identificador": "EQ007", "nome": "Caminhão basculante", "tipo": "Transporte"},
        ]

        lista_equipamentos = []
        for item in dados_equipamentos:
            equip, _ = Equipamento.objects.get_or_create(
                identificador=item["identificador"],
                defaults={
                    "nome": item["nome"],
                    "tipo": item["tipo"],
                },
            )
            lista_equipamentos.append(equip)

       
        registros = []
        for indice in range(72):
            horas = gerador.uniform(6, 10)
            area = gerador.uniform(70, 180)
            condicao = gerador.choice([1, 2, 3])
            horas_equipamento = gerador.uniform(4, horas)
            tempo_ocioso = gerador.uniform(0, 2)
            fator_condicao = {1: 0.8, 2: 1.0, 3: 1.15}[condicao]
            produtividade = (area / horas) * fator_condicao

            # Sorteia um dos 7 equipamentos de forma randômica a cada registro
            equipamento_escolhido = gerador.choice(lista_equipamentos)

            # Sorteia o par correto de serviço e equipe correspondente
            servico_escolhido, equipe_escolhida = gerador.choice(pares_servico_equipe)

            registros.append(
                RegistroProdutividade(
                    obra=obra,
                    equipe=equipe_escolhida,
                    servico=servico_escolhido,
                    equipamento=equipamento_escolhido,
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
        
        # Cria telemetria baseada no primeiro equipamento
        RegistroTelemetria.objects.create(
            equipamento=lista_equipamentos[0],
            obra=obra,
            horas_operacao=7.5,
            tempo_ocioso=0.8,
            producao=125,
        )

        self.stdout.write(
            self.style.SUCCESS("Base criada com sucesso!")
        )