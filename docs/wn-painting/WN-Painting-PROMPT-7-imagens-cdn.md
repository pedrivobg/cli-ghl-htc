# WN Painting — Prompt 7: imagens pelo CDN do GHL (sem anexo)

Lighthouse de 28/09, 19h (o site publicado ainda não tem o Prompt 7: o logo e o selo
continuam nos PNGs originais e nenhuma foto passa pelo CDN):
- home mobile: **62 a 74** (varia entre execuções);
- /services/interior-painting mobile: **77**;
- home desktop: **95**;
- Agentic Browsing: **100** (era 75);
- acessibilidade: **96**;
- SEO: 100.

O que ainda pesa no mobile:
- **Logo:** continua sendo o PNG de 355 KB. A troca do Prompt 6 não entrou.
- **Selo da CrewSystems:** é um PNG de 888 KB.
- **Fotos:** vão com 1200 px de largura para um celular de 412 px.

O CDN de imagens do próprio GHL (`images.leadconnectorhq.com`) redimensiona e converte
qualquer imagem na hora. Testei com as imagens do site:

| Imagem | Hoje | Pelo CDN |
|---|---|---|
| Logo | 355 KB | 12 KB (480 px, WebP, fundo transparente mantido) |
| Selo CrewSystems | 888 KB | 2 KB (240 px) |
| Hero | 230 KB | 32 KB (400 px), 74 KB (600 px), 116 KB (800 px) |

```
Performance fix for images only. Do NOT change the design, layout, text or which image is used where.

GoHighLevel's image CDN resizes and converts any image on the fly with this URL format:
https://images.leadconnectorhq.com/image/f_webp/q_80/r_<WIDTH>/u_<ORIGINAL_URL>
(ORIGINAL_URL is the full https://vibe.filesafe.space/... URL, not encoded.)

1. Create a helper, e.g. cdnImg(url: string, width: number) => `https://images.leadconnectorhq.com/image/f_webp/q_80/r_${width}/u_${url}`.

2. Logo (header and footer): src = cdnImg(LOGO_URL, 480) where LOGO_URL is the current logo (.../attachments/861a214f-644e-4fb6-a9c2-658869578491.png). Keep the same rendered size (h-10 w-auto) and set width="480" height="160". Keep the original PNG URL only for the JSON-LD "logo".

3. "CrewSystems" footer badge: src = cdnImg(BADGE_URL, 240) where BADGE_URL is .../attachments/3a9ea03d-6047-4082-a613-a6606ef35838.png; loading="lazy".

4. Every photo <img> that uses a vibe.filesafe.space URL (hero, services, before/after, why us, gallery, final CTA, area heroes, team):
   - src = cdnImg(url, 800)
   - srcset = `${cdnImg(url, 400)} 400w, ${cdnImg(url, 800)} 800w, ${cdnImg(url, 1200)} 1200w`
   - sizes: full-width images (hero, area/service page heroes, final CTA background) = "100vw"; cards in a grid = "(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"; adjust to the real layout of each section.
   - keep width/height, object-fit cover, loading="lazy" decoding="async" (hero stays eager + fetchpriority="high").

5. Hero preload: update the home preload (index.html inline script and/or the <link rel="preload"> in the head) to preload the CDN version with imagesrcset and imagesizes="100vw" matching the hero <img>, so the browser does not download the image twice.

6. Keep og:image, twitter:image and JSON-LD "image" pointing to the ORIGINAL URLs (social networks need the full file).

7. Accessibility: text using the accent blue #0e3995 on dark backgrounds still fails contrast (the big stat numbers and their <span>, and the service links on dark cards "text-[hsl(var(--clay))] group-hover:text-white"). On dark backgrounds use a light tint of that blue (e.g. #9db8ff) so contrast is at least 4.5:1. Keep the blue on light backgrounds.

8. /get-your-discount page copy: the subtitle says "we'll send your exclusive discount straight to your inbox", but the form only asks for name and phone. Change it to "Complete the form below and we'll text you your exclusive discount." Keep the embedded form as is.

Publish and list every file changed.
```

Depois de publicar, me avise que eu rodo o Lighthouse de novo.
