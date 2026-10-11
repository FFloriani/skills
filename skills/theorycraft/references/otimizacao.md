# Otimização de builds

## 1. Defina o problema antes de buscar
- **Objetivo**: DPS sustentado (luta longa), burst (janela curta), vida efetiva, tempo para matar
  um chefe, ou combinação. Escreva como uma função na calculadora.
- **Restrições**: nível, itens que o jogador tem ou consegue, slots, requisitos de atributo, limites
  de pontos, sets.
- **Premissas**: nível, defesa e resistências do inimigo, buffs e debuffs ativos, uptime de cada
  efeito, distância e tempo de reação. Todo resultado é "melhor sob estas premissas".
- Para equilibrar dano e sobrevivência, prefira "máximo DPS com vida efetiva mínima de X" a somar
  os dois com pesos inventados.

## 2. Escolha a busca pelo tamanho do problema
| Tamanho | Como buscar |
|---|---|
| até ~200 mil combinações | exaustiva (`buscar` da calculadora faz sozinha) |
| maior, slots quase independentes | feixe slot a slot (`buscar` troca sozinha), depois troca local |
| árvore de talentos ou pontos | guloso pelo ganho marginal por ponto, depois troca local para escapar de breakpoints |
| muito grande com regras de set | poda por limite superior: descarte ramos que mesmo no melhor caso perdem do atual |

Depois de qualquer busca não exaustiva, rode trocas locais (troque um item por vez) até não melhorar.

## 3. Pesos de atributo
- `pesos_de_atributo` mede quanto o objetivo sobe com +delta de cada atributo. Use deltas que o
  jogo realmente oferece (o valor típico de um item), não 1 ponto.
- Pesos mudam com a build: recalcule perto do resultado final.
- Saltos grandes num atributo indicam breakpoint ou teto; confira a curva desse atributo.

## 4. Sensibilidade
Refaça o ranking variando as premissas (inimigo com mais defesa, uptime menor, sem um buff). Build
que só vence numa premissa estreita deve vir com esse aviso.

## 5. Como apresentar
- A resposta primeiro: a build e o número que importa.
- Tabela com as melhores (top 3 a 5): itens, DPS, vida efetiva, diferença para a primeira.
- O detalhamento da campeã: cada fator da fórmula com seu valor.
- Pesos de atributo e breakpoints próximos.
- Premissas e o que ainda é `inferido` ou `medido-jogando`.

## 6. Combos e rotação
- **Dados de cada ação**: dano (já com as fórmulas do personagem), tempo até poder agir de novo,
  janelas de cancelamento (em que quadro dá para emendar o quê), recarga, custo e geração de
  recurso, buffs e debuffs que a ação aplica (duração, efeito) e bônus de combo.
- **Jogo de ação ou luta**: os cancelamentos formam um grafo (golpe → golpes que podem vir em
  seguida). Busque o caminho de maior dano, ou de maior dano por segundo, até o combo terminar
  (fim de cadeia, inimigo sai do alcance, limite de acertos ou de redução de dano por combo).
- **Rotação com recargas (MMO, ARPG)**: simule a luta em passos de tempo com uma lista de
  prioridade e compare variações; ou busque em feixe sobre as sequências possíveis numa janela de
  tempo (ex.: 30 s), e depois confirme a vencedora numa luta longa. Considere a manutenção de buffs,
  janelas de bônus do chefe e o recurso no fim (rotação que esvazia a mana só vale em luta curta).
- **Entregue**: o combo ou a lista de prioridade, o dano total e por segundo, o tempo de execução,
  a dificuldade (janelas apertadas em quadros) e uma versão mais fácil com a perda em porcentagem.

## 7. Rotina e diárias (MMO)
- **Liste as atividades**: nome, reset (diário, semanal, horário), limite de vezes, tempo gasto
  (medido pelo jogador; tempo de fila incluso), recompensa e pré-requisito. Converta recompensas
  para uma moeda comum (ouro, material raro, progresso) e diga a taxa usada.
- **Energia e estamina**: veja teto e regeneração nas tabelas. Energia que bate no teto é
  desperdício: o plano gasta antes de encher.
- **Plano para o tempo do dia**: ordene por valor por minuto e preencha o tempo disponível; com
  poucas atividades, escolha exata com mochila 0/1 (tempo = peso, valor = recompensa). Semanais
  entram no dia em que o valor por minuto delas for maior que o da diária que deslocam.
- **Entregue**: a ordem do dia com horário, tempo e recompensa esperada de cada passo, o que pular
  quando faltar tempo e o que muda se o jogador tiver mais ou menos minutos.
- Recompensa e chance de drop costumam ser do servidor: marque `medido-jogando` e diga a amostra.

## 8. Conferência antes de recomendar
- A build campeã faz sentido diante das builds fortes conhecidas da comunidade? Se diverge muito,
  procure o erro (grupo de bônus, teto, ordem) antes de anunciar descoberta.
- Teste no jogo: o número da ficha do personagem e o dano no boneco batem com a calculadora?
