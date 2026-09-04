# ═══════════════════════════════════════════════════════════
#  hexa-sec — Makefile
#  Orchestrate the security pack + the guards.
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────
#  Variables
# ─────────────────────────────────────

POETRY  := poetry
PYTHON  := $(POETRY) run python
PYTEST  := $(POETRY) run pytest
RUFF    := $(POETRY) run ruff
MYPY    := $(POETRY) run mypy
HEXAGUARD := hexa_guard.py

CARGO := cargo
RUST_DIR := rust

# ─────────────────────────────────────
#  Dev setup
# ─────────────────────────────────────

.PHONY: install deps-export

install:
	@echo "📦 Installing all dependencies (venv in-project)..."
	$(POETRY) install --with dev
	@echo "✅ Dependencies installed"

deps-export:
	@echo "📋 Exporting requirements.txt from Poetry..."
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes --without dev
	@echo "✅ requirements.txt updated — commit this file"

# ─────────────────────────────────────
#  Code quality
# ─────────────────────────────────────

.PHONY: lint format format-check type-check check env-validate

lint:
	@echo "🔍 Linting Python with ruff..."
	$(RUFF) check src/ hexa_guard.py
	@echo "✅ Lint passed"

format:
	@echo "🎨 Formatting Python with ruff..."
	$(RUFF) format src/ hexa_guard.py
	@echo "✅ Formatting done"

format-check:
	@echo "📐 Checking Python formatting with ruff..."
	$(RUFF) format --check src/ hexa_guard.py
	@echo "✅ Format check passed"

type-check:
	@echo "🔎 Running mypy strict type check..."
	$(MYPY) src/
	@echo "✅ Type check passed"

check:
	@echo "🔍 Running all quality checks..."
	@echo ""
	@$(MAKE) lint
	@$(MAKE) format-check
	@$(MAKE) type-check
	@$(MAKE) env-validate
	@echo ""
	@echo "✅ All checks passed"

# ─────────────────────────────────────
#  Tests (Python)
# ─────────────────────────────────────

.PHONY: test test-integration test-e2e test-e2e-ci test-all coverage update-badge \
	docker-check test-docker

test:
	@echo "🧪 Running Python unit tests..."
	$(PYTEST) tests/unit/ -m "not integration and not e2e" --tb=short -q
	@echo "✅ Unit tests passed"

test-integration:
	@echo "🔬 Running Python integration tests (real SQLite, real Docker)..."
	$(PYTEST) tests/integration/ -v -m integration --strict-markers --tb=short
	@echo "✅ Integration tests passed"

docker-check:
	@echo "🐳 Checking Docker availability..."
	@docker version --format '{{.Server.Version}}' >/dev/null 2>&1 || ( \
		echo "❌ Docker daemon not available — install Docker or start it."; \
		exit 1)
	@echo "✅ Docker available"

test-docker:
	@echo "🐳 Running the Docker runtime integration test..."
	$(MAKE) docker-check
	$(PYTEST) tests/integration/test_docker_runtime.py -v -m integration --strict-markers --tb=short
	@echo "✅ Docker runtime test passed"

test-e2e:
	@echo "🧪 Running Python E2E tests (mocked, no real target)..."
	$(PYTEST) tests/e2e/ -v -m e2e --strict-markers --tb=short
	@echo "✅ E2E tests passed"

test-e2e-ci:
	@echo "🧪 Running E2E tests (release CI)..."
	$(PYTEST) tests/e2e/ -v -m e2e --strict-markers --tb=short
	@echo "✅ E2E tests passed"

test-all:
	@echo "🧪 Running all Python tests (unit + integration)..."
	$(PYTEST) tests/unit/ tests/integration/ -v
	@echo "✅ All tests passed"

coverage:
	@echo "📊 Running Python tests with coverage (>=95%, unit only — no Docker)..."
	$(PYTEST) tests/ -m "not e2e and not integration" --cov=hexa_sec --cov-report=term-missing --cov-fail-under=95
	@echo "✅ Coverage threshold met"

update-badge:
	@echo "🏷️  Updating test count badge in README.md..."
	$(PYTHON) scripts/update_test_badge.py 2>/dev/null || echo "⚠️  No badge script yet"
	@echo "✅ Badge updated"

env-validate:
	@echo "🔑 Validating .env contract (required keys + unknown rejection)..."
	$(PYTHON) -m hexa_sec.infrastructure.config.env_contract
	@echo "✅ .env contract valid"

# ─────────────────────────────────────
#  Guard
# ─────────────────────────────────────

.PHONY: guard

guard:
	@echo "🛡️  Running hexa_guard (architecture + security purity)..."
	$(PYTHON) $(HEXAGUARD) --check
	@echo "✅ Guard rules validated"

# ─────────────────────────────────────
#  Rust (parsing hotspots behind driven ports)
# ─────────────────────────────────────

.PHONY: rust-build rust-check rust-test

rust-build:
	@echo "🦀 Building Rust (maturin develop --release)..."
	cd $(RUST_DIR) && $(POETRY) run maturin develop --release
	@echo "✅ Rust built"

rust-check:
	@echo "🦀 Checking Rust (fmt --check + clippy -D warnings)..."
	cd $(RUST_DIR) && $(CARGO) fmt --check
	cd $(RUST_DIR) && $(CARGO) clippy --workspace --all-targets -- -D warnings
	@echo "✅ Rust check passed"

rust-test:
	@echo "🦀 Running Rust tests (cargo test --workspace)..."
	cd $(RUST_DIR) && $(CARGO) test --workspace
	@echo "✅ Rust tests passed"

# ─────────────────────────────────────
#  Mutation testing (Python mutmut + Rust cargo-mutants)
# ─────────────────────────────────────

# mutation-python : run COMPLET frais (sandbox purgé) — chiffres officiels.
# mutation-python-module : run ciblé par module/glob, sans purge (itération).
#   Ex : make mutation-python-module MODULE="hexa_sec.domain.correlation*"
# mutation-results / mutation-show : inspecter le dernier run.
#   Ex : make mutation-show ID=hexa_sec.domain.X.y__mutmut_42
# mutation-rust : cargo-mutants frais (outputs purgés, legacy .old supprimé).

.PHONY: mutation mutation-python mutation-python-module mutation-results mutation-show \
	mutation-rust mutation-report mutation-badge mutation-clean

mutation-python:
	@echo "🧬 Running Python mutation testing (fresh full run, mutmut)..."
	rm -rf mutants
	$(POETRY) run mutmut run --max-children 8
	@echo "🧬 Python mutation done — see mutants/mutmut-cicd-stats.json"
	$(POETRY) run mutmut export-cicd-stats
	@echo "✅ Python mutation stats exported"

mutation-python-module:
	@echo "🧬 Running Python mutation on module: $(MODULE)..."
	$(POETRY) run mutmut run "$(MODULE)" --max-children 8
	@echo "✅ Module mutation done"

mutation-results:
	@echo "🧬 Surviving mutants of the last run:"
	$(POETRY) run mutmut results

mutation-show:
	@echo "🧬 Showing mutant $(ID):"
	$(POETRY) run mutmut show "$(ID)"

mutation-rust:
	@echo "🧬 Running Rust mutation testing (cargo-mutants, fresh)..."
	rm -rf $(RUST_DIR)/mutants.out $(RUST_DIR)/mutants.out.old
	cd $(RUST_DIR) && cargo mutants --no-times
	@echo "✅ Rust mutation done — see rust/mutants.out/outcomes.json"

mutation-report:
	@echo "📊 Aggregating mutation results (Python + Rust)..."
	$(PYTHON) scripts/mutation_report.py
	@echo "✅ Mutation report written"

mutation-badge:
	@echo "🏷️  Updating mutation badge in README.md..."
	$(PYTHON) scripts/mutation_report.py --badge
	@echo "✅ Mutation badge updated"

mutation: mutation-python mutation-rust mutation-report
	@echo "✅ Mutation testing complete"

mutation-clean:
	@echo "🧹 Cleaning mutation sandbox and reports..."
	rm -rf mutants rust/mutants.out rust/mutants.out.old
	@echo "✅ Mutation artifacts cleaned"

# ─────────────────────────────────────
#  All gates
# ─────────────────────────────────────

.PHONY: all clean

all:
	@echo "🔨 Running all green gates..."
	@echo ""
	@$(MAKE) check
	@$(MAKE) guard
	@$(MAKE) test
	@$(MAKE) coverage
	@$(MAKE) rust-check
	@$(MAKE) rust-test
	@echo ""
	@echo "✅ All gates green"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/ .coverage coverage.xml htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	@echo "✅ Clean complete"

# ─────────────────────────────────────
#  Help
# ─────────────────────────────────────

.PHONY: help

help:
	@echo ""
	@echo "══════════════════════════════════════════"
	@echo "     🛡️  hexa-sec — Security Audit Pack"
	@echo "══════════════════════════════════════════"
	@echo ""
	@echo "📦 DEV SETUP"
	@echo "  make install               → Install Poetry dependencies (venv in-project)"
	@echo ""
	@echo "🧪 CODE QUALITY"
	@echo "  make lint                  → Lint Python with ruff"
	@echo "  make format                → Auto-format Python with ruff"
	@echo "  make format-check          → Check formatting with ruff"
	@echo "  make type-check            → Strict mypy type check"
	@echo "  make check                 → Run lint + format-check + type-check"
	@echo "  make guard                 → Run hexa_guard.py rules (purity + security)"
	@echo ""
	@echo "🧪 TESTS (PYTHON)"
	@echo "  make test                  → Run unit tests (mocks only)"
	@echo "  make test-integration      → Run integration tests (real SQLite, no network)"
	@echo "  make test-e2e              → Run E2E tests (mocked)"
	@echo "  make test-e2e-ci           → Run E2E tests (release CI)"
	@echo ""
	@echo "🐳 DOCKER RUNTIME"
	@echo "  make docker-check          → Verify Docker daemon is available"
	@echo "  make test-docker           → Run the Docker runtime integration test"
	@echo "  make test-integration      → Run integration tests (SQLite + Docker)"
	@echo "  make test-all              → Run unit + integration tests"
	@echo "  make coverage              → Run tests with coverage (≥95%)"
	@echo "  make update-badge          → Update test count badge in README.md"
	@echo ""
	@echo "🦀 RUST (parsing hotspots behind driven ports)"
	@echo "  make rust-build            → maturin develop --release"
	@echo "  make rust-check            → cargo fmt --check + cargo clippy -D warnings"
	@echo "  make rust-test             → cargo test --workspace"
	@echo ""
	@echo "🧬 MUTATION TESTING (quality — slow, run before merge)"
	@echo "  make mutation-python       → fresh full mutmut run + stats (official numbers)"
	@echo "  make mutation-python-module MODULE=... → mutmut scoped to a module glob"
	@echo "  make mutation-results      → list surviving mutants of the last run"
	@echo "  make mutation-show ID=...  → show the diff of one mutant"
	@echo "  make mutation-rust         → fresh cargo-mutants on the parse crate"
	@echo "  make mutation-report       → aggregate Python + Rust into report.json"
	@echo "  make mutation-badge        → update the README mutation badge"
	@echo "  make mutation-clean        → purge sandbox (mutants/ + rust/mutants.out*)"
	@echo "  make mutation              → python + rust + report"
	@echo ""
	@echo "🔨 ALL"
	@echo "  make all                   → check + guard + test + coverage + rust-check + rust-test"
	@echo "  make clean                 → remove build artifacts"
	@echo ""
