import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .models import RegistroProdutividade


CAMPOS_NUMERICOS = [
    "area",
    "horas_trabalhadas",
    "condicao_trabalho",
    "quantidade_funcionarios",
    "horas_equipamento",
    "tempo_ocioso",
]
CAMPOS_CATEGORICOS = ["servico_id", "obra_id", "equipamento_id"]
CAMPOS_MODELO = CAMPOS_NUMERICOS + CAMPOS_CATEGORICOS


def _carregar_dados():
    registros = RegistroProdutividade.objects.select_related("equipe").filter(
        produtividade__isnull=False
    )

    return pd.DataFrame(
        [
            {
                "area": registro.area,
                "horas_trabalhadas": registro.horas_trabalhadas,
                "condicao_trabalho": registro.condicao_trabalho,
                "quantidade_funcionarios": registro.equipe.quantidade_funcionarios,
                "horas_equipamento": registro.horas_equipamento,
                "tempo_ocioso": registro.tempo_ocioso,
                "servico_id": registro.servico_id,
                "obra_id": registro.obra_id,
                "equipamento_id": registro.equipamento_id or 0,
                "produtividade": registro.produtividade,
            }
            for registro in registros
        ]
    )


def treinar_modelo():
    dados = _carregar_dados()

    if len(dados) < 10:
        raise ValueError(
            "É necessário ter pelo menos 10 registros para gerar uma previsão."
        )

    x = dados[CAMPOS_MODELO]
    y = dados["produtividade"]
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
    )

    preparador = ColumnTransformer(
        transformers=[
            ("categorias", OneHotEncoder(handle_unknown="ignore"), CAMPOS_CATEGORICOS),
        ],
        remainder="passthrough",
    )
    modelo = Pipeline(
        steps=[
            ("preparacao", preparador),
            (
                "regressor",
                RandomForestRegressor(n_estimators=100, random_state=42),
            ),
        ]
    )
    modelo.fit(x_treino, y_treino)
    previsoes = modelo.predict(x_teste)
    erro = mean_absolute_error(y_teste, previsoes)

    return modelo, erro, len(dados)


def prever_produtividade(
    area,
    horas,
    condicao,
    equipe,
    servico,
    obra,
    equipamento=None,
    horas_equipamento=0,
    tempo_ocioso=0,
):
    modelo, erro, quantidade_registros = treinar_modelo()
    entrada = pd.DataFrame(
        [
            {
                "area": area,
                "horas_trabalhadas": horas,
                "condicao_trabalho": condicao,
                "quantidade_funcionarios": equipe.quantidade_funcionarios,
                "horas_equipamento": horas_equipamento,
                "tempo_ocioso": tempo_ocioso,
                "servico_id": servico.id,
                "obra_id": obra.id,
                "equipamento_id": equipamento.id if equipamento else 0,
            }
        ]
    )
    previsao = modelo.predict(entrada)

    return {
        "produtividade_prevista": round(float(previsao[0]), 2),
        "erro_medio": round(float(erro), 2),
        "registros_utilizados": quantidade_registros,
    }
