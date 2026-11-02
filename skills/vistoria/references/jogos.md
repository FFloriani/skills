# Regras de segurança para jogos

Estas regras vêm das fontes oficiais lidas em 01/11/2026. Nenhuma fonte traz medida de eficácia. Confira no código e marque o que falta como achado, com `leitura própria` em quem marcou.

Fontes: [Securing the client-server boundary, Roblox Creator Hub](https://create.roblox.com/docs/scripting/security/client-server-boundary) e [Going multiplayer: Making games that keep cheaters away, Unite 2025](https://www.youtube.com/watch?v=VtMiQvBiA-A).

## Roblox

Comece por todo `OnServerEvent` e `OnServerInvoke`. O cliente pode mandar qualquer valor, a qualquer momento. Em cada um, confira:

| O que conferir | Como o erro aparece | O que deve existir |
|---|---|---|
| Permissão e estado | O evento executa sem ver se o jogador pode fazer aquilo agora | Checagem no servidor antes de agir |
| Tipo e estrutura | Argumento usado direto | `typeof` em cada argumento |
| Valor | Preço, quantidade ou posição aceitos como vieram | Faixa conferida; o preço vem do servidor, nunca do cliente |
| NaN e infinito | `x > 0` passa com `inf`, e NaN passa em checagem de tipo | Rejeitar com `math.isfinite` |
| Instância falsa | Tabela no lugar de `Instance` burla preço e dono | `typeof(x) == "Instance"` e `x:IsDescendantOf(...)` |
| Frequência | Evento sem limite | Limite por jogador, por exemplo token bucket |
| Distância | Servidor confia em `ProximityPrompt`, `ClickDetector` ou `DragDetector` | Conferir a distância no servidor: eles podem ser disparados de qualquer lugar |
| Combate | Dano calculado com o que o cliente disse | Validar origem do tiro, acerto, obstáculo, cadência, munição, time e vida |
| Duplicação | Dados inválidos ou corrida ao salvar | Commit tipo transação, com reversão, no DataStore |
| Compra | Item entregue por evento do cliente | Só por `ProcessReceipt`, no servidor |

## Unity e outros jogos com servidor

- **Nunca confie no cliente:** o servidor autoritativo recebe só o input e calcula o resultado.
- **Não mande o que o jogador não pode ver:** posição de inimigo escondido em memória vira wallhack.
- **Tempo do servidor:** o relógio do aparelho não serve para tempo de recarga nem para recompensa diária.

## O que não dá para resolver assim

Diga isto no relatório quando valer:

- Servidor autoritativo não impede aimbot com input válido nem wallhack que só lê dados.
- Anti-cheat no cliente só encarece a trapaça, segundo o próprio fabricante do ACTk.
- No Roblox, o anti-cheat do cliente é da plataforma (Hyperion). Não achei página oficial da Roblox sobre o que ele cobre.
- Em jogo casual, servidor autoritativo completo pode não compensar. Aponte o risco e deixe a decisão com o dono.
