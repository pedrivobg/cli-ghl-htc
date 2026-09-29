# WN Painting — performance, "Agentic Browsing" e Search Console

## Onde estamos (Lighthouse 13.5, o mesmo motor do PageSpeed, rodado em 28/09)

| | Performance | Acessibilidade | Boas práticas | SEO | Agentic Browsing |
|---|---|---|---|---|---|
| Mobile | 64 | 94 | 77 | 100 | 75 (3 de 4) |
| Desktop | 90 | 94 | 78 | 100 | — |

O que segura o mobile, em ordem de impacto:
1. **O navegador só descobre a foto do hero depois que o JavaScript roda.** O visitante recebe a casca do app; o pré-render é só para robôs. O LCP fica em 5,2 s.
2. **Logo em PNG de 355 KB** (2172×724 px) mostrado com 120×40 px. Sozinho, é metade do peso desperdiçado. O selo da CrewSystems no rodapé é outro PNG, de 888 KB.
3. **CSS bloqueando a página:** o Google Fonts atrasa a primeira pintura em ~0,9 s.
4. **JavaScript:** um arquivo só com o site inteiro, 67 KB não usados na home e 450 ms de bloqueio.
5. **Acessibilidade:** texto cinza (#65758b) com contraste 4,37, e o mínimo é 4,5. O número azul (#0e3995) sobre fundo escuro tem contraste 1,72. Há títulos `h4` fora de ordem.
6. **Agentic Browsing 3/4:** o Lighthouse procura `/.well-known/ai-catalog.json`. Como o site responde qualquer endereço com a página do app, ele recebe HTML e acusa "JSON inválido". Validei o arquivo abaixo no próprio verificador do Lighthouse: zero erros.

Fora do nosso alcance, e por isso as Boas práticas não passam de ~80:
- o cookie `__cf_bm`, que o Cloudflare do servidor de imagens do GHL (vibe.filesafe.space) coloca;
- a falta de source maps, porque a configuração do Vite no AI Studio é somente leitura.

---

## Prompt 6 — anexar `wn-logo.webp` e `crew-systems-badge.webp`

```
Performance and accessibility pass. Fix only the items below. Do NOT change the design, the text or the page structure.

1. Images (upload the 2 attached files as project assets):
   - wn-logo.webp (480x160) replaces the current logo PNG (.../attachments/861a214f-644e-4fb6-a9c2-658869578491.png) EVERYWHERE: header, footer, schema "logo". Keep it rendered at the same visual size (h-10 w-auto); set width="480" height="160" on the <img>.
   - crew-systems-badge.webp replaces the "CrewSystems" badge PNG (.../attachments/3a9ea03d-6047-4082-a613-a6606ef35838.png) in the footer. Keep the same visual size, loading="lazy".

2. Make the home hero image discoverable before the JS bundle runs. In index.html, as the FIRST child of <head> after the meta charset/viewport, add a tiny inline script that runs only on the home page:
   <script>if(location.pathname==="/"){var l=document.createElement("link");l.rel="preload";l.as="image";l.href="HERO_URL";l.fetchPriority="high";document.head.appendChild(l);}</script>
   where HERO_URL is the exact current value of the hero image (heroPhoto). Keep it in sync if the hero changes. Keep the existing <img> with loading="eager" fetchpriority="high".

3. Fonts: stop Google Fonts from blocking render. In index.html keep the two preconnects (fonts.googleapis.com and fonts.gstatic.com crossorigin), then load the stylesheet non-blocking:
   <link rel="preload" as="style" href="FONTS_URL">
   <link rel="stylesheet" href="FONTS_URL" media="print" onload="this.media='all'">
   <noscript><link rel="stylesheet" href="FONTS_URL"></noscript>
   and keep only the weights actually used by the Tailwind classes (display=swap stays).

4. JavaScript: code-split the routes. Keep the home page in the main bundle, and load every other page (services, service pages, areas, area pages, about, contact, privacy-policy, terms, review, get-your-discount, thank-you, marketing-form, 404) with React.lazy + Suspense (a minimal fallback with the same background color, no spinner flash). Make sure the pre-rendered HTML for robots still contains the full page content.

5. Accessibility:
   - The muted text color (--ink-mute, currently #65758b) must reach a contrast ratio of at least 4.5:1 on every background it is used on. Darken it slightly (e.g. #56657a) without changing the look.
   - Text using the clay/blue accent (#0e3995) on dark backgrounds (e.g. the big stat numbers and the <span> next to them) must use a light tint of that blue (e.g. #9db8ff) so contrast is at least 4.5:1 on the dark background.
   - Heading order: footer column titles and small card titles that are <h4> directly after an <h2> must become <h3> (or <p> for footer titles), keeping exactly the same styles.

6. Create public/.well-known/ai-catalog.json with exactly this content (served as application/json):
{"specVersion":"1.0","host":{"displayName":"WN Painting & Remodeling","documentationUrl":"https://wnpaintingremodeling.com/llms.txt"},"entries":[]}

Publish and list every file changed.
```

Depois de publicar, me avise que eu rodo o Lighthouse de novo, no mobile e no desktop.

---

## Sitemap no Google Search Console, passo a passo

Não consigo fazer isso daqui: o Search Console exige login na conta Google que vai ser
dona do site. O sitemap o AI Studio já entrega pronto, em
https://wnpaintingremodeling.com/sitemap.xml (18 páginas, sem as utilitárias).

1. Abra https://search.google.com/search-console com a conta Google da agência (ou a
   do cliente, se ele tiver).
2. **Adicionar propriedade** → escolha **Prefixo do URL** → digite
   `https://wnpaintingremodeling.com/` → **Continuar**.
3. Na tela de verificação, abra **Tag HTML** e copie só o valor do `content="..."`.
4. No AI Studio da WN, mande este prompt, trocando pelo valor copiado:
   ```
   Add <meta name="google-site-verification" content="COLE_O_CODIGO_AQUI" /> inside <head> in index.html. Change nothing else. Publish.
   ```
5. Depois de publicar, volte no Search Console e clique em **Verificar**.
6. Menu da esquerda → **Sitemaps** → em "Adicionar um novo sitemap", digite `sitemap.xml`
   → **Enviar**. O status deve ficar "Sucesso", com 18 páginas descobertas.
7. Menu da esquerda → **Inspeção de URL** → cole `https://wnpaintingremodeling.com/` →
   **Solicitar indexação**. Repita para /services e /contact.
8. Bing: abra https://www.bing.com/webmasters → **Importar do Google Search Console** →
   escolha o site. O sitemap vem junto.

Alternativa ao passo 2: a propriedade do tipo **Domínio** cobre também www e http, mas
exige um registro TXT no DNS de quem registrou o domínio. Use o **Prefixo do URL** se o
DNS estiver com o cliente.
