# Mutation Testing — hexa-sec

> Suivi du mutation testing sur hexa-sec : **mutmut** (Python, cœur
> déterministe) + **cargo-mutants** (Rust, `hexa-sec-parse`).
> Mis à jour au fil des sessions — le coverage dit ce que les tests *exécutent*,
> la mutation dit ce qu'ils *prouvent*.

## Configuration

`pyproject.toml` → `[tool.mutmut]` :

```toml
[tool.mutmut]
source_paths = ["src/hexa_sec"]
also_copy = ["scripts", "datasets", "packs", "hexa_guard.py"]
only_mutate = [
    "src/hexa_sec/domain/*",
    "src/hexa_sec/application/service/*",
]
do_not_mutate = ["src/hexa_sec/domain/*/__init__.py", "src/hexa_sec/application/service/__init__.py"]
pytest_add_cli_args_test_selection = [
    "tests/unit/domain",
    "tests/unit/application",
    "-m",
    "not integration and not e2e",
]
mutate_only_covered_lines = true
```

> **Pourquoi ce périmètre** : les adapters primaires (MCP/CLI) tirent le SDK
> `mcp`, dont la couche `cryptography` n'est pas sûre vis-à-vis du sandbox
> `fork` de mutmut (crash `HKDF`/`os.urandom` au fork). Les adapters secondaires
> sont de fines traductions déjà ~100 % couvertes en branches. Le **cœur
> déterministe** (`domain/` + `application/service/`) est là où un mutant
> survivant a du sens métier.

## Commandes utiles

```bash
make mutation-python            # mutmut run + export-cicd-stats
make mutation-rust              # cargo mutants (dans rust/)
make mutation-report            # scripts/mutation_report.py → docs/mutation/report.json
make mutation-badge             # + mise à jour du badge README

# par module (mutmut prend un glob de nom de mutant)
poetry run mutmut run "hexa_sec.domain.scoring*"
poetry run mutmut results
poetry run mutmut show "hexa_sec.domain.X.y_z__mutmut_42"

# purge sandbox après un changement de config / d'import
rm -rf mutants rust/mutants.out
```

## Résultats

### Python — mutmut (cœur déterministe)

| Passe | Date | Killed | Survived | Total | Score |
|---|---|---|---|---|---|
| Baseline | 2026-09-04 | 1086 | 236 | 1322 | 82.1 % |
| Renforcement services + scoring | 2026-09-04 | 1144 | 178 | 1322 | **86.5 %** |
| **Passe 3 — domaine (run ciblé `hexa_sec.domain.*`)** | 2026-09-04 | 655 | 37 | 692 | **94.7 %** |
| **Passe 3 — services (run ciblé `hexa_sec.application.service*`)** | 2026-09-04 | 506 | 4 | 510 | 99.2 % |
| **Passe 3 — global (run complet `domain/*` + `service/*`)** | 2026-09-04 | **1161** | **41** | **1202** | **96.6 %** |
| **Passe 4 — infra (config + container + SQLite store)** | 2026-09-04 | 245 | 9 | 254 | **96.5 %** |
| **Passe 4 — global étendu (domain + service + infra)** | 2026-09-04 | **1406** | **50** | **1456** | **96.6 %** |

> Le total global a baissé de 1322 → 1202 (passe 3) puis remonté à **1456** à la
> passe 4 : le scope mutmut a été étendu à `infrastructure/config/*`,
> `infrastructure/bootstrap/*` et
> `infrastructure/adapters/secondary/report_store/*` (après le déplacement de
> `adapters/` sous `infrastructure/`). Les totaux des lignes « ciblées » sont sur
> le sous-ensemble du scope ; seule la ligne **global** est comparable d'une
> passe à l'autre.

### Rust — cargo-mutants (`hexa-sec-parse`)

| Passe | Date | Caught | Missed | Timeout | Total | Score |
|---|---|---|---|---|---|---|
| Baseline (1 test) | 2026-09-04 | 25 | 10 | 2 | 37 | 67.6 % |
| Renforcement (12 tests) | 2026-09-04 | 32 | 0 | 5 | 37 | **86.5 %** |
| **Refactor itératif de `json_keys`** | 2026-09-04 | 14 | 0 | 0 | 14 | **100 %** |

> Refactor du scanner naïf en style itératif (paires de guillemets, plus aucune
> arithmétique de curseur `index`/`cursor`) : les mutants `+=` → `*=` qui
> bouclaient à l'infini ont **disparu** (les sites n'existent plus). Résultat :
> **14/14 caught, 0 TIMEOUT, 0 MISSED** — comportement inchangé (12 tests),
> `cargo fmt` + `clippy -D warnings` propres.

## Passe 3 — ce qui a été tué

Run complet **domain + services** sur l'arbre de travail actuel. Cible : les
**vrais manques**, équivalents documentés ensuite.

### Domain — `correlation` (28 survivants → 4 équivalents)

Les tests ne vérifiaient que le **type** de corrélation (`_types`), jamais les
champs. Tests ajoutés/renforcés dans `test_correlation_checker.py` :

1. `.assets == (AssetId(...),)` épinglé sur les 5 familles → tue les 10 mutants
   `assets` → `None` / `AssetId(None)`.
2. `impact` et `reason` **exacts** (`ERP` + `CRITICAL` → `ImpactScore(1.0)`,
   reason littérale) → tue les mutants de formule `/5.0`→`/6.0`, `/4.0`→`/5.0`.
3. Tri par `correlation_id` : 2 corrélations sur le même asset → l'ordre
   `(COMPLIANCE, EXPOSURE)` ≠ ordre d'insertion → tue les 3 mutants de clé de
   `sorted` (sans clé, `Correlation` n'a pas d'ordre → `TypeError`).
4. `correlation_id.value` **exact** avec des `FindingId` explicites
   (`cor:attack-chain:host1:fnd_a,fnd_b,fnd_c`) → tue les mutants `_id`
   (`None`/séparateur).
5. `noise_reduction` : 10 × `LOGIN`/LOW non-NOISE → détecté (tue `or`→`and`) ;
   10 × `LOGIN`/MEDIUM non faibles → rien (tue `severity not in _LOW`).
6. Temporal à **2 kinds nouveaux** → reason exacte → tue le mutant de séparateur.
7. Borne business-impact : `ERP` + `INFO` → score exactement 0.5 → émis (tue
   `<` → `<=`).

### Domain — normalize & value objects (20 tués)

| Module | Kill |
|---|---|
| `web owasp_category` | messages `invalid`/`unknown` distingués + bornes (`a1`, `a99`, `a0x`) |
| `api owasp_category` | bornes (`api11`) + message stable |
| `dmarc_status` | enregistrement sans espace `v=DMARC1;p=quarantine` + message stable |
| `alert_type` | séparateurs répétés → compact (`NEW  SECRET`, `fix--resolved`) |
| `protocol_strength` | version avec tiret `TLS-1.2` |
| `email_risk` | ordre-indépendance worst DMARC (MISSING/NONE, NONE/QUARANTINE, QUARANTINE/REJECT) |
| `compliance` | dedup garde l'impact max dans les **deux** ordres (HIGH puis LOW) |
| `threat_intel` | ordre total du lien canonique (assets puis findings) à sévérité égale |

### Services (20 survivants → 4 équivalents)

`scan_asset_service` :
- les scanners reçoivent bien l'asset (`test_scan_passes_asset_to_every_wired_scanner`),
- `duration_ms` **exact** via `monkeypatch` de `time.perf_counter` (1500 ms),
- `digest == ""` et `recorded_at` finit par `+00:00` (UTC) épinglés,
- messages ancrés `^...$` (le sous-match `in` ne tuait pas le mutant `XX...XX`).

`score_report_service` : label **exact** du score (`100`/`critical`).
`generate_report_service` : preuve corrélation à 2 findings **exacte**
(`(findings : fnd_1, fnd_2)`).
`manage_mandate_service` : `recorded_at` UTC épinglé.

### Infra (passe 4 — après déplacement `adapters/` → `infrastructure/adapters/`)

Au passage, le refactor humain a été **finalisé** (tests déplacés dans
`tests/unit/infrastructure/adapters/`, imports `src.hexa_sec.…` fautifs corrigés,
`SQL_DIR` du store recalé, entrée CLI + scope mutmut mis à jour).

- **`SqliteReportStore`** : round-trip **exact de tous les champs** de l'audit
  (le test vérifiait 3 champs sur 10 → 34 survivants), mapping NULL→`""`/`0`,
  erreur `ReportStoreError` épinglée **message + context structuré**
  (`{"tenant_id": ...}`) → l'isolation tenant et la traduction d'erreur sont
  prouvées.
- **`env_contract`** : sortie `main` épinglée via `capsys`, sections par défaut
  (`ROOT` avant tout header), secret documenté rejeté, violations épinglées par
  message, commentaire `.env` coupé au premier `#`, `argv` sans dossier.
- **`container`** : les 5 use cases sont des instances du bon type **avec un
  service injecté** (`_service is not None`).

## Analyse des mutants survivants (Passe 4 — 50 restants)

Tous les survivants restants sont des **équivalents structurels purs** (aucune
entrée ne peut les distinguer du code original) — vérifiés un à un sur le run
complet. Aux 41 équivalents des passes 3 (domaine + services) s'ajoutent **9
équivalents infra** :

| Catégorie | Exemple | Modules |
|---|---|---|
| **Encodage `read_text`** | `encoding="utf-8"` → `None`/`"UTF-8"` (décodage identique) | env `_load`, store `_load_sql` |
| **Commentaire `#` non-matching** | `startswith("XX#XX")` : aucune ligne ne commence par un `#` ET matche `_KEY_RE` | env `parse_env` |
| **`split("#")` premier élément** | `maxsplit` 1/2/par-défaut → même 1er segment | env `parse_env` |
| **Message succès = sous-chaîne** | `main` succès `XX…XX` : le `capsys` vérifie une sous-chaîne | env `main` |
| **`or`/`and` sur ligne vide** | ligne vide + commentaire mutuellement exclusifs | env `parse_env` |

> Règle : on documente, on ne chasse pas un équivalent à l'infini. Un mutant
> classé équivalent n'est re-testé qu'après un changement du code qui rendrait
> son chemin atteignable.

| Catégorie | Exemple | Modules |
|---|---|---|
| **Comparateur `>`→`>=` sous garde `!=`** | `if a.rank != b.rank: return a.rank > b.rank` | code/config/iaac/identity/exploit risk `_prefer` |
| **`>=` / `<=` sur clé de tri en cas d'égalité totale** | duplicates identiques → même sortie | cloud, dns, wifi, notification, threat `_prefer`, business/compliance dedup, email `_prefer` |
| **Champ injecté jamais lu** | `_secret_store` du `ScanAssetService` | scan_asset `__init__` |
| **Valeur VO inobservable dans le flux** | `AssetType.HOST` : les scanners reçoivent la `str`, pas l'`Asset` | scan `scan` |
| **Fallback défensif inatteignable** | `compute_score(...) or RiskScore.from_value(0.0)` (severity toujours requise) | score_report `_score_item` |
| **`default=` de `max` jamais atteint** | un asset a toujours ≥ 1 signal | correlation `_business_impact` |
| **Normalisation redondante** | `.lstrip("0")` avant `int(code)` ; `.replace(" ","_")` sur enum mono-mot ; compact lookup = lookup exact | api owasp, dmarc, alert_type |
| **`strict=` de `zip` (parts ≡ weights)** | `strict=None`/omis ≡ `False` ; `True` inatteignable (longueurs toujours égales) | scoring_engine |
| **Séparateur d'id mono-élément** | un seul asset par corrélation → join inchangé | correlation `_id` |

> Règle : on documente, on ne chasse pas un équivalent à l'infini. Un mutant
> classé équivalent n'est re-testé qu'après un changement du code qui rendrait
> son chemin atteignable.

## Règles / pièges

1. **Asserts exacts > asserts relatifs** : `== "…exact…"` tue, `in`/`> 0` ne tue pas.
2. **Épingler TOUS les champs** d'un record tracé : un champ jamais lu = mutant
   survivant garanti (`digest`, `recorded_at` UTC…).
3. **Les `match=` de `pytest.raises` doivent être ancrés** `^…$` : un `match` non
   ancré survit au mutant `"XX…XX"` (le sous-texte reste présent).
4. **Un champ/une valeur qu'on n'observe pas** (`AssetType.HOST`, `_secret_store`)
   = mutant survivant : soit on l'épinglé, soit on le documente équivalent.
5. **`mutmut run <glob>`** prend un **nom de module** (`hexa_sec.domain.scoring*`),
   pas un chemin `src/...`.
6. **Purge `mutants/`** après un changement de `source_paths`/`also_copy` :
   mutmut déduplique par hash git et peut ignorer les nouveaux fichiers.
7. **`also_copy` doit couvrir tout ce que les tests importent** : ici
   `scripts/`, `datasets/`, `packs/`, `hexa_guard.py`.
8. **Never `git stash`/commit** : l'humain commit ; on ne manipule pas l'historique.
9. **Rust** : `cargo mutants --no-times` ; résultats dans
   `rust/mutants.out/outcomes.json` + `caught.txt`/`missed.txt`.

## Prochaines passes

Aucun vrai manque restant sur `domain/*`, `application/service/*` ni sur
l'infrastructure scrutée (config + container + SQLite store) — les **50
survivants** sont des équivalents documentés. Prochaines cibles possibles :

- **Re-cibler après évolution du code** : toute PR qui touche un équivalent
  (ex : `_secret_store` branché, `Asset` passé aux scanners, fallback de score
  atteint, encodage de `read_text`, message succès de `main`) doit re-tuer ces
  mutants.
- **Scanners secondaires sous `infrastructure/adapters/secondary/scanners/`** :
  toujours exclus (fines traductions) — sauf `report_store` qui est scruté car
  c'est de la vraie logique d'accès aux données (SQL + isolation tenant).
- **Rust** `hexa-sec-parse` : **14/14 caught (100 %)**, 0 timeout, 0 missed —
  le refactor itératif a supprimé les 5 TIMEOUT anti-hang. À ré-analyser quand la
  Phase 5 remplacera le scanner naïf par les vrais parseurs serde.
- Sortir `mutants.out.old/` de la racine rust/ (reliquat de session, non commité).

## Fichiers

- `scripts/mutation_report.py` — agrégation Python + Rust → JSON + badge
- `.github/workflows/mutation.yml` — gate nocturne sur `main`
- `docs/mutation/report.json` — dernier rapport agrégé (généré, non commité)
