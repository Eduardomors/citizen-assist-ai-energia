# Testes com usuários - módulo de Energia

## Como testamos

- **Participantes:** 3 pessoas de fora da equipe (P1, P2 e P3).
- **Data e local:** 18/11/2026, **pessoalmente**, no computador da equipe. Cada participante usou o teclado e o programa sozinho; a equipe só leu as situações, observou e anotou.
- A equipe **não disse** quais palavras usar nem em qual menu clicar. Quando o participante não sabia um valor, a única orientação foi "pode apertar Enter".
- **Privacidade:** não registramos nome, idade, endereço, valor da conta nem outro dado pessoal. Um texto com dado pessoal foi colado por engano no programa durante os testes; esse registro foi apagado do `data/historico.json` e não entra nos indicadores.
- Cada participante fez **2 situações**, e as 6 situações foram testadas.
- Ao fim de cada simulação, o próprio programa perguntou se a explicação ficou clara e se ajuda a decidir algo; ao sair, cada participante deu uma nota de facilidade de 1 a 5. Os registros estão em `data/simulacoes_energia.json` e `data/historico.json`.

## Situações testadas

| # | Situação lida para o participante | O que esperávamos |
|---|---|---|
| S1 | "A conta de luz da sua casa veio alta. Usa o programa pra descobrir o porquê." | Chegar a uma orientação que explique o gasto. |
| S2 | "Quanto custa por ano o banho da sua casa? Usa os números da sua casa." | Usar o menu 5 > 2 e entender o resultado. |
| S3 | "Seu tio disse que aquecedor solar se paga rápido. É verdade pra sua casa?" | Ver o retorno em anos para a própria casa. |
| S4 | "Você vai dividir um apartamento alugado. Dá pra usar energia solar?" | Chegar na energia solar por assinatura. |
| S5 | "Quanto gasta o videogame ou o computador ligado todo dia?" | Usar o menu 5 > 1 e entender a conta em kWh. |
| S6 | "A conta veio dizendo 'bandeira vermelha'. O que é isso?" | Entender a bandeira e quanto ela pesa na conta. |

## Resultados

| Part. | Sit. | O que fez | Encontrou? | Clara? | Útil? | Comentário do participante |
|---|---|---|---|---|---|---|
| P1 | S1 | Menu 1: perguntou por que a conta veio quase R$ 200 mais cara sem mudar a rotina nem comprar aparelhos | Sim, disse que respondeu (orientação do chuveiro, confiança ALTA) | - | - | "Não mudaria nada" |
| P1 | S2 | Escreveu a dúvida em texto no menu de Energia (2 vezes "Opção inválida"), depois menu 5 > 2; digitou "4 pessoas.", 15 min, "5500 W (5,5 kW)." (recusado) e depois 5500 | Sim (depois de reabrir o programa, que fechou por um atalho do teclado) | Sim | Sim | Entendeu, mas achou **muita informação** |
| P2 | S4 | Menu 5 > 2; disse que não pode instalar nada | Sim: recomendou a energia solar por assinatura | Sim | Sim | Entendeu, mas a **tabela tem um design estranho e é confusa** |
| P2 | S5 | Voltou ao menu principal e entrou de novo no 5 > 1 > Videogame; trocou o uso padrão pelo dela (4 h/dia, 27 dias) | Sim: R$ 16,85 por mês | Sim | Sim | "Sim, entendi o que o assistente disse" |
| P3 | S3 | Menu 5 > 2 (3 pessoas, 15 min, pode instalar) | Sim: aquecedor se paga em 2,7 a 5,5 anos | Sim | Sim | "Entendi a comparação de kWh, custo e economia, muito bom" |
| P3 | S6 | Voltou ao menu principal e entrou de novo no 5 > 3 | Sim: + R$ 8,93 no mês na vermelha 1 para 200 kWh | Sim | Sim | "As respostas são bem claras" |

**Notas de facilidade (1 a 5):** P1 = 3, P2 = 4, P3 = 5 (média 4,0).

### Indicadores registrados pelo programa (menu 3)

| Indicador | Resultado |
|---|---|
| Perguntas em texto livre (menu 1) | 1 atendimento, resposta encontrada em 100%, ajudou em 100%, 2 tentativas, 454,6 s |
| Simulações de energia | 5 (3 de banho, 1 de aparelho, 1 de bandeira) |
| Explicação clara | 100% |
| Útil para decidir | 100% |
| Tempo médio por simulação | 90,3 s |
| Facilidade de uso | 4,0 (3 avaliações) |

## Problemas observados e ajustes feitos

| # | Problema observado (quem) | Ajuste feito |
|---|---|---|
| 1 | **Tabela confusa e com muita informação** (P1 e P2) | A simulação do banho agora mostra primeiro um **resumo** (quanto o banho custa hoje) e as recomendações; a tabela completa só aparece se a pessoa pedir. A legenda passou a explicar também a coluna "Economia". |
| 2 | Quem **não pode instalar** nada via o aquecedor solar na tabela, com retorno em anos (observado no teste da P2) | Quando a pessoa responde "n", a tabela esconde o aquecedor solar e avisa por quê. |
| 3 | O programa considerava **1 banho por dia**; a P1 toma 2 e não percebeu que o gasto real dela era o dobro do mostrado | Nova pergunta: "Quantos banhos cada pessoa toma por dia?" (Enter = 1). |
| 4 | A pergunta da P1 era sobre um **aumento sem mudar a rotina**, mas a resposta falou do chuveiro em geral, com confiança ALTA | Nova orientação "A conta de luz aumentou sem eu mudar nada" (bandeira, reajuste, dias cobrados, frio, aparelho com defeito, revisão da leitura). A mesma pergunta agora cai nela. |
| 5 | A P1 escreveu a dúvida em texto no menu e só recebeu "Opção inválida" | A mensagem agora explica que ali vai só o número da opção e que a dúvida em texto vai na opção 1 do menu principal. |
| 6 | "5500 W (5,5 kW)." foi recusado (P1) | O programa passou a ignorar o que vem entre parênteses e o ponto final. |
| 7 | P2 e P3 voltaram ao menu principal para fazer a segunda simulação, sem precisar | Depois de cada simulação aparece: "Você continua no menu de Energia: escolha outra opção ou 0 para voltar." |
| 8 | A tela da bandeira não mostrava a vermelha patamar 2 (a mais cara) | Incluída a vermelha 2 (R$ 7,877 a cada 100 kWh) e o aviso de que a bandeira do mês aparece na conta. |

## O que aprendemos

As três pessoas entenderam as explicações e acharam o assistente útil, mas **duas acharam a tabela pesada**. Mostrar primeiro o resumo e a recomendação, e deixar a tabela como opcional, ficou mais adequado ao nosso público. O teste também mostrou que as pessoas **não seguem o roteiro que imaginamos**: escrevem frases nos menus, digitam números com unidades e têm hábitos que não tínhamos previsto (2 banhos por dia). O erro mais grave, o banho contado pela metade, **ninguém percebeu**, e só apareceu porque comparamos o que a pessoa disse com o que o programa calculou.

**Limitação:** foram 3 participantes em um único dia, sem novo teste depois dos ajustes.
