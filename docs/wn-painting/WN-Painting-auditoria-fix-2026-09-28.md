# WN Painting — /auditar-site (28/09/2026)

`seo-audit.sh wnpaintingremodeling.com` → **VERMELHO: 43 falhas, 7 alertas**.

O que já está certo:
- as imagens trocadas (nenhuma foto de IA nem JPG antigo no código);
- o formulário usa `locationId` e ID de rastreamento da WN, com Service Needed e Your
  Message;
- a rota /marketing-form existe;
- as páginas indexáveis são pré-renderizadas, com canonical próprio;
- o sitemap tem 15 URLs.

O que falhou:

| # | Falha | Sprint |
|---|---|---|
| 1 | 11 links internos com barra no fim (`/services/interior-painting/`…). O pré-render cria a versão com barra como página vazia: 22 falhas | 3 |
| 2 | /about, /privacy-policy e /terms não existem (devolvem a casca vazia) | 3 |
| 3 | robots.txt sem OAI-SearchBot e PerplexityBot explícitos (alerta) | 3 |
| 4 | Páginas utilitárias (/review, /get-your-discount, /thank-you, /marketing-form) e a 404 sem `noindex`; URL inexistente responde 200 | 2 |
| 5 | Schema: home como `PaintingService`, e o padrão é `HousePainter` + `LocalBusiness`; /services, /areas e /contact sem schema; sem `@id`, `WebSite` e breadcrumb | 2 |
| 6 | /contact mostra "Licensed & insured", mas a WN não informou licença nem seguro | 4 |
| 7 | llms.txt com links relativos e com barra no fim | 4 |
| 8 | Mapa do /contact é do OpenStreetMap, com marcador genérico no centro da cidade | 5 |
| 9 | Hero sem `fetchpriority="high"` | 6 |

CEP confirmado: **19154**. O site hoje mostra 19152; o Prompt 1 corrige em todo lugar
(rodapé, contato, schema, llms.txt e páginas novas).

Mande um prompt por vez, publique e me avise. Eu rodo a auditoria de novo até dar
VERDE.

---

## Prompt 1 — Sprint 3: rotas, links, sitemap e robots

```
Fix only the items below. Do NOT change the design.

0. Business address: the correct ZIP code is 19154. Replace "19152" with "19154" everywhere in the project (src and public: footer, contact page, schema, llms.txt, business data). The full address is "10848 Modena Drive, Philadelphia, PA 19154".

1. Internal links WITHOUT trailing slash everywhere: every link to /services/..., /areas/... and any other route must be "/services/interior-painting", never "/services/interior-painting/". Check header, footer, service cards, area cards, related-service cards and area pages.

2. Add these routes (above the "*" catch-all), each with its own title, meta description and self canonical (absolute, no trailing slash):
   - /about → About page from the business data: Wesley Ferreira Neves started as a painter in 2003 and opened WN Painting & Remodeling in 2008 (20+ years of experience); services; service area Philadelphia, Bucks County and West Chester, PA; CTA to /contact. Do NOT mention license, insurance or awards. Indexable.
   - /privacy-policy and /terms → standard pages using legal name "WN PAINTING & REMODELING LLC", email wesleynevespainting@gmail.com, phone (267) 439-9848 and address 10848 Modena Drive, Philadelphia, PA 19154. The privacy policy MUST include an SMS section: mobile information is not shared with third parties or affiliates for marketing purposes; message frequency varies; message and data rates may apply; reply STOP to opt out and HELP for help. Indexable.
   - Footer: "Privacy Policy" → /privacy-policy, "Terms" → /terms, add "About" → /about.

3. public/sitemap.xml: include "/", "/services", every "/services/:slug", "/areas", every "/areas/:slug", "/about", "/contact", "/privacy-policy", "/terms". EXCLUDE /review, /get-your-discount, /thank-you, /marketing-form and the 404. Base https://wnpaintingremodeling.com, no trailing slashes, <lastmod> with today's date.

4. public/robots.txt exactly:
User-agent: *
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

Sitemap: https://wnpaintingremodeling.com/sitemap.xml

List every file changed.
```

## Prompt 2 — Sprint 2: noindex, 404 e schema

```
Fix only the items below. Do NOT change the design.

1. SEO head: pages /review, /get-your-discount, /thank-you and /marketing-form must output <meta name="robots" content="noindex, follow"> and NO canonical. The NotFound (404) page too: noindex, follow, no canonical.

2. JSON-LD (read values from one business data object, not hardcoded in each page):
   - Business: "@id": "https://wnpaintingremodeling.com/#business", "@type": ["HousePainter", "LocalBusiness"] (replace PaintingService), name "WN Painting & Remodeling", legalName "WN PAINTING & REMODELING LLC", telephone "+12674399848", email "wesleynevespainting@gmail.com", url "https://wnpaintingremodeling.com/", logo = site logo URL, image = the social share image, address { streetAddress: "10848 Modena Drive", addressLocality: "Philadelphia", addressRegion: "PA", postalCode: "19154", addressCountry: "US" }, geo { latitude: 40.08208, longitude: -74.99237 }, openingHours Mo-Sa 07:00-17:00, areaServed = Philadelphia PA, Bucks County PA, West Chester PA (as City objects). No priceRange, no aggregateRating, no review.
   - WebSite: { "@type": "WebSite", "@id": "https://wnpaintingremodeling.com/#website", url, name, publisher: { "@id": ".../#business" } }.
   - Service pages: Service { name, serviceType, description, url (absolute, no trailing slash), areaServed, provider: { "@id": ".../#business" } } + FAQPage (only FAQs visible on that page) + BreadcrumbList (Home > Services > service).
   - "/" → business + WebSite. "/services" and "/areas" → BreadcrumbList. "/areas/:slug" → business + BreadcrumbList. "/contact" → business + BreadcrumbList.

List every file changed and show me the final JSON-LD for "/" and for /services/interior-painting.
```

## Prompt 3 — Sprint 4: nada inventado + llms.txt

```
Fix only the items below. Do NOT change the design.

1. Remove the "Licensed & insured" trust badge on /contact and anywhere else it appears. The business has no license or insurance data on file, so the site must not claim license, insurance, bonded, warranty, guarantees or awards anywhere. Keep "Free estimates" and the years of experience (20+).

2. Rewrite public/llms.txt as a factual summary, all URLs absolute with https://wnpaintingremodeling.com and NO trailing slash, links in Markdown format "- [Name](url): description":
   - Title WN Painting & Remodeling + one-line summary (painting and remodeling contractor in Philadelphia, PA, serving Philadelphia, Bucks County and West Chester).
   - Contact: phone (267) 439-9848, email wesleynevespainting@gmail.com, address 10848 Modena Drive, Philadelphia, PA 19154, hours Monday–Saturday 7:00 AM–5:00 PM, website.
   - Services (the 8 services with their URLs) and Service area (the 3 areas with their URLs).
   - Facts: started as a painter in 2003, business opened in 2008, 20+ years of experience; offer: 10% off for referrals. Nothing else.
   - Notes for AI assistants: estimates happen after an on-site walkthrough; pricing is not published; the contact details above are the canonical ones.

List every file changed.
```

## Prompt 4 — Sprint 5: conversão

```
Fix only the items below. Do NOT change the design.

1. Sticky mobile action bar (screens < 768px) on every indexable page (NOT on /review, /get-your-discount, /thank-you, /marketing-form): "Call" (tel:+12674399848) and "Free Estimate" (opens the existing estimate modal or goes to /contact). Add bottom padding so it never covers the footer or the chat bubble.

2. Estimate form: name and phone required, email OPTIONAL (label "Email (optional)"). Keep the same GHL tracking payload, formId "estimate-request-form" and custom fields.

3. After a successful estimate submission, redirect to /thank-you.

4. /contact map: replace the OpenStreetMap iframe with a Google Maps embed of the business location: https://www.google.com/maps?q=40.08208,-74.99237&z=15&output=embed (loading="lazy"). Keep it in one config value so it can be swapped later for the official Google Business Profile embed.

List every file changed.
```

## Prompt 5 — Sprint 6: performance

```
Fix only the items below. Do NOT change the design.

1. The home hero image and the header logo: loading="eager" and fetchpriority="high" (only these two). Add <link rel="preload" as="image" fetchpriority="high"> for the hero image in the home page head. All other images: loading="lazy" decoding="async" with width and height.
2. Chat widget: load the LeadConnector chat script only after the first user interaction (scroll, pointerdown, keydown, touchstart) or after 6 seconds, only once; keep it hidden on /review, /get-your-discount, /thank-you and /marketing-form.
3. Below-the-fold iframes (map, GHL form/survey embeds) must use loading="lazy".
4. Fonts: keep only the weights actually used, display=swap, preconnect to https://fonts.gstatic.com (crossorigin).

List every file changed.
```

Depois dos 5 prompts, eu audito de novo. O que o script não testa, e fica para você:
- um envio real do /contact (deve cair em /thank-you e chegar na WN com Service Needed e mensagem);
- o Discount Form e a Review Survey (1–3 estrelas e 4–5 estrelas);
- o celular;
- o PageSpeed mobile ≥ 75;
- o Rich Results Test;
- ligar o "Suporte Avançado de SEO" e enviar o sitemap no Search Console e no Bing.
