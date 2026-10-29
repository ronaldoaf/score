#!/usr/bin/env python3
"""Exploratory analysis of Hyperdash trader snapshots (standard library only).

Usage:
    python scripts/analyze_copy_score.py /path/to/hyperdash_traders.json

The script deliberately treats a missing copyScoreV2 as missing, not as zero.
It reports associations; it does not claim to recover Hyperdash's proprietary formula.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable


FEATURES = (
    "copyScore",  # legacy score, useful only as a comparison
    "pnl",
    "perpsEquity",
    "winrate",
    "totalTrades",
    "totalLongTrades",
    "totalShortTrades",
    "totalWinningTrades",
    "totalLosingTrades",
    "sharpe",
    "drawdown",
    "winrate7d",
    "winrate30d",
    "winrate90d",
    "winrate180d",
    "winrate365d",
    "winrateLifetime",
    "trades7d",
    "trades30d",
    "sharpe7d",
    "sharpe30d",
    "sharpe90d",
    "sharpe180d",
    "sharpe365d",
    "sortino",
    "sortino7d",
    "sortino30d",
    "sortino90d",
    "sortino180d",
    "sortino365d",
    "drawdown7d",
    "drawdown30d",
    "drawdown90d",
    "drawdown180d",
    "drawdown365d",
    "totalVolume",
    "lastTradeAt",
)


def as_number(value: Any) -> float | None:
    """Parse JSON numbers and numeric strings; reject nulls and non-finite values."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        parsed = float(value)
    elif isinstance(value, str):
        try:
            parsed = float(value)
        except ValueError:
            return None
    else:
        return None
    return parsed if math.isfinite(parsed) else None


def extract_rows(payload: Any) -> list[dict[str, Any]]:
    """Accept a JSON list, or a common GraphQL/data wrapper around that list."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("traders", "data", "getSystemGroupTraders"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                nested = extract_rows(value)
                if nested:
                    return nested
    raise ValueError("O JSON precisa conter uma lista de traders.")


def quantile(values: Iterable[float], probability: float) -> float | None:
    """Linear-interpolated quantile (same convention as common data tools)."""
    ordered = sorted(values)
    if not ordered:
        return None
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def average_ranks(values: list[float]) -> list[float]:
    """Return one-based average ranks, preserving ties."""
    ordered_indices = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(ordered_indices):
        end = start + 1
        while end < len(ordered_indices) and values[ordered_indices[end]] == values[ordered_indices[start]]:
            end += 1
        rank = (start + 1 + end) / 2
        for position in range(start, end):
            ranks[ordered_indices[position]] = rank
        start = end
    return ranks


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    cov = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    var_x = sum((a - mean_x) ** 2 for a in x)
    var_y = sum((b - mean_y) ** 2 for b in y)
    denominator = math.sqrt(var_x * var_y)
    return cov / denominator if denominator else None


def spearman(x: list[float], y: list[float]) -> float | None:
    """Spearman rho, using average ranks for tied values."""
    if len(x) != len(y) or len(x) < 2:
        return None
    return pearson(average_ranks(x), average_ranks(y))


def correlation_rows(
    rows: list[dict[str, Any]], target: str, fields: Iterable[str]
) -> list[dict[str, Any]]:
    results = []
    for field in fields:
        pairs = [
            (feature, score)
            for row in rows
            if (score := as_number(row.get(target))) is not None
            and (feature := as_number(row.get(field))) is not None
        ]
        if len(pairs) < 10:
            continue
        x = [pair[0] for pair in pairs]
        y = [pair[1] for pair in pairs]
        rho = spearman(x, y)
        if rho is not None:
            results.append({"field": field, "n": len(pairs), "rho": rho})
    return sorted(results, key=lambda item: (-abs(item["rho"]), item["field"]))


def fmt(value: float | None, digits: int = 2) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def make_report(rows: list[dict[str, Any]], source: str) -> str:
    total = len(rows)
    legacy_values = [as_number(row.get("copyScore")) for row in rows]
    legacy_values = [value for value in legacy_values if value is not None]
    v2_values = [as_number(row.get("copyScoreV2")) for row in rows]
    scored_rows = [
        row for row, score in zip(rows, v2_values) if score is not None
    ]
    scores = [score for score in v2_values if score is not None]
    positive_rows = [
        row
        for row, score in zip(rows, v2_values)
        if score is not None and score > 0
    ]
    positive_scores = [score for score in scores if score > 0]
    zero_count = sum(score == 0 for score in scores)
    missing_count = total - len(scores)
    legacy_zero_count = sum(score == 0 for score in legacy_values)

    lines = [
        "# Análise exploratória do Copy Score Hyperdash",
        "",
        f"Arquivo analisado: `{source}`",
        "",
        "> Esta análise mede associações nos exemplos fornecidos. Ela não recupera nem confirma a fórmula proprietária da Hyperdash.",
        "",
        "## Cobertura e distribuição",
        "",
        "| Medida | Valor |",
        "|---|---:|",
        f"| Traders no arquivo | {total:,} |",
        f"| `copyScore` (legado) não nulo | {len(legacy_values):,} |",
        f"| `copyScore` (legado) igual a zero | {legacy_zero_count:,} |",
        f"| `copyScoreV2` não nulo | {len(scores):,} |",
        f"| `copyScoreV2` nulo | {missing_count:,} |",
        f"| `copyScoreV2` exatamente zero | {zero_count:,} |",
        f"| `copyScoreV2` positivo | {len(positive_scores):,} |",
        f"| Faixa de `copyScoreV2` não nulo | {fmt(min(scores) if scores else None)}–{fmt(max(scores) if scores else None)} |",
        f"| Mediana de `copyScoreV2` (inclui zeros) | {fmt(quantile(scores, 0.5))} |",
        f"| Mediana entre `copyScoreV2` positivos | {fmt(quantile(positive_scores, 0.5))} |",
        "",
        "**Importante:** `null` e `0` são estados diferentes neste arquivo. O relatório não converte valores ausentes em zero.",
        "",
        "## `copyScoreV2` por estilo (`tag`)",
        "",
        "| Estilo | n | Score zero | % zero | Mediana | Média |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    tag_groups: dict[str, list[float]] = {}
    for row in scored_rows:
        tag = row.get("tag")
        label = str(tag) if tag not in (None, "") else "sem tag"
        tag_groups.setdefault(label, []).append(as_number(row.get("copyScoreV2")) or 0.0)
    for label, values in sorted(tag_groups.items(), key=lambda item: item[0]):
        zeros = sum(value == 0 for value in values)
        lines.append(
            f"| {label} | {len(values)} | {zeros} | {fmt(100 * zeros / len(values), 1)}% | "
            f"{fmt(quantile(values, 0.5))} | {fmt(sum(values) / len(values))} |"
        )

    lines.extend(
        [
            "",
            "## Associação com métricas numéricas",
            "",
            "Spearman (ρ), com ranks médios para empates e remoção par a par de nulos. A primeira tabela inclui scores zero; a segunda condiciona a `copyScoreV2 > 0`.",
            "",
            "### Todos os `copyScoreV2` não nulos",
            "",
            "| Campo | n pareado | ρ de Spearman |",
            "|---|---:|---:|",
        ]
    )
    for item in correlation_rows(scored_rows, "copyScoreV2", FEATURES):
        lines.append(f"| `{item['field']}` | {item['n']} | {item['rho']:+.3f} |")

    lines.extend(
        [
            "",
            "### Apenas `copyScoreV2 > 0`",
            "",
            "| Campo | n pareado | ρ de Spearman |",
            "|---|---:|---:|",
        ]
    )
    for item in correlation_rows(positive_rows, "copyScoreV2", FEATURES):
        lines.append(f"| `{item['field']}` | {item['n']} | {item['rho']:+.3f} |")

    v1zero_positive_v2 = [
        (as_number(row.get("copyScore")), as_number(row.get("copyScoreV2")))
        for row in rows
        if as_number(row.get("copyScore")) == 0
        and (as_number(row.get("copyScoreV2")) or 0) > 0
    ]
    v1positive_v2zero = [
        (as_number(row.get("copyScore")), as_number(row.get("copyScoreV2")))
        for row in rows
        if (as_number(row.get("copyScore")) or 0) > 0
        and as_number(row.get("copyScoreV2")) == 0
    ]
    lines.extend(
        [
            "",
            "## Comparação com o campo legado",
            "",
            f"- `copyScore = 0` e `copyScoreV2 > 0`: **{len(v1zero_positive_v2)}** casos.",
            f"- `copyScore > 0` e `copyScoreV2 = 0`: **{len(v1positive_v2zero)}** casos.",
        ]
    )
    if v1zero_positive_v2:
        best = max(v1zero_positive_v2, key=lambda pair: pair[1] or 0)
        lines.append(
            f"- Exemplo mais alto do primeiro grupo: legado **{fmt(best[0])}**, V2 **{fmt(best[1])}**."
        )
    if v1positive_v2zero:
        best = max(v1positive_v2zero, key=lambda pair: pair[0] or 0)
        lines.append(
            f"- Maior legado no segundo grupo: legado **{fmt(best[0])}**, V2 **{fmt(best[1])}**."
        )
    lines.extend(
        [
            "",
            "## Leitura correta",
            "",
            "- Correlação não prova que um campo entre diretamente na fórmula; métricas e tags podem ser proxies de fatores não observados.",
            "- Score zero pode ser um score calculado ou uma regra de elegibilidade; o JSON sozinho não revela sua semântica.",
            "- Uma única fotografia, sem horário de captura e sem curva de equity/fills, não permite separar causalidade, defasagem de atualização e dados ausentes.",
            "- Para avançar: coletar snapshots repetidos dos mesmos endereços, garantir `copyScoreV2` não nulo, e acrescentar curva de equity / trades fechados / PnL por janela. Validar qualquer modelo em carteiras e datas fora da amostra de ajuste.",
            "",
            "## Fontes e hipóteses externas",
            "",
            "- A documentação oficial descreve o uso do score no ranking/filtro, mas não publica pesos ou equação: [Copy Trade](https://docs.hyperdash.com/copy-trade) e [Trader Explore](https://docs.hyperdash.com/wallet-explore).",
            "- As notas da API no repositório público do projeto irmão documentam `copyScore` como alias de `copyScoreV2` para o valor exibido e `copyScoreV1` como campo legado; elas também alertam que `sortBy: copyScore` parece ordenar pela versão antiga. Use o campo V2 explícito ao montar novos conjuntos: [hyperdash_api.md](https://github.com/ronaldoaf/Hyperliquid_CopyTrade/blob/main/docs/hyperdash_api.md). Isso é uma anotação do projeto, não documentação oficial da fórmula.",
            "- Um artigo editorial no domínio da Hyperdash cita consistência, drawdown, frequência de trades e PnL como dimensões. Como não informa pesos nem fórmula, isso é apenas uma hipótese externa para orientar testes, não uma conclusão deste dataset: [artigo](https://hyperdash.com/learn/best-tools-trading-hyperliquid).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path, help="Arquivo JSON de traders da Hyperdash")
    parser.add_argument(
        "-o", "--output", type=Path, help="Gravar o relatório Markdown neste caminho (padrão: stdout)"
    )
    args = parser.parse_args()

    try:
        payload = json.loads(args.json_file.read_text(encoding="utf-8"))
        rows = extract_rows(payload)
        report = make_report(rows, str(args.json_file))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 2

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
        print(f"Relatório salvo em {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
