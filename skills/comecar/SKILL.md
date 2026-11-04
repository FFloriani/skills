---
name: comecar
description: "Começa um projeto novo do jeito certo, com um comando. Estuda os produtos parecidos (o que acertaram, onde erraram, do que os usuários reclamam, armadilhas técnicas), manda uma única mensagem de decisões com a recomendação em cada uma, monta a base e constrói a versão 0.1 com a tela principal funcionando e conferida. Use com /comecar, /comecar rapido ou /comecar pesquisa, e sempre que o dono quiser construir, criar ou começar um app, site, jogo, ferramenta ou projeto novo ('vamos construir...', 'quero fazer um...'), mesmo sem dizer comecar. Não use para mudar um projeto que já existe."
argument-hint: "[rapido|pesquisa] <a ideia, links, prints>"
---

# Começar um projeto

O dono fala da ideia do jeito dele e responde uma mensagem de decisões. O resto fica com você: pesquisar o que dá para descobrir, montar a base e entregar a primeira versão rodando e revisada.

Como trabalhar:

- **Pergunte só o que é decisão do dono.** Fato (linguagem, biblioteca, preço, como os parecidos fazem) se pesquisa. Agente de código costuma chutar em vez de perguntar, e uma etapa obrigatória de perguntas recupera quase toda a perda (UnderSpecBench, Ask or Assume).
- **Nada de aprovação no meio.** Entre as etapas, siga sem pedir licença para o que dá para desfazer. Pare só para a mensagem de decisões, gastar dinheiro, publicar, instalar algo fora do projeto, apagar o que não volta ou criar conta.
- **A primeira versão rodando vale mais que um documento perfeito.** Spec longa antes do código já fez gente passar horas e receber a coisa errada. Um dia de trabalho nunca termina sem a tela principal funcionando.
- **Construa você mesmo.** Nos testes, processos pesados construindo empataram com o agente sozinho seguido de revisor novo, custando de 2 a 20 vezes mais.
- **/revisar e /vistoria só quando o dono digita.** São demoradas e gastam muitos tokens: nunca chame as duas sozinho. No fim, diga em uma linha que elas existem.

## Modos

| Pedido | O que roda |
|---|---|
| `/comecar <ideia>` | Tudo: etapas 1 a 7 |
| `/comecar rapido <ideia>` | Para coisa pequena (um arquivo, ferramenta pessoal). Pesquisa curta com 2 agentes, decisões e construção; sem prova de risco |
| `/comecar pesquisa <ideia>` | Etapas 1 a 3 e o SPEC.md, sem construir. Para avaliar uma ideia antes de gastar tempo |

## Etapa 1: entender a ideia

1. Leia tudo o que o dono mandou: texto, links e prints. Procure no disco e na memória do projeto, se houver, trabalho anterior parecido.
2. Diga em uma linha:
   - **o tipo:** app de PC, site, ferramenta, jogo Roblox, jogo de PC ou outro;
   - **o tamanho:** pequeno, médio ou grande;
   - **a aposta:** hobby, ferramenta própria ou produto para vender;
   - **o modo** que vai usar.

   A aposta calibra o resto: produto para vender pede pesquisa mais funda que uma ferramenta própria. Na dúvida, o tamanho maior. Ele só sobe durante o trabalho, nunca desce.
3. Se o projeto tem partes independentes (ex.: jogo, painel e loja), diga a divisão e comece pela parte que entrega valor primeiro. As outras vão para depois.
4. Se faltar algo que muda a pesquisa inteira (ex.: celular ou PC?), faça só essa pergunta já, e comece a pesquisa pelo que não depende dela.

## Etapa 2: raio X, em paralelo

Leia [references/raio-x.md](references/raio-x.md) e dispare os pesquisadores como subagentes, todos na mesma mensagem, em segundo plano:

| Agente | Pergunta | Modo rápido |
|---|---|---|
| A. Parecidos | Quais são, o que fazem, para quem, preço, se são mantidos, o que fazem bem e mal | Sim |
| B. Reclamações e pedidos | Do que os usuários reclamam, o que elogiam, o que pedem e ninguém faz, e a visão contrária | Junto com o A |
| C. Armadilhas técnicas | O que quebra nos parecidos (issues do GitHub), limites e mudanças das APIs e da plataforma | Não |
| D. Ponto de partida | Linguagem e bibliotecas, com versão conferida na documentação oficial, e o modelo oficial (template) para partir | Sim |

Use a ferramenta de pesquisa profunda que estiver instalada (ex.: /trawl). Sem ela, use busca web, leitura de página e `gh`. Guarde o material na pasta de trabalho com a data.

Quando voltarem, junte tudo numa síntese:
- tabela dos parecidos;
- reclamações por tema, com "X de Y fontes";
- o que ninguém resolve;
- diferenciais, ligados às reclamações (o que não tem prova fica como hipótese);
- o que não copiar;
- armadilhas, cada uma com o sinal de alerta e a versão em que será tratada.

## Etapa 3: uma mensagem de decisões

Uma mensagem só, nesta ordem:

1. **O que a pesquisa achou**, em até 6 linhas: os parecidos mais próximos, o maior erro deles, o que ninguém resolve.
2. **De 5 a 7 perguntas numeradas**, só o que é decisão do dono. Cada uma traz a sua recomendação e o motivo tirado da pesquisa:

   ```
   Q1. Plataformas da primeira versão: Twitch e YouTube; Kick depois.
   ➜ Recomendo: 4 de 9 fontes pedem multiplataforma, e a conexão da Kick mudou em outubro e quebrou três apps parecidos.
   ```

   Ordem: escopo, segurança, experiência, técnico. Sempre entram:
   - o que vai na 0.1;
   - nome e pasta do projeto;
   - a linguagem recomendada, com o motivo (uma recomendação, não um menu);
   - qualquer gasto (API ou asset pago).
3. **"Responda 'sim' para aceitar tudo, ou diga só o número que muda."**

O que não virou pergunta entra no SPEC como [SUPOSIÇÃO]. Se a resposta abrir uma decisão nova, faça uma segunda rodada só com ela. No modo `pesquisa`, escreva o SPEC.md (etapa 5) na pasta de trabalho e pare aqui.

## Etapa 4: provar o maior risco (modo completo)

Pegue a suposição que mais pode derrubar o projeto, na lista de armadilhas (ex.: "a API deixa ler o chat sem servidor?" ou "o Roblox permite isso?"). Teste em até 15 minutos, com código descartável fora do projeto. Se falhar, isso vira decisão do dono: mostre o que falhou e a alternativa antes de construir.

## Etapa 5: base do projeto

Sem pedir aprovação:

1. Crie a pasta decidida e inicie o git. Se existir um modelo oficial (template ou scaffold), comece por ele. Não o rebaixe a "só referência".
2. **SPEC.md**, curto:
   - objetivo e para quem;
   - "Você disse" e "Eu supus", separados;
   - requisitos em **v1**, **v2** e **fora**, com o motivo. Cada um tem um critério que dá para testar ("QUANDO o jogador abre o baú, O JOGO DEVE mostrar o item em até 1 s"). Em jogo, o critério é algo que se vê jogando;
   - diferenciais e o que não copiar, ligados ao raio X;
   - armadilhas e em que versão tratar cada uma;
   - versões: a 0.1 é a tela ou o fluxo principal funcionando de ponta a ponta. Cada versão traz de 2 a 5 frases do tipo "o que precisa ser verdade", e todo requisito da v1 cai numa versão.
3. **CLAUDE.md do projeto**, com menos de 200 linhas:
   - o que é;
   - como rodar e testar;
   - as decisões tomadas, como regras;
   - onde ficam o SPEC e a pesquisa.
4. A síntese e o material do raio X em `docs/pesquisa/`.
5. **Guia visual** (app ou site) **ou GDD** (jogo): se houver uma skill instalada para isso, use. Senão, uma seção curta no SPEC.
6. Registre as decisões na memória do projeto, se houver, com as palavras do dono.

## Etapa 6: versão 0.1

1. Escreva primeiro os testes dos critérios da 0.1. Escritos depois, eles só confirmam o código que já existe.
2. Construa a tela ou o fluxo principal, de ponta a ponta, antes de qualquer acabamento.
3. Rode e use: os testes passando, o programa aberto e um print.

## Etapa 7: conferir e entregar

1. **Confira você mesmo** os requisitos da 0.1 no SPEC.md: rode os testes e o programa e olhe o resultado. A /revisar e a /vistoria não rodam aqui: só quando o dono digita.
2. **Entrega ao dono**, começando pelo resultado:
   - o que roda, com o print;
   - o que você conferiu e o que não deu para conferir;
   - em uma linha: `/revisar` (revisor novo que reproduz cada defeito) e `/vistoria rapida` (segurança) conferem a 0.1 a fundo, quando ele quiser;
   - o que vem na 0.2;
   - onde estão o SPEC e a pesquisa.

   Diga em uma linha o que falta para a v1 inteira. Pergunte só o que for decisão dele.
