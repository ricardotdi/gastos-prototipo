# gastos-prototipo — contexto do projeto

## O que é isto

Protótipo de app de controlo de gastos pessoais, com leitura de QR Code de
faturas portuguesas (formato AT). Primeira de uma **família de apps utilitárias
gratuitas sob a marca Fin+** — a estratégia é usar apps bem feitas e úteis no
dia a dia para gerar afinidade com a marca Fin+ (intermediário de crédito de
Ricardo Vagner Paiva Custódio), não apps para vender diretamente.

Sempre que se criar uma nova app desta família, o objetivo é repetir o mesmo
padrão técnico e visual descrito abaixo, para consistência entre apps e para
poupar tempo de configuração.

## Stack técnica (repetir nas próximas apps)

- **Frontend**: HTML/CSS/JS puro num único ficheiro `index.html`, sem build
  step, sem framework. Mantém o deploy trivial (GitHub Pages).
- **Hosting**: GitHub Pages, branch `main`, ficheiro `index.html` na raiz.
  Repositório público (Pages grátis exige isso, a não ser que haja GitHub
  Pro/Team).
- **Login**: Firebase Authentication, com **Google** e **Facebook**
  (`signInWithPopup`), usando o SDK **compat** do Firebase via CDN
  (`firebase-app-compat.js`, `firebase-auth-compat.js`,
  `firebase-firestore-compat.js` — `https://www.gstatic.com/firebasejs/<versão>/...`).
  O SDK compat foi escolhido de propósito porque o site não usa bundler nem
  `<script type="module">`, e mantém a API global `firebase.*` simples de
  integrar num script inline. Erros de login mapeados para mensagens em
  português em `mensagemErroLogin(codigo)`.
  - **Decisão explícita do utilizador: nada de métodos de login pagos, e
    evitar fricção/burocracia desnecessária.** Histórico do que já foi
    tentado:
    - **Email+password**: implementado e depois removido a pedido do
      utilizador (o problema de fundo nem era o código — era a entrega de
      emails da Firebase (reset de password) cair sempre em spam, e alguns
      filtros de spam "pré-clicam" links, invalidando o link de reset antes do
      utilizador o abrir).
    - **Apple Sign-In**: rejeitado — exige Apple Developer Program, 99
      USD/ano.
    - **SMS/telefone**: rejeitado — exige mudar o projeto Firebase do plano
      Spark para o Blaze (pagas o que usares) e custa por SMS enviado.
    - **Microsoft**: tentado e abandonado — a conta pessoal Microsoft do
      utilizador (`ricardotdi@gmail.com`, criada via Gmail) não tem um tenant
      Entra ID válido para registar uma app (erro "not contained within any
      directory"). O M365 Developer Program (que dá um tenant sandbox grátis
      sem cartão de crédito) recusou a candidatura ("You don't currently
      qualify"). A única via restante era "sign up for Azure" (free trial),
      que pede cartão de crédito para verificação de identidade (não cobra
      nada em si, mas o utilizador preferiu não avançar). Se no futuro se
      quiser retomar isto, o caminho é: o utilizador criar/obter um tenant
      Entra ID válido por outra via (conta Microsoft 365 de trabalho/escola,
      ou aceitar dar cartão no signup do Azure), registar uma app em **App
      registrations** (tipo "Web", suportar contas pessoais + organizacionais,
      redirect URI `https://gastos-prototipo-ef57a.firebaseapp.com/__/auth/handler`),
      e colar o Client ID + Client Secret em Firebase → Authentication →
      Sign-in method → Microsoft.
    - **Facebook**: implementado — precisa de uma app em
      developers.facebook.com com "Valid OAuth Redirect URI" =
      `https://gastos-prototipo-ef57a.firebaseapp.com/__/auth/handler`, e o
      App ID/Secret colados em Firebase → Authentication → Sign-in method →
      Facebook. Nota: enquanto a app do Facebook estiver em modo
      "Development", só o developer e testers explicitamente adicionados
      conseguem entrar — para funcionar para qualquer pessoa é preciso mudar
      para "Live", o que exige preencher uma Política de Privacidade (URL),
      ainda não feita nesta app.
    - Regra geral: não avançar com nenhum método novo de login sem confirmar
      primeiro que é gratuito, e sem assumir que o utilizador quer lidar com
      burocracia de contas externas (Azure/Meta/Apple) — perguntar primeiro.
- **Dados**: Cloud Firestore (plano gratuito Spark — dá para sempre neste tipo
  de app, ver conversa anterior sobre limites). Sincronização em tempo real via
  `onSnapshot`, sem `localStorage` como fonte de verdade (só cache offline do
  Firestore).
- **Modelo de partilha multi-utilizador**: cada utilizador pertence a um
  "grupo" (`groups/{groupId}`, `members: [uid, ...]`). Ao criar conta, cria-se
  automaticamente um grupo pessoal (`groupId == uid`). Partilha entre pessoas
  (ex: casal) é feita por código de convite de 6 carateres, guardado em
  `invites/{code}` → `{ groupId, createdBy }`; quem recebe o código
  adiciona-se a si próprio ao array `members` do grupo alvo (regras do
  Firestore permitem um não-membro auto-adicionar-se, mas só a si próprio, nada
  mais no documento).
- **Regras de segurança do Firestore**: só membros de um grupo podem ler/escrever
  os dados desse grupo. As regras completas e atualizadas vivem só na consola
  Firebase (não há ficheiro `firestore.rules` neste repo) — se precisares delas,
  pede para as reconstruir a partir desta descrição ou confirma com o
  utilizador se as tem guardadas noutro lado.
- **Categorias**: personalizáveis por grupo, guardadas em `groups/{groupId}.categorias`
  (array de strings). Renomear uma categoria migra automaticamente os
  documentos existentes (`gastos`, `recorrentes`) e o mapa de orçamentos.
- **Sem build/CI**: por design. Se uma futura app precisar de mais complexidade
  (múltiplos ficheiros JS, testes), reconsiderar esta escolha nessa altura, não
  antes.

## Identidade visual Fin+ (repetir nas próximas apps)

- **Logótipo**: `Fin_plus_logo_euro.png` (wordmark "Fin+" em gradiente
  cobre/dourado-rosado, com símbolo de euro por cima, fundo transparente).
  Fica no topo do ecrã de login e no cabeçalho principal, acima do eyebrow.
- **Tagline**: "Finanças Positivas" — texto eyebrow no topo, por cima do
  título da app.
- **Paleta de cores** (definida em `:root` no CSS):
  - `--ink:#12202E` (texto principal)
  - `--navy:#1A3C5E` / `--navy-deep:#0E2740` (fundo do cabeçalho, gradiente)
  - `--gold:#A19276` / `--gold-soft:#C9BFA8` (acento, textos secundários sobre navy)
  - `--paper:#F6F4EF` (fundo geral da página)
  - `--line:#DAD4C6` (bordas subtis)
  - `--danger:#B4543A` (erro/remover/acima do orçamento)
  - `--good:#4C7A5D` (dentro do orçamento, estado positivo)
- **Tipografia**: `'Segoe UI', system-ui, -apple-system, sans-serif` — sem
  webfonts externas (mantém tudo self-contained, sem pedidos a CDNs de fontes).
- **Tom**: sóbrio, "banca privada"/consultoria financeira — não é uma app
  gamificada ou colorida. Cantos arredondados moderados, sem gradientes
  berrantes, sem emojis na UI (só nos ícones de estado tipo ✕ e ✓).

## Ambiente de desenvolvimento (contexto da sessão Claude Code)

- O ambiente onde o Claude corre tem uma política de rede restritiva: não
  consegue aceder diretamente a `cdnjs.cloudflare.com`, `*.github.io`, nem à
  maioria dos domínios externos via `curl`/`WebFetch`. **`registry.npmjs.org`
  está acessível** — por isso, quando é preciso obter o código-fonte de uma
  biblioteca JS (ex: para inlining num Artifact, ou para verificar uma API),
  usar `npm install <pacote>` num diretório scratch e ler os ficheiros de
  `node_modules`, em vez de tentar `curl` diretamente ao CDN.
- Não há acesso a `gh` CLI nem à API REST genérica do GitHub — todas as
  operações GitHub passam pelas tools MCP `mcp__github__*`. Não há tool GitHub
  para ativar Pages nem para criar repositórios fora do scope já autorizado —
  isso exige ação manual do utilizador na consola GitHub/Firebase.
- Não há tool para gerir o projeto Firebase (criar projeto, ativar
  Authentication, publicar regras do Firestore) — essa configuração é sempre
  feita manualmente pelo utilizador na consola Firebase, guiado passo a passo.
- Ficheiros que o utilizador refere por caminho local do Windows (ex:
  `C:\Users\...\Dropbox\...`) **não são acessíveis** a partir desta sessão —
  não há sistema de ficheiros partilhado. A única forma de obter um ficheiro do
  utilizador é ele fazer upload direto no GitHub
  (`https://github.com/<owner>/<repo>/upload/<branch>`) ou anexá-lo como
  ficheiro real na conversa (colar a imagem inline no chat nem sempre fica
  acessível como ficheiro — já aconteceu falhar; upload direto no GitHub é o
  método mais fiável).

## Testar mudanças

Não há testes automatizados. Fluxo de verificação usado até agora:
1. Validar sintaxe do JS embutido com `node -e 'new Function(script)'` antes
   de publicar (o `<script>` final do ficheiro é o código da app).
2. Verificar que não há `id` duplicados nem `getElementById` a apontar para
   elementos inexistentes (scripts ad-hoc usados nas sessões anteriores).
3. Push para `main` → GitHub Pages atualiza-se automaticamente (~1 min).
4. Pedir ao utilizador para testar em aba anónima no telemóvel (para evitar
   cache) e reportar o resultado.

## Funcionalidades já implementadas

Login Google + partilha de grupo (convites), despesas fixas/recorrentes,
orçamento mensal por categoria com aviso visual, comparação com o mês anterior
(geral e por categoria), ecrã de Histórico navegável por mês/trimestre/
semestre/ano, categorias personalizáveis (criar/renomear com migração
automática/remover), datas editáveis nos gastos, deteção de faturas
duplicadas (mesmo NIF + valor + dia, só faz sentido em gastos vindos de QR),
modal de confirmação próprio da app (não usar `confirm()`/`alert()` nativos do
browser — mostram sempre o domínio do site e não são personalizáveis).

## Próximos passos identificados (backlog)

- Ler QR a partir de foto da galeria, não só câmara ao vivo
- Empacotar como app Android instalável via TWA (Trusted Web Activity, usando
  Bubblewrap) — reaproveita este site sem reescrever nada; só nessa fase é que
  entra o SHA-256 do certificado de assinatura do APK (Digital Asset Links,
  `assetlinks.json`), não confundir com o SHA-1 do Firebase Google Sign-In
  nativo (que não é necessário para o caminho TWA).
- Se algum dia se quiser melhorar a entrega de emails da Firebase (ex: reset de
  password, se for reintroduzido), a causa da entrega em spam é a falta de
  domínio próprio verificado — resolver isso implicaria o utilizador ter um
  domínio (ex: para a marca Fin+) e configurá-lo na Firebase.
