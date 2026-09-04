# TICKETS-SEC.md — Ordre d'implémentation hexa-sec (SEC)

> **Fichier local de pilotage.** Reflet de la roadmap Jira `SEC` (projet hexa-sec).
> **hexa-sec = le pack cybersécurité** : il ORCHESTRE les scanners du marché
> et CORRÈLE leurs findings (DDD).
> **La phrase** : « Nessus trouve des failles. Burp trouve des failles.
> hexa-sec trouve la faille qui compte. »
> **Roadmap longue** : 6 mois et plus — chaque ticket est pensé, rien n'est
> précipité. La vision est posée, l'exécution attendra son heure.
>
> **Ordre global** : bootstrap → domaine DDD → cœur (corrélation/scoring) →
> adapters scanners (TOUS les outils) → MCP/CLI → Rust (parsing) →
> Docker (isolation) → rapport/AI → docs.

---

## Légende

- ✅ = ticket **Terminé** · ⬜ = **À faire** · 🦀 = candidat **Rust**
- **1 label par ticket** (la règle) : chaque ticket a UN SEUL label = son territoire
- Le domaine est PUR : les scanners sont des adapters interchangeables
- **Pas de MVP** : l'inventaire des outils est EXHAUSTIF — chaque catégorie a
  TOUS ses outils, ils se branchent au fur et à mesure (1 adapter par outil)

---

## 📊 Avancement global

- [x] **2/2 bootstrap** — le repo existe (hexa-tools/hexa-sec, branche `dev`) ; SEC-1 (structure + domaine) + SEC-2 (.env) **Terminés** (HS-1, HS-2 sur Jira)
- [ ] **Priorité actuelle** : PHASE 1 — Domaine DDD (les 37 contextes) — **SEC-3 ouvert** (HS-3, spec : `tickets/96-sec-domain.md`)
- [ ] **Contexte 5 (scan_status) spécifié** (2026-08-31) — spec : `tickets/97-sec-scan-status.md` — reste à implémenter (TDD RED→GREEN)

---

## PHASE 0 — Bootstrap (🔒)

> La fondation : repo, structure hexagonale, domaine, guard, MCP server.

| Avancement | Ticket · Labels | Rôle |
|---|---|---|
| ✅ | **SEC-1** · bootstrap | Bootstrap — repo + structure hexagonale + domaine DDD (les 37 contextes) · **spec : `tickets/92-sec-bootstrap.md`** · HS-1 |
| ✅ | **SEC-2** · infra | .env — création + inventaire complet des clés (tous les projets, le template .env.example) · **spec : `tickets/93-sec-env.md`** · HS-2 |

### 📎 Les specs détaillées (les fichiers tickets)

> Les specs complètes vivent dans `tickets/` (le pattern hexagents).
> La roadmap ci-dessus EST le pilotage ; les fichiers tickets SONT le détail.

**SEC-1 — Bootstrap** (Story · label `bootstrap`)
- **Les 5 ports driven** (les familles de scanners) :

| Port | Vendors (adapters) |
|---|---|
| WebScannerPort | Burp, ZAP, Nuclei, WPScan, Nikto |
| NetworkScannerPort | Nessus, OpenVAS, Qualys, Nmap, Masscan |
| CodeScannerPort | Gitleaks, TruffleHog, Semgrep, Bandit, Trivy, OSV |
| ConfigScannerPort | OpenSCAP, Lynis, Sslscan, Wazuh, Checkov |
| KnowledgePort | NVD, EPSS, Exploit-DB, Shodan, Censys, WHOIS/DNS |

- **Les 5 use cases** (le cerveau) : `scan_asset` (US-1) · `correlate` (US-2, **LE CŒUR**) · `score_report` (US-3) · `manage_mandate` (US-4, le légal) · `generate_report` (US-5)
- **Critères de succès** : repo public Apache 2.0 + badge · structure hexagonale complète · domaine (37 contextes : squelettes + value objects) · serveur MCP (`entrypoint: mcp://`, les 5 tools) · mandat dans le domaine (Godfrain) — AUCUN scan sans mandat · `hexa_guard.py` (R15-R19) vert · TDD RED→GREEN (asset, finding, correlation, mandate) · coverage ≥ 95 % · datasets de fixtures (Nessus XML, Burp JSON, Nuclei JSON…) · `make guard/check/test` verts
- ⚠️ **Écart 30→37** : le ticket 92 montre encore 30 contextes (version initiale) ; la roadmap en a **37** (ajout de wifi/email/dns/cloud/container/mobile/api + hydra). **La roadmap fait foi** — le ticket sera aligné à l'implémentation.

**SEC-2 — .env & inventaire des clés** (Tâche · label `infra`)
- **La règle d'or des clés** : `.env` (clés RÉELLES) → **jamais commité** (`.gitignore`) · `.env.example` (clés VIDES) → **commité** (le contrat) · chaque clé **chiffrée au repos** · chaque tenant a **SES clés** · `make check` valide que les clés REQUISES sont présentes
- **L'inventaire complet par projet** (le contenu du template `.env.example`) :

```bash
# 🦊 HEXAGENTS (le harness — les LLM)
OPENAI_API_KEY=            # OpenAI (chat/completions)
ANTHROPIC_API_KEY=         # Anthropic (Claude)
DEEPSEEK_API_KEY=          # DeepSeek (le SLM distant)
OPENROUTER_API_KEY=        # OpenRouter (le fallback)
XAI_API_KEY=               # xAI (Grok)
GROQ_API_KEY=              # Groq (les modèles rapides)
MISTRAL_API_KEY=           # Mistral
GEMINI_API_KEY=            # Google Gemini
AZURE_OPENAI_KEY=          # Azure OpenAI (l'enterprise)
AZURE_OPENAI_ENDPOINT=     # l'endpoint Azure
OLLAMA_BASE_URL=http://localhost:11434   # Ollama (le SLM local, optionnel)
FAL_KEY=                   # fal.ai (image gen)
KREA_API_KEY=              # Krea (image gen)
ELEVENLABS_API_KEY=        # ElevenLabs (TTS)
PICOVOICE_API_KEY=         # Porcupine (wake word)
BROWSER_CDP_URL=           # le CDP du browser (optionnel)

# ⚓ HEXAWYN (k8s — le CP)
KUBECONFIG=                # le kubeconfig du client (jamais partagé)
KUBERNETES_CONTEXT=        # le contexte k8s actif
HEXAWYN_CP_URL=            # l'URL du control plane
HEXAWYN_CP_TOKEN=          # le token d'accès au CP
AWS_ACCESS_KEY_ID=         # AWS (billing)
AWS_SECRET_ACCESS_KEY=
AZURE_CLIENT_ID=           # Azure (billing)
AZURE_CLIENT_SECRET=
GCP_SERVICE_ACCOUNT=       # GCP (billing)
GCP_CREDENTIALS_PATH=
POLAR_API_KEY=             # Polar.sh (les paiements)
POLAR_WEBHOOK_SECRET=      # la signature des webhooks Polar

# 💚 HEXA-HEALTH (data-stack — les vendors)
SNOWFLAKE_ACCOUNT=         # Snowflake
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
DATABRICKS_HOST=           # Databricks
DATABRICKS_TOKEN=
GCP_PROJECT_ID=            # GCP (BigQuery)
GCP_CREDENTIALS_PATH=
AWS_REGION=                # AWS (Redshift, S3, Athena)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AZURE_CONNECTION_STRING=   # Azure (Synapse, Blob)
KAFKA_BOOTSTRAP_SERVERS=   # Kafka
KAFKA_API_KEY=
FIVETRAN_API_KEY=          # Fivetran
FIVETRAN_API_SECRET=
AIRBYTE_API_URL=           # Airbyte
AIRBYTE_API_TOKEN=
AIRFLOW_API_URL=           # Airflow
AIRFLOW_API_TOKEN=
DAGSTER_API_URL=           # Dagster
DAGSTER_API_TOKEN=
PREFECT_API_URL=           # Prefect
PREFECT_API_TOKEN=
TRINO_HOST=                # Trino
TRINO_USER=
TRINO_PASSWORD=
HEXA_HEALTH_MCP_TOKEN=     # le token du serveur MCP

# 🛡️ HEXA-SEC (la sécurité — les scanners)
SHODAN_API_KEY=            # Shodan (exposition Internet — ~49 $/mois)
NVD_API_KEY=               # NVD (la base des CVE — gratuite, quota+)
CENSYS_API_ID=             # Censys (inventaire Internet)
CENSYS_API_SECRET=
WHOISXML_API_KEY=          # WHOIS (la surface)
NESSUS_URL=                # Nessus (le serveur privé)
NESSUS_ACCESS_KEY=         # le token Nessus
NESSUS_SECRET_KEY=
QUALYS_USERNAME=           # Qualys (le cloud scanner)
QUALYS_PASSWORD=
AWS_ACCESS_KEY_ID=         # AWS (audit cloud)
AWS_SECRET_ACCESS_KEY=
AZURE_CLIENT_ID=           # Azure
AZURE_CLIENT_SECRET=
AZURE_TENANT_ID=
GCP_SERVICE_ACCOUNT=       # GCP
GCP_CREDENTIALS_PATH=
AD_DOMAIN=                 # le domaine AD du client (BloodHound — avec mandat)
AD_USERNAME=               # le compte d'audit (droits limités)
AD_PASSWORD=
HEXA_SEC_MCP_TOKEN=        # le token du serveur MCP
GITHUB_TOKEN=              # Gitleaks/TruffleHog sur les repos privés (optionnel)
GITLAB_TOKEN=
SLACK_WEBHOOK_URL=         # les notifications (optionnel)

# ☁️ HEXA-CLOUD (la caisse — les paiements)
JWT_PRIVATE_KEY=           # la clé de signature des licences (RS256)
JWT_PUBLIC_KEY=
MAGIC_LINK_SECRET=         # la signature des magic links
POLAR_API_KEY=             # Polar.sh
POLAR_WEBHOOK_SECRET=
STRIPE_SECRET_KEY=         # Stripe (si utilisé)
STRIPE_WEBHOOK_SECRET=
RESEND_API_KEY=            # Resend (les emails transactionnels)
DATABASE_URL=              # PostgreSQL
REDIS_URL=                 # Valkey/Redis (la queue)
ENCRYPTION_KEY=            # AES-256-GCM (les secrets des tenants)

# 🧊 HEXAGENTS-CLOUD (le privé — les packs)
DATABASE_URL=              # PostgreSQL (les tenants)
REDIS_URL=                 # Valkey (la queue HC-19)
POLAR_API_KEY=             # la caisse (partagée avec hexa-cloud)
POLAR_WEBHOOK_SECRET=
TELEGRAM_BOT_TOKEN=        # Pack Telegram (HC-24)
WHATSAPP_API_TOKEN=        # Pack WhatsApp (HC-25 — Business API)
SLACK_BOT_TOKEN=           # Pack Slack (HC-26)
SLACK_APP_TOKEN=
LINKEDIN_CLIENT_ID=        # LinkedIn (l'API — HC-28 le pack social)
LINKEDIN_CLIENT_SECRET=
TWITTER_API_KEY=           # X
TWITTER_API_SECRET=
INSTAGRAM_TOKEN=           # IG
FACEBOOK_APP_TOKEN=        # FB
TIKTOK_CLIENT_KEY=         # TikTok
ENCRYPTION_KEY=            # AES-256-GCM (les secrets par tenant)
```

- **La matrice des clés** (le résumé) :

| Projet | Clés obligatoires | Clés optionnelles |
|---|---|---|
| **hexagents** | LLMPort (≥1 provider) | Ollama, vision, TTS |
| **hexawyn** | KUBECONFIG | CP token, billing cloud, Polar |
| **hexa-health** | ≥1 vendor data | les autres vendors, MCP token |
| **hexa-sec** | ≥1 scanner + le mandat | les autres scanners, cloud, AD |
| **hexa-cloud** | JWT, Polar, Resend, DB | Stripe, encryption |
| **hexagents-cloud** | DB, Redis, Polar | les canaux, le social |

- **Critères de succès** : `.env.example` créé (le template versionné, toutes les clés) · `.env` dans `.gitignore` · `make check` valide (requises présentes, inconnues refusées) · clés chiffrées au repos · chaque projet a SA section · la doc « où va chaque clé » · `make guard/check/test` verts
- 💡 Le contrat : le template EST le CONTRAT — si une clé manque au template, elle manque au système. Les secrets d'hexa-sec sont les plus sensibles (les scanners donnent accès au SI).

---

## PHASE 1 — Domaine DDD (🐍 le cœur pur)

> Les 37 contextes bornés — le domaine ne connaît AUCUN scanner.
> Chaque contexte = value objects + agrégats + tests (coverage ≥ 95 %).
> **Ordre logique** : les fondations (asset/finding/vuln) → la valeur
> (correlation/scoring) → le légal (consent) → le reste.

| # | Contexte · Label | Rôle |
|---|---|---|
| ⬜ | **SEC-3** · domain | **Domaine DDD — compléter les 37 contextes** (les 7 manquants : wifi/email/dns/cloud/container/mobile/api + consolidation des 30) · **spec : `tickets/96-sec-domain.md`** · HS-3 |
| 1 | asset · domain | Asset Management — l'inventaire de ce qu'on audite |
| 2 | finding · domain | Finding — ce qu'un scanner a trouvé (normalisé) |
| 3 | vulnerability · domain | Vulnerability — CVE, CVSS, EPSS |
| 4 | scan · domain | Scan orchestration + statuts |
| 5 | scan_status · domain | L'état du scan (PENDING/RUNNING/DONE/FAILED) — **spécifié** : `tickets/97-sec-scan-status.md` |
| 6 | asset_inventory · domain | Les ports, services, versions détectés |
| 7 | correlation · domain | **LA VALEUR : le croisement des findings (6 types)** |
| 8 | scoring · domain | Le score : sévérité × exploitabilité × exposition × impact |
| 9 | report · domain | Le rapport « fix first » + priority actions |
| 10 | consent · domain | **LE LÉGAL : mandat + autorisation écrite (Godfrain)** |
| 11 | web_risk · domain | Les failles web (OWASP Top 10) |
| 12 | network_risk · domain | L'exposition réseau |
| 13 | secret_risk · domain | Les secrets commités |
| 14 | dependency_risk · domain | Les dépendances + licences |
| 15 | code_risk · domain | Le code statique |
| 16 | config_risk · domain | Les benchmarks CIS |
| 17 | tls_risk · domain | Les certificats TLS |
| 18 | iaac_risk · domain | L'infra-as-code (terraform/helm) |
| 19 | compliance · domain | ISO 27001, RGPD, NIS2, PCI-DSS |
| 20 | identity_risk · domain | AD, SSO, accès |
| 21 | wifi_risk · domain | **Le réseau sans fil — SSID, chiffrement, clients** |
| 22 | email_risk · domain | **L'usurpation d'email (SPF, DKIM, DMARC)** |
| 23 | dns_risk · domain | **Les sous-domaines oubliés, le DNS exposé** |
| 24 | cloud_risk · domain | **Les ressources cloud mal configurées** |
| 25 | container_risk · domain | **Les images et runtimes containers** |
| 26 | mobile_risk · domain | **Les applications mobiles** |
| 27 | api_risk · domain | **Les API exposées** |
| 28 | threat_intel · domain | Les menaces connues |
| 29 | exploit_intel · domain | Les exploits publiés |
| 30 | temporal · domain | Ce qui a changé entre 2 scans |
| 31 | business_impact · domain | La criticité métier des assets |
| 32 | remediation · domain | Les fixes et leur statut |
| 33 | notification · domain | Les alertes |
| 34 | evidence · domain | La preuve + audit trail |
| 35 | tenant · domain | L'isolation par client |
| 36 | ai_assist · domain | Le résumé LLM du rapport |
| 37 | pack_config · domain | Le manifest pack.yaml (mcp://) |

---

## PHASE 2 — Cœur application (🐍 le cerveau)

> Les use cases : l'orchestration + LA corrélation + le scoring.
> **Pourquoi hexa-sec est le pack LE MOINS CHRONOPHAGE** : on orchestre des
> outils existants au lieu de tout construire — chaque scanner = un adapter
> (un fichier), pas un moteur à écrire. Le code à écrire = la corrélation +
> le scoring + le rapport = le cerveau, pas les muscles.

| Avancement | Ticket · Labels | Rôle |
|---|---|---|
| ⬜ | scan_asset · backend | US-1 : lancer les scanners sur un asset (avec mandat) |
| ⬜ | correlate · backend | US-2 : **corréler les findings — LE CŒUR** (attack-chain, exposure, noise, temporal, compliance, business) |
| ⬜ | score_report · backend | US-3 : scorer et trier « corrige CECI d'abord » |
| ⬜ | manage_mandate · backend | US-4 : le consentement légal (obligatoire avant tout scan) |
| ⬜ | generate_report · backend | US-5 : le rapport final (score + top 5 + résumé LLM) |

---

## PHASE 2a — Les 4 entrées du pack (🎯 ce que hexa-sec reçoit)

> hexa-sec est un pack « à entrées riches » : il faut 4 choses pour lancer un
> audit. L'entrée la plus importante est le MANDAT (le contrat légal) — sans
> lui, les 3 autres ne servent à rien.

| Entrée | Ce que c'est | Fournie par | Format / Domaine |
|---|---|---|---|
| **1. Les CIBLES** (ce qu'on audite) | Domaines (acme.com), IPs/plages (192.168.0.0/24), URLs, repos git, réseau WiFi (SSID) | Le client, dans le mandat | `manage_mandate` (consent/ + asset/) |
| **2. Les CLÉS des outils** (les identifiants) | Chaque scanner exige une auth : Shodan (api_key ~49 $/mois), NVD (api_key gratuite), Nessus (url+token), Prowler (AWS keys), BloodHound (credentials AD), Qualys (user+password) — SANS clé → 401 · JAMAIS en clair (chiffrées) · chaque tenant a SES clés | L'opérateur (toi), dans la config | `pack_config` (le manifest + le store de secrets) |
| **3. Le MANDAT** (le légal) | Le client · le périmètre exact (cibles AUTORISÉES) · les dates de validité · la signature — AUCUN scan sans mandat (loi Godfrain) · encore plus vrai pour les outils offensifs (Metasploit, Pacu, Wifiphisher) | Le client signé | `manage_mandate` (consent/) |
| **4. Les PARAMÈTRES du scan** (comment auditer) | La profondeur (rapide/complet/offensif) · les exclusions (ne pas toucher tel hôte) · le créneau (le scan la nuit) · le manifest de scan | L'opérateur (toi ou l'agent) | `scan_asset` (scan/) |

**Le flux complet** :
```
LE CLIENT                       TOI (l'opérateur)
│  mandat signé + cibles          │  clés des outils + paramètres
▼                                 ▼
manage_mandate (US-4) → le mandat validé → scan_asset (US-1)
                                              │
                                              ▼
                              les scanners tournent (avec les clés)
                                              │
                                              ▼
                              correlate (US-2) → score (US-3) → report (US-5)
                                              │
                                              ▼
                              LE RAPPORT (le livrable au client)
```

**La bonne nouvelle** : les 4 entrées sont DÉJÀ dans le domaine du bootstrap —
`consent/` (le mandat), `asset/` (les cibles), `pack_config/` (les clés),
`scan/` (les paramètres). Les contextes conçus SONT les entrées.

---

## PHASE 2b — Le rapport d'audit (📊 LE livrable vendu)

> **Le rapport EST le produit** — c'est ce que le client achète et lit.
> Pas une liste de failles : UNE page qui dit la vérité en langage clair.

**`generate_audit_report(mandate_id, snapshot_id) → AuditReport`**

Le rapport d'audit a 5 sections — dans CET ordre (le client lit la 1re, le
technicien lit la 4e) :

```
| # | Section | Ce qu'elle contient | Pour qui |
|---|---|---|---|
| **1** | 🎯 **LE SCORE GLOBAL** (la page 1) | « Votre SI est à 62/100 — niveau MODÉRÉ » · le score par domaine (web, réseau, secrets, config, wifi, email, dns, cloud, containers, mobile, api) · la jauge visuelle (rouge/orange/vert) · l'évolution vs le scan précédent (↑ 12 points) | Le CTO (lit la 1re) |
| **2** | 🔴 **LE TOP 5** (le « fix first ») | Chaque item : la faille, POURQUOI elle compte, le fix, l'effort · « 1. Un token API exposé → révoquez-le (5 min) » · trié par sévérité × exploitabilité × exposition × impact × facilité | Le CTO / l'équipe |
| **3** | 🧠 **LA CORRÉLATION** (LA valeur) | « La chaîne d'attaque : le serveur X a une CVE critique ET une app SQLi ET le token commité » · « 3 ports visibles sur Internet sans nécessité » · « 14 alertes Nessus sont en fait sans risque » | Le CTO (ce qu'aucun outil seul ne voit) |
| **4** | 🔬 **LE DÉTAIL TECHNIQUE** (la preuve) | Chaque finding : la CVE, le CVSS, l'EPSS, l'évidence (la capture), la remediation exacte · les 200 pages de Nessus CONDENSÉES en 10 pages lisibles | Le RSSI / le tech (lit la 4e) |
| **5** | 📋 **LA CONFORMITÉ** (le budget obligatoire) | Le score ISO 27001 / RGPD / NIS2 / PCI-DSS par domaine · « Vous êtes prêt pour l'audit annuel » / « Voici les 4 écarts » | Le DSI / la conformité |
```

### Les 3 formats de sortie

| Format | Pour qui | Quand |
|---|---|---|
| **Le rapport Markdown** | Le client (le livrable) | Toujours |
| **Le rapport HTML** | Le dashboard interactif | L'option web |
| **Le résumé LLM (AI assist)** | Le CTO pressé | Toujours (le 1er paragraphe) |

### Les critères du rapport

- [ ] Le score global + jauge + évolution (la page 1)
- [ ] Le top 5 « fix first » (le différenciateur)
- [ ] Les corrélations racontées en langage clair (LA valeur)
- [ ] Le détail technique avec les preuves (l'évidence)
- [ ] Le score conformité (ISO/RGPD/NIS2/PCI-DSS)
- [ ] Le résumé LLM en 1er paragraphe
- [ ] Le rapport est VENDU — c'est le livrable, pas un sous-produit

---

## PHASE 3 — Adapters scanners (🔌 TOUS les outils du marché)

> **L'inventaire EXHAUSTIF** — pas de MVP : chaque catégorie a TOUS ses outils,
> chacun devient un adapter (un fichier qui traduit son format → Asset/Finding).
> Les 12 familles couvrent TOUT le SI d'une entreprise.

### 3.1 🕸️ Scanners WEB (les applications)
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| WebScannerPort · burp | Burp Suite | Les failles web (SQLi, XSS, auth) — le standard |
| WebScannerPort · zap | OWASP ZAP | Le clone open source de Burp |
| WebScannerPort · nuclei | Nuclei (ProjectDiscovery) | Les templates de vulnérabilités |
| WebScannerPort · wpscan | WPScan | Les failles WordPress |
| WebScannerPort · nikto | Nikto | Les misconfigurations serveur web |
| WebScannerPort · arachni | Arachni | Le scanner web complet |
| WebScannerPort · sqlmap | sqlmap | L'injection SQL automatisée |
| WebScannerPort · dirsearch | dirsearch | La découverte de répertoires cachés |
| WebScannerPort · ffuf | ffuf | Le fuzzing (répertoires, params, sous-domaines) |
| WebScannerPort · gobuster | Gobuster | La force brute de répertoires/DNS |
| WebScannerPort · acunetix | Acunetix | Le scanner web commercial (SQLi, XSS, auth — le standard payant) |
| WebScannerPort · appscan | HCL AppScan | Le scanner web enterprise (les gros SI) |
| WebScannerPort · invicti | Invicti (Netsparker) | Le scanner DAST commercial (proof-based) |
| WebScannerPort · wapiti | Wapiti | Le scanner web open source (le FR) |
| WebScannerPort · wfuzz | Wfuzz | Le fuzzing web (paramètres, payloads) |
| WebScannerPort · feroxbuster | Feroxbuster | La force brute de répertoires (Rust — rapide) |

### 3.2 🖥️ Scanners RÉSEAU & INFRA
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| NetworkScannerPort · nessus | Nessus (Tenable) | Les CVE par host — le standard enterprise |
| NetworkScannerPort · openvas | OpenVAS | Le clone open source de Nessus |
| NetworkScannerPort · qualys | Qualys | Le cloud scanner (les gros SI) |
| NetworkScannerPort · nmap | Nmap | Les ports + versions + services |
| NetworkScannerPort · masscan | Masscan | Le scan de ports ultra-rapide (l'inventaire) |
| NetworkScannerPort · zmap | Zmap | Le scan Internet entier (la recherche) |
| NetworkScannerPort · netdiscover | Netdiscover | La découverte ARP du réseau local |
| NetworkScannerPort · naabu | Naabu (ProjectDiscovery) | Le scan de ports rapide (la découverte) |
| NetworkScannerPort · rustscan | RustScan | Le scan de ports ultra-rapide (Rust) |
| NetworkScannerPort · arp-scan | arp-scan | La découverte ARP des hôtes (l'inventaire) |
| NetworkScannerPort · hping3 | hping3 | Le test des pare-feux (paquets forgés) |
| NetworkScannerPort · bettercap | Bettercap | Le couteau suisse réseau (MITM, ARP, sniffing) |

### 3.3 📡 Scanners WIFI (le réseau sans fil)
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| WifiScannerPort · aircrack | Aircrack-ng | L'audit WiFi complet (capture, analyse) |
| WifiScannerPort · kismet | Kismet | La découverte de réseaux + clients + intrusions |
| WifiScannerPort · wifite | Wifite | L'audit WiFi automatisé |
| WifiScannerPort · wireshark | Wireshark | L'analyse des paquets (la preuve) |
| WifiScannerPort · reaver | Reaver | Le test des WPS faibles |
| WifiScannerPort · hashcat | hashcat | Le test de robustesse des mots de passe WiFi |
| WifiScannerPort · wifiphisher | Wifiphisher | Le test de l'ingénierie sociale WiFi (avec mandat !) |
| WifiScannerPort · mdk4 | MDK4 | Les tests de robustesse (deauth, beacon flood) |
| WifiScannerPort · pixiewps | Pixiewps | Le test des WPS hors ligne (offline) |
| WifiScannerPort · bully | Bully | Le brute-force WPS (le complément de reaver) |
| WifiScannerPort · fluxion | Fluxion | Le test du jumeau maléfique (evil twin — avec mandat !) |
| WifiScannerPort · eaphammer | EAPhammer | Le test WPA2-Enterprise (evil twin — avec mandat !) |

### 3.4 🔑 Scanners de SECRETS & CODE
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| CodeScannerPort · gitleaks | Gitleaks (Go) | Les secrets commités (tokens, clés) |
| CodeScannerPort · trufflehog | TruffleHog | Les secrets + l'historique git |
| CodeScannerPort · semgrep | Semgrep | Les patterns de code risqués |
| CodeScannerPort · bandit | Bandit | Les failles Python |
| CodeScannerPort · trivy | Trivy | Les dépendances vulnérables + licences + images |
| CodeScannerPort · osv | OSV Scanner | Les CVE des dépendances (API gratuite) |
| CodeScannerPort · snyk | Snyk | Les dépendances + IaC + containers |
| CodeScannerPort · detect_secrets | detect-secrets | Les secrets (Yelp) |
| CodeScannerPort · git_secrets | git-secrets | Le garde anti-secrets (Amazon) |
| CodeScannerPort · ggshield | GitGuardian | Les secrets commités (le standard SaaS) |
| CodeScannerPort · sonarqube | SonarQube | La qualité ET la sécurité du code (le standard) |
| CodeScannerPort · gosec | Gosec | Les failles Go (le statique) |
| CodeScannerPort · brakeman | Brakeman | Les failles Ruby/Rails (le statique) |
| CodeScannerPort · flawfinder | Flawfinder | Les failles C/C++ (le statique) |

### 3.5 🔐 Scanners CONFIG & IDENTITÉ
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| ConfigScannerPort · openscap | OpenSCAP | La conformité CIS benchmarks |
| ConfigScannerPort · lynis | Lynis | L'audit de durcissement système |
| ConfigScannerPort · sslscan | Sslscan | Les certificats TLS |
| ConfigScannerPort · testssl | testssl.sh | L'analyse TLS complète |
| ConfigScannerPort · wazuh | Wazuh | Les agents + la posture des hosts |
| ConfigScannerPort · checkov | Checkov | L'infra-as-code (terraform/helm) risquée |
| ConfigScannerPort · ciscat | CIS-CAT | Le scanner officiel CIS |
| ConfigScannerPort · tfsec | tfsec | L'infra-as-code Terraform risquée (le statique) |
| ConfigScannerPort · kics | KICS (Checkmarx) | L'infra-as-code multi (terraform, helm, k8s) |
| ConfigScannerPort · inspec | Chef InSpec | Les tests de conformité en code |

### 3.6 📧 Scanners EMAIL (l'usurpation — le vecteur n°1 des PME)
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| EmailScannerPort · checkdmarc | checkdmarc | SPF/DKIM/DMARC — la conformité email |
| EmailScannerPort · dmarctest | dmarctest.org | Le diagnostic DMARC complet |
| EmailScannerPort · mailspoof | MailSpoof | Le test d'usurpation d'expéditeur |
| EmailScannerPort · mxtoolbox | MxToolbox | Le diagnostic DNS/email |
| EmailScannerPort · swaks | swaks | Le test SMTP (spoofing, auth, STARTTLS) |

### 3.7 🌐 Scanners DNS (les portes oubliées)
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| DnsScannerPort · subfinder | subfinder | La découverte de sous-domaines (passive) |
| DnsScannerPort · amass | Amass (OWASP) | L'énumération DNS complète |
| DnsScannerPort · dnsrecon | dnsrecon | La reconnaissance DNS |
| DnsScannerPort · dnsenum | dnsenum | L'énumération DNS classique |
| DnsScannerPort · massdns | MassDNS | L'énumération DNS à grande échelle |
| DnsScannerPort · dnsx | dnsx (ProjectDiscovery) | L'énumération DNS multiple (le standard) |
| DnsScannerPort · puredns | Puredns | L'énumération DNS à grande échelle (le fork maintenu) |
| DnsScannerPort · dnstwist | DNSTwist | Les typosquats de votre domaine (le phishing) |
| DnsScannerPort · crtsh | crt.sh | Les certificats émis (CT logs — passif) |

### 3.8 ☁️ Scanners CLOUD (le SI moderne)
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| CloudScannerPort · prowler | Prowler | L'audit AWS/Azure/GCP (CIS cloud) |
| CloudScannerPort · scoutsuite | Scout Suite | L'audit multi-cloud |
| CloudScannerPort · cloudsploit | CloudSploit | Les risques cloud |
| CloudScannerPort · pacu | Pacu | Le framework d'attaque AWS (avec mandat !) |
| CloudScannerPort · pmapper | PMapper | Le mapping des privilèges IAM AWS (les chemins) |
| CloudScannerPort · cloudfox | CloudFox | La reconnaissance cloud offensive (multi-cloud) |
| CloudScannerPort · skyark | SkyArk | Les shadow admins Azure (l'AAD) |

### 3.9 🏢 Scanners AD / IDENTITÉ (le cœur des SI d'entreprise)
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| IdentityScannerPort · bloodhound | BloodHound | Le mapping des chemins d'attaque AD |
| IdentityScannerPort · crackmapexec | CrackMapExec | L'évaluation des accès AD |
| IdentityScannerPort · impacket | Impacket | Le toolkit d'analyse AD |
| IdentityScannerPort · responder | Responder | La détection des protocoles faibles |
| IdentityScannerPort · ldapsearch | ldapsearch | L'inspection LDAP |
| IdentityScannerPort · kerbrute | Kerbrute | Le test des comptes AD |
| IdentityScannerPort · hydra | THC-Hydra | Le brute-force des credentials réseau (SSH, RDP, HTTP — avec mandat !) |
| IdentityScannerPort · pingcastle | PingCastle | L'hygiène AD (le score — le standard gratuit) |
| IdentityScannerPort · purpleknight | Purple Knight (Quest) | L'évaluation AD (le complément enterprise) |
| IdentityScannerPort · certipy | Certipy | Les attaques AD CS (certificats — avec mandat !) |
| IdentityScannerPort · rubeus | Rubeus | Les attaques Kerberos (Kerberoasting — avec mandat !) |
| IdentityScannerPort · mimikatz | Mimikatz | Le test des credentials Windows (avec mandat !) |

### 3.10 🐳 Scanners CONTAINERS & K8S
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| ContainerScannerPort · falco | Falco | Le runtime containers (intrusions) |
| ContainerScannerPort · kubehunter | kube-hunter | Les failles Kubernetes |
| ContainerScannerPort · kubeench | kube-bench | La conformité CIS Kubernetes |
| ContainerScannerPort · grype | Grype | Les vulnérabilités des images |
| ContainerScannerPort · dockle | Dockle | Les bonnes pratiques Docker |
| ContainerScannerPort · hadolint | Hadolint | Le lint des Dockerfiles |
| ContainerScannerPort · kubescape | Kubescape (ARMO) | La posture Kubernetes + les CVE (le standard) |
| ContainerScannerPort · popeye | Popeye | L'hygiène des clusters (le sanitizer) |
| ContainerScannerPort · kubeaudit | kubeaudit | L'audit de config Kubernetes (les permissions) |
| ContainerScannerPort · clair | Clair | Les vulnérabilités des images (le standard Red Hat) |
| ContainerScannerPort · polaris | Polaris (Fairwinds) | La conformité des workloads (le checker) |

### 3.11 📱 Scanners MOBILE
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| MobileScannerPort · mobsf | MobSF | L'analyse statique/dynamique Android+iOS |
| MobileScannerPort · apktool | Apktool | Le déassemblage APK |
| MobileScannerPort · jadx | JADX | Le décompilateur Android |
| MobileScannerPort · frida | Frida | L'instrumentation dynamique (le framework) |
| MobileScannerPort · objection | Objection | L'exploration runtime mobile (Frida) |
| MobileScannerPort · drozer | Drozer | La surface d'attaque Android (les exports) |
| MobileScannerPort · androguard | Androguard | L'analyse statique Android (le SDK) |

### 3.12 🔌 Scanners API
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| ApiScannerPort · 42crunch | 42Crunch | L'audit de sécurité des API |
| ApiScannerPort · apisec | APIsec | Les tests de sécurité API |
| ApiScannerPort · owasp_apisec | OWASP API Security | Le top 10 API |
| ApiScannerPort · schemathesis | Schemathesis | Le fuzzing des API (les contrats OpenAPI) |
| ApiScannerPort · mitmproxy | mitmproxy | L'interception et les tests API (le proxy) |
| ApiScannerPort · akto | Akto | Les tests de sécurité API (l'open source) |

### 3.13 🧠 Sources de CONNAISSANCE (pas des scanners — des bases)
| Port · Adapter | Vendor | Rôle |
|---|---|---|
| KnowledgePort · nvd | NVD / CVE.org | La base des CVE (la référence) |
| KnowledgePort · epss | EPSS (FIRST) | La probabilité d'exploitation |
| KnowledgePort · exploitdb | Exploit-DB | Les exploits PUBLIÉS pour chaque CVE |
| KnowledgePort · searchsploit | SearchSploit | La recherche d'exploits locale |
| KnowledgePort · shodan | Shodan | L'exposition INTERNET des assets |
| KnowledgePort · censys | Censys | L'inventaire internet |
| KnowledgePort · whois_dns | WHOIS/DNS | La surface : domaines, sous-domaines |
| KnowledgePort · metasploit | Metasploit | Le framework d'exploitation (avec mandat !) |
| KnowledgePort · cisa_kev | CISA KEV | Les vulnérabilités EXPLOITÉES dans la nature (le must) |
| KnowledgePort · mitre_attck | MITRE ATT&CK | La cartographie des attaques (les chaînes de corrélation) |
| KnowledgePort · greynoise | GreyNoise | Le bruit Internet (filtrer les fausses alertes) |
| KnowledgePort · virustotal | VirusTotal | La réputation fichiers/IP (multi-antivirus) |
| KnowledgePort · misp | MISP | Le partage de threat intel (la communauté) |

---

## PHASE 4 — MCP server & CLI (🔌 la surface)

> Le pack se branche sur hexagents via le protocole MCP (entrypoint: mcp://).

| Avancement | Ticket · Labels | Rôle |
|---|---|---|
| ⬜ | mcp_server · mcp | Le serveur MCP : scan_asset, correlate, score_report, manage_mandate, generate_report |
| ⬜ | cli · cli | La CLI : hexa-sec check/correlate/report/mandate |
| ⬜ | report_store · backend | La persistance des rapports (SQLite) |

---

## PHASE 5 — Rust (🦀 les hotspots)

> Le pattern pyo3 (comme hexa-health) : le parsing des rapports des scanners
> est CPU-bound — Nessus sort du XML, Burp/Trivy du JSON/SARIF, potentiellement
> des Mo. serde (Rust) parse 10× plus vite que Python.
> **Ordre conseillé** : bootstrap → parsing SARIF/JSON → parsing XML.

| Avancement | Ticket · Labels | Rôle |
|---|---|---|
| ⬜ | rust_bootstrap · rust | Rust: Bootstrap — workspace cargo + pyo3 (la fondation) |
| ⬜ | rust_parse_json · rust | Rust: Parsing JSON/SARIF des scanners (Burp, Trivy, Nuclei — serde 10×) |
| ⬜ | rust_parse_xml · rust | Rust: Parsing XML des scanners (Nessus, OpenVAS, Nmap — serde/xml 10×) |
| ⬜ | rust_parse_goblin · rust | Rust: Parsing des binaires/APK (MobSF, JADX — goblin 10×) |

---

## PHASE 5b — Docker (🐳 l'isolation des scanners)

> **La stratégie Docker (vision dès maintenant, pas de course après)** :
> le pack hexa-sec tourne en DIRECT (pip install, comme les autres packs),
> mais les scanners LOCAUX sont dockerisés à l'échelle — isolation + versions
> figées + sécurité (un scanner compromis ne touche pas l'hôte).
>
> **La règle des 3** :
> 1. Le pack (Python MCP) → **direct** (pip install — jamais de conteneur)
> 2. Les scanners LOCAUX (Nuclei, Nmap, Aircrack, Gitleaks, Trivy...) →
>    **un conteneur CHACUN** quand leur nombre grossit (les conflits de versions)
> 3. Les scanners SaaS (Nessus Pro, Qualys, Shodan, NVD, EPSS...) →
>    **API, jamais de conteneur** (l'adapter appelle leur API)

| Avancement | Ticket · Labels | Rôle |
|---|---|---|
| ⬜ | docker_scanners · infra | Docker: chaque scanner local dans SON conteneur — versions figées + isolation |
| ⬜ | docker_orchestrator · infra | Docker: l'orchestrateur qui lance les conteneurs scanners (le worker cloud HC-20, le même modèle) |
| ⬜ | docker_reproducibility · infra | Docker: la reproductibilité — « ce scan a été fait avec Nuclei 3.2 » (la traçabilité dans l'audit trail) |

> **Pourquoi cette vision dès maintenant** : les scanners bougent vite (les
> templates Nuclei changent chaque jour) — Docker fige les versions et rend
> les résultats REPRODUCTIBLES. C'est la suite logique du worker dockerisé
> (HC-20) déjà posé.

---

## PHASE 6 — Rapport & AI assist (📄 la lecture)

> Le rapport que le CTO comprend — contre les 200 pages de Nessus.
> **Le cœur est déterministe, le SLM ne rédige que la page 1** — un audit
> coûte quelques centimes de SLM local (Qwen-3-8B sur 1080Ti), pas des euros
> de frontier. Le SLM explique, il ne décide jamais.

| Avancement | Ticket · Labels | Rôle |
|---|---|---|
| ⬜ | report_md · backend | Le rapport Markdown : score global + top 5 + par domaine |
| ⬜ | ai_summary · ai | Le résumé LLM en langage clair (« votre SI est à 62/100 ») — SLM local |
| ⬜ | report_html · react | La visualisation web du rapport (le dashboard) |

---

## PHASE 7 — Docs (📄)

| Avancement | Ticket · Labels | Rôle |
|---|---|---|
| ⬜ | docs · docs | README complet + guide + la doc du format de rapport |

---

## Notes

- **hexa-sec est un pack MCP** : il se branche via le protocole (entrypoint: mcp://)
- **Le mandat/consentement est OBLIGATOIRE** (loi Godfrain) — dans le domaine
  dès le bootstrap, AUCUN scan sans mandat. Encore plus vrai pour les outils
  offensifs (Metasploit, Pacu, Wifiphisher, Hydra — avec mandat uniquement)
- **La corrélation est LA valeur** : attack-chain, exposure, noise-reduction,
  temporal, compliance, business-impact — le DDD de la sécurité
- **Rust** : le parsing des rapports des scanners (JSON/SARIF/XML/APK) = le
  même goulot que les manifest dbt → serde 10×
- **SLM** : le cœur (corrélation, scoring, tri) est 100 % déterministe — le
  SLM ne rédige que le rapport. Un audit = quelques centimes.
- **Docker** : la règle des 3 — pack direct, scanners locaux en conteneurs,
  SaaS en API
- **1 label par ticket** (la règle) : bootstrap, domain, backend, scanner,
  mcp, cli, rust, infra, ai, react, docs — un SEUL par ticket
- **12 familles de scanners** : web, réseau, wifi, secrets/code, config,
  email, dns, cloud, ad/identité, containers, mobile, api + les sources de
  connaissance — l'inventaire est EXHAUSTIF, chaque outil se branche comme
  un adapter au fur et à mesure
- **Les specs complètes des tickets vivent dans `tickets/`** (le pattern
  hexagents) : `92-sec-bootstrap.md` (SEC-1) · `93-sec-env.md` (SEC-2) ·
  `96-sec-domain.md` (SEC-3) · `97-sec-scan-status.md` (contexte 5, dans SEC-3) —
  la roadmap ci-dessus EST le pilotage, les fichiers tickets SONT le détail
