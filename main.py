"""
main.py - Ponto de Entrada para Relatório no Terminal
"""

import sys
from funcoes import (
    carregar_dados,
    tratar_e_validar_dados_ausentes,
    padronizar_texto_e_regex,
    validar_regra_entrega_cancelamento,
    formatar_datas_venda,
)


def exibir_relatorio(
    df: object,
    metricas_ausentes: dict,
    metricas_regex: dict,
    metricas_entrega: dict,
    metricas_tempo: dict,
) -> None:
    total_linhas = len(df)
    total_cancelados = int((df["status_pedido"] == "Cancelado").sum())

    print("=" * 65)
    print("RELATÓRIO DE STATUS E AUDITORIA DA BASE - FESTA EM CENA")
    print("=" * 65)
    print(f"Total de linhas lidas: {total_linhas}")
    print(
        f"Categorias vazias preenchidas: {metricas_ausentes['categorias_vazias_preenchidas']}"
    )
    print(
        f"Categorias com pontuação corrigidas: {metricas_regex['categorias_com_pontuacao_alteradas']}"
    )
    print(
        f"Total de pedidos com problemas numéricos: {metricas_ausentes['total_pedidos_com_problema_numerico']}"
    )
    print(
        f"  - Quantidades inválidas (<= 0): {metricas_ausentes['problemas_quantidade']}"
    )
    print(
        f"  - Preços ausentes/negativos: {metricas_ausentes['problemas_preco_unitario']}"
    )
    print(
        f"Datas de venda inválidas: {metricas_tempo['datas_invalidas_ou_vazias']}"
    )
    print(f"Total de pedidos cancelados: {total_cancelados}")
    print("-" * 65)
    print("VALIDAÇÃO DA REGRA DE NEGÓCIO: DATA DE ENTREGA")
    print(
        f"Pedidos sem entrega e Cancelados: {metricas_entrega['sem_entrega_e_cancelados']}"
    )
    print(
        f"Pedidos sem entrega e Outros Status: {metricas_entrega['sem_entrega_outros_status']}"
    )
    if not metricas_entrega["hipotese_confirmada"]:
        print("--> HIPÓTESE FALSA: Existem pedidos sem entrega não cancelados.")
        for ex in metricas_entrega["exemplos_contraexemplos"]:
            print(
                f"    * ID: {ex['pedido_id']} | Status: {ex['status_pedido']} | Canal: {ex['canal_venda']}"
            )
    print("-" * 65)

    # Contagem por Canal
    df_canal = df[df["canal_venda_padrao"] != "Desconhecido"]
    contagem_canal = df_canal["canal_venda_padrao"].value_counts()
    print("CONTAGEM DE PEDIDOS POR CANAL DE VENDA")
    for canal, qtd in contagem_canal.items():
        print(f"  * {canal:<15}: {qtd:>4} pedidos")
    print("-" * 65)

    # Contagem por Ano-Mês
    df_tempo = df[~df["data_venda_invalida"]]
    contagem_tempo = df_tempo["ano_mes"].value_counts().sort_index()
    print("CONTAGEM DE PEDIDOS POR ANO-MÊS")
    for anomes, qtd in contagem_tempo.items():
        print(f"  * {anomes}: {qtd:>4} pedidos")
    print("=" * 65)


def main():
    caminho = "halloween_vendas.csv"
    try:
        df_raw = carregar_dados(caminho)
        df_ausentes, met_ausentes = tratar_e_validar_dados_ausentes(df_raw)
        df_regex, met_regex = padronizar_texto_e_regex(df_ausentes)
        met_entrega = validar_regra_entrega_cancelamento(df_regex)
        df_final, met_tempo = formatar_datas_venda(df_regex)

        exibir_relatorio(
            df_final, met_ausentes, met_regex, met_entrega, met_tempo
        )
    except FileNotFoundError:
        print(f"Arquivo '{caminho}' não encontrado no diretório atual.")
        sys.exit(1)


if __name__ == "__main__":
    main()