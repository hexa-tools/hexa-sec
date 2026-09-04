# hexa-sec

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-1092_passed-brightgreen.svg)]()
[![codecov](https://codecov.io/gh/hexa-tools/hexa-sec/branch/main/graph/badge.svg)](https://codecov.io/gh/hexa-tools/hexa-sec)
[![Mutation](https://img.shields.io/badge/mutation-96.6%25-brightgreen.svg)](docs/mutation/PROGRESS.md)
[![Mutation Python](https://img.shields.io/badge/mutation--python-96.6%25-brightgreen.svg)](docs/mutation/PROGRESS.md)
[![Mutation Rust](https://img.shields.io/badge/mutation--rust-100.0%25-brightgreen.svg)](docs/mutation/PROGRESS.md)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

<p>
  <img
    src="assets/hexa-sec.svg"
    alt="Hexa-sec"
    width="800"
  />
</p>

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

## 🧬 Mutation testing

Le coverage mesure ce que les tests *exécutent* ; la mutation testing mesure ce
que les tests *prouvent*. On mute le code (inverse une condition, change un
`+` en `-`, vide un champ…) : un mutant qui survit = un test qui ne détecterait
pas une vraie régression.

Deux outils, un rapport agrégé :

| Langage | Outil | Périmètre | Rapport brut |
|---|---|---|---|
| Python | `mutmut` | le cœur déterministe (`domain/` + `application/service/`) | `mutants/mutmut-cicd-stats.json` |
| Rust | `cargo-mutants` | le crate `hexa-sec-parse` | `rust/mutants.out/outcomes.json` |

```bash
make mutation-python    # mutmut sur le cœur déterministe (lent ~10 min)
make mutation-rust      # cargo-mutants sur le crate de parsing (rapide)
make mutation-report    # agrège les deux → docs/mutation/report.json
make mutation-badge     # met à jour le badge README
make mutation           # tout enchaîner
```

> Le périmètre Python est volontairement le **cœur déterministe** : les adapters
> primaires (MCP/CLI) tirent le SDK `mcp` dont la couche `cryptography` n'est pas
> sûre vis-à-vis du sandbox `fork` de mutmut, et les adapters secondaires sont de
> fines traductions déjà couvertes à ~100 % en branches.

Le suivi module-par-module et l'analyse des mutants survivants (équivalents
structurels vs vrais manques) vivent dans
[`docs/mutation/PROGRESS.md`](docs/mutation/PROGRESS.md). Un workflow CI dédié
(`.github/workflows/mutation.yml`) rejoue le tout sur `main` chaque nuit et
public les rapports en artifacts.
