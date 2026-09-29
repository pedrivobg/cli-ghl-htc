# WN Painting — troca de imagens no AI Studio (4 mensagens, até 5 imagens cada)

Como usar:
1. Mande o **Prompt 1** com as imagens da pasta `parte-1` anexadas (5 imagens).
2. Confira o preview. Depois mande o **Prompt 2** com a `parte-2` (4 imagens), o
   **Prompt 3** com a `parte-3` (5) e o **Prompt 4** com a `parte-4` (2).
3. Publique no fim e me avise: eu confiro no site ao vivo se sobrou alguma imagem
   antiga ou de IA.

Não renomeie os arquivos. Cada imagem é citada pelo número no nome (01, 02…) e
também pela descrição.

---

## Prompt 1 — anexar a pasta parte-1 (imagens 01 a 05)

```
I'm attaching 5 real project photos from WN Painting & Remodeling (files 01 to 05, WebP, 1200x1600, 3:4 portrait). This is part 1 of 4 of an image replacement. Change ONLY images, their alt text and image attributes. Do not change any text, headings, layout, links, routes, meta titles/descriptions or forms.

Each service has ONE image reused everywhere that service appears: home page service cards, the /services page, the service page hero, "related services" cards on other service pages, and the service grid on each area page (/areas/philadelphia, /areas/bucks-county, /areas/west-chester). Update that single service → image mapping so all those places use the new photo, and set that service page's og:image / twitter:image to it.

1. HOME HERO (currently the AI-generated painter in a blue shirt: https://vibe.filesafe.space/1790021411576976864/assets/5e8cac2d-278d-4ee4-9a78-d9d3793ecc32.png)
   → file 01 (painter in a red shirt refinishing a door). alt: "WN Painting & Remodeling painter refinishing an interior door in a Philadelphia home". This is the LCP image: loading="eager" fetchpriority="high".

2. SERVICE IMAGES (right now Interior Painting shows a flooring photo, Exterior Painting shows a bedroom and Flooring shows a front door — fix that):
   - Interior Painting → file 02 (den with terracotta walls). alt: "Den with a terracotta painted accent wall and natural hardwood floor"
   - Exterior Painting → file 03 (wood front door, white brick facade). alt: "Refinished wood front door on a white brick row home"
   - Deck Services → file 04 (multi-level stained deck). alt: "Multi-level backyard deck after staining and surface protection"
   - Flooring → file 05 (empty living room with hardwood floor and globe pendant). alt: "Finished hardwood floor in a freshly painted living room"

For every image you touch: keep the current layout and object-fit cover, add width="1200" height="1600", and use loading="lazy" decoding="async" on everything except the hero. Don't touch any other image yet; more files come in the next messages.
```

---

## Prompt 2 — anexar a pasta parte-2 (imagens 06 a 09)

```
Part 2 of 4 of the image replacement. Same rules: change ONLY images, alt text and image attributes; keep all text, layout, links and routes as they are. Same service → image mapping as before: the image must change everywhere the service appears (home cards, /services, the service page hero and og:image, related-service cards, area page service grids).

- Tile Installation → file 06 (bathroom with gray tile floor and floating vanity). alt: "Bathroom with gray tile floor, floating vanity and navy walls"
- Drywall → file 07 (painter on a ladder, patched walls, drop cloths). alt: "Painter repairing and prepping walls before interior painting"
- Bathroom Remodeling → file 08 (green powder room). alt: "Powder room painted in deep green with new hardwood floor"
  This replaces the AI image https://vibe.filesafe.space/1790021411576976864/assets/8a331364-a4f6-40ae-aee3-964d37f22fac.png — it must not be referenced anywhere afterwards.
- Carpentry → file 09 (white mudroom built-in lockers with bench). alt: "Custom mudroom built-in lockers with bench and drawers"

Attributes: width="1200" height="1600", object-fit cover, loading="lazy" decoding="async".
```

---

## Prompt 3 — anexar a pasta parte-3 (imagens 10 a 14)

```
Part 3 of 4 of the image replacement. Same rules: change ONLY images, alt text and image attributes.

1. BEFORE / AFTER section ("See what professional painting can do"):
   - Before → file 10 (kitchen with masked cabinets). alt: "Kitchen cabinets masked and prepped before painting"
   - After → file 11 (finished kitchen, white uppers, green lowers). alt: "Kitchen after cabinet painting: white uppers and green lowers"

2. "WHY US" section image → file 12 (bedroom with navy accent wall and window bench). alt: "Bedroom with navy accent wall and custom window bench"

3. PROJECT PORTFOLIO / GALLERY (keep the same 6 titles and order, only fix the images):
   - "Living Room Interior Paint & Finished Hardwood Flooring" → file 13. alt: "Living room painted sage green with stone fireplace and refinished hardwood"
   - "Exterior Entryway, Custom Wood Front Door & Masonry Accents" → file 14. alt: "Refinished wood front door on a brick row home"
   - "Master Bedroom Deep Navy Accent Wall & Custom Window Bench" → file 12
   - "Spacious Multi-Level Deck Painting & Surface Protection" → the Deck Services image (file 04, from part 1)
   - "Modern Bathroom Renovation, Floating Sink & Tile Installation" → the Tile Installation image (file 06, from part 2)
   - "Custom Kitchen Cabinet Paint & Detailed Trim Remodel" → file 11

4. AREA AND INDEX PAGE heroes (also set each page's og:image to the same image):
   - /areas/philadelphia → file 14. alt: "Refinished front door on a Philadelphia brick row home"
   - /areas/bucks-county → the Deck Services image (file 04). alt: "Stained multi-level deck in Bucks County"
   - /areas (index) → file 14
   - /services (index) → file 11

Attributes: width="1200" height="1600", object-fit cover, loading="lazy" decoding="async".
```

---

## Prompt 4 — anexar a pasta parte-4 (imagens 15 e 16)

```
Part 4 of 4, the last one. Same rules: change ONLY images, alt text and image attributes.

1. FINAL CTA section ("We transform your home") → file 15 (stone house with double wood entry doors). alt: "Refinished double entry doors on a stone house"
2. /areas/west-chester hero and og:image → file 15. alt: "Refinished double entry doors on a stone house in West Chester"
3. DEFAULT SOCIAL / SCHEMA IMAGE → file 16 (wn-painting-16-social-share-kitchen.jpg, 1200x630). Use it as og:image and twitter:image on the home page and /contact, and as the business "image" in the JSON-LD schema.

Final check: after this, none of these old images may be referenced anywhere (pages, og tags, JSON-LD, sitemap). Search the whole project and replace any leftover following the mapping above:
https://vibe.filesafe.space/1790021411576976864/attachments/205157b6-3b2a-477e-9587-dcf742cd4496.jpg
https://vibe.filesafe.space/1790021411576976864/attachments/cbfd98e0-47a1-42ab-a331-a763c4492b3b.jpg
https://vibe.filesafe.space/1790021411576976864/attachments/7d38ce66-a7c4-4c8a-8b91-35a92f92c709.jpg
https://vibe.filesafe.space/1790021411576976864/attachments/e5e8a0b4-6635-4403-92fc-c086383645ab.jpg
https://vibe.filesafe.space/1790021411576976864/attachments/0ae057c0-5f77-4131-8846-1f45e9dd0c2b.jpg
https://vibe.filesafe.space/1790021411576976864/attachments/8f860391-bf08-4b75-a1fb-d7f3b64728a5.jpg
https://vibe.filesafe.space/1790021411576976864/attachments/b1e9592d-6fda-4dea-861b-707403171b89.jpg
https://vibe.filesafe.space/1790021411576976864/assets/5e8cac2d-278d-4ee4-9a78-d9d3793ecc32.png
https://vibe.filesafe.space/1790021411576976864/assets/8a331364-a4f6-40ae-aee3-964d37f22fac.png
Keep the logo and the CrewSystems footer badge as they are. Then publish.
```
