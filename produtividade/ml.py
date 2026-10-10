import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

from .models import RegistroProdutividade


def treinar_modelo():

    registros = RegistroProdutividade.objects.all()

    dados = list(
        registros.values(
            "area",
            "horas_trabalhadas",
            "condicao_trabalho",
            "produtividade",
            "equipe_id",
            "servico_id",
            "obra_id"
        )
    )

    df = pd.DataFrame(dados)

    if len(df) < 10:
        raise ValueError(
            "É necessário ter pelo menos 10 registros."
        )

    X = df[
        [
            "area",
            "horas_trabalhadas",
            "condicao_trabalho",
            "equipe_id",
            "servico_id",
            "obra_id"
        ]
    ]

    y = df["produtividade"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    modelo = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    modelo.fit(X_train, y_train)

    previsoes = modelo.predict(X_test)

    erro = mean_absolute_error(
        y_test,
        previsoes
    )

    return modelo, erro


def prever_produtividade(
    area,
    horas,
    condicao,
    equipe,
    servico,
    obra
):

    modelo, erro = treinar_modelo()

    entrada = pd.DataFrame([
        {
            "area": area,
            "horas_trabalhadas": horas,
            "condicao_trabalho": condicao,
            "equipe_id": equipe,
            "servico_id": servico,
            "obra_id": obra
        }
    ])

    previsao = modelo.predict(entrada)

    return {
        "produtividade_prevista": round(
            float(previsao[0]),
            2
        ),
        "erro_medio": round(
            float(erro),
            2
        )
    }