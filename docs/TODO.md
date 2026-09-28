# To-do — HTC e Crew Systems

Atualizado em 28/09/2026. Cada item diz quem faz. "Claude" = sessão do Claude Code
neste repositório; os scripts citados estão em `tools/`.

## HTC — Halo e leads

### Pedro / time
- [ ] **Autorizar a restauração das configurações que os salvamentos pela API
      desligaram** (ver "Claude" abaixo). Enquanto não restaurar, o lead só passa uma
      vez pelo atendimento da Halo, e os SMS de review da Crew podem sair de madrugada.
- [ ] **Carlos** (`0CflyMyn8opXdYGIEd2C`, chat do site, 28/09 02h05): está testando o
      GHL e quer entrar na comunidade; respondeu duas vezes pelo STEVO sem retorno. O
      John precisa chamar.
- [ ] **Criar e aprovar os templates do WhatsApp oficial** da sequência do
      `1.2 Opt In (Wpp)`, com os textos dos nós de SMS de hoje: Wpp #1 (primeira
      mensagem, com "John"), Wpp #2 ("Posso te enviar mais informações sobre o GHL?"),
      Wpp #5 ("Tá parecendo a minha ex…") e Wpp #7 (mural de depoimentos). Os templates
      de materiais e de cases já existem e estão no fluxo, desligados.
- [ ] **Saber que, enquanto for SMS/STEVO:** a Halo não responde quem retorna pelo
      STEVO, e a sequência não para quando o lead responde (resposta pelo STEVO não
      conta como "Customer replied").
- [ ] **Snapshot Crew [LAS VEGAS]:** decidir sobre 4 workflows que perderam
      "permitir entrar mais de uma vez" num salvamento pela API que não foi do Claude:
      "0.0 Form Submission -> Confirmation", "0.1 Chat Widget Lead In -> Confirmation",
      "1.0 10 Days Passed -> Marketing Form Reminder" e "Discount Form Filled In".
- [ ] **HTC Onboarding PPL - Appointment Confirmation + Reminder:** aponta para um
      calendário apagado (`dHKDVdsG3BUl2pFlkiEU`). Trocar o calendário no gatilho; do
      jeito que está, provavelmente não dispara.
- [ ] **Decidir** sobre duas regras antigas do "HTC | Atendimento IA Halo": a tag
      `demo-halo` impede que o lead seja atendido pela Halo uma segunda vez, e o bot
      desliga 1 dia depois da primeira resposta do lead.
- [ ] **Autorizar o conector do monday.com** em claude.ai → Settings → Connectors.

### Claude
- [ ] **Restaurar as configurações** (depende da autorização acima). Script pronto:
      volta só os valores que cada workflow tinha antes do salvamento.
  - HTC | Atendimento IA Halo: "permitir entrar mais de uma vez" (perdido em 21/09)
  - HTC | Reminders Agendamento IA Halo: "permitir entrar mais de uma vez"
  - IG DM -> Add Pipeline: "permitir mais de uma oportunidade"
  - Review Request Sent e Refer a Friend, no snapshot e nas subcontas da Crew
    (Best Painting, WN, SV Rental, VIX, MK Freitas, ALI): "permitir entrar mais de
    uma vez" e a janela de envio das 8h às 21h
- [ ] **Quando os templates forem aprovados:** trocar os nós de SMS por templates no
      1.2, com a primeira mensagem em "John aqui do HTC", e fazer o teste real com um
      WhatsApp do time.
- [ ] **Depois da troca:** conferir numa conversa real que a Halo responde e que a
      sequência para quando o lead responde.

### Feito em 28/09
- Prompt da Halo com 1.878 palavras (o limite do GHL é 2.000). O texto antigo está em
  `tools/halo_prompt/anterior-2026-09-28.txt`.
- Transferências da Halo, calendário "Halo - Call de Ativacao GHL" e os avisos dos 4
  workflows da Halo (transferência, lembretes, chat do site, ticket de afiliado) vão
  para o John. Os demais processos continuam com quem estava.
- Ação "Agendar call com o John" criada na Halo.
- Workflow "HTC | Ativar Halo" criado; o 1.2 liga a Halo antes da primeira mensagem.
  Testado: a Halo fica calada até o lead escrever e responde em ~15 s no WhatsApp
  oficial.
- Halo ligada para 71 leads parados (58 do 1st Step, 13 do Opt In).
- 1.2: "pesquisando" e "trabalha" corrigidos; 2 dias entre o Wpp #4 e o Wpp #5.

## Crew Systems — sites, GBP e automações

### Pedro / time
- [ ] **Rafa:** criar as páginas /review, /contact e /get-your-discount em SV Rental,
      MK Freitas, ALI e VIX, com os embeds do GHL. IDs:
  - VIX: survey `kJo0uSMmqe4CeQcMlXez`, discount `1OrNJQrhte9fG7oEz5RD`,
    website `ZLRXkBjPlp3CkRrMpb5W`
  - SV Rental: survey `o4Jv691syfZSc5J9qQRP`, discount `kNzZNxcYvfmZ0T7RoFtB`,
    website `x5SVDVc0hf14MEHWd3Bf` (a página de termos está dando 404)
  - MK Freitas: discount `cGdEGSvevc0iAuqroFVq`
  - ALI: survey `yOu4qSahDylhLVWWl2J1`, discount `N8UkWlsVtXWFKeCSEf3E`,
    website `Tzk80MbBa69EntMsGrtq`
- [ ] **Rafa (WN):** executar o passo a passo do GBP e subir as fotos, no site e no
      GMN (zip já entregue). Não renomear o perfil.
- [ ] **Pedro (WN site, AI Studio):** mandar os 2 prompts de
      `entregas/WN-Painting-PROMPTS-AI-STUDIO.md`, cada um com as 8 imagens da sua
      pasta (`entregas/WN-Painting-AI-Studio-imagens.zip`). Tira as 2 imagens de IA
      (hero e Bathroom Remodeling), corrige as fotos trocadas (Interior, Exterior e
      Flooring) e passa tudo para WebP (Sprint 6). Depois, o Claude confere no site ao
      vivo.
- [ ] **Pedro:** instalar o app do Claude no GitHub na organização crew-systems
      (https://claude.ai/connect-github), para o Claude acessar o `crew-hq` e rodar o
      `/auditar-site` da tarefa de auditoria da WN. O ClickUp já está conectado.
- [ ] **Best Painting:** trocar a logo do GBP (Pesquisa ou Maps → Fotos → Alterar
      logotipo; quadrada, 720×720 px).
- [ ] **Best Painting:** pedir ao Marcelo os vídeos originais. Os do Drive vieram
      comprimidos pelo WhatsApp (478×850), e dois passam de 30 s.
- [ ] **Best Painting:** manter a pasta de fotos do Drive pública até 23/10, porque o
      Google busca a imagem de cada post agendado na hora de publicar.
- [ ] **WN:** conectar o Google no Social Planner da subconta, para dar para agendar
      posts.
- [ ] **Valores de desconto** de SV Rental e VIX.
- [ ] **MK Freitas:** o service_area está como Tallahassee, mas a empresa é em Destin.
      Confirmar.
- [ ] **Storm Electrical:** ainda não tem subconta.
- [ ] **Snapshot Crew [LAS VEGAS]:** salvar de novo o snapshot na agência, para o
      review_google_url (agora vazio) chegar às próximas subcontas.

### Claude
- [ ] Depois que o Rafa publicar as páginas: preencher discount_form_link e
      review_survey_link em cada subconta.
- [ ] Best Painting: agendar os posts de novembro no GBP (a fila atual vai até 23/10).
- [ ] WN: agendar os posts semanais depois que o Social Planner estiver conectado.
- [ ] Acompanhar o roteiro de GBP por cliente no playbook:
      https://claude.ai/artifact/SFGjdM7ee4ypbBAuLXBJFk

### Feito
- Custom values da Crew alinhados com o snapshot (`tools/crew_custom_values.py`).
- SMS de review restaurados com a doação (`tools/crew_reviews_restore.py`); a
  pesquisa de estrelas foi mantida, por decisão do time.
- Link do SMS de indicação apontando para discount_form_link, e o texto do SMS #5
  corrigido (`tools/crew_referral_fix.py`).
- Fotos da WN e da Best Painting selecionadas e entregues (JPG e WebP).
- Best Painting: GBP conectado, primeiro post publicado e 4 posts agendados (quintas,
  de 02/10 a 23/10, 10h em Boston) (`tools/crew_gbp_posts.py`).
