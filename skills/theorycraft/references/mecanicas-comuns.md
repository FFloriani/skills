# Mecânicas comuns: o que procurar e como conferir

Checklist dos sistemas que decidem build. Para cada um: ache no código onde o número é usado
(busque por nomes como Damage, Calc, Modifier, Stat, Formula, Resist, Crit, Armor e pelos nomes das
colunas das tabelas), escreva a ficha em `mecanicas/<sistema>.md` e crie casos de teste na
calculadora com números vistos no jogo.

## Sumário
1. Dano e grupos de bônus
2. Crítico
3. Velocidade, recarga e breakpoints
4. Defesa, resistência e vida efetiva
5. Penetração e ordem das reduções
6. Dano ao longo do tempo e efeitos
7. Procs e gatilhos
8. Escalamento por nível e dificuldade
9. Aleatoriedade, drop e progressão
10. Arredondamento e limites

## 1. Dano e grupos de bônus
- Bônus no mesmo grupo somam; grupos diferentes multiplicam. Muitos jogos têm "aumentado"
  (soma) e "mais" (multiplica). Errar isso inverte rankings de build.
- Anote a ordem: base, conversão de tipo de dano, bônus planos, bônus percentuais, multiplicadores
  finais, mitigação do inimigo.
- Conferir: some um bônus pequeno de cada grupo e veja se o dano no boneco sobe na proporção
  esperada pelo modelo.

## 2. Crítico
- Chance com teto? Multiplicador base e se os bônus somam ao multiplicador ou multiplicam.
- Crítico pode ser rolado por acerto, por projétil ou por tick de dano ao longo do tempo.
- Conferir: média de muitos acertos contra o valor esperado `1 + chance x (mult - 1)`.

## 3. Velocidade, recarga e breakpoints
- Ataque e animação costumam durar um número inteiro de quadros: velocidade só ajuda ao cruzar
  um breakpoint. Ache a taxa de quadros da lógica (não a do monitor).
- Redução de recarga costuma acumular multiplicando `1 - produto(1 - r)`, às vezes com teto.
- Conferir: meça com cronômetro ou contando quadros em vídeo antes e depois do breakpoint.

## 4. Defesa, resistência e vida efetiva
- Formas comuns: `a / (a + k)` (k pode depender do nível do atacante), redução percentual com teto,
  retornos decrescentes `1 - e^(-x/k)`, tabelas por faixa.
- Várias reduções costumam multiplicar entre si: `total = 1 - produto(1 - r_i)`.
- Vida efetiva = vida / (1 - redução total), separada por tipo de dano quando as reduções diferem.
- Conferir: tome dano de um ataque conhecido com e sem o item de defesa.

## 5. Penetração e ordem das reduções
- Penetração reduz a defesa do alvo antes da curva; redução de resistência pode ir abaixo de zero.
- A ordem (plano antes do percentual, penetração antes ou depois do teto) muda tudo. Só vale a do
  código.

## 6. Dano ao longo do tempo e efeitos
- Taxa de tick, se o dano é calculado ao aplicar (snapshot) ou a cada tick, se acumula ou renova.
- Efeitos com acúmulo (veneno, sangramento, choque): teto de pilhas e o que acontece ao reaplicar.

## 7. Procs e gatilhos
- Chance de proc, recarga interna, coeficiente por habilidade, se proc pode gerar outro proc.
- Conferir com muitas repetições e intervalo de confiança, não com uma tentativa.

## 8. Escalamento por nível e dificuldade
- Vida, dano e defesa dos inimigos por nível; multiplicadores de dificuldade; penalidade por
  diferença de nível. Quase sempre há uma tabela ou curva para isso.

## 9. Aleatoriedade, drop e progressão
- Tabelas de drop com peso, proteção contra azar (pity), distribuição pseudoaleatória (a chance
  sobe a cada falha). Em jogo online o drop costuma ser do servidor.
- Curvas de XP e de custo: tabela ajustada à mão é comum; não force uma fórmula.

## 10. Arredondamento e limites
- Arredondar por acerto ou no total, para baixo ou para o mais próximo, int ou float: diferenças
  pequenas por acerto viram grandes em DPS.
- Tetos suaves (retorno diminui) e duros (para de subir). Teste a calculadora perto deles.

## Status de cada afirmação
`confirmado` (corpo do código lido), `inferido` (nome, assinatura, tooltip), `localizado-não-expandido`
(achou onde está, não leu) e `medido-jogando` (medido no jogo, com o método anotado).
