from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Equipamento, Equipe, Obra, RegistroProdutividade, Servico


class ProdutividadeAPITests(APITestCase):
    def setUp(self):
        self.obra = Obra.objects.create(nome="Obra teste", local="Araras")
        self.equipe = Equipe.objects.create(
            nome="Equipe A",
            quantidade_funcionarios=5,
        )
        self.servico = Servico.objects.create(nome="Terraplenagem", unidade="m²")
        self.equipamento = Equipamento.objects.create(
            nome="Escavadeira",
            identificador="EQ-001",
            tipo="Máquina pesada",
        )

    def criar_registros(self, quantidade=10):
        for indice in range(quantidade):
            RegistroProdutividade.objects.create(
                obra=self.obra,
                equipe=self.equipe,
                servico=self.servico,
                equipamento=self.equipamento,
                area=80 + indice * 5,
                horas_trabalhadas=8,
                horas_equipamento=6,
                tempo_ocioso=1,
                condicao_trabalho=(indice % 3) + 1,
                produtividade=10 + indice * 0.5,
            )

    def test_calcula_produtividade_quando_valor_nao_e_informado(self):
        registro = RegistroProdutividade.objects.create(
            obra=self.obra,
            equipe=self.equipe,
            servico=self.servico,
            area=120,
            horas_trabalhadas=8,
            condicao_trabalho=3,
        )

        self.assertEqual(registro.produtividade, 15)

    def test_previsao_exige_dez_registros(self):
        resposta = self.client.post(
            reverse("prever"),
            {
                "area": 100,
                "horas": 8,
                "condicao": 2,
                "equipe": self.equipe.id,
                "servico": self.servico.id,
                "obra": self.obra.id,
            },
            format="json",
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retorna_previsao_com_base_suficiente(self):
        self.criar_registros(12)
        resposta = self.client.post(
            reverse("prever"),
            {
                "area": 130,
                "horas": 8,
                "condicao": 3,
                "equipe": self.equipe.id,
                "servico": self.servico.id,
                "obra": self.obra.id,
                "equipamento": self.equipamento.id,
                "horas_equipamento": 6,
                "tempo_ocioso": 1,
            },
            format="json",
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertIn("produtividade_prevista", resposta.data)
        self.assertEqual(resposta.data["registros_utilizados"], 12)

    def test_resumo_retorna_indicadores(self):
        self.criar_registros(2)
        resposta = self.client.get(reverse("resumo"))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data["total_registros"], 2)
        self.assertEqual(resposta.data["total_obras"], 1)

    def test_dashboard_esta_disponivel(self):
        resposta = self.client.get(reverse("dashboard"))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertContains(resposta, "Painel de produtividade")
