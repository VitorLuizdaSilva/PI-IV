from django.core.validators import MinValueValidator
from django.db import models


class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    quantidade_funcionarios = models.PositiveIntegerField()

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


class Equipamento(models.Model):
    nome = models.CharField(max_length=100)
    identificador = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.identificador} - {self.nome}"


class RegistroProdutividade(models.Model):
    class CondicaoTrabalho(models.IntegerChoices):
        RUIM = 1, "Ruim"
        REGULAR = 2, "Regular"
        BOA = 3, "Boa"

    class Origem(models.TextChoices):
        MANUAL = "manual", "Apontamento manual"
        IOT = "iot", "Dispositivo IoT"

    obra = models.ForeignKey(Obra, on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    area = models.FloatField(validators=[MinValueValidator(0.01)])
    horas_trabalhadas = models.FloatField(validators=[MinValueValidator(0.01)])
    horas_equipamento = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    tempo_ocioso = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    condicao_trabalho = models.IntegerField(choices=CondicaoTrabalho.choices)
    produtividade = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    origem = models.CharField(
        max_length=10,
        choices=Origem.choices,
        default=Origem.MANUAL,
    )
    data = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.produtividade is None and self.horas_trabalhadas:
            self.produtividade = self.area / self.horas_trabalhadas
        super().save(*args, **kwargs)

    def __str__(self):
        produtividade = self.produtividade or 0
        return f"{self.servico} - {produtividade:.2f}"


class RegistroTelemetria(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE)
    horas_operacao = models.FloatField(validators=[MinValueValidator(0)])
    tempo_ocioso = models.FloatField(validators=[MinValueValidator(0)])
    producao = models.FloatField(validators=[MinValueValidator(0)])
    registrado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipamento} - {self.registrado_em:%d/%m/%Y %H:%M}"



class HistoricoPrevisao(models.Model):
    """
    Guarda cada previsão calculada pelo modelo de Machine Learning.
    """

    criado_em = models.DateTimeField(auto_now_add=True)

    obra = models.ForeignKey(
        "produtividade.Obra",
        on_delete=models.PROTECT,
        related_name="previsoes",
    )

    equipe = models.ForeignKey(
        "produtividade.Equipe",
        on_delete=models.PROTECT,
        related_name="previsoes",
    )

    servico = models.ForeignKey(
        "produtividade.Servico",
        on_delete=models.PROTECT,
        related_name="previsoes",
    )

    equipamento = models.ForeignKey(
        "produtividade.Equipamento",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="previsoes",
    )

    area = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    horas = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    condicao = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )


    horas_equipamento = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )

    tempo_ocioso = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )

    produtividade_prevista = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )

    erro_medio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Previsão {self.pk} - {self.criado_em:%m/%Y}"


class FechamentoMensal(models.Model):
    """
    Salva uma fotografia dos indicadores de produção de cada mês.
    """

    mes = models.DateField(
        unique=True,
        help_text="Primeiro dia do mês de referência.",
    )

    total_registros = models.PositiveIntegerField(default=0)
    area_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    horas_totais = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    produtividade_media = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=0,
    )

    fechado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mes.strftime("%m/%Y")

    class Meta:
        ordering = ["-mes"]
