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

.PHONY: test test-integration test-e2e test-e2e-ci test-all coverage update-badge

test:
	@echo "🧪 Running Python unit tests..."
	$(PYTEST) tests/unit/ -m "not integration and not e2e" --tb=short -q
	@echo "✅ Unit tests passed"

test-integration:
	@echo "🔬 Running Python integration tests (real SQLite, no network)..."
	$(PYTEST) tests/integration/ -v -m integration --strict-markers --tb=short
	@echo "✅ Integration tests passed"

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
	@echo "📊 Running Python tests with coverage (>=95%)..."
	$(PYTEST) tests/ -m "not e2e" --cov=hexa_sec --cov-report=term-missing --cov-fail-under=95
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
	@echo "  make test-all              → Run unit + integration tests"
	@echo "  make coverage              → Run tests with coverage (≥95%)"
	@echo "  make update-badge          → Update test count badge in README.md"
	@echo ""
	@echo "🦀 RUST (parsing hotspots behind driven ports)"
	@echo "  make rust-build            → maturin develop --release"
	@echo "  make rust-check            → cargo fmt --check + cargo clippy -D warnings"
	@echo "  make rust-test             → cargo test --workspace"
	@echo ""
	@echo "🔨 ALL"
	@echo "  make all                   → check + guard + test + coverage + rust-check + rust-test"
	@echo "  make clean                 → remove build artifacts"
	@echo ""
