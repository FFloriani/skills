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

## 6. Conferência antes de recomendar
- A build campeã faz sentido diante das builds fortes conhecidas da comunidade? Se diverge muito,
  procure o erro (grupo de bônus, teto, ordem) antes de anunciar descoberta.
- Teste no jogo: o número da ficha do personagem e o dano no boneco batem com a calculadora?
