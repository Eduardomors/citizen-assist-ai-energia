"""Gera os cálculos da análise de energia usados no README e nas respostas do assistente.

Execute com: python analise_energia.py
Saídas: docs/energia/comparacao_alternativas.csv e docs/energia/sensibilidade.csv
"""

import csv
import os

from energia import Premissas, comparar_alternativas, energia_kwh, formatar, vazao_l_min

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Cenário de referência (premissas da equipe, explicadas em docs/energia/ANALISE_ENERGIA.md)
PESSOAS = 4
MINUTOS = 12
POTENCIA_W = 5500


def main():
    premissas = Premissas("data/energia_premissas.json")
    if not premissas.carregar():
        return
    tarifa = round(premissas.tarifa_com_tributos(), 2)

    print("=== 1. Tarifa ===")
    print(f"B1 2026 sem tributos = 0,72518 x (1 + 0,0902) = R$ {formatar(premissas.tarifa_sem_tributos(), 4)}/kWh")
    print(f"Com tributos = {formatar(premissas.tarifa_sem_tributos(), 4)} / (1 - 0,18 - 0,059) "
          f"= R$ {formatar(premissas.tarifa_com_tributos(), 4)}/kWh  -> usado: R$ {formatar(tarifa)}")

    print("\n=== 2. Física do banho ===")
    vazao = vazao_l_min(POTENCIA_W, premissas.valor("calor_especifico_agua"), premissas.valor("delta_t_banho"))
    print(f"Vazão aquecida = P / (c x ΔT) = 5500 / (4186 x 20) = {formatar(vazao / 60, 4)} kg/s "
          f"= {formatar(vazao, 1)} L/min")
    banho = energia_kwh(POTENCIA_W, MINUTOS / 60)
    print(f"Energia de 1 banho de {MINUTOS} min = 5,5 kW x {formatar(MINUTOS / 60, 2)} h = {formatar(banho, 2)} kWh "
          f"(R$ {formatar(banho * tarifa)})")

    print(f"\n=== 3. Comparação ({PESSOAS} pessoas, {MINUTOS} min, {POTENCIA_W} W, 1 ano) ===")
    resultados = comparar_alternativas(PESSOAS, MINUTOS, POTENCIA_W, tarifa, premissas)
    campos = ["nome", "renovavel", "kwh_ano", "custo_ano", "economia_ano", "investimento_min",
              "investimento_max", "retorno_min_anos", "retorno_max_anos", "economia_10_anos",
              "co2_evitado_kg", "agua_economizada_l", "viabilidade"]
    linhas = []
    for r in resultados:
        inv = r["investimento"] or (0, 0)
        ret = r["retorno_anos"] or ("", "")
        linhas.append({
            "nome": r["nome"], "renovavel": "sim" if r["renovavel"] else "não",
            "kwh_ano": round(r["kwh_ano"], 1), "custo_ano": round(r["custo_ano"], 2),
            "economia_ano": round(r["economia_ano"], 2),
            "investimento_min": inv[0], "investimento_max": inv[1],
            "retorno_min_anos": round(ret[0], 1) if ret[0] != "" else "",
            "retorno_max_anos": round(ret[1], 1) if ret[1] != "" else "",
            "economia_10_anos": round(r["economia_10_anos"], 2),
            "co2_evitado_kg": round(r["co2_evitado_kg"], 1),
            "agua_economizada_l": round(r["agua_economizada_l"]),
            "viabilidade": r["viabilidade"],
        })
        print(f"{r['nome']:<38} {formatar(r['kwh_ano'], 0):>6} kWh  R$ {formatar(r['custo_ano']):>9}  "
              f"economia R$ {formatar(r['economia_ano']):>9}  CO2 evitado {formatar(r['co2_evitado_kg'], 1)} kg"
              + (f"  retorno {formatar(ret[0], 1)}-{formatar(ret[1], 1)} anos" if ret[0] != "" else ""))

    os.makedirs("docs/energia", exist_ok=True)
    with open("docs/energia/comparacao_alternativas.csv", "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)

    print("\n=== 4. Sensibilidade: retorno do aquecedor solar por tamanho da família ===")
    with open("docs/energia/sensibilidade.csv", "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["pessoas", "minutos", "economia_solar_ano", "retorno_min_anos", "retorno_max_anos"])
        for pessoas in range(1, 7):
            for minutos in (8, 12):
                solar = comparar_alternativas(pessoas, minutos, POTENCIA_W, tarifa, premissas)[2]
                ret = solar["retorno_anos"]
                escritor.writerow([pessoas, minutos, round(solar["economia_ano"], 2),
                                   round(ret[0], 1), round(ret[1], 1)])
                print(f"{pessoas} pessoa(s), {minutos:>2} min: economia R$ {formatar(solar['economia_ano']):>9}/ano, "
                      f"retorno {formatar(ret[0], 1)} a {formatar(ret[1], 1)} anos")
    print("\nArquivos gerados em docs/energia/.")


if __name__ == "__main__":
    main()
