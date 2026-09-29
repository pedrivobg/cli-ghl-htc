# WN Painting — corrigir as imagens trocadas (1 prompt, 1 anexo)

Anexe **só** o arquivo `wn-painting-04-deck-staining-multi-level.webp` (pasta `parte-1`
do zip) e cole o prompt abaixo.

```
Fix only the image mapping below. Do NOT change the design, text or anything else. Several images ended up in the wrong place and one URL is broken.

In the images object (the one with heroPhoto, services, gallery), set EXACTLY these values:

1. heroPhoto → https://vibe.filesafe.space/1790021411576976864/attachments/7e4a82e3-4ea7-434c-83ae-b15219ed2865.webp  (painter in a red shirt refinishing a door)
   Also update the hero <link rel="preload"> in the home head to this same URL. alt: "WN Painting & Remodeling painter refinishing an interior door in a Philadelphia home"

2. services.interior → https://vibe.filesafe.space/1790021411576976864/attachments/ea120a0b-dfc8-4447-aa35-4bd56363fa83.webp  (den with terracotta walls)
   The current value ".../d5b9500a-bc9d-46ea-bbd6-c7757aecf8c.webp" is a broken URL (404) — remove it everywhere.

3. services.exterior → https://vibe.filesafe.space/1790021411576976864/attachments/21ca6955-7308-493d-9a47-79efc725fb62.webp  (wood front door on a white brick facade). alt: "Refinished wood front door on a white brick row home"

4. services.flooring → https://vibe.filesafe.space/1790021411576976864/attachments/eece46ff-0bac-440d-9197-047866724a03.webp  (empty living room with hardwood floor). alt: "Finished hardwood floor in a freshly painted living room"

5. services.outdoorLiving (used by Deck Services and the Bucks County hero) → the ATTACHED image (wn-painting-04-deck-staining-multi-level.webp, a multi-level stained deck). Upload it as a project asset. alt: "Multi-level backyard deck after staining and surface protection"

6. Gallery item "Spacious Multi-Level Deck Painting & Surface Protection" → the same attached deck image (it currently shows the painter photo).

Keep every other image exactly as it is. After the change, the painter photo (7e4a82e3...) must be used ONLY as the hero. Then publish and list every value you changed.
```

Depois de publicar, me avise que eu confiro no site ao vivo.
