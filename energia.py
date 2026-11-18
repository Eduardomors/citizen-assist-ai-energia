"""Módulo de Energia do Citizen Assist AI.

Contribuição da disciplina Soluções em Energias Renováveis e Sustentáveis.
Ajuda o jovem que começou a trabalhar (e passou a ajudar com as contas de casa)
a entender quanto cada aparelho gasta e a comparar alternativas para o maior
vilão da conta de luz: o banho com chuveiro elétrico.

Todas as contas usam as premissas de data/energia_premissas.json, com fonte e tipo
(oficial ou estimado). Os resultados são ESTIMATIVAS, não garantias.
"""

import json
import re
import time
from datetime import datetime

from assistente import ler_opcao, ler_sim_nao

DIAS_ANO = 365
HORIZONTE_ANOS = 10

LIMITACOES = [
    "Os valores são estimativas para 1 ano. A economia real depende do seu uso, do clima e da tarifa do mês.",
    "A tarifa muda todo ano (reajuste da ANEEL) e todo mês (bandeiras e PIS/COFINS).",
    "A fração solar de 70% é um valor de projeto: em dias nublados ou com mais gente em casa, o aquecedor solar rende menos.",
    "Preços de aquecedor solar e descontos de assinatura variam por empresa. Peça orçamentos antes de decidir.",
    "Não consideramos o custo da água, juros de financiamento nem a instalação de tubulação extra.",
    "Este assistente NÃO é um canal oficial nem substitui a avaliação de um profissional.",
]


# ---------------------------------------------------------------------------
# Funções de cálculo (sem input/print: fáceis de testar)
# ---------------------------------------------------------------------------
def energia_kwh(potencia_w, horas):
    """Energia (kWh) = Potência (kW) x tempo (h)."""
    return potencia_w / 1000 * horas


def vazao_l_min(potencia_w, calor_especifico, delta_t):
    """Vazão que um chuveiro consegue aquecer: Q = m.c.ΔT  ->  m/s = P / (c.ΔT).

    Considera 1 kg de água = 1 litro e eficiência de 100% (resistência elétrica).
    """
    return potencia_w / (calor_especifico * delta_t) * 60


def formatar(valor, casas=2):
    """Formata número no padrão brasileiro: 1234.5 -> '1.234,50'."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


class Premissas:
    """Lê os dados e premissas usados nos cálculos (com origem e fonte)."""

    def __init__(self, caminho="data/energia_premissas.json"):
        self.caminho = caminho
        self.itens = {}
        self.verificado_em = ""

    def carregar(self):
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            self.itens = dados["premissas"]
            self.verificado_em = dados.get("verificado_em", "")
            return True
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            print(f"Erro: não foi possível ler {self.caminho}.")
            return False

    def valor(self, chave):
        return self.itens[chave]["valor"]

    def tarifa_sem_tributos(self):
        """Tarifa B1 2026 = tarifa 2025 x (1 + reajuste 2026)."""
        return self.valor("tarifa_b1_2025_sem_tributos") * (1 + self.valor("reajuste_b1_2026"))

    def tarifa_com_tributos(self):
        """ICMS e PIS/COFINS são 'por dentro': preço final = tarifa / (1 - tributos)."""
        tributos = self.valor("icms") + self.valor("pis_cofins")
        return self.tarifa_sem_tributos() / (1 - tributos)


def comparar_alternativas(pessoas, minutos, potencia_w, tarifa, premissas, banhos_dia=1):
    """Compara alternativas para a MESMA necessidade (banho quente da casa) em 1 ano.

    Retorna uma lista de dicionários, um por cenário.
    """
    p = premissas.valor
    emissao = p("fator_emissao_kg_kwh")
    vazao = vazao_l_min(potencia_w, p("calor_especifico_agua"), p("delta_t_banho"))

    # Situação atual
    banhos_ano = pessoas * banhos_dia * DIAS_ANO
    horas_ano = banhos_ano * minutos / 60
    base_kwh = energia_kwh(potencia_w, horas_ano)
    base_custo = base_kwh * tarifa

    # A) Hábito: banho de até 8 min + posição verão nos meses quentes
    minutos_a = min(minutos, p("minutos_banho_meta"))
    fracao_meses_verao = p("meses_posicao_verao") / 12
    fator_verao = fracao_meses_verao * (1 - p("reducao_posicao_verao")) + (1 - fracao_meses_verao)
    a_kwh = energia_kwh(potencia_w, banhos_ano * minutos_a / 60) * fator_verao
    agua_a = (minutos - minutos_a) * vazao * banhos_ano

    # B) Aquecedor solar de água (fonte renovável) com o chuveiro como apoio
    b_kwh = base_kwh * (1 - p("fracao_solar"))
    inv_min, inv_max = p("custo_aquecedor_solar_min"), p("custo_aquecedor_solar_max")

    # C) Energia solar por assinatura (fonte renovável, sem obra)
    desc_min, desc_max = p("desconto_assinatura_min"), p("desconto_assinatura_max")
    desc_medio = (desc_min + desc_max) / 2

    # A + B juntos
    ab_kwh = a_kwh * (1 - p("fracao_solar"))

    def cenario(nome, kwh, custo, renovavel, investimento, viabilidade, agua=0.0):
        economia = base_custo - custo
        if investimento and economia > 0:
            retorno = (investimento[0] / economia, investimento[1] / economia)
        else:
            retorno = None
        return {
            "nome": nome,
            "renovavel": renovavel,
            "kwh_ano": kwh,
            "custo_ano": custo,
            "economia_ano": economia,
            "economia_10_anos": economia * HORIZONTE_ANOS - (sum(investimento) / 2 if investimento else 0),
            "investimento": investimento,
            "retorno_anos": retorno,
            "co2_evitado_kg": (base_kwh - kwh) * emissao,
            "agua_economizada_l": agua,
            "viabilidade": viabilidade,
        }

    return [
        cenario("Situação atual (chuveiro elétrico)", base_kwh, base_custo, False, None,
                "É o que a casa já faz hoje."),
        cenario("A) Banho de 8 min + posição verão", a_kwh, a_kwh * tarifa, False, None,
                "Sem custo e começa hoje. Depende só do hábito de todos da casa.", agua_a),
        cenario("B) Aquecedor solar de água", b_kwh, b_kwh * tarifa, True, (inv_min, inv_max),
                "Precisa de telhado com sol, caixa d'água e autorização do dono do imóvel."),
        cenario("C) Solar por assinatura", base_kwh, base_custo * (1 - desc_medio), True, None,
                "Sem obra, bom para quem aluga. Exige contrato (veja prazo, multa e consumo mínimo)."),
        cenario("A + B juntos", ab_kwh, ab_kwh * tarifa, True, (inv_min, inv_max),
                "Mesma exigência do aquecedor solar, somada à mudança de hábito.", agua_a),
    ]


def recomendar(resultados, pode_instalar, vida_util):
    """Monta as recomendações a partir dos números calculados."""
    atual, habito, solar, assinatura = resultados[0], resultados[1], resultados[2], resultados[3]
    dicas = []

    if habito["agua_economizada_l"] == 0 and habito["economia_ano"] > 0:
        dicas.append(
            f"Seus banhos já são curtos. Usar a chave na posição verão nos meses quentes economiza "
            f"cerca de R$ {formatar(habito['economia_ano'])} por ano, sem gastar nada.")
    elif habito["economia_ano"] > 0:
        dicas.append(
            f"1º passo (sem gastar nada): banho de até 8 min e chave no verão nos meses quentes. "
            f"Economia estimada de R$ {formatar(habito['economia_ano'])} por ano "
            f"({habito['economia_ano'] / atual['custo_ano'] * 100:.0f}% do gasto com banho).")
    else:
        dicas.append("Seus banhos já são curtos. Use a posição verão nos dias quentes para economizar mais.")

    retorno = solar["retorno_anos"]
    if pode_instalar and retorno and retorno[1] <= vida_util:
        dicas.append(
            f"Vale pesquisar um aquecedor solar: a economia estimada paga o investimento em "
            f"{formatar(retorno[0], 1)} a {formatar(retorno[1], 1)} anos, e os coletores duram {vida_util}+ anos.")
    elif pode_instalar and retorno and retorno[0] > vida_util:
        dicas.append(
            f"O aquecedor solar NÃO compensa no seu caso: levaria de {formatar(retorno[0], 1)} a "
            f"{formatar(retorno[1], 1)} anos para se pagar, mais que a vida útil dos coletores ({vida_util} anos). "
            f"Fique com a mudança de hábito.")
    elif pode_instalar and retorno:
        dicas.append(
            f"O aquecedor solar levaria de {formatar(retorno[0], 1)} a {formatar(retorno[1], 1)} anos para se pagar, "
            f"perto da vida útil dos coletores ({vida_util} anos). Só vale se o orçamento vier no valor mais baixo.")
    else:
        dicas.append(
            "Como não dá para instalar nada no imóvel, a opção renovável é a energia solar por assinatura: "
            f"cerca de R$ {formatar(assinatura['economia_ano'])} por ano a menos só na parte do banho, "
            "e o desconto vale para a conta inteira.")

    dicas.append("Antes de assinar contrato ou comprar equipamento, compare pelo menos 3 orçamentos.")
    return dicas


# ---------------------------------------------------------------------------
# Leitura de números (aceita vírgula e Enter para valor padrão)
# ---------------------------------------------------------------------------
def limpar_numero(texto):
    """Aceita o jeito que as pessoas digitam: 'R$ 1,10', '5.500', '5500W', '12 min'."""
    texto = re.sub(r"\(.*?\)", "", texto.lower())  # '5500 W (5,5 kW)' -> '5500 W'
    texto = texto.replace("r$", "").replace("kwh", "").rstrip(". ")
    texto = re.sub(r"[a-z\s/]", "", texto)
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", texto):  # 5.500 -> 5500 (ponto de milhar)
        texto = texto.replace(".", "")
    return texto.replace(",", ".")


def ler_numero(mensagem, minimo, maximo, padrao=None):
    while True:
        entrada = limpar_numero(input(mensagem))
        if entrada == "" and padrao is not None:
            return padrao
        try:
            numero = float(entrada)
        except ValueError:
            print("Valor inválido: digite apenas números (ex.: 8 ou 1,05).")
            continue
        if minimo <= numero <= maximo:
            return numero
        print(f"Valor fora da faixa. Digite de {formatar(minimo, 0)} a {formatar(maximo, 0)}.")


# ---------------------------------------------------------------------------
# Interação com o usuário
# ---------------------------------------------------------------------------
class ModuloEnergia:
    """Menu de energia integrado ao Citizen Assist AI."""

    def __init__(self, premissas, caminho_aparelhos="data/aparelhos.json",
                 caminho_simulacoes="data/simulacoes_energia.json"):
        self.premissas = premissas
        self.caminho_aparelhos = caminho_aparelhos
        self.caminho_simulacoes = caminho_simulacoes
        self.aparelhos = []
        self.simulacoes = []
        self._carregar()

    def _carregar(self):
        try:
            with open(self.caminho_aparelhos, "r", encoding="utf-8") as arquivo:
                self.aparelhos = json.load(arquivo)["aparelhos"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            print("Aviso: lista de aparelhos indisponível. Você ainda pode digitar a potência.")
        try:
            with open(self.caminho_simulacoes, "r", encoding="utf-8") as arquivo:
                self.simulacoes = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            self.simulacoes = []

    def _salvar_simulacao(self, tipo, entradas, resultado, inicio):
        """Registra a simulação (sem dados pessoais) para os testes com usuários."""
        clara = ler_sim_nao("\nA explicação ficou clara? (s/n): ")
        util = ler_sim_nao("Isso vai te ajudar a decidir algo em casa? (s/n): ")
        self.simulacoes.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "entradas": entradas,
            "resultado": resultado,
            "clara": clara,
            "util": util,
            "tempo_segundos": round(time.time() - inicio, 1),
        })
        try:
            with open(self.caminho_simulacoes, "w", encoding="utf-8") as arquivo:
                json.dump(self.simulacoes, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar a simulação.")

    def ler_tarifa(self):
        padrao = round(self.premissas.tarifa_com_tributos(), 2)
        print("\nQuanto custa o kWh na sua conta? Procure 'Preço unit. com tributos' (R$/kWh).")
        return ler_numero(f"Digite o valor ou Enter para usar R$ {formatar(padrao)} (estimado Enel SP 2026): ",
                          0.3, 3.0, padrao)

    def menu(self):
        while True:
            print("\n=== Energia: economizar na conta de luz ===")
            print("1. Quanto gasta um aparelho?")
            print("2. Banho da casa: comparar alternativas (inclui energia solar)")
            print("3. Quanto a bandeira tarifária pesa na minha conta?")
            print("4. Ver dados, fontes e limitações dos cálculos")
            print("0. Voltar")
            opcao = ler_opcao("Escolha uma opção: ", 0, 4)
            if opcao == 0:
                return
            if opcao == 1:
                self.consumo_aparelho()
                print("\n(Você continua no menu de Energia: escolha outra opção ou 0 para voltar.)")
            elif opcao == 2:
                self.comparar_banho()
                print("\n(Você continua no menu de Energia: escolha outra opção ou 0 para voltar.)")
            elif opcao == 3:
                self.bandeiras()
                print("\n(Você continua no menu de Energia: escolha outra opção ou 0 para voltar.)")
            else:
                self.mostrar_premissas()

    # ---- 1. Consumo de um aparelho ----
    def consumo_aparelho(self):
        inicio = time.time()
        print("\n=== Quanto gasta um aparelho? ===")
        for numero, aparelho in enumerate(self.aparelhos, start=1):
            print(f"{numero}. {aparelho['nome']} (~{formatar(aparelho['potencia_w'], 0)} W)")
        print(f"{len(self.aparelhos) + 1}. Outro (vou digitar a potência)")
        print("0. Voltar")
        escolha = ler_opcao("Escolha: ", 0, len(self.aparelhos) + 1)
        if escolha == 0:
            return

        if escolha <= len(self.aparelhos):
            aparelho = self.aparelhos[escolha - 1]
            nome = aparelho["nome"]
            potencia = ler_numero(f"Potência em watts (Enter = {formatar(aparelho['potencia_w'], 0)} W): ",
                                  1, 15000, aparelho["potencia_w"])
            horas = ler_numero(f"Horas de uso por dia (Enter = {formatar(aparelho['horas_dia'], 2)}): ",
                               0.01, 24, aparelho["horas_dia"])
            dias = ler_numero(f"Dias de uso no mês (Enter = {aparelho['dias_mes']}): ",
                              1, 31, aparelho["dias_mes"])
        else:
            nome = "Outro aparelho"
            potencia = ler_numero("Potência em watts (veja a etiqueta): ", 1, 15000)
            horas = ler_numero("Horas de uso por dia: ", 0.01, 24)
            dias = ler_numero("Dias de uso no mês: ", 1, 31)

        tarifa = self.ler_tarifa()
        kwh_mes = energia_kwh(potencia, horas * dias)
        custo_mes = kwh_mes * tarifa
        print(f"\n>> {nome}")
        print(f"Cálculo: {formatar(potencia, 0)} W ÷ 1000 × {formatar(horas, 2)} h × {formatar(dias, 0)} dias "
              f"= {formatar(kwh_mes, 1)} kWh por mês")
        print(f"Custo: {formatar(kwh_mes, 1)} kWh × R$ {formatar(tarifa)} = R$ {formatar(custo_mes)} por mês "
              f"(R$ {formatar(custo_mes * 12)} por ano)")
        print(f"Emissão estimada: {formatar(kwh_mes * 12 * self.premissas.valor('fator_emissao_kg_kwh'), 1)} kg de CO2 por ano")
        if potencia >= 2000:
            print("Dica: aparelhos de alta potência pesam mesmo com pouco tempo de uso. "
                  "Reduzir minutos aqui economiza mais do que desligar carregadores.")
        print("Estimativa: confira a potência real na etiqueta do aparelho.")
        self._salvar_simulacao("aparelho", {"aparelho": nome, "potencia_w": potencia, "horas_dia": horas,
                                            "dias_mes": dias, "tarifa": tarifa},
                               {"kwh_mes": round(kwh_mes, 2), "custo_mes": round(custo_mes, 2)}, inicio)

    # ---- 2. Comparação de alternativas para o banho ----
    def comparar_banho(self):
        inicio = time.time()
        print("\n=== Banho da casa: comparar alternativas ===")
        print("O chuveiro elétrico costuma ser o aparelho que mais gasta numa casa.")
        pessoas = int(ler_numero("Quantas pessoas tomam banho na sua casa? ", 1, 15))
        banhos_dia = ler_numero("Quantos banhos cada pessoa toma por dia? (Enter = 1) ", 1, 5, 1)
        minutos = ler_numero("Quantos minutos dura cada banho, em média? (Enter = 12) ", 1, 60, 12)
        padrao_w = self.premissas.valor("potencia_chuveiro_w")
        potencia = ler_numero(f"Potência do chuveiro em watts (Enter = {formatar(padrao_w, 0)} W, o mais comum): ",
                              1000, 9000, padrao_w)
        tarifa = self.ler_tarifa()
        pode_instalar = ler_sim_nao("A casa é própria ou o dono deixaria instalar algo no telhado? (s/n): ")

        resultados = comparar_alternativas(pessoas, minutos, potencia, tarifa, self.premissas, banhos_dia)
        atual = resultados[0]
        print("\n=== Resumo ===")
        print(f"Hoje o banho da casa custa cerca de R$ {formatar(atual['custo_ano'], 0)} por ano "
              f"(R$ {formatar(atual['custo_ano'] / 12, 0)} por mês). Valores estimados.")

        print("\n--- O que recomendamos para você ---")
        vida_util = int(self.premissas.valor("vida_util_coletor_anos"))
        for dica in recomendar(resultados, pode_instalar, vida_util):
            print(f"* {dica}")

        habito = resultados[1]
        if habito["agua_economizada_l"] > 0:
            print(f"* Bônus: banhos mais curtos também economizam cerca de "
                  f"{formatar(habito['agua_economizada_l'] / 1000, 1)} mil litros de água por ano.")

        if ler_sim_nao("\nQuer ver a tabela comparando todas as alternativas? (s/n): "):
            self.exibir_tabela(resultados, pode_instalar)

        print("\nAtenção: são estimativas, não economia garantida. "
              "Veja fontes e limitações na opção 4 do menu de Energia.")

        melhor = max(resultados[1:], key=lambda r: r["economia_ano"])
        self._salvar_simulacao("banho", {"pessoas": pessoas, "banhos_dia": banhos_dia, "minutos": minutos, "potencia_w": potencia,
                                         "tarifa": tarifa, "pode_instalar": pode_instalar},
                               {"kwh_ano_atual": round(resultados[0]["kwh_ano"], 1),
                                "maior_economia": melhor["nome"],
                                "economia_ano": round(melhor["economia_ano"], 2)}, inicio)

    def exibir_tabela(self, resultados, pode_instalar=True):
        if not pode_instalar:
            resultados = [r for r in resultados if r["investimento"] is None]
        print(f"\nPeríodo de referência: 1 ano ({DIAS_ANO} dias). Valores ESTIMADOS.")
        print(f"{'Alternativa':<38}{'kWh/ano':>8}{'R$/ano':>9}{'Economia':>11}{'Investimento':>17}{'Retorno':>17}{'CO2 evitado':>13}")
        print("-" * 113)
        for r in resultados:
            economia = "-" if r["economia_ano"] <= 0.005 else f"R$ {formatar(r['economia_ano'], 0)}"
            if r["investimento"]:
                invest = f"R$ {formatar(r['investimento'][0], 0)}-{formatar(r['investimento'][1], 0)}"
            else:
                invest = "R$ 0"
            if r["retorno_anos"]:
                retorno = f"{formatar(r['retorno_anos'][0], 1)}-{formatar(r['retorno_anos'][1], 1)} anos"
            elif r["investimento"] is None and r["economia_ano"] > 0:
                retorno = "imediato"
            else:
                retorno = "-"
            co2 = f"{formatar(r['co2_evitado_kg'], 1)} kg" if r["co2_evitado_kg"] > 0 else "-"
            marca = " (renov.)" if r["renovavel"] else ""
            print(f"{(r['nome'] + marca)[:37]:<38}{formatar(r['kwh_ano'], 0):>8}{formatar(r['custo_ano'], 0):>9}"
                  f"{economia:>11}{invest:>17}{retorno:>17}{co2:>13}")
        print("\nComo ler: 'Economia' é quanto você deixa de gastar por ano em relação a hoje. "
              "'Retorno' é quanto tempo a economia leva para pagar o investimento.")
        if not pode_instalar:
            print("O aquecedor solar não aparece porque você disse que não pode instalar nada no imóvel.")
        for r in resultados[1:]:
            if r["nome"] != "A + B juntos":
                print(f"  {r['nome']}: {r['viabilidade']}")

    # ---- 3. Bandeiras tarifárias ----
    def bandeiras(self):
        inicio = time.time()
        print("\n=== Bandeira tarifária ===")
        print("A bandeira é um valor extra cobrado quando gerar energia fica mais caro (ex.: poucas chuvas).")
        consumo = ler_numero("Quantos kWh a sua casa gasta por mês? (está na conta; Enter = 200) ",
                             1, 5000, 200)
        amarela = consumo * self.premissas.valor("bandeira_amarela_kwh")
        vermelha = consumo * self.premissas.valor("bandeira_vermelha1_kwh")
        vermelha2 = consumo * self.premissas.valor("bandeira_vermelha2_kwh")
        print(f"Bandeira verde: R$ 0,00 a mais")
        print(f"Bandeira amarela: + R$ {formatar(amarela)} no mês (sem contar impostos)")
        print(f"Bandeira vermelha 1: + R$ {formatar(vermelha)} no mês (sem contar impostos)")
        print(f"Bandeira vermelha 2: + R$ {formatar(vermelha2)} no mês (sem contar impostos)")
        print("A bandeira do mês aparece escrita na sua conta de luz.")
        print("Dica: em meses de bandeira vermelha, cortar minutos de banho compensa ainda mais.")
        print("A cor da bandeira de cada mês é divulgada pela ANEEL no fim do mês anterior.")
        self._salvar_simulacao("bandeira", {"consumo_kwh": consumo},
                               {"amarela": round(amarela, 2), "vermelha1": round(vermelha, 2),
                                "vermelha2": round(vermelha2, 2)}, inicio)

    # ---- 4. Premissas, fontes e limitações ----
    def mostrar_premissas(self):
        print(f"\n=== Dados e premissas (verificados em {self.premissas.verificado_em}) ===")
        for chave, item in self.premissas.itens.items():
            print(f"\n- {chave}: {item['valor']} {item['unidade']} [{item['tipo'].upper()}]")
            print(f"  {item['origem']}")
            print(f"  Fonte: {item['fonte']}")
        print(f"\nTarifa estimada sem tributos (2026): R$ {formatar(self.premissas.tarifa_sem_tributos(), 4)}/kWh")
        print(f"Tarifa estimada com tributos: R$ {formatar(self.premissas.tarifa_com_tributos(), 4)}/kWh")
        print("\nLimitações:")
        for limite in LIMITACOES:
            print(f"  - {limite}")

    # ---- Indicadores ----
    def indicadores(self):
        print("\n=== Indicadores de Energia ===")
        total = len(self.simulacoes)
        if total == 0:
            print("Ainda não há simulações de energia registradas.")
            return
        claras = sum(1 for s in self.simulacoes if s["clara"])
        uteis = sum(1 for s in self.simulacoes if s["util"])
        tempo = sum(s["tempo_segundos"] for s in self.simulacoes) / total
        print(f"Simulações registradas: {total}")
        for tipo in ("aparelho", "banho", "bandeira"):
            print(f"  - {tipo}: {sum(1 for s in self.simulacoes if s['tipo'] == tipo)}")
        print(f"Explicação clara: {claras / total * 100:.1f}%")
        print(f"Útil para decidir: {uteis / total * 100:.1f}%")
        print(f"Tempo médio por simulação: {tempo:.1f} s")
