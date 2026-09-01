# hexa-sec

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-744_passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

> **Nessus trouve des failles. Burp trouve des failles. hexa-sec trouve la
> faille qui compte.**

`hexa-sec` est le pack cybersécurité d'HexAgents. Il **orchestre les scanners
du marché** (Nessus, Burp, Nuclei, Nmap, Trivy, Prowler...) et **corrèle leurs
findings** pour révéler la chaîne d'attaque, l'exposition réelle et la
criticité métier qu'aucun outil seul ne montre.

**On n'écrit pas de scanner.** Chaque outil devient un *adapter* qui traduit
son format en `Asset`/`Finding`. Le code à écrire = la **corrélation** + le
**scoring** + le **rapport** — le cerveau, pas les muscles.

## Architecture

- **Ports & adapters** (Alistair Cockburn) — le domaine est **pur**, il ne
  connaît aucun scanner.
- **DDD** (Vaughn Vernon) — 30 contextes bornés sous `src/hexa_sec/domain/`,
  avec value objects + agrégats + tests (coverage ≥ 95 %).
- **Cœur 100 % déterministe** — corrélation, scoring et tri sont du code pur.
  Le SLM local ne rédige que le résumé du rapport (page 1).

```
src/hexa_sec/
  domain/            # LE CŒUR PUR (zéro import externe)
  application/       # ports (driving/driven) + use cases + services
  adapters/          # primary (MCP, CLI) + secondary (scanners, knowledge)
  infrastructure/    # SQLite, config, logging, composition root
rust/                # hotspots de parsing (serde, derrière les ports)
tests/               # unit, integration, e2e (mocks only)
datasets/            # fixtures : Nessus XML, Burp JSON, Nuclei JSON...
```

## 🔴 Le légal — loi Godfrain

**Aucun scan sans mandat valide.** `scan_asset` refuse tout lancement si le
mandat n'existe pas, ne couvre pas la cible exacte, est expiré, ou de niveau
insuffisant. Les outils offensifs exigent un mandat `offensive` explicite.
Le consentement est un objet du domaine (`domain/consent/`), pas une
vérification optionnelle.

## Développement

```bash
make install   # poetry install (venv in-project)
make guard     # hexa_guard.py (architecture + security purity)
make check     # ruff + mypy strict
make test      # pytest (unit, mocks only)
make coverage  # pytest + coverage >= 95 %
```
