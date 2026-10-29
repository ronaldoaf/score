# Análise exploratória do Copy Score Hyperdash

Arquivo analisado: `hyperdash_traders.json` (anexo fornecido; não incluído no repositório)

> Esta análise mede associações nos exemplos fornecidos. Ela não recupera nem confirma a fórmula proprietária da Hyperdash.

## Cobertura e distribuição

| Medida | Valor |
|---|---:|
| Traders no arquivo | 2,000 |
| `copyScore` (legado) não nulo | 2,000 |
| `copyScore` (legado) igual a zero | 1,267 |
| `copyScoreV2` não nulo | 725 |
| `copyScoreV2` nulo | 1,275 |
| `copyScoreV2` exatamente zero | 173 |
| `copyScoreV2` positivo | 552 |
| Faixa de `copyScoreV2` não nulo | 0.00–95.83 |
| Mediana de `copyScoreV2` (inclui zeros) | 74.43 |
| Mediana entre `copyScoreV2` positivos | 77.21 |

**Importante:** `null` e `0` são estados diferentes neste arquivo. O relatório não converte valores ausentes em zero.

## `copyScoreV2` por estilo (`tag`)

| Estilo | n | Score zero | % zero | Mediana | Média |
|---|---:|---:|---:|---:|---:|
| algo | 77 | 63 | 81.8% | 0.00 | 13.59 |
| intraday | 87 | 24 | 27.6% | 58.91 | 45.84 |
| position | 55 | 4 | 7.3% | 78.17 | 69.80 |
| scalp | 46 | 20 | 43.5% | 25.17 | 28.21 |
| sem tag | 85 | 25 | 29.4% | 50.71 | 44.98 |
| swing | 375 | 37 | 9.9% | 77.44 | 66.86 |

## Associação com métricas numéricas

Spearman (ρ), com ranks médios para empates e remoção par a par de nulos. A primeira tabela inclui scores zero; a segunda condiciona a `copyScoreV2 > 0`.

### Todos os `copyScoreV2` não nulos

| Campo | n pareado | ρ de Spearman |
|---|---:|---:|
| `copyScore` | 725 | +0.531 |
| `totalVolume` | 725 | -0.211 |
| `drawdown7d` | 725 | +0.193 |
| `winrate` | 725 | +0.190 |
| `perpsEquity` | 725 | +0.174 |
| `sharpe90d` | 725 | +0.145 |
| `drawdown30d` | 725 | +0.133 |
| `totalShortTrades` | 725 | -0.131 |
| `drawdown` | 725 | +0.128 |
| `totalLosingTrades` | 725 | -0.117 |
| `sharpe180d` | 558 | +0.109 |
| `sortino180d` | 558 | +0.102 |
| `sortino90d` | 725 | +0.093 |
| `totalTrades` | 725 | -0.084 |
| `totalLongTrades` | 725 | -0.077 |
| `trades7d` | 725 | -0.069 |
| `winrate180d` | 708 | +0.062 |
| `sharpe` | 587 | -0.062 |
| `totalWinningTrades` | 725 | -0.062 |
| `winrate365d` | 716 | +0.059 |
| `lastTradeAt` | 719 | +0.056 |
| `sharpe30d` | 587 | -0.055 |
| `sortino` | 587 | -0.055 |
| `sortino30d` | 587 | -0.055 |
| `winrate30d` | 549 | +0.053 |
| `winrate90d` | 683 | +0.052 |
| `drawdown90d` | 725 | +0.037 |
| `winrateLifetime` | 719 | +0.036 |
| `pnl` | 725 | +0.031 |
| `drawdown365d` | 725 | -0.029 |
| `drawdown180d` | 725 | -0.013 |
| `sortino365d` | 342 | -0.012 |
| `trades30d` | 725 | -0.012 |
| `sharpe365d` | 342 | -0.008 |
| `winrate7d` | 367 | +0.004 |

### Apenas `copyScoreV2 > 0`

| Campo | n pareado | ρ de Spearman |
|---|---:|---:|
| `copyScore` | 552 | +0.547 |
| `lastTradeAt` | 550 | +0.390 |
| `trades30d` | 552 | +0.343 |
| `perpsEquity` | 552 | +0.336 |
| `winrate` | 552 | +0.334 |
| `sortino365d` | 240 | +0.334 |
| `sharpe180d` | 412 | +0.333 |
| `sharpe365d` | 240 | +0.331 |
| `totalWinningTrades` | 552 | +0.325 |
| `sortino180d` | 412 | +0.303 |
| `totalTrades` | 552 | +0.297 |
| `totalLongTrades` | 552 | +0.294 |
| `trades7d` | 552 | +0.287 |
| `totalShortTrades` | 552 | +0.259 |
| `totalLosingTrades` | 552 | +0.252 |
| `drawdown7d` | 552 | +0.234 |
| `sharpe90d` | 552 | +0.208 |
| `drawdown365d` | 552 | -0.198 |
| `drawdown180d` | 552 | -0.177 |
| `sharpe30d` | 437 | +0.172 |
| `sharpe` | 437 | +0.167 |
| `sortino` | 437 | +0.164 |
| `sortino30d` | 437 | +0.164 |
| `winrate7d` | 260 | +0.153 |
| `pnl` | 552 | +0.135 |
| `sortino90d` | 552 | +0.130 |
| `winrate30d` | 419 | +0.120 |
| `drawdown90d` | 552 | -0.102 |
| `drawdown` | 552 | +0.100 |
| `drawdown30d` | 552 | +0.098 |
| `totalVolume` | 552 | +0.087 |
| `winrate365d` | 548 | +0.044 |
| `winrateLifetime` | 550 | +0.027 |
| `winrate180d` | 543 | +0.023 |
| `winrate90d` | 530 | -0.006 |

## Comparação com o campo legado

- `copyScore = 0` e `copyScoreV2 > 0`: **125** casos.
- `copyScore > 0` e `copyScoreV2 = 0`: **78** casos.
- Exemplo mais alto do primeiro grupo: legado **0.00**, V2 **89.21**.
- Maior legado no segundo grupo: legado **87.06**, V2 **0.00**.

## Leitura correta

- Correlação não prova que um campo entre diretamente na fórmula; métricas e tags podem ser proxies de fatores não observados.
- Score zero pode ser um score calculado ou uma regra de elegibilidade; o JSON sozinho não revela sua semântica.
- Uma única fotografia, sem horário de captura e sem curva de equity/fills, não permite separar causalidade, defasagem de atualização e dados ausentes.
- Para avançar: coletar snapshots repetidos dos mesmos endereços, garantir `copyScoreV2` não nulo, e acrescentar curva de equity / trades fechados / PnL por janela. Validar qualquer modelo em carteiras e datas fora da amostra de ajuste.

## Fontes e hipóteses externas

- A documentação oficial descreve o uso do score no ranking/filtro, mas não publica pesos ou equação: [Copy Trade](https://docs.hyperdash.com/copy-trade) e [Trader Explore](https://docs.hyperdash.com/wallet-explore).
- As notas da API no repositório público do projeto irmão documentam `copyScore` como alias de `copyScoreV2` para o valor exibido e `copyScoreV1` como campo legado; elas também alertam que `sortBy: copyScore` parece ordenar pela versão antiga. Use o campo V2 explícito ao montar novos conjuntos: [hyperdash_api.md](https://github.com/ronaldoaf/Hyperliquid_CopyTrade/blob/main/docs/hyperdash_api.md). Isso é uma anotação do projeto, não documentação oficial da fórmula.
- Um artigo editorial no domínio da Hyperdash cita consistência, drawdown, frequência de trades e PnL como dimensões. Como não informa pesos nem fórmula, isso é apenas uma hipótese externa para orientar testes, não uma conclusão deste dataset: [artigo](https://hyperdash.com/learn/best-tools-trading-hyperliquid).
