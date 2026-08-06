# Ficha da Play Store — Fin+ Gastos

Copia e cola estes textos diretamente nos campos da Play Console
(Grow → Store presence → Main store listing).

---

## Título da app (máx. 30 carateres)

```
Fin+ Gastos
```

## Descrição curta (máx. 80 carateres)

```
Regista gastos por QR Code, controla orçamentos e divide despesas em casal.
```

## Descrição completa (máx. 4000 carateres)

```
Fin+ Gastos é uma app gratuita de controlo financeiro pessoal, pensada para o dia a dia em Portugal.

APONTA A CÂMARA E PRONTO
Lê o QR Code de qualquer fatura portuguesa e o valor fica registado automaticamente — sem escrever nada à mão. Também podes ler o QR a partir de uma foto já tirada, ou inserir o gasto manualmente.

ORÇAMENTOS COM AVISO
Define um limite mensal por categoria e recebe um aviso visual quando te aproximas ou ultrapassas o valor definido.

DESPESAS FIXAS
Renda, subscrições, seguros — regista uma vez as despesas que se repetem todos os meses e elas contam automaticamente, sem teres de as inserir de novo.

HISTÓRICO COMPLETO
Consulta os teus gastos por mês, trimestre, semestre ou ano, com comparação automática face ao período anterior.

CONTAS A ACERTAR (casal ou família)
Convida a tua parceira ou parceiro e passem a dividir despesas em conjunto: cada um regista o que pagou, a app calcula quem deve o quê, e quando acertarem contas fica tudo registado com um número de referência.

CATEGORIAS AO TEU GOSTO
Cria, renomeia ou remove categorias como quiseres — a app adapta-se a ti.

PRIVACIDADE
Os teus dados ficam associados à tua conta Google, nunca são vendidos, e podes pedir a eliminação completa a qualquer momento. Sem anúncios.

Fin+ Gastos é a primeira de uma família de apps gratuitas da Fin+, criadas para ajudar as pessoas a organizarem melhor a sua vida financeira no dia a dia.
```

---

## Categoria da app

**Finanças** (Finance)

## Classificação de conteúdo (questionário)

App utilitária de finanças pessoais, sem violência, sem conteúdo adulto, sem
jogo/apostas, sem interação social pública. Deve resultar em classificação
"Para todos" (PEGI 3 / Everyone).

---

## Formulário "Data safety" (Play Console → App content → Data safety)

Responde de acordo com o que a política de privacidade já publicada
(`privacidade.html`) declara:

**Recolhe dados do utilizador?** Sim

**Tipos de dados recolhidos:**
- **Informação pessoal** → Nome, Endereço de email
  - Recolhido via login "Entrar com Google" (Firebase Authentication)
  - Finalidade: Funcionalidade da app, Gestão de conta
  - Partilhado com terceiros? **Não**
  - Opcional ou obrigatório? Obrigatório (é preciso para usar a app)

- **Informação financeira** → Outra informação financeira (valores/categorias
  de gastos que o utilizador insere)
  - Finalidade: Funcionalidade da app
  - Partilhado com terceiros? **Não** (só visível para o próprio utilizador
    e, se aceitar um convite de partilha, para a outra pessoa desse grupo —
    isto **não conta como "terceiro"** nos termos da Play Store, é
    partilha dentro da própria funcionalidade da app)

**Os dados são encriptados em trânsito?** Sim (Firebase usa HTTPS/TLS)

**Podes pedir para os teus dados serem eliminados?** Sim — através de
`geral.finmais@gmail.com` (como consta na política de privacidade)

**A app usa publicidade ou analítica de terceiros?** Não

---

## Link da política de privacidade

```
https://ricardotdi.github.io/gastos-prototipo/privacidade.html
```

---

## Capturas de ecrã (tens de tirar tu, no telemóvel)

Mínimo 2, recomendo 4 a 6, tiradas na app real:

1. Ecrã principal (total do mês + gráfico)
2. A scanear um QR Code de uma fatura
3. Orçamentos por categoria (com a barra de aviso)
4. Histórico (qualquer separador — Mês, Liquidações, etc.)
5. Contas a Acertar (as duas colunas)

Formato: PNG ou JPEG, entre 320px e 3840px no lado mais pequeno, proporção
16:9 ou 9:16. Tira screenshots normais do telemóvel (botão ligar+volume) —
servem perfeitamente, não precisam de ser editadas.

## Ícone da app (512×512)

Já está pronto em `icons/icon-512.png` no repositório — faz download desse
ficheiro e usa-o no campo "App icon" da Play Console.

---

## Passos finais na Play Console

1. **Produção → Criar nova versão** (ou "Internal testing" primeiro, se
   quiseres testar antes de ir a público — recomendável para a primeira
   versão)
2. Faz upload do `Fin+ Gastos.aab` (está em
   `C:\Users\User\Dropbox\Empresa Finmais\App Android\`)
3. Preenche as notas da versão (ex: "Primeira versão pública.")
4. Confirma que "App content" está tudo verde (Data safety, classificação de
   conteúdo, política de privacidade, público-alvo)
5. **Submeter para revisão** — a Google costuma demorar de algumas horas a
   poucos dias a rever a primeira versão
