"""
funcoes.py - Módulo de Tratamento, Auditoria e Agregação de Dados
Dataset: Festa em Cena (Halloween)
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Tuple
import pandas as pd


def carregar_dados(caminho_csv: str) -> pd.DataFrame:
    """Lê o arquivo CSV de vendas usando pd.read_csv()."""
    return pd.read_csv(caminho_csv)


def tratar_e_validar_dados_ausentes(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Valida integridade numérica e preenche categorias vazias."""
    df_tratado = df.copy()

    # Preenchimento de categorias vazias
    cat_vazias_qtd = int(df_tratado["categoria"].isna().sum())
    df_tratado["categoria"] = df_tratado["categoria"].fillna("sem categoria")

    # Quantidade: inteiro maior que zero
    cond_qtd_invalida = (
        df_tratado["quantidade"].isna()
        | (df_tratado["quantidade"] <= 0)
        | (df_tratado["quantidade"] % 1 != 0)
    )
    problemas_qtd = int(cond_qtd_invalida.sum())

    # Preço unitário: preenchido e >= 0
    cond_preco_invalido = (
        df_tratado["preco_unitario"].isna() | (df_tratado["preco_unitario"] < 0)
    )
    problemas_preco = int(cond_preco_invalido.sum())

    # Pedidos com problema numérico único
    df_tratado["problema_numerico"] = cond_qtd_invalida | cond_preco_invalido
    total_afetados_num = int(df_tratado["problema_numerico"].sum())

    metricas = {
        "categorias_vazias_preenchidas": cat_vazias_qtd,
        "problemas_quantidade": problemas_qtd,
        "problemas_preco_unitario": problemas_preco,
        "total_pedidos_com_problema_numerico": total_afetados_num,
    }
    return df_tratado, metricas


def padronizar_texto_e_regex(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Aplica regex e normalização em categoria e canal_venda."""
    df_padrao = df.copy()

    def limpar_categoria(texto: Any) -> str:
        if not isinstance(texto, str) or texto.strip() == "":
            return "sem categoria"
        limpo = re.sub(r"[^a-zA-Z\s]", "", texto)
        limpo = limpo.strip().lower()
        return limpo if limpo != "" else "sem categoria"

    cat_com_pontuacao = 0
    for val in df["categoria"].dropna():
        if re.search(r"[^a-zA-Z\s]", str(val)):
            cat_com_pontuacao += 1

    df_padrao["categoria_limpa"] = df_padrao["categoria"].apply(
        limpar_categoria
    )

    mapa_canais = {
        "web": "Web",
        "loja física": "Loja física",
        "loja fisica": "Loja física",
        "mercado": "Mercado",
    }

    def ajustar_canal(canal: Any) -> str:
        if pd.isna(canal):
            return "Desconhecido"
        return mapa_canais.get(str(canal).strip().lower(), "Desconhecido")

    df_padrao["canal_venda_padrao"] = df_padrao["canal_venda"].apply(
        ajustar_canal
    )

    metricas = {"categorias_com_pontuacao_alteradas": cat_com_pontuacao}
    return df_padrao, metricas


def validar_regra_entrega_cancelamento(df: pd.DataFrame) -> Dict[str, Any]:
    """Testa se ausência de data_entrega equivale a status Cancelado."""
    sem_entrega = df[df["data_entrega"].isna()]
    sem_entrega_canc = sem_entrega[sem_entrega["status_pedido"] == "Cancelado"]
    sem_entrega_outros = sem_entrega[
        sem_entrega["status_pedido"] != "Cancelado"
    ]

    contraexemplos = sem_entrega_outros[
        ["pedido_id", "status_pedido", "canal_venda"]
    ].head(3).to_dict(orient="records")

    return {
        "total_sem_entrega": len(sem_entrega),
        "sem_entrega_e_cancelados": len(sem_entrega_canc),
        "sem_entrega_outros_status": len(sem_entrega_outros),
        "exemplos_contraexemplos": contraexemplos,
        "hipotese_confirmada": len(sem_entrega_outros) == 0,
    }


def formatar_datas_venda(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Converte datas via strptime e formata no padrão brasileiro."""
    df_tempo = df.copy()

    anos: List[Any] = []
    meses: List[Any] = []
    dias: List[Any] = []
    horas: List[Any] = []
    datas_ptbr: List[Any] = []
    ano_mes: List[Any] = []
    datas_invalidas_flag: List[bool] = []

    total_invalidas = 0

    for val in df_tempo["data_venda"]:
        if pd.isna(val):
            total_invalidas += 1
            datas_invalidas_flag.append(True)
            for lst in (anos, meses, dias, horas, datas_ptbr, ano_mes):
                lst.append(None)
            continue

        try:
            dt_obj = datetime.strptime(str(val).strip(), "%Y-%m-%d %H:%M:%S")
            anos.append(dt_obj.year)
            meses.append(dt_obj.month)
            dias.append(dt_obj.day)
            horas.append(dt_obj.hour)
            datas_ptbr.append(dt_obj.strftime("%d/%m/%Y"))
            ano_mes.append(dt_obj.strftime("%Y-%m"))
            datas_invalidas_flag.append(False)
        except (ValueError, TypeError):
            total_invalidas += 1
            datas_invalidas_flag.append(True)
            for lst in (anos, meses, dias, horas, datas_ptbr, ano_mes):
                lst.append(None)

    df_tempo["ano"] = anos
    df_tempo["mes"] = meses
    df_tempo["dia"] = dias
    df_tempo["hora"] = horas
    df_tempo["data_venda_br"] = datas_ptbr
    df_tempo["ano_mes"] = ano_mes
    df_tempo["data_venda_invalida"] = datas_invalidas_flag

    metricas = {"datas_invalidas_ou_vazias": total_invalidas}
    return df_tempo, metricas


def executar_pipeline_completo(
    caminho_csv: str = "halloween_vendas.csv",
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Função utilitária que roda o pipeline sequencial e retorna o DataFrame final e todas as métricas."""
    df_raw = carregar_dados(caminho_csv)
    df_ausentes, met_ausentes = tratar_e_validar_dados_ausentes(df_raw)
    df_regex, met_regex = padronizar_texto_e_regex(df_ausentes)
    met_entrega = validar_regra_entrega_cancelamento(df_regex)
    df_final, met_tempo = formatar_datas_venda(df_regex)

    metricas_consolidadas = {
        "ausentes": met_ausentes,
        "regex": met_regex,
        "entrega": met_entrega,
        "tempo": met_tempo,
        "total_linhas": len(df_final),
        "total_cancelados": int((df_final["status_pedido"] == "Cancelado").sum()),
    }
    return df_final, metricas_consolidadas