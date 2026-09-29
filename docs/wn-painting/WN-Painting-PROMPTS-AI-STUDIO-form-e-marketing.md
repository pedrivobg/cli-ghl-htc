# WN Painting — prompts do AI Studio: formulário de orçamento e /marketing-form

Mande um de cada vez e publique no fim. Nenhum dos dois precisa de anexo.

## Prompt A — formulário de orçamento mandando o lead para a conta certa

```
The estimate request form (the "Get Your Free Quote" form on /contact and the estimate modal) is sending leads to the WRONG GoHighLevel account. It posts to https://backend.leadconnectorhq.com/external-tracking/events with locationId "OapfddiSt8scplnWw4oI" and trackingId "tk_7a365365ef774b539fae007737ae3ca6", which belong to another client (this site was copied from another project).

Fix it:
1. Use THIS site's own GoHighLevel sub-account: locationId = "emq5z0PS5ddzVY2lGz74" (WN Painting & Remodeling), and this project's own external tracking ID for that location. Keep projectId "1790021411576976864". Put locationId, trackingId and projectId in one config object (e.g. SITE.ghl) and read them from there instead of hardcoding them in the form component.
2. Keep formId exactly "estimate-request-form" (a GoHighLevel automation is triggered by that form identifier).
3. The form currently only sends first_name, last_name, email and phone. Also send the other two fields as contact custom fields, with the custom field ID as the key in formData and a label in formLabels:
   - selected service → custom field "Wj8uisiBI9U1dxqAN84s" (label "Service Needed")
   - project details / message → custom field "ITeFboOwitpZkMvI2kUQ" (label "Your Message")
   The service dropdown options must be the site's service list: Interior Painting, Exterior Painting, Deck Services, Flooring, Tile Installation, Drywall, Bathroom Remodeling, Carpentry.
4. Do not change the form's design, copy or the success message.

When done, search the whole project and confirm "OapfddiSt8scplnWw4oI" and "tk_7a365365ef774b539fae007737ae3ca6" no longer appear anywhere.
```

## Prompt B — criar a página /marketing-form

```
Create the route /marketing-form. It is an internal page for the business owner, not for customers:
- Minimal layout: no header, no footer, no sticky bar, no chat widget.
- Embed the GoHighLevel form with ID "lCm90buo3M7DvBr2ef7p" (Client Review Form) exactly the same way /get-your-discount embeds its form (same iframe embed + form_embed.js script), full width, centered, max-width around 640px.
- Small heading above the form: "Send a review request to a client".
- noindex, follow (meta robots) and a self canonical https://wnpaintingremodeling.com/marketing-form.
- Do NOT link to it from any page, menu or footer, and do NOT add it to sitemap.xml or llms.txt.
Do not change anything else on the site.
```

## Logos para trocar no GHL (subconta da WN)

Logo da WN: o do perfil da empresa (custom value **Logo URL**).

| Onde | Nome no GHL | ID | Hoje |
|---|---|---|---|
| Sites → Surveys | **Review Survey** | ek1jsJ1RYUKWI3P8di2u | Logo da CrewSystems |
| Sites → Forms | **Client Review + 1 Year Followup Sequence Form** | lCm90buo3M7DvBr2ef7p | Imagem da CrewSystems no topo |
| Sites → Forms | **Discount Form** | Azn2PIzKFaTaYbRbXTkI | Sem logo |
| Sites → Forms | **Website Form** | BMIbFdsl0lr68Cc6HZZu | Sem logo (não é usado no site; opcional) |
