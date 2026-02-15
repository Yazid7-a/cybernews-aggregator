# Informe diario de ciberseguridad — 2026-02-15
Ventana analizada: últimas **24h**
Noticias incluidas en reporte: **3** (limit=25)

## Top 5 del día
1. **CTM360: Lumma Stealer and Ninja Browser malware campaign abusing Google Groups** 
 - Severidad: **media** | Categoría: **malware** 
 - URL: https://www.bleepingcomputer.com/news/security/ctm360-lumma-stealer-and-ninja-browser-malware-campaign-abusing-google-groups/
2. **Microsoft Discloses DNS-Based ClickFix Attack Using Nslookup for Malware Staging** 
 - Severidad: **baja** | Categoría: **malware** 
 - URL: https://thehackernews.com/2026/02/microsoft-discloses-dns-based-clickfix.html
3. **Pastebin comments push ClickFix JavaScript attack to hijack crypto swaps** 
 - Severidad: **baja** | Categoría: **general** 
 - URL: https://www.bleepingcomputer.com/news/security/pastebin-comments-push-clickfix-javascript-attack-to-hijack-crypto-swaps/

## Tendencias (términos repetidos)
`clickfix`(2), `attack`(2), `malware`(2), `microsoft`(1), `discloses`(1), `dns-based`(1), `nslookup`(1), `staging`(1), `ctm360`(1), `lumma`(1)

## Detalle por noticia
### Microsoft Discloses DNS-Based ClickFix Attack Using Nslookup for Malware Staging
- Fuente: **TheHackerNews** | Dominio: `thehackernews.com`
- Publicado: **2026-02-15T19:40:00**
- Categoría: **malware** | Severidad: **baja**
- URL: https://thehackernews.com/2026/02/microsoft-discloses-dns-based-clickfix.html
**Resumen (3–5 líneas):**
Microsoft has disclosed details of a new version of the ClickFix social engineering tactic in which the attackers trick unsuspecting users into running commands that carry out a Domain Name System (DNS) lookup to retrieve the next-stage payload. Specifically, the attack relies on using the "nslookup" (short for nameserver lookup) command to execute a custom DNS lookup triggered via the Windows
**Qué debería mirar un SOC:**
Revisar logs/telemetría relevante, extraer IoCs, validar exposición y aplicar mitigaciones.
(BAJA) Monitorizar y registrar.

### CTM360: Lumma Stealer and Ninja Browser malware campaign abusing Google Groups
- Fuente: **BleepingComputer** | Dominio: `www.bleepingcomputer.com`
- Publicado: **2026-02-15T11:30:41**
- Categoría: **malware** | Severidad: **media**
- URL: https://www.bleepingcomputer.com/news/security/ctm360-lumma-stealer-and-ninja-browser-malware-campaign-abusing-google-groups/
**Resumen (3–5 líneas):**
CTM360 reports 4,000+ malicious Google Groups and 3,500+ Google-hosted URLs used to spread the Lumma Stealer infostealing malware and a trojanized "Ninja Browser." The report details how attackers abuse trusted Google services to steal credentials and maintain persistence across Windows and Linux systems.
**Qué debería mirar un SOC:**
Validar alcance, revisar actividad anómala, extraer IoCs y ajustar detecciones/alertas.
(MEDIA) Revisar en el día y ajustar detecciones.

### Pastebin comments push ClickFix JavaScript attack to hijack crypto swaps
- Fuente: **BleepingComputer** | Dominio: `www.bleepingcomputer.com`
- Publicado: **2026-02-15T10:17:27**
- Categoría: **general** | Severidad: **baja**
- URL: https://www.bleepingcomputer.com/news/security/pastebin-comments-push-clickfix-javascript-attack-to-hijack-crypto-swaps/
**Resumen (3–5 líneas):**
Threat actors are abusing Pastebin comments to distribute a new ClickFix-style attack that tricks cryptocurrency users into executing malicious JavaScript in their browser, allowing attackers to hijack Bitcoin swap transactions and redirect funds to attacker-controlled wallets.
**Qué debería mirar un SOC:**
Revisar logs/telemetría relevante, extraer IoCs, validar exposición y aplicar mitigaciones.
(BAJA) Monitorizar y registrar.
