from django.db import models

class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    quantidade_funcionarios = models.IntegerField()

    def __str__(self):
        return self.nome


class Obra(models.Model):
    nome = models.CharField(max_length=150)
    local = models.CharField(max_length=150)

    def __str__(self):
        return self.nome


class Servico(models.Model):
    nome = models.CharField(max_length=150)
    unidade = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class RegistroProdutividade(models.Model):

    obra = models.ForeignKey(
        Obra,
        on_delete=models.CASCADE
    )

    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.CASCADE
    )

    servico = models.ForeignKey(
        Servico,
        on_delete=models.CASCADE
    )

    area = models.FloatField()

    horas_trabalhadas = models.FloatField()

    condicao_trabalho = models.IntegerField(
        choices=[
            (1, "Ruim"),
            (2, "Regular"),
            (3, "Boa"),
        ]
    )

    produtividade = models.FloatField()

    data = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.servico} - {self.produtividade}"
