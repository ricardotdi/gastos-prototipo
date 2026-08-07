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
- **Login**: Firebase Authentication, **só com Google** (decisão final do
  utilizador — ver histórico abaixo, chegou a ter Facebook implementado mas
  foi removido a pedido para manter simples)
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
    - **Facebook**: chegou a ser implementado (código + instruções dadas),
      mas foi removido a pedido do utilizador para simplificar — decidiu ficar
      só com Google. Se se quiser reintroduzir: precisa de uma app em
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
  - Código gerado por `gerarConviteUnico()`: usa uma **transação Firestore**
    (lê + escreve num único passo atómico) em vez de `set()` direto, para
    fechar a janela entre "verificar se o código já existe" e "gravá-lo".
    Em caso de colisão (rara — alfabeto de 32 carateres sem 0/O/1/I, 6
    posições = 32⁶ combinações), tenta outro código até 5 vezes.
- **Regras de segurança do Firestore**: só membros de um grupo podem ler/escrever
  os dados desse grupo. As regras completas e atualizadas vivem só na consola
  Firebase (não há ficheiro `firestore.rules` neste repo) — se precisares delas,
  pede para as reconstruir a partir desta descrição ou confirma com o
  utilizador se as tem guardadas noutro lado.
- **Categorias**: personalizáveis por grupo, guardadas em `groups/{groupId}.categorias`
  (array de strings). Renomear uma categoria migra automaticamente os
  documentos existentes (`gastos`, `recorrentes`) e o mapa de orçamentos.
- **Contas a Acertar** (divisão de despesas com parceiro/parceira): coleções
  **totalmente separadas** dos gastos mensais, por pedido explícito do
  utilizador ("não quero que adicione às despesas do mês"):
  - `groups/{groupId}/despesasPartilhadas/{id}`: `{ valor, descricao, data,
    nif, pagoPor (uid), criadoPor, liquidacaoId }`. `liquidacaoId` é `null`
    enquanto a despesa está em aberto.
  - `groups/{groupId}/liquidacoes/{id}`: `{ numero, ano, data, valor,
    quemDevia (uid ou null se empatado), quemRecebia (uid ou null), totalEu,
    totalOutro, criadoPor }`. Numeração tipo "Nº 3/2026" — reinicia a cada
    ano, calculada em `liquidacoes.filter(l => l.ano === anoAtual).length + 1`
    (não transacional; aceitável para 2 utilizadores, risco de colisão
    desprezável).
  - Só faz sentido matematicamente para grupos de **exatamente 2 membros**
    (`outroMembroUid()` devolve `null` para outros tamanhos, escondendo a
    funcionalidade).
  - Acesso: menu "Menu▾" → "Contas a Acertar" (overlay `#contasOverlay`), com 2
    colunas (uma por pessoa), botão "+ Adicionar despesa partilhada" que abre
    o **mesmo scanner/formulário do "+"** principal mas em `scanMode =
    'partilhada'` (variável global `scanMode`: `'gasto'` | `'partilhada'`,
    controla se `confirmAdd` grava em `gastos` ou em `despesasPartilhadas`, e
    se mostra o form-row de categoria ou o de "quem pagou"). Botão
    "Liquidado" fecha (`liquidacaoId`) todas as despesas em aberto e cria o
    registo numerado.
  - Histórico das liquidações também acessível em **Histórico → separador
    "Liquidações"** (5º modo, ao lado de Mês/Trimestre/Semestre/Ano),
    clicável para expandir o cálculo `(totalEu − totalOutro) ÷ 2` e a lista
    de despesas incluídas nessa liquidação.
  - `nomeDoMembro(uid)` e `outroMembroUid()` são helpers genéricos reutilizados
    em várias partes (Contas a Acertar, formulário de despesa partilhada).
- **Sem build/CI**: por design. Se uma futura app precisar de mais complexidade
  (múltiplos ficheiros JS, testes), reconsiderar esta escolha nessa altura, não
  antes.
- **Leitura de QR Code** (fatura portuguesa, formato AT — `parseFaturaQR`):
  dois caminhos, câmara ao vivo ou foto da galeria, ambos a acabar na mesma
  `onQrDecodedText(texto)`:
  - **Câmara ao vivo**: `BarcodeDetector` nativo do browser (ML Kit no
    Chrome/Android) quando disponível (`iniciarScannerNativo`), com fallback
    para a biblioteca `html5-qrcode` via CDN (`iniciarScannerHtml5Qrcode`) em
    browsers sem suporte nativo (ex: iOS Safari).
  - **Foto da galeria** (`processarArquivoQR`, botão "ou ler QR de uma foto da
    galeria"): mesmo padrão de fallback — `BarcodeDetector.detect()` sobre um
    `createImageBitmap(file)` primeiro, senão `Html5Qrcode.scanFile()`.
  - Confirmado a funcionar em produção pelo utilizador (fotos reais tiradas
    antes, não só fatura ao vivo).
- **Exportação para PDF** (botão real `📄 Exportar PDF` + `🔗 Partilhar` no
  Histórico, lado a lado, e atalho `📄 Exportar relatório PDF` destacado no
  menu principal que abre o Histórico — antes tudo isto era um único link de
  texto pequeno "escondido" — pedido explícito do utilizador em agosto/2026
  para tornar isto mais visível, e depois para separar download de partilha
  em dois botões distintos): `gerarDocumentoHistoricoPDF()` monta o `jsPDF`
  (via CDN) com o resumo por categoria do período selecionado (não a lista de
  gastos individuais — decisão explícita do utilizador para manter simples),
  logótipo, total, **gráfico de barras por categoria** (Chart.js, gerado num
  canvas fora do ecrã via `gerarImagemGrafico()`), tabela de categorias, e
  uma secção **"Comparações"** com duas comparações lado a lado (pedido
  explícito do utilizador, agosto/2026: "quero comparação com o mês anterior
  E com o mês homólogo do ano anterior"):
  - **Período anterior** — `periodoAnterior(ano, modo, periodo)` devolve
    `{ano, periodo}` do período imediatamente anterior no mesmo modo (mês
    anterior/trimestre anterior/semestre anterior/ano anterior — mesma
    lógica de "andar para trás" do `navegarHistorico()`, mas pura, sem
    efeitos secundários).
  - **Período homólogo** — mesmo período do ano anterior (`historicoAno - 1`).
  - Cada uma mostra o total do período e a variação em valor e percentagem
    (a vermelho se subiu, verde se desceu), e as duas partilham um único
    **gráfico de barras agrupadas por categoria com 3 séries** (atual/
    anterior/homólogo — navy/azul-claro `#8FA6BC`/dourado). Pagina
    automaticamente (`garantirEspaco()`) se o conteúdo não couber numa
    página A4. Rodapé com "Gerado em {data} · Fin+ Finanças Positivas" e
    "www.finmais.pt" centrado.
  - `exportarHistoricoPDF()` (botão "Exportar PDF"): gera o documento e
    `doc.save()` — download direto, sem tentar partilhar.
  - `partilharHistoricoPDF()` (botão "Partilhar"): gera o documento e tenta
    `navigator.share` (Web Share API, com `files`) para abrir o menu nativo
    de partilha do telemóvel — deve continuar a funcionar numa futura app
    Android via TWA; se não houver suporte, cai também para `doc.save()`.
- **Aviso "relatório mensal disponível"** (`verificarRelatorioMensal()`,
  banner navy no topo do ecrã principal, dentro de `<main>`): pedido
  explícito do utilizador (agosto/2026) para o relatório do mês que acabou
  de fechar "ficar disponível no 1º dia do mês". Implementação **só
  client-side** — decisão deliberada, não pedida ao utilizador porque decorre
  diretamente da regra já estabelecida "não quero nada pago": notificação
  push ou email agendados exigiriam Cloud Functions + Cloud Scheduler, que
  só funcionam no plano pago Blaze do Firebase. Em vez disso, sempre que a
  app abre (`auth.onAuthStateChanged`, depois do login), `verificarRelatorioMensal()`
  corre no cliente: se o dia do mês for ≤ 7, calcula o mês anterior via
  `periodoAnterior()` e mostra o banner a convidar a ver/exportar esse
  relatório (o botão "Ver relatório" abre o Histórico já nesse mês — mesma
  função `gerarDocumentoHistoricoPDF()` acima, com as duas comparações). O
  botão "Agora não" guarda uma chave `relatorioMensalDispensado_{ano}-{mes}`
  em `localStorage` (por dispositivo, não sincronizado entre contas/telemóveis
  — aceitável para um simples lembrete) para não voltar a incomodar nesse mês.
  Testado (Playwright, sem login real): banner aparece com o texto certo,
  "Ver relatório" abre o Histórico no mês certo, "Agora não" persiste e não
  volta a aparecer.
  - **Bug pré-existente encontrado e corrigido nesta alteração**: `doc.
    addImage()` sem o parâmetro de compressão embute imagens de
    `HTMLImageElement`/canvas sem qualquer compressão — o logótipo sozinho
    inflacionava o PDF para ~2,3 MB. Corrigido passando `'FAST'` como
    parâmetro de compressão em todas as chamadas a `addImage` (logótipo e os
    dois gráficos) — reduz um PDF de teste de ~4,9 MB para ~145 KB, sem perda
    visível de qualidade. Se adicionar mais `addImage()` no futuro, incluir
    sempre este parâmetro.
  - **Limitação descoberta e contornada**: a fonte base do jsPDF (Helvetica
    core, sem TTF embutido) não tem o glifo do símbolo "€" nem do travessão
    "—" — ficam em branco/apagados no PDF gerado (confirmado por inspeção
    direta dos bytes do PDF, não só visualmente). $, £, R$ e Kz renderizam
    bem na mesma fonte. Por isso o PDF usa sempre `moedaAtual().simboloPDF`
    em vez de `moedaAtual().simbolo` para os valores monetários (ver secção
    "Idioma e moeda" abaixo) — no ecrã continua tudo normal com "€"/"£"/etc.,
    é só uma limitação da biblioteca de PDF. Se um dia se quiser reintroduzir
    o símbolo "€" no PDF, a solução seria embutir uma fonte TTF com esse
    glifo via `doc.addFont()`, não tentar contornar de outra forma.
  - **Como testar isto no ambiente de desenvolvimento**: o sandbox bloqueia
    `cdnjs.cloudflare.com` (Chart.js/jsPDF) e `gstatic.com` (Firebase) por
    política de rede — não dá para abrir a app real no browser aqui. Testado
    com sucesso via Playwright interceptando esses pedidos (`page.route()`)
    e servindo cópias locais das mesmas versões instaladas via `npm install
    chart.js@4.4.0 jspdf@4.2.1`, com um stub mínimo do `firebase` global, a
    chamar `exportarHistoricoPDF()` real da página com dados fictícios em
    `gastos`/`historicoAno`/etc. — confirma que a função corre sem erros e
    inspeciona o PDF gerado (o `Read` tool lê PDFs diretamente).
- **Idioma e moeda** (Definições, menu → "Definições"/"Settings"): dois
  estados globais, `idioma` (`'pt'` | `'en'`) e `moedaCodigo` (`'EUR'` |
  `'USD'` | `'GBP'` | `'BRL'` | `'AOA'`, ver array `MOEDAS`), guardados por
  **conta** em `users/{uid}.idioma` / `users/{uid}.moeda` (não por aparelho/
  `localStorage`) — decisão explícita do utilizador para sincronizar entre
  dispositivos e permitir que cada pessoa num grupo partilhado (casal) tenha
  a sua própria preferência mesmo partilhando os mesmos gastos.
  - **Moeda**: só muda o símbolo apresentado (`formatoEuro`/`formatoEuroPDF`
    usam `moedaAtual().simbolo`/`.simboloPDF`) — decisão explícita de não
    fazer conversão cambial real (sem API de taxas de câmbio, sem
    complexidade extra). Os valores numéricos guardados nunca mudam.
  - **Idioma**: cobre toda a interface via dicionário `T = { pt: {...}, en:
    {...} }` + função `t(chave, vars)` (interpolação tipo `{nome}` nas
    strings). Texto estático em HTML tem `id` próprio e é aplicado por
    `aplicarTraducoes()` (chamada no arranque e sempre que o idioma muda);
    texto gerado em JS (listas, histórico, mensagens de erro/confirmação)
    chama `t()` diretamente. Nomes de meses em `MESES.pt`/`MESES.en`;
    formatação de datas/números usa `localeAtual()` (`'pt-PT'` ou `'en-GB'`)
    em vez de `'pt-PT'` fixo.
  - **Categorias de despesas não são traduzidas** — são dados escritos pelo
    próprio utilizador (`categoriasAtuais`), não texto da interface.
  - Ao adicionar uma nova string de interface: adicionar a chave em **ambos**
    `T.pt` e `T.en` (há um teste ad-hoc feito em sessões anteriores que
    compara as chaves usadas com `t(...)` contra as duas listas — vale a pena
    repetir esse tipo de verificação antes de publicar).

## Regras de segurança do Firestore (versão atual, colar na consola Firebase)

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    match /groups/{groupId} {
      allow get: if request.auth != null && request.auth.uid in resource.data.members;
      allow create: if request.auth != null && request.auth.uid in request.resource.data.members;
      allow update: if request.auth != null && (
        request.auth.uid in resource.data.members ||
        (
          request.resource.data.diff(resource.data).affectedKeys().hasOnly(['members', 'memberInfo']) &&
          request.resource.data.members.hasAll(resource.data.members) &&
          request.resource.data.members.size() == resource.data.members.size() + 1 &&
          request.auth.uid in request.resource.data.members
        )
      );

      match /gastos/{gastoId} {
        allow read, write: if request.auth != null &&
          request.auth.uid in get(/databases/$(database)/documents/groups/$(groupId)).data.members;
      }

      match /recorrentes/{recId} {
        allow read, write: if request.auth != null &&
          request.auth.uid in get(/databases/$(database)/documents/groups/$(groupId)).data.members;
      }

      match /despesasPartilhadas/{id} {
        allow read, write: if request.auth != null &&
          request.auth.uid in get(/databases/$(database)/documents/groups/$(groupId)).data.members;
      }

      match /liquidacoes/{id} {
        allow read, write: if request.auth != null &&
          request.auth.uid in get(/databases/$(database)/documents/groups/$(groupId)).data.members;
      }
    }

    match /invites/{code} {
      allow read: if request.auth != null;
      allow create: if request.auth != null &&
        request.resource.data.createdBy == request.auth.uid &&
        request.auth.uid in get(/databases/$(database)/documents/groups/$(request.resource.data.groupId)).data.members;
      allow update, delete: if false;
    }
  }
}
```

Nota: existe uma coleção órfã `acertos` de uma versão anterior/abandonada da
funcionalidade de partilha (antes de virar "Contas a Acertar" separado) — sem
regras próprias, sem código a usá-la, inofensiva mas pode ser ignorada ou
limpa manualmente na consola se algum dia incomodar.

## Identidade visual Fin+ (repetir nas próximas apps)

- **Logótipo**: `Fin_plus_logo_euro.png` (wordmark "Fin+" em gradiente
  cobre/dourado-rosado, com símbolo de euro por cima, fundo transparente).
  Fica no topo do ecrã de login e no cabeçalho principal, acima do eyebrow.
- **Ícone da app** (`icons/icon-192.png`, `icons/icon-512.png`): gerado a
  partir do símbolo "€" recortado do logótipo (bounding box aproximado
  x:342–555, y:25–229 em `Fin_plus_logo_euro.png`), centrado sobre um fundo
  navy sólido (`#1A3C5E`, sem transparência — necessário para o ícone da
  Play Store). Gerado com a biblioteca `jimp` (script ad-hoc, não fica no
  repo). Se for preciso regenerar ou fazer variantes, repetir o recorte do
  símbolo "€" (a wordmark "Fin+" completa é larga demais para um ícone
  quadrado legível a tamanhos pequenos).
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
- **Nota**: dependendo da sessão/ambiente, pode não haver acesso direto a
  ferramentas GitHub nem sistema de ficheiros partilhado (ver acima); numa
  sessão que tiver acesso a Bash/Git normal, o fluxo prático que funcionou
  foi clonar o repo para um diretório scratch, editar lá, e `git push`.
- **Clone de trabalho em `C:\Users\User\Dropbox\Empresa Finmais\App Android\gastos-prototipo`**
  (cópia de segurança pedida pelo utilizador, agosto 2026, ver memory
  `project-gastos-prototipo`): por estar dentro de uma pasta sincronizada
  pelo Dropbox, `.git/refs/remotes/` pode ter atributo `ReparsePoint` e o
  `git fetch`/`git pull` pode falhar intermitentemente com
  `error: couldn't set 'refs/remotes/origin/main'` (o Dropbox bloqueia
  momentaneamente o ficheiro da referência interna do git). **O `git push`
  em si não falha** — só a atualização da referência local de tracking.
  Se acontecer: confirmar que o push chegou com
  `git ls-remote origin main`, e corrigir a referência local manualmente,
  ex.: `git update-ref refs/remotes/origin/main <sha>` ou recriar o ficheiro
  à mão com `mv` (um `mv` direto costuma funcionar mesmo quando o git falha
  a fazer o mesmo internamente). Não é perda de dados, é só bookkeeping
  local a precisar de correção.
- **Sem Java, Android SDK, nem `keytool`** neste tipo de ambiente de
  desenvolvimento — por isso não é possível correr `bubblewrap` (CLI oficial
  da Google para gerar o `.aab` de uma TWA) localmente sem antes descarregar
  JDK + Android SDK Command Line Tools (vários GB). Alternativa escolhida:
  **PWABuilder.com** (Microsoft) — gera o `.aab` na nuvem a partir do URL
  público do site, sem precisar de nada instalado localmente. Ver secção
  "Empacotamento Android / Play Store" abaixo.

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

Login Google + partilha de grupo (convites, geração atómica sem colisão),
despesas fixas/recorrentes, orçamento mensal por categoria com aviso visual,
comparação com o mês anterior (geral e por categoria), ecrã de Histórico
navegável por mês/trimestre/semestre/ano/liquidações, categorias
personalizáveis (criar/renomear com migração automática/remover), datas
editáveis nos gastos, deteção de faturas duplicadas (mesmo NIF + valor + dia,
só faz sentido em gastos vindos de QR), leitura de QR por câmara ao vivo **ou
foto da galeria**, exportação/partilha em PDF do resumo do Histórico, escolha
de idioma (PT/EN, cobre toda a interface) e moeda (símbolo apresentado, sem
conversão cambial), modal de confirmação próprio da app (não usar
`confirm()`/`alert()` nativos do browser — mostram sempre o domínio do site e
não são personalizáveis), logótipo/identidade Fin+, e **Contas a Acertar**
(divisão de despesas entre casal, ver secção própria acima) com liquidação
numerada nº/ano.

**Testado e confirmado a funcionar em produção pelo utilizador** (não é só
"implementado", foi mesmo validado por ele): tudo o que está acima até e
incluindo Contas a Acertar/Liquidações, a leitura de QR a partir de foto da
galeria, idioma/moeda, o botão de menu "Menu▾", e agora também **toda a
exportação/partilha de PDF** (botões "Exportar PDF"/"Partilhar" no Histórico,
gráficos, comparação com período anterior e homólogo, aviso de relatório
mensal) — utilizador confirmou em agosto/2026 que testou e gostou.

## Empacotamento Android / Play Store (em curso)

Decisões já tomadas (respostas do utilizador, agosto 2026):
- **Build do `.aab`**: via **PWABuilder.com**, não Bubblewrap local (ver nota
  sobre falta de Java/Android SDK no ambiente de desenvolvimento, acima).
- **Conta Google Play Console**: o utilizador ainda não tem — tem de a criar
  e pagar (25 USD, pagamento único) em play.google.com/console; isto não pode
  ser feito pelo Claude (conta/pagamento).
- **Política de privacidade**: escrita pelo Claude (o utilizador não tinha
  nenhuma) — `privacidade.html`, bilingue PT/EN, cobre: dados recolhidos
  (conta Google, dados de gastos, dados de partilha em grupo), onde ficam
  (Firebase/Google Cloud, sem analítica/publicidade de terceiros), direito a
  pedir eliminação de conta (contacto: geral.finmais@gmail.com). Link visível no
  ecrã de login e nas Definições (exigência da Play Store: link acessível
  dentro da própria app, não só na ficha da loja).

Já preparado no repo para a instalabilidade PWA (pré-requisito do
PWABuilder):
- `manifest.json` (nome "Fin+ Gastos", cores da marca, ícones 192/512).
- `icons/icon-192.png`, `icons/icon-512.png` (ver secção "Identidade visual"
  acima para como foram gerados).
- `<link rel="manifest">` + `<meta name="theme-color">` no `<head>` do
  `index.html`.
- `.nojekyll` (ficheiro vazio na raiz) — **necessário**: o GitHub Pages usa
  Jekyll por padrão, que ignora pastas começadas por ponto (como
  `.well-known/`); sem este ficheiro o `assetlinks.json` abaixo dava 404 e a
  TWA nunca ficaria verificada (mostraria sempre a barra de endereço).
- `.well-known/assetlinks.json` — Digital Asset Links, gerado automaticamente
  pelo PWABuilder ao criar o pacote Android e copiado para o repo:
  - Package name: `io.github.ricardotdi.twa`
  - SHA-256 do certificado: `C8:34:71:69:96:A5:E4:35:81:42:E2:94:87:E3:51:FB:0F:A8:B5:3D:50:8A:64:95:93:A1:B5:3D:1B:A7:5D:8F`
  - (Este SHA-256 é suposto ser público — não é secreto. Não confundir com o
    SHA-1 do Firebase Google Sign-In nativo, que não é necessário para TWA.)

**Chave de assinatura (`.keystore`)**: gerada pelo PWABuilder, **NUNCA está
no repositório** (é público) — fica só em
`C:\Users\User\Dropbox\Empresa Finmais\App Android\signing.keystore` +
`signing-key-info.txt` (password, alias `my-key-alias`, dados do signer).
Se precisares de reconstruir o `assetlinks.json` ou gerar uma nova versão do
`.aab` no futuro, a chave e a password estão só ali — pede ao utilizador, o
Claude não deve tentar guardar a password em lado nenhum do repo.

**Falta** (passos seguintes, fora do que o Claude consegue fazer sozinho):
1. ~~Utilizador cria a conta Google Play Console~~ — feito (confirmado pelo
   utilizador: pagou os 25 USD e está certificado para publicar).
2. ~~Gerar o pacote Android no PWABuilder~~ — feito (agosto 2026): `.aab`,
   `.apk` e `.keystore` guardados em
   `C:\Users\User\Dropbox\Empresa Finmais\App Android\`.
3. ~~Preparar `assetlinks.json`~~ — feito, ver acima.
4. Ficha da Play Store: texto pronto (título, descrição curta/longa,
   categoria, classificação de conteúdo, guia do formulário Data Safety,
   link da política de privacidade, lista de capturas de ecrã a tirar) está
   em **`play-store-listing.md`** neste repositório. Ícone 512×512 já existe
   (`icons/icon-512.png`). Falta só: o utilizador tirar as capturas de ecrã
   reais do telemóvel (não há emulador Android nesta sessão) e colar o texto
   nos campos da Play Console.
5. Fazer upload do `Fin+ Gastos.aab` na Play Console e submeter para revisão
   da Google.

**Descoberta importante (agosto 2026):** contas de developer novas na Play
Console são **obrigadas a correr um "Closed testing"** (teste fechado) com
**pelo menos 12 testers, durante no mínimo 14 dias consecutivos**, antes de
poderem sequer pedir acesso à produção (publicação pública). Isto é uma
política anti-spam da Google, aplica-se a todas as contas novas — não há como
saltar este passo por este caminho. O utilizador confirmou que vai recrutar
12 pessoas (família/amigos/clientes Fin+) para o teste fechado, em vez de
distribuir o `.apk` diretamente fora da Play Store.

**Progresso no Play Console** (app já criada):
- Nome: `Fin+ Gastos`, Package name: `io.github.ricardotdi.twa`
- App criada (Home → Fin+ Gastos), checklist "Finish setting up your app" em
  curso.
- **Sign-in details**: a Google exige uma conta de teste dedicada para os
  revisores (não pode ser a conta pessoal do utilizador). Conta criada:
  `finmaisteste@gmail.com`. Preencher em Play Console → App content →
  Sign-in details → Add sign-in details: Name = `Google Test Account`;
  email = `finmaisteste@gmail.com`; password = a que o utilizador definiu
  (não guardada aqui); "Any other information" (em inglês) = instrução a
  dizer para usar "Sign in with Google" com esta conta, sem 2-Step
  Verification ativo; marcar a checkbox de acesso total; Add.
- Ainda por fazer: confirmar 2-Step Verification desligado nessa conta,
  concluir o resto do checklist (Ads, Content rating, Target audience, Data
  safety — usar `play-store-listing.md` —, Government apps, Financial
  features, Health, categoria/contactos, Store Listing), depois publicar uma
  versão em "Closed testing" com o `.aab`, adicionar a lista dos 12 testers
  (emails), gerar e partilhar o link de opt-in, esperar os 14 dias, depois
  "Apply for production access".

**Os 12 testers escolhidos** (agosto/2026, nomes confirmados pelo
utilizador — falta recolher o email de conta Google de cada um antes de os
adicionar à lista "Email lists" da Play Console):
1. André — andfbcoelho@gmail.com
2. Aires — email: _por recolher_
3. Paula — email: _por recolher_
4. Marina — email: _por recolher_
5. Nuno — email: _por recolher_
6. Pai — email: _por recolher_
7. Mãe — email: _por recolher_
8. Hugo — m962774765@gmail.com
9. Graça — email: _por recolher_
10. Ricardo — email: _por recolher_
11. Raquel — email: _por recolher_

~~Cátia~~ — removida (tem iPhone, não consegue instalar uma app Android da
Play Store). **Só ficam 11 pessoas — falta arranjar mais 1 substituta/o para
voltar aos 12 mínimos exigidos pela Google.**

Mensagem pronta para pedir os emails e explicar o que têm de fazer (opt-in +
instalar + abrir a app uma vez) está guardada como referência nesta
conversa; se precisares de a recriar, o essencial é: pedir o email da conta
Google de cada um, e depois (quando houver link de opt-in) pedir para
abrirem o link, tocarem em "Tornar-me testador", instalarem e abrirem a app.

## Próximos passos identificados (backlog)

- Concluir o empacotamento Android/Play Store (ver secção própria acima).
- Se algum dia se quiser melhorar a entrega de emails da Firebase (ex: reset de
  password, se for reintroduzido), a causa da entrega em spam é a falta de
  domínio próprio verificado — resolver isso implicaria o utilizador ter um
  domínio (ex: para a marca Fin+) e configurá-lo na Firebase.
