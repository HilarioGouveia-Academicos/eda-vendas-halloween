# Relatório Executivo de Auditoria e Descobertas: Festa em Cena

## 1. Contexto e Qualidade dos Dados

A Festa em Cena realizou um levantamento operacional de sua base de vendas sazonal de Halloween, totalizando 1.500 registros. A auditoria inicial revelou pontos críticos de higienização:

- **Dados Ausentes e Inconsistências:** Foram identificadas 18 categorias vazias, preenchidas com o valor sentinela `sem categoria`, e 19 pedidos com problemas numéricos graves (7 registros com quantidade negativa igual a -1 e 12 registros com preço unitário nulo). Tais ocorrências não foram corrigidas por estimativas ou médias arbitrárias para evitar distorções no faturamento contábil.
- **Higienização Textual:** Aplicou-se normalização por expressões regulares e limpeza de espaços/caixa baixa, corrigindo 55 categorias com pontuação excessiva (como exclamações) e padronizando 100% dos canais de venda em três frentes: Web (666 pedidos), Loja física (551 pedidos) e Mercado (283 pedidos).
- **Validação Temporal:** Das 1.500 ordens, 4 apresentaram textos corrompidos no campo de data e foram isoladas com segurança, permitindo o processamento cronológico de 1.496 pedidos válidos entre os anos de 2024 e 2025.

## 2. Refutação de Regra de Negócio

A gestão operava sob a premissa de que a ausência de preenchimento da data de entrega indicaria cancelamento da venda. A auditoria comprovou que a hipótese é falsa: dos 143 pedidos sem data de entrega registrada, 109 estavam de fato cancelados, porém 34 correspondiam a pedidos concluídos (como os pedidos IDs 1170, 990 e 740). Interpretar omissões de rastreio como cancelamentos provocaria perda indevida de dados e subnotificação de receitas operacionais.

## 3. Principais Descobertas e Recomendações

1. **Predominância Digital (Canal Web):** O canal Web liderou com 44,4% dos pedidos registrados (666), superando a Loja física (36,7%) e o Mercado (18,9%). O consumidor prioriza a antecedência e conveniência digital nas compras temáticas. *Limitação:* O indicador reflete contagem de pedidos, sem mensurar a margem líquida por canal ou custos de frete.
2. **Hiperconcentração Sazonal (Outubro):** Os meses de outubro de 2024 (393 pedidos) e outubro de 2025 (410 pedidos) concentraram 53,7% de todo o histórico transacional da loja. Houve uma expansão orgânica de 4,3% nas intenções de compra entre os dois anos. *Limitação:* A métrica não distingue rupturas de estoque no fim do mês e considera todos os status cadastrais, não representando o faturamento líquido efetivado.

Recomenda-se implementar validações nos formulários de entrada de dados (front-end)
