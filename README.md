# Engenharia reversa exploratória do Copy Score da Hyperdash

Este repositório reúne uma análise inicial do `copyScoreV2` com base no JSON de exemplos fornecido. **O objetivo é identificar sinais e testar hipóteses; não afirmar uma fórmula exata sem evidência.**

## O que já sabemos

- A página da Hyperdash apresenta o Copy Score numa escala de 0 a 100. As páginas oficiais consultadas explicam ranking, filtros e copy trading, mas não publicam a equação nem os pesos: [Copy Trade](https://docs.hyperdash.com/copy-trade) e [Trader Explore](https://docs.hyperdash.com/wallet-explore).
- As notas da API no repositório público do projeto irmão documentam que o campo exibido é `copyScoreV2` e que `copyScore` é a versão legada: [hyperdash_api.md](https://github.com/ronaldoaf/Hyperliquid_CopyTrade/blob/main/docs/hyperdash_api.md). Elas também registram que `sortBy: copyScore` parece ordenar pela versão legada; ao coletar mais exemplos, use o valor explícito de `copyScoreV2`, não a ordem retornada.
- Um artigo editorial da Hyperdash cita consistência, drawdown, frequência de trades e PnL como dimensões do score, sem revelar pesos ou equação. Isso é uma hipótese para orientar os testes, não uma fórmula confirmada: [artigo](https://hyperdash.com/learn/best-tools-trading-hyperliquid).
- No arquivo analisado há 2.000 traders, mas `copyScoreV2` só está preenchido em 725. Entre esses 725, há 173 scores iguais a zero e 552 positivos. **Nulo não foi tratado como zero.**
- `copyScoreV2` não é uma simples cópia/conversão do score legado: há 125 carteiras com `copyScore = 0` e V2 positivo, e 78 com score legado positivo e V2 igual a zero.
- Os scores zero aparecem com frequência muito maior na categoria `algo` (63 de 77; 81,8%) do que em `swing` (37 de 375; 9,9%). Isso sugere um fator de estilo/copiabilidade ou uma regra de elegibilidade, mas não prova causalidade.
- Entre scores V2 positivos, as associações monotônicas mais fortes no snapshot são o score legado (Spearman ρ=0,547), `lastTradeAt` (0,390), `trades30d` (0,343), `winrate` (0,334), `sharpe180d` (0,333), `sharpe365d` (0,331) e `drawdown365d` (-0,198). PnL bruto tem associação bem mais fraca (ρ=0,135). São correlações, não pesos da fórmula.

O relatório com tabelas, contagens e limitações está em [`docs/analise_inicial.md`](docs/analise_inicial.md).

## Reproduzir a análise

O JSON original não foi copiado para o repositório. Rode o script apontando para o arquivo anexado/local:

```bash
python scripts/analyze_copy_score.py /caminho/para/hyperdash_traders.json
```

Para salvar a saída em Markdown:

```bash
python scripts/analyze_copy_score.py /caminho/para/hyperdash_traders.json \
  --output docs/relatorio_gerado.md
```

O script usa somente a biblioteca padrão do Python e calcula estatísticas, Spearman com empates e associações por estilo. Ele foi intencionalmente implementado como ferramenta de análise — **não calcula um score substituto**.

## Próximos passos para aproximar a fórmula

1. Coletar vários snapshots dos mesmos endereços, com timestamp da coleta e `copyScoreV2` não nulo.
2. Registrar a curva de equity/portfolio graph, trades fechados e PnL por janela; o resumo atual não contém todas as variáveis que podem alimentar o score.
3. Comparar traders pareados por estilo, idade da conta e volume, e medir mudanças do score ao longo do tempo.
4. Separar explicitamente score `null`, score `0` e traders inelegíveis; validar qualquer modelo em endereços e datas não usados para ajustar a hipótese.

Sem esses dados, o resultado responsável é uma lista de fatores candidatos e limitações — não uma equação exata.
