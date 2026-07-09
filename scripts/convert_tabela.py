"""
Converte tabela.csv (INMET, ';'-separated, decimal com virgula, Data/Hora em colunas
separadas) para CSV comma-separated com datetime_utc unificado no mesmo formato
usado em data_hora_gmt do focos (YYYY-MM-DD HH:MM:SS).

Recorta o intervalo para bater com a cobertura de dias do focos_paragominas
(2026-07-01 a 2026-07-07) e descarta linhas sem nenhuma medicao (horas futuras
ainda nao registradas na estacao).
"""
import csv
from datetime import datetime

INPUT = "tabela.csv"
OUTPUT = "tabela_paragominas_202607.csv"

MIN_DATE = "2026-07-01"
MAX_DATE = "2026-07-07"  # ultimo dia com dados no focos_paragominas

NEW_HEADERS = [
    "datetime_utc", "temp_inst_c", "temp_max_c", "temp_min_c",
    "umi_inst_pct", "umi_max_pct", "umi_min_pct",
    "pto_orvalho_inst_c", "pto_orvalho_max_c", "pto_orvalho_min_c",
    "pressao_inst_hpa", "pressao_max_hpa", "pressao_min_hpa",
    "vel_vento_ms", "dir_vento_graus", "raj_vento_ms",
    "radiacao_kjm2", "chuva_mm",
]


def to_num(value: str) -> str:
    value = value.strip()
    return value.replace(",", ".") if value else ""


def main() -> None:
    rows_written = 0
    with open(INPUT, encoding="utf-8") as f_in, \
         open(OUTPUT, "w", encoding="utf-8", newline="") as f_out:
        reader = csv.reader(f_in, delimiter=";")
        writer = csv.writer(f_out)
        writer.writerow(NEW_HEADERS)
        next(reader)  # pula cabecalho original

        for row in reader:
            if not row or len(row) < 18:
                continue

            data_str = row[0].strip().strip('"')
            hora_str = row[1].strip().strip('"')
            if not data_str or not hora_str:
                continue

            # linhas sem nenhuma medicao (ex.: horas futuras do dia corrente)
            if all(c.strip().strip('"') == "" for c in row[2:]):
                continue

            date_iso = datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            if date_iso < MIN_DATE or date_iso > MAX_DATE:
                continue

            hora = hora_str.zfill(4)
            dt = f"{date_iso} {hora[:2]}:{hora[2:]}:00"
            values = [to_num(c) for c in row[2:18]]
            writer.writerow([dt] + values)
            rows_written += 1

    print(f"Linhas escritas: {rows_written}")


if __name__ == "__main__":
    main()
