# Week 1: Review Triage Model Comparison

Holdout: 20 hand-labelled Olist reviews (4 per star rating, seed 42).
All models run locally through Ollama, so API cost is $0.

| Metric | qwen3.5:0.8b | qwen3.5:2b |
|---|---|---|
| schema_valid_rate | 100% | 100% |
| retry_rate | 0% | 0% |
| category_accuracy | 65% | 70% |
| category_macro_f1 | 0.44 | 0.43 |
| severity_accuracy | 70% | 95% |
| needs_response_accuracy | 95% | 100% |
| mean_latency_s | 1.30s | 2.40s |
| p95_latency_s | 1.14s | 3.18s |
| tokens_per_s | 36.8 | 21.3 |
| size_gb | 1.24 GB | 3.12 GB |
| cost_usd | $0.00 | $0.00 |

## Category misses: qwen3.5:0.8b (7)

- `7d8d252c` gold **not_received**, pred **delivery_delay**: Demora de entrega
- `7a00c170` gold **seller_or_support**, pred **delivery_delay**: Depois que fiz a compra, passou 30 dias para a loja me informar que não tem mais a mercadoria
- `d0e64a92` gold **wrong_or_missing_item**, pred **delivery_delay**: ainda não entregaram meu produto, apenas o outros que avia comprado junto, mas o cabo HDMI NÃO foi entregue
- `e9f2aec0` gold **damaged_or_defective**, pred **product_quality**: Vieram 2 rastreadores e nenhum dos dois funcionou. O fornecedor falou que o lote inteiro veio com problema. Devolvi e es
- `54e65ea9` gold **damaged_or_defective**, pred **product_quality**: tem problema com un cartucho o preto nao funciona
- `fcfdb4a7` gold **positive_feedback**, pred **delivery_delay**: Produto chegou conforme eu havia solicitado em um prazo menor do que havia informado. Estou usando a lente sem nenhum pr
- `8d26e643` gold **other**, pred **product_quality**: poderiam descrever as medidas da bolsa. o mais foi ótimo comprar na loja,

## Category misses: qwen3.5:2b (6)

- `7d8d252c` gold **not_received**, pred **delivery_delay**: Demora de entrega
- `7a00c170` gold **seller_or_support**, pred **not_received**: Depois que fiz a compra, passou 30 dias para a loja me informar que não tem mais a mercadoria
- `d0e64a92` gold **wrong_or_missing_item**, pred **not_received**: ainda não entregaram meu produto, apenas o outros que avia comprado junto, mas o cabo HDMI NÃO foi entregue
- `e9f2aec0` gold **damaged_or_defective**, pred **delivery_delay**: Vieram 2 rastreadores e nenhum dos dois funcionou. O fornecedor falou que o lote inteiro veio com problema. Devolvi e es
- `54e65ea9` gold **damaged_or_defective**, pred **product_quality**: tem problema com un cartucho o preto nao funciona
- `8d26e643` gold **other**, pred **product_quality**: poderiam descrever as medidas da bolsa. o mais foi ótimo comprar na loja,

## Recommendation

`qwen3.5:2b` scores highest on category accuracy (70%), breaking ties on schema validity and then latency. Weigh this against memory use and latency in the table above before choosing a default.
