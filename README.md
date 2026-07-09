# Documentação da Oficina

Por conta da falta de estrutura dos dados brutos e para facilitar o andamento da oficina, foi realizada a transformação dos dados brutos recolhido das fontes com o seguinte processo:

## Arquivos de entrada

- [`focos_mensal_br_202607.csv`](dados_originais/focos_mensal_br_202607.csv) - focos de calor (detecções de satélite) para todo o Brasil em julho de 2026.
- [`tabela.csv`](dados_originais/tabela.csv) - série horária da estação metereológica de Paragominas, PA em julho de 2026.

## Scripts

- [`filter_focos.py`](scripts/filter_focos.py) - gera [`focos_paragominas_202607.csv`](dados_tratados/focos_paragominas_202607.csv)
- [`convert_tabela.py`](scripts/convert_tabela.py) - gera [`tabela_paragominas_202607.csv`](dados_tratados/tabela_paragominas_202607.csv)

## O que cada script faz

### [`filter_focos.py`](scripts/filter_focos.py)

1. Lê [`focos_mensal_br_202607.csv`](dados_originais/focos_mensal_br_202607.csv) com `csv.DictReader`.
2. Mantém apenas linhas com `municipio == "PARAGOMINAS"`.
3. Remove espaços em branco de todos os campos (`lat`/`lon` vinham com espaços à esquerda, ex: `"  -8.593300"`).
4. Escreve [`focos_paragominas_202607.csv`](dados_tratados/focos_paragominas_202607.csv) com as mesmas 16 colunas do original, agora limpo.

Resultado: 265 linhas, cobrindo `2026-07-01 00:00:00` até `2026-07-07 18:38:00`.

### [`convert_tabela.py`](scripts/convert_tabela.py)

1. Lê [`tabela.csv`](dados_originais/tabela.csv) com delimitador `;`.
2. Junta `Data` (`DD/MM/YYYY`) + `Hora (UTC)` (`HHMM`) em uma única coluna `datetime_utc` no formato `YYYY-MM-DD HH:MM:SS` — o mesmo formato de `data_hora_gmt` do arquivo de focos, para permitir join direto entre os dois arquivos.
3. Converte todos os valores numéricos de decimal-vírgula (`25,5`) para decimal-ponto (`25.5`).
4. Renomeia as colunas para `snake_case` sem acentos/parênteses (ex. `"Temp. Ins. (C)"` → `temp_inst_c`).
5. Descarta linhas sem nenhuma medição (horas do dia corrente ainda não registradas pela estação).
6. Filtra para o intervalo `2026-07-01` a `2026-07-07`, mesma cobertura de dias do [`focos_paragominas_202607.csv`](dados_tratados/focos_paragominas_202607.csv).

Resultado: 168 linhas (7 dias * 24 horas), de `2026-07-01 00:00:00` a `2026-07-07 23:00:00`.

## Sobre o alinhamento temporal

O período (dia inicial e dia final) bate exatamente entre os dois arquivos: `2026-07-01` a `2026-07-07`.

Os timestamps individuais **não** batem hora a hora, e isso é esperado:

- [`tabela_paragominas_202607.csv`](dados_tratados/tabela_paragominas_202607.csv) é uma série regular e faz uma leitura por hora, todo dia.
- [`focos_paragominas_202607.csv`](dados_tratados/focos_paragominas_202607.csv) são detecções reais de satélite (eventos), não amostras programadas. A frequência cai conforme a atividade de queimada muda:

| dia | nº de detecções |
|---|---|
| 01/07 | 102 |
| 02/07 | 91 |
| 03/07 | 37 |
| 04/07 | 30 |
| 05/07 | 2 |
| 06/07 | 1 |
| 07/07 | 2 (última às 18:38) |

Por isso o último registro de foco em 07/07 é às 18:38, enquanto a estação segue até 23:00 no mesmo dia.

## Arquivos de saída

- [`focos_paragominas_202607.csv`](dados_tratados/focos_paragominas_202607.csv)
- [`tabela_paragominas_202607.csv`](dados_tratados/tabela_paragominas_202607.csv)

---

## Prompts de partida

### Prompt 1 - Pré-processamento e junção diária

```
Estou no Google Colab com dois arquivos CSV sobre Paragominas/PA (01 a 07/07/2026):

- focos_paragominas_202607.csv: uma linha por detecção de foco de calor (INPE).
  Colunas: id, lat, lon, data_hora_gmt, satelite, municipio, estado, pais,
  municipio_id, estado_id, pais_id, numero_dias_sem_chuva, precipitacao,
  risco_fogo, bioma, frp.

- tabela_paragominas_202607.csv: uma linha por hora, estação meteorológica (INMET).
  Colunas: datetime_utc, temp_inst_c, temp_max_c, temp_min_c, umi_inst_pct,
  umi_max_pct, umi_min_pct, pto_orvalho_inst_c, pto_orvalho_max_c,
  pto_orvalho_min_c, pressao_inst_hpa, pressao_max_hpa, pressao_min_hpa,
  vel_vento_ms, dir_vento_graus, raj_vento_ms, radiacao_kjm2, chuva_mm.

Escreva um script em pandas que:
1. carregue os dois CSVs;
2. agregue focos_paragominas por dia (data): contagem de detecções, soma de frp,
   média de risco_fogo;
3. agregue tabela_paragominas por dia: temperatura média (temp_inst_c), umidade
   média (umi_inst_pct), soma de chuva (chuva_mm);
4. una os dois agregados em um único dataframe diário via merge por data
   (inner join);
5. mostre a tabela final, uma linha por dia.

Comente cada etapa em poucas palavras explicando o porquê, não só o quê.
```

### Prompt 2 - Gráfico de dispersão e eixo duplo

```
A partir do dataframe diário unificado (colunas: data, focos_dia, frp_total,
risco_fogo_medio, temp_media, umidade_media, chuva_total), gere dois gráficos
com matplotlib:

1. Gráfico de eixo duplo: eixo Y esquerdo com barras (focos_dia por dia), eixo Y
   direito com uma linha (chuva_total por dia). Título, rótulos de eixo e
   legenda para cada série.

2. Gráfico de dispersão: eixo X = temp_media, eixo Y = focos_dia, com uma linha
   de tendência (regressão linear simples) sobreposta.

Explique no código como funciona a criação de um segundo eixo Y (twinx) e por
que ele é necessário quando as duas variáveis têm escalas muito diferentes.
```

### Prompt 3 - Refinamento estético e interpretação

```
Refine os dois gráficos anteriores:
- paleta de cores acessível para daltonismo;
- fonte maior nos títulos e eixos;
- anotação no dia com maior número de focos.

Depois, escreva um parágrafo curto interpretando o que os gráficos sugerem sobre queimadas vs. clima em Paragominas nesse período. Além disso, liste pelo menos duas limitações desse recorte temporal curto para uma análise climática séria.
```
