"""
Filtra focos_mensal_br_202607.csv mantendo apenas o municipio de Paragominas.
Entrada ja e comma-separated, so precisa de limpeza de espacos em lat/lon.
"""
import csv

INPUT = "focos_mensal_br_202607.csv"
OUTPUT = "focos_paragominas_202607.csv"

with open(INPUT, encoding="utf-8") as f_in, \
     open(OUTPUT, "w", encoding="utf-8", newline="") as f_out:
    reader = csv.DictReader(f_in)
    writer = csv.writer(f_out)
    writer.writerow(reader.fieldnames)

    count = 0
    for row in reader:
        if row["municipio"].strip().upper() == "PARAGOMINAS":
            clean_row = [v.strip() if isinstance(v, str) else v for v in row.values()]
            writer.writerow(clean_row)
            count += 1

    print(f"Linhas escritas: {count}")
