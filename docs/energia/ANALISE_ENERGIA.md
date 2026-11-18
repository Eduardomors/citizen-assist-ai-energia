# Análise de energia - banho quente com chuveiro elétrico

Contribuição de **Soluções em Energias Renováveis e Sustentáveis** ao Citizen Assist AI.
Todos os números abaixo são gerados por `python analise_energia.py` (arquivos `comparacao_alternativas.csv` e `sensibilidade.csv` nesta pasta). Dados verificados em 18/11/2026.

## 1. Contexto

**Público:** jovens de 14 a 24 anos que estão conseguindo o primeiro emprego ou estágio. Com o primeiro salário, muitos passam a ajudar com as contas de casa (ou vão morar sozinhos ou dividir apartamento) e recebem a primeira conta de luz sem saber de onde vem o valor.

**Necessidade energética:** água quente para o banho. O chuveiro elétrico é o aparelho de maior potência da casa (cerca de 5.500 W) e, segundo a Pesquisa de Posses e Hábitos da Eletrobras/Procel, responde em média por 24% do consumo residencial no Brasil. É onde uma mudança traz mais resultado.

**Como as orientações ajudam:** o assistente mostra, com os números da própria casa, quanto o banho custa por ano e compara alternativas para a mesma necessidade, dizendo qual faz sentido para quem tem casa própria e para quem mora de aluguel.

## 2. Dados e premissas

Todos os valores ficam em `data/energia_premissas.json`, com unidade, origem, fonte e tipo (**oficial** ou **estimado**). Os principais:

| Dado | Valor | Tipo | Origem |
|---|---|---|---|
| Tarifa B1 Enel SP 2025 (sem tributos) | R$ 0,72518/kWh | Oficial | ANEEL, reajuste 2025 |
| Reajuste B1 Enel SP 2026 | 9,02% (desde 04/07/2026) | Oficial | ANEEL, 30/06/2026 |
| ICMS | 18% | Estimado | Alíquota mais comum nas contas residenciais (pode ser 12% em contas menores) |
| PIS/COFINS | 5,9% | Estimado | Varia todo mês |
| Potência do chuveiro | 5.500 W | Estimado | Modelo mais comum (Idec) |
| Redução na posição verão | 30% | Oficial | Idec |
| Meses na posição verão | 6 por ano | Estimado | Premissa da equipe (out a mar) |
| Meta de tempo de banho | 8 min | Estimado | Cartilha Cemig |
| Fração solar do aquecedor | 70% | Estimado | Valor de projeto da NBR 15569; estudo UFRGS |
| Preço do aquecedor solar | R$ 3.000 a 6.000 | Estimado | Idec |
| Vida útil dos coletores | 15 anos | Estimado | Idec (15 a 25 anos) |
| Desconto da assinatura solar | 10% a 20% (média 15%) | Estimado | Folhapress |
| Fator de emissão da rede | 0,0599 kg CO2eq/kWh | Oficial | BEN 2025 (EPE), ano-base 2024 |
| Bandeiras amarela / vermelha 1 / vermelha 2 | R$ 1,885 / R$ 4,463 / R$ 7,877 por 100 kWh | Oficial | ANEEL |

**Cenário de referência (premissa da equipe):** casa com 4 pessoas, 1 banho por pessoa por dia, de 12 minutos, chuveiro de 5.500 W, **período de 1 ano (365 dias)**. Para o aquecedor solar também olhamos 10 anos. No assistente, a pessoa troca esses valores pelos dela.

## 3. Cálculos

### 3.1 Tarifa
- Tarifa 2026 sem tributos = 0,72518 × (1 + 0,0902) = **R$ 0,7906/kWh**
- ICMS e PIS/COFINS são cobrados "por dentro", então: preço final = 0,7906 ÷ (1 − 0,18 − 0,059) = **R$ 1,04/kWh**
- Se a pessoa digitar o "Preço unit. com tributos" da conta dela, o assistente usa esse valor.

### 3.2 Potência x energia
Energia (kWh) = Potência (kW) × tempo (h).
- 1 banho de 12 min: 5,5 kW × 0,2 h = **1,1 kWh ≈ R$ 1,14**
- Situação atual: 4 pessoas × 0,2 h × 365 dias × 5,5 kW = **1.606 kWh/ano ≈ R$ 1.670/ano** (134 kWh por mês)

### 3.3 Conferência física (Q = m · c · ΔT)
Toda a potência do chuveiro vira calor na água (resistência elétrica, eficiência ≈ 100%). Para aquecer a água em 20 °C:
vazão = P ÷ (c · ΔT) = 5.500 ÷ (4.186 × 20) = 0,0657 kg/s ≈ **3,9 L/min**.
Isso também permite estimar a água economizada quando o banho fica mais curto.

### 3.4 Alternativas (mesma necessidade, mesmo período)

- **A) Hábito:** banho de até 8 min e posição verão em 6 meses do ano.
  4 × (8/60) h × 365 × 5,5 kW = 1.071 kWh; com a posição verão: 1.071 × (0,5 × 0,7 + 0,5 × 1) = **910 kWh/ano**
- **B) Aquecedor solar de água (renovável):** o sol cobre 70% da energia e o chuveiro faz o resto.
  1.606 × (1 − 0,70) = **482 kWh/ano**
- **C) Energia solar por assinatura (renovável):** o consumo continua 1.606 kWh, mas a conta tem 15% de desconto.
  1.670 × (1 − 0,15) = **R$ 1.420/ano**
- **A + B juntos:** 910 × 0,30 = **273 kWh/ano**

Retorno do investimento = investimento ÷ economia anual. CO2 evitado = kWh economizados × 0,0599.

### 3.5 Resultado (cenário de referência, 1 ano)

| Alternativa | kWh/ano | R$/ano | Economia/ano | Investimento | Retorno | CO2 evitado | Água economizada |
|---|---|---|---|---|---|---|---|
| Situação atual | 1.606 | 1.670 | - | - | - | - | - |
| A) 8 min + posição verão | 910 | 946 | **R$ 724** (43%) | R$ 0 | imediato | 41,7 kg | ~23 mil L |
| B) Aquecedor solar | 482 | 501 | **R$ 1.169** (70%) | R$ 3.000-6.000 | 2,6 a 5,1 anos | 67,3 kg | - |
| C) Solar por assinatura | 1.606 | 1.420 | **R$ 251** (15%) | R$ 0 | imediato | 0 (no cálculo) | - |
| A + B | 273 | 284 | **R$ 1.386** (83%) | R$ 3.000-6.000 | 2,2 a 4,3 anos | 79,8 kg | ~23 mil L |

### 3.6 Sensibilidade: o aquecedor solar não serve para todo mundo

| Pessoas | Banho 8 min | Banho 12 min |
|---|---|---|
| 1 | 15,4 a 30,8 anos | 10,3 a 20,5 anos |
| 2 | 7,7 a 15,4 anos | 5,1 a 10,3 anos |
| 3 | 5,1 a 10,3 anos | 3,4 a 6,8 anos |
| 4 | 3,8 a 7,7 anos | 2,6 a 5,1 anos |
| 5 | 3,1 a 6,2 anos | 2,1 a 4,1 anos |

Para quem mora sozinho, o aquecedor pode levar mais tempo para se pagar do que a vida útil dos coletores (15 anos). Por isso o assistente **não** recomenda o aquecedor quando o retorno passa da vida útil.

## 4. Justificativa das recomendações

| Critério | A) Hábito | B) Aquecedor solar | C) Assinatura |
|---|---|---|---|
| Custo | Nenhum | R$ 3.000 a 6.000 | Nenhum (mensalidade embutida no desconto) |
| Economia | Média (43%) | Alta (70%) | Baixa (10-20%) |
| Viabilidade para o nosso público | Alta: depende só de combinar com a família | Média/baixa: precisa de telhado, caixa d'água e autorização do dono; o jovem raramente decide sozinho | Alta para quem aluga, mas exige contrato e conta no nome de alguém |
| Reduz o consumo? | Sim | Sim | Não (só muda de onde vem a energia e o preço) |
| Riscos | Voltar ao hábito antigo | Dias nublados, manutenção, instalação ruim | Multa de cancelamento, consumo mínimo, mudança de regras (ANEEL revisando em 2026) |

Por isso a ordem das recomendações é:
1. **Sempre começar pelo hábito (A):** custo zero, retorno imediato e já reduz quase metade do gasto do banho.
2. **Casa própria (ou com autorização) e família de 3+ pessoas:** pesquisar o **aquecedor solar (B)**, que dá a maior economia e se paga bem antes do fim da vida útil.
3. **Quem mora de aluguel ou não pode mexer no imóvel:** **energia solar por assinatura (C)**, lendo o contrato com cuidado.

## 5. Impactos ambientais

- **Emissões:** a eletricidade brasileira é muito renovável (59,9 kg CO2eq por MWh em 2024). Por isso o CO2 evitado é pequeno: 42 a 80 kg por ano na casa de referência. Não exageramos esse número.
- **Pico de consumo:** o maior ganho ambiental do aquecedor solar e do banho mais curto é aliviar o horário de pico (início da noite), quando muitos chuveiros ligam ao mesmo tempo e o sistema pode precisar de usinas térmicas, mais caras e poluentes.
- **Água:** banhos mais curtos economizam cerca de 23 mil litros por ano na casa de referência.
- **Fabricação e descarte:** o aquecedor solar usa cobre, alumínio, vidro e isolantes. A vida útil longa (15 a 25 anos) compensa esse impacto, mas o descarte precisa ser correto.
- **Assinatura solar:** não diminui o consumo; o benefício ambiental é financiar usinas renováveis. A usina ocupa área de terreno.

## 6. Limitações

- São estimativas para 1 ano, **não resultados garantidos**. A economia real depende do uso, do clima e da tarifa do mês.
- A tarifa muda todo ano (reajuste) e todo mês (bandeira e PIS/COFINS). A tarifa padrão vale para a área da Enel SP.
- Os 70% de fração solar são um valor de projeto. Instalação ruim, sombra ou dias nublados reduzem a economia.
- Preços e descontos variam por empresa; não consideramos juros, manutenção, custo da água nem obras extras.
- O assistente não substitui a avaliação de um instalador ou a leitura completa de um contrato.

## 7. Referências (acessadas em 18/11/2026)

- ANEEL / Cenário Energia - Reajuste Enel SP 2026 (B1 9,02%): https://cenarioenergia.com.br/2026/06/30/aneel-aprova-reajuste-da-enel-sao-paulo-com-efeito-medio-de-1018/
- Exame - Tarifa B1 Enel SP 2025 (R$ 725,18/MWh): https://exame.com/economia/conta-de-luz-sp-aumento-enel-reajuste-tarifa-aneel-julho
- Lei Complementar 194/2022 (ICMS sobre energia): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp194.htm
- Idec - Economia com aquecedor solar (preço, vida útil, retorno): https://idec.org.br/dicas-e-direitos/economia-com-aquecedor-solar
- Idec - Como economizar energia elétrica (posição verão -30%): https://idec.org.br/consultas/dicas-e-direitos/saiba-como-economizar-energia-eletrica
- Cemig - Cartilha de eficiência energética: https://www.cemig.com.br/wp-content/uploads/2025/09/Cartilha-Eficiencia-Energetica-Saiba-como-economizar-energia.pdf
- UFRGS (Ambiente Construído) - Aquecedor solar x chuveiro elétrico, NBR 15569: https://seer.ufrgs.br/ambienteconstruido/article/download/25706/21162
- Revista Brasileira de Energia Solar - Chuveiro = 24% do consumo residencial (PPH Eletrobras/Procel): https://rbens.emnuvens.com.br/rbens/article/download/67/67/133
- Folhapress / Acessa - Energia solar por assinatura (10% a 20%): https://www.acessa.com/economia/2023/06/amp/154724-veja-os-pros-e-contras-do-servico-de-energia-solar-por-assinatura.html
- O Setor Elétrico - BEN 2025 (59,9 kg CO2eq/MWh): https://www.osetoreletrico.com.br/?p=164398
- Bandeira amarela 2026 (R$ 1,885/100 kWh) e bandeira verde em novembro: https://tagdlaw.com.br/?p=16921
- Canal Solar - Bandeira vermelha 1 (R$ 4,463/100 kWh): https://canalsolar.com.br/conta-luz-ficara-mais-cara-sao-paulo/
- Diário do Comércio / Folhapress - Bandeira vermelha 2 (R$ 7,877/100 kWh): https://diariodocomercio.com.br/economia/conta-luz-aumenta-bandeira-vermelha-economizar/
- Idec - Você entende sua conta de luz? (dias cobrados e leitura): https://idec.org.br/print/26995
