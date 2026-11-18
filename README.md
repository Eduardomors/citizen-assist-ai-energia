# Citizen Assist AI - Energia no primeiro emprego

Módulo de **energia e sustentabilidade** do Citizen Assist AI, o assistente em Python que orienta **jovens que estão no primeiro emprego ou estágio**. Ele mostra quanto cada aparelho gasta, compara alternativas para reduzir o gasto com o banho (incluindo energia solar) e explica tudo com dados, fontes e limitações.

> Global Solution 2026.2 - **Soluções em Energias Renováveis e Sustentáveis** (FIAP, Ciência da Computação, 1CCPX)
> O assistente base (busca por pontuação, histórico, indicadores) foi feito em Pensamento Computacional e Automação com Python. **A contribuição desta disciplina está nos arquivos marcados com ⚡ na estrutura abaixo.**

## Integrantes

| Nome | RM |
|---|---|
| Brenno Ferreira Gomes dos Santos | 570525 |
| Eduardo Moreira Silva | 569923 |

## Público e problema

**Público:** jovens de 14 a 24 anos que começaram a trabalhar ou estagiar. Com o primeiro salário, muitos passam a ajudar nas contas de casa ou vão morar sozinhos e dividir aluguel.

**Problema:** a conta de luz chega alta e ninguém sabe o motivo. O maior vilão costuma ser o **chuveiro elétrico** (cerca de 5.500 W e, em média, 24% do consumo das casas brasileiras). Na internet circulam promessas de economia sem conta nenhuma ("energia solar zera sua conta"), e o jovem não tem como saber o que vale a pena para a casa dele.

**Como ajudamos:** o assistente calcula o gasto do banho com os números da casa e compara, para o mesmo período (1 ano), três alternativas: mudar o hábito, instalar aquecedor solar e assinar energia solar. Depois recomenda o que faz sentido para quem tem casa própria e para quem mora de aluguel.

## Funcionalidades de energia

No menu principal, opção **5. Energia: calcular e economizar na conta de luz**:

1. **Quanto gasta um aparelho?** Escolha um aparelho (ou digite a potência da etiqueta) e veja kWh, R$ por mês e por ano e CO2, com a conta mostrada passo a passo.
2. **Banho da casa: comparar alternativas.** Informe pessoas, banhos por dia, minutos de banho, potência do chuveiro e preço do kWh da sua conta. O assistente mostra um resumo com o gasto de hoje e as recomendações; a tabela comparativa completa aparece se você pedir.
3. **Quanto a bandeira tarifária pesa na minha conta?** Acréscimo das bandeiras amarela, vermelha 1 e vermelha 2 para o seu consumo.
4. **Ver dados, fontes e limitações.** Lista cada premissa com valor, unidade, tipo (oficial ou estimado) e fonte.

Também foram incluídas **8 orientações na categoria Energia** da base de conhecimento. Elas respondem perguntas em texto livre (menu 1), por exemplo "minha conta de luz tá alta", "vale a pena aquecedor solar?", "moro de aluguel, tem energia solar?", "o que é bandeira vermelha", "tarifa social" e "a conta aumentou sem eu mudar nada", e citam os números da análise.

Cada simulação pergunta se a explicação ficou clara e se ajuda a decidir algo. As respostas ficam em `data/simulacoes_energia.json` e entram nos indicadores (menu 3), sem nenhum dado pessoal.

## Como executar

Requisito: Python 3.10 ou superior. Não usa bibliotecas externas.

```bash
git clone https://github.com/Eduardomors/citizen-assist-ai-energia.git
cd citizen-assist-ai-energia
python main.py              # assistente (opção 5 = Energia)
python analise_energia.py   # refaz todos os cálculos e gera os CSV da análise
```

**Teste rápido:** menu 5 > 2 > 4 pessoas > Enter (1 banho) > Enter (12 min) > Enter (5.500 W) > Enter (R$ 1,04) > s > s (ver tabela). Deve aparecer a tabela da seção "Cálculos e comparação" abaixo.

## Estrutura

```
citizen-assist-ai-energia/
├── README.md
├── main.py                      # menu principal (opção 5 = Energia)
├── assistente.py                # classe Assistente (PCP)
├── base_conhecimento.py         # busca por pontuação (PCP)
├── orientacao.py                # exibe orientações (ajustada para a categoria Energia)
├── energia.py                   ⚡ cálculos, comparação, recomendações e menu de energia
├── analise_energia.py           ⚡ gera a análise e os CSV
├── data/
│   ├── base_conhecimento.json   # 22 orientações (⚡ ids 15 a 22 = categoria Energia)
│   ├── energia_premissas.json   ⚡ dados, unidades, origem, fonte e tipo de cada premissa
│   ├── aparelhos.json           ⚡ potências típicas (estimadas)
│   └── historico.json
└── docs/energia/                ⚡
    ├── ANALISE_ENERGIA.md       # contexto, dados, cálculos, comparação, impactos, referências
    ├── comparacao_alternativas.csv
    ├── sensibilidade.csv
    └── TESTES_USUARIOS.md       # situações testadas, comentários e ajustes
```

## Dados e premissas

Período de referência: **1 ano**. Tarifa padrão: **R$ 1,04/kWh**, calculada a partir da tarifa residencial B1 da Enel SP homologada pela ANEEL (R$ 0,72518 em 2025 + reajuste de 9,02% em 2026) com ICMS de 18% e PIS/COFINS estimados em 5,9%. O usuário pode digitar o valor da própria conta.

Cada premissa está em `data/energia_premissas.json` marcada como **oficial** (ANEEL, EPE) ou **estimado** (premissa da equipe ou faixa de mercado). A tabela completa, com fontes, está em [docs/energia/ANALISE_ENERGIA.md](docs/energia/ANALISE_ENERGIA.md).

## Cálculos e comparação

Conceitos usados: **potência x energia** (kWh = kW × h), **Q = m · c · ΔT** para conferir a vazão de água que o chuveiro consegue aquecer (≈ 3,9 L/min), **fração solar**, **retorno do investimento** e **fator de emissão** da rede.

**Cenário de referência:** 4 pessoas, banho de 12 min, chuveiro de 5.500 W, 1 ano.

| Alternativa | kWh/ano | R$/ano | Economia/ano | Investimento | Retorno | CO2 evitado |
|---|---|---|---|---|---|---|
| Situação atual (chuveiro elétrico) | 1.606 | 1.670 | - | - | - | - |
| A) Banho de 8 min + posição verão | 910 | 946 | R$ 724 (43%) | R$ 0 | imediato | 41,7 kg |
| B) Aquecedor solar de água (renovável) | 482 | 501 | R$ 1.169 (70%) | R$ 3.000-6.000 | 2,6 a 5,1 anos | 67,3 kg |
| C) Energia solar por assinatura (renovável) | 1.606 | 1.420 | R$ 251 (15%) | R$ 0 | imediato | - |
| A + B juntos | 273 | 284 | R$ 1.386 (83%) | R$ 3.000-6.000 | 2,2 a 4,3 anos | 79,8 kg |

Para quem mora sozinho, o aquecedor solar leva de 10 a 30 anos para se pagar, então o assistente não o recomenda nesse caso. Veja a análise de sensibilidade em [ANALISE_ENERGIA.md](docs/energia/ANALISE_ENERGIA.md#36-sensibilidade-o-aquecedor-solar-não-serve-para-todo-mundo).

## Recomendações e justificativas

1. **Sempre começar pelo hábito:** não custa nada e corta quase metade do gasto com banho.
2. **Casa própria (ou com autorização do dono) e 3 pessoas ou mais:** pesquisar o aquecedor solar. É a maior economia e se paga bem antes do fim da vida útil dos coletores (15+ anos).
3. **Quem mora de aluguel:** energia solar por assinatura, sem obra. Não reduz o consumo, e o contrato precisa ser lido com cuidado (prazo, multa, consumo mínimo).

**Impacto ambiental:** como a eletricidade brasileira já é muito renovável (59,9 kg CO2eq/MWh), o CO2 evitado é pequeno, e nós dizemos isso. O ganho maior é tirar carga do horário de pico do início da noite, economizar água (cerca de 23 mil litros por ano com banhos mais curtos) e usar uma fonte renovável no lugar da resistência elétrica. Detalhes, incluindo fabricação e descarte do aquecedor, na análise.

## Limitações

- Os resultados são **estimativas**, não economia garantida. Dependem do uso real, do clima e da tarifa do mês.
- A tarifa padrão vale para a área da Enel SP e muda todo ano (reajuste) e todo mês (bandeira, PIS/COFINS).
- A fração solar de 70% é um valor de projeto: sombra, dias nublados e instalação ruim reduzem a economia.
- Preços de aquecedor e descontos de assinatura variam por empresa. Não consideramos juros, manutenção, custo da água nem obras extras.
- O assistente não substitui um instalador nem a leitura completa de um contrato, e **não é um canal oficial**.

## Testes com usuários

Testamos pessoalmente com **3 pessoas de fora da equipe**, em 6 situações do dia a dia. Todas acharam a explicação clara e útil (nota média de facilidade 4,0 de 5), mas duas acharam a tabela pesada, e os testes revelaram 8 problemas, todos corrigidos. Os principais: a simulação passou a mostrar um resumo antes da tabela, a perguntar quantos banhos cada pessoa toma por dia e a explicar por que a conta pode subir sem mudança de hábito. Detalhes em [docs/energia/TESTES_USUARIOS.md](docs/energia/TESTES_USUARIOS.md).

## Referências

Lista completa, com links, em [docs/energia/ANALISE_ENERGIA.md](docs/energia/ANALISE_ENERGIA.md#7-referências-acessadas-em-18112026). Principais: ANEEL (reajuste Enel SP 2026 e bandeiras), EPE (Balanço Energético Nacional 2025), Idec (aquecedor solar e dicas de economia), ABNT NBR 15569 (via estudo da UFRGS) e Eletrobras/Procel (Pesquisa de Posses e Hábitos).

## Vídeo técnico

[link do vídeo no YouTube - não listado]
