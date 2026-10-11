# Combate e animação: moveset, dano e tempos de inimigos e chefes

## Sumário
1. Vocabulário de tempo
2. Onde estão os tempos, por engine
3. Onde estão o dano e a escolha do golpe
4. Ficha do inimigo
5. "Qual golpe dá mais dano"
6. Conferir no jogo

## 1. Vocabulário de tempo
- **Preparação** (startup, "delay"): do início da animação até o golpe começar a acertar.
- **Ativo**: quanto tempo a área de acerto fica ligada.
- **Recuperação**: do fim do ativo até o inimigo poder agir de novo. É a janela de punir.
- Tempo real = tempo na animação / velocidade da animação (velocidade do estado, multiplicadores
  da IA, efeitos de lentidão). Em quadros: segundos x taxa de lógica do jogo (muitas vezes 60 ou
  30; ache a do jogo, não a do monitor).
- Esquiva do jogador também tem janela de invencibilidade, nos mesmos arquivos de animação do
  personagem. Compare as duas para dizer se um golpe é esquivável e com quanta folga.

## 2. Onde estão os tempos, por engine
| Engine | Onde |
|---|---|
| Unity | Clipes de animação (exportados pelo AssetRipper como `.anim`, texto): taxa de amostragem, duração e eventos de animação com o tempo em segundos e o nome da função chamada (ex.: algo como "AtivarHitbox" ou "AttackStart"). O Animator Controller tem a velocidade de cada estado e as transições. Às vezes as janelas ficam em ScriptableObjects de ataque, e não em eventos. |
| Unreal | AnimSequence e AnimMontage (FModel): duração, taxa de reprodução e a lista de notifies com o tempo de cada um. Janelas de acerto, de esquiva e de invencibilidade costumam ser notify states com início e duração. Habilidades no Gameplay Ability System trazem custo, recarga e os efeitos de dano em assets próprios. |
| Godot | Recursos de animação do AnimationPlayer: duração, passo e trilhas com chamada de método ou propriedade (ex.: ligar a área de acerto) no tempo de cada chave. |
| 2D por quadros | Sprites com duração por quadro e quadros marcados como ativos nas tabelas de ataque do jogo. |

Se a janela vem de código (ex.: um temporizador no script do ataque), leia o método; o nome do
evento sozinho é `inferido`.

## 3. Onde estão o dano e a escolha do golpe
- **Dano**: tabelas de ataque ou de habilidade do inimigo (dano base, multiplicador, tipo de dano,
  dano de postura ou atordoamento), escalado por nível e dificuldade. Aplique as fórmulas de defesa
  do jogador (ficha em `mecanicas/`) para dar o dano final contra a defesa informada.
- **Escolha**: árvore de comportamento ou máquina de estados da IA: distância, ângulo, peso de
  cada golpe, recarga própria do golpe, combos encadeados, e mudança de fase por porcentagem de
  vida ou por tempo.

## 4. Ficha do inimigo (`inimigos/<nome>.md`)
```
# <Nome> — versão <x.y.z>
Vida, defesas e resistências: <por dificuldade/nível>
Fases: <gatilho de cada fase e o que muda>

| Golpe | Dano (vs defesa D) | Tipo | Preparação | Ativo | Recuperação | Esquiva | Alcance | Quando usa | Peso | Fase | Fonte | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <nome> | <número> | <físico/fogo…> | <q / s> | <q> | <q> | <janela e direção> | <m> | <condição> | <%> | <1/2> | <arquivo> | <status> |

Combos: <sequências possíveis e chance>
Como punir: <golpes com maior recuperação>
```

## 5. "Qual golpe dá mais dano"
Diga em três réguas, porque a resposta muda:
1. Dano por acerto (o golpe mais forte isolado).
2. Dano esperado por uso (dano x chance de acertar todos os hits do golpe ou combo).
3. Ameaça na luta (dano esperado x frequência com que a IA escolhe o golpe naquela fase).

## 6. Conferir no jogo
Grave a luta a 60 quadros por segundo e conte os quadros de preparação e recuperação de dois ou
três golpes. Compare o dano tomado com a ficha, com a defesa do personagem anotada. O que bater vira
`confirmado` com teste; o que só foi medido é `medido-jogando`.
