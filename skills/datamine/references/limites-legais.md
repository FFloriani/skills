# Limites legais em linguagem simples

Texto informativo, não é aconselhamento jurídico. Situação verificada em 2026-10-11; leis e
decisões mudam.

## Sumário

1. Resumo
2. Termos usados
3. Seguro, cinza e arriscado (Brasil, EUA, UE)
4. Por que mecânica é livre
5. Por que decompilar é cinza
6. Por que decifrar é o passo mais arriscado
7. O que perde processos
8. O que "copiar" pode e não pode significar
9. Riscos fora do direito autoral

## 1. Resumo

Estudar como o jogo funciona e recriar a mecânica com coisas suas é seguro. Decompilar (converter
o programa de volta em código legível) e extrair arquivos é zona cinzenta. Decifrar uma cópia fica
entre cinza e arriscado, mesmo sem publicar. Publicar o que veio do jogo, ou pôr no seu jogo código,
arte, texto ou visual copiados, é o que perde processos.

## 2. Termos usados

- **EULA:** o contrato de licença que você aceita ao instalar ou comprar o jogo. Muitos proíbem
  engenharia reversa.
- **Medida de proteção:** cifra, DRM (trava contra cópia) ou outra trava que controla o acesso aos
  arquivos. Contornar é desativar ou passar por ela; decifrar conta como contornar nos EUA.
- **Interoperabilidade:** fazer um programa seu funcionar junto com outro. Estudar um jogo para
  criar outro não é interoperabilidade.
- **Fair use (uso justo):** defesa da lei dos EUA que aceita certos usos sem autorização, decidida
  caso a caso.
- **DMCA:** lei de direitos autorais dos EUA. O §1201 dela proíbe contornar proteção; "notificação
  DMCA" é o pedido de remoção que o dono manda a um site.
- **Anti-cheat:** programa que roda junto do jogo para detectar trapaça.

## 3. Seguro, cinza e arriscado (Brasil, EUA, UE)

Para quem tem a própria cópia comprada e não publica nada:

| O que você faz | Brasil | EUA | União Europeia | Resultado |
|---|---|---|---|---|
| Jogar, medir, anotar, montar planilhas e curvas | regras de jogo não são protegidas (Lei 9.610, art. 8º, II) | mecânica é ideia (Tetris v. Xio, Data East v. Epyx) | observar e testar o programa é direito de quem o usa e contrato não pode proibir (Diretiva 2009/24, arts. 5(3) e 8) | Seguro |
| Recriar a mecânica com código, arte, textos e números seus | art. 8º, II e VII | regras são livres (Tetris v. Xio) | reproduzir a funcionalidade não infringe (SAS v WPL) | Seguro |
| Ler wikis e código liberado; citar trechos curtos com a fonte | citação para estudo (art. 46, III) | uso justo (*fair use*), não pesquisado a fundo | — | Seguro |
| Decompilar o código localmente para entender fórmulas | a Lei 9.609, art. 6º, não traz exceção para decompilar | pode ser *fair use* (Sega v. Accolade), mas a cláusula da EULA vale como contrato (Davidson v. Jung) | só para interoperabilidade (art. 6) ou para corrigir erro (Top System) | Cinza |
| Extrair assets e tabelas para uma pasta privada | vai além de "pequenos trechos" (art. 46, II) | não testado em tribunal; EULA | outra diretiva cobre assets (não pesquisado) | Cinza |
| Decifrar uma cópia local, mesmo sem publicar | inutilizar dispositivo contra cópia gera indenização (Lei 9.610, art. 107) | decifrar é "contornar" (17 U.S.C. §1201); não há isenção para estudo | regras de medidas técnicas (não pesquisado) | Cinza a arriscado |
| Publicar código, assets, arquivos decifrados, chaves ou ferramentas | violar direito de programa é crime, com reclusão de 1 a 4 anos se for para comércio (Lei 9.609, art. 12) | tráfico de ferramenta de contorno (§1201(a)(2)) | repassar a terceiros o que veio da decompilação, fora da interoperabilidade, é proibido (art. 6(2)) | Arriscado |
| Pôr no seu jogo código, arte, áudio, texto, layout ou tabelas copiados, alterados ou não | reproduzir e transformar exigem autorização (Lei 9.610, art. 29) | Tetris v. Xio, Spry Fox v. Lolapps | SAS v WPL | Arriscado |
| Contornar DRM ou anti-cheat; mexer em jogo online ou servidor | art. 107 | Davidson v. Jung, MDY v. Blizzard | — | Arriscado e fora da skill |

## 4. Por que mecânica é livre

- **Brasil:** o art. 8º, II, da Lei 9.610 exclui da proteção "os esquemas, planos ou regras para
  realizar atos mentais, jogos ou negócios". Os dados em si também não são protegidos (art. 7º,
  §2º), mas a seleção e a organização de uma tabela podem ser. Por isso, recalcule os números em
  vez de copiar a tabela inteira.
- **EUA:** em Tetris v. Xio (2012), a ideia de blocos que caem, giram e limpam linhas não foi
  protegida. Em Data East v. Epyx (1988), o que é próprio do gênero (golpes de um jogo de caratê)
  também não.
- **UE:** em SAS v WPL (Tribunal de Justiça da UE, 2012), funcionalidade, linguagem de programação
  e formato de arquivo de dados não são expressão protegida.

## 5. Por que decompilar é cinza

- **Brasil:** o art. 6º da Lei 9.609 só permite quatro coisas: cópia de segurança, citação parcial
  para ensino, semelhança imposta pela função e integração para uso próprio. Decompilar não está
  na lista. O risco prático de quem estuda em casa é baixo (o crime depende de queixa do dono),
  mas o ato não é expressamente lícito.
- **EUA:** em Sega v. Accolade (1992), desmontar o código foi aceito porque havia motivo legítimo
  e nenhum outro meio de chegar às partes funcionais. Quem aceitou uma EULA que proíbe engenharia
  reversa, porém, renunciou a isso (Davidson v. Jung, 2005). E muita mecânica pode ser medida
  jogando, o que enfraquece o "nenhum outro meio".
- **UE:** quem usa o programa pode observá-lo, estudá-lo e testá-lo enquanto ele roda, e contrato
  não pode proibir. Decompilar só é permitido para interoperabilidade ou para corrigir erro.

## 6. Por que decifrar é o passo mais arriscado

- **EUA:** o §1201(a)(3)(A) define contornar incluindo "to decrypt an encrypted work" sem
  autorização. É uma violação à parte, mesmo sem copiar nada; no 9º Circuito (tribunal de apelação
  que cobre a Califórnia), nem precisa haver violação de direito autoral (MDY v. Blizzard,
  2010). As isenções oficiais para jogos cobrem só restaurar, para jogar localmente, um jogo cujo
  servidor de autenticação foi desligado, e a preservação feita por instituições (37 CFR 201.40).
- **Brasil:** pelo art. 107, I, da Lei 9.610, responde por perdas e danos quem "alterar,
  suprimir, modificar ou inutilizar, de qualquer maneira, dispositivos técnicos" usados para
  evitar ou restringir cópia. Não há exceção para estudo, e quando o número de cópias é
  desconhecido a indenização mínima é calculada sobre 3.000 exemplares (art. 103).
- Arquivo sem cifra não levanta essa questão; ficam só direito autoral e EULA.

A skill permite decifrar só uma cópia, para leitura ("Escopo e limites" do SKILL.md). Dê este aviso
ao usuário uma vez, antes de decifrar:

> Em alguns países, como EUA e Brasil, decifrar um arquivo protegido já pode contar como contornar
> proteção, mesmo sem publicar nada. Vou trabalhar só numa cópia em `estudo/<jogo>/`, sem gravar
> nada de volta no jogo e sem publicar chave, arquivo aberto ou ferramenta.

## 7. O que perde processos

- **Tetris v. Xio (2012):** a Xio copiou o visual e o comportamento (tabuleiro 20×10, peça-fantasma,
  prévia da próxima peça) achando que arte e áudio novos bastavam. Perdeu.
- **Spry Fox v. Lolapps (2012):** o Yeti Town trocou os ursos do Triple Town por iétis, e isso não
  bastou. Preços iguais na loja e diálogos parecidos contaram, e o tribunal disse que a comparação
  "must focus on what is similar, not what is different". Terminou em acordo, com a Spry Fox
  ficando com o Yeti Town.
- **Asset alterado:** modificar uma obra gera obra derivada, que precisa de autorização (Lei 9.610,
  arts. 5º, VIII, "g", e 29, III; 17 U.S.C. §101 e §106(2)). Não existe porcentagem de mudança que
  libere o uso.

## 8. O que "copiar" pode e não pode significar

| Pode copiar | Recrie do zero ou use asset licenciado |
|---|---|
| regra, sistema, fluxo, estrutura de dados, forma de uma curva, ritmo, orçamento técnico (triângulos, resolução, número de quadros) | código, modelos, texturas, sprites, animações, áudio, textos, nomes, layout de interface, tabelas de números inteiras, personagens e mundo de outra franquia |

Usar personagens e mundo de outra franquia é arriscado mesmo com arte nova: o remake AM2R, de
Metroid II, recebeu notificações DMCA da Nintendo logo após o lançamento, em 2016.

## 9. Riscos fora do direito autoral

- Patente pode cobrir uma mecânica (Nintendo v. Pocketpair, no Japão, sem decisão final até
  2026-10-11).
- Lojas têm regra própria contra imitação, como a diretriz 4.1 da App Store.
- A maioria das disputas termina em pedido de remoção (*takedown*), acordo ou banimento, não em
  sentença, e isso custa caro do mesmo jeito para um desenvolvedor pequeno.

## Fontes

[Lei 9.609/98](https://www.planalto.gov.br/ccivil_03/leis/l9609.htm) ·
[Lei 9.610/98](https://www.planalto.gov.br/ccivil_03/leis/l9610.htm) ·
[17 U.S.C. §1201](https://www.law.cornell.edu/uscode/text/17/1201) ·
[37 CFR 201.40](https://www.law.cornell.edu/cfr/text/37/201.40) ·
[Diretiva 2009/24/CE](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024) ·
[SAS v WPL](https://husovec.eu/2012/05/cjeu-decided-in-sas-v-wpl/) ·
[Top System](https://www.scl.org/12394-court-of-justice-rules-that-software-buyers-can-decompile-programs-to-correct-errors/) ·
[Sega v. Accolade](https://law.resource.org/pub/us/case/reporter/F2/977/977.F2d.1510.92-15655.html) ·
[Davidson v. Jung](https://law.resource.org/pub/us/case/reporter/F3/422/422.F3d.630.04-3654.html) ·
[MDY v. Blizzard](https://en.wikipedia.org/wiki/MDY_Industries,_LLC_v._Blizzard_Entertainment,_Inc.) ·
[Tetris v. Xio](https://en.wikipedia.org/wiki/Tetris_Holding%2C_LLC_v._Xio_Interactive%2C_Inc.) ·
[Spry Fox v. Lolapps](https://en.wikipedia.org/wiki/Spry_Fox%2C_LLC_v._Lolapps%2C_Inc.) ·
[Data East v. Epyx](https://en.wikipedia.org/wiki/Data_East_USA,_Inc._v._Epyx,_Inc.) ·
[AM2R](https://en.wikipedia.org/wiki/AM2R)
