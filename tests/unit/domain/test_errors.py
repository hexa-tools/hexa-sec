"""Edge cases — catégorie « erreur & sa propagation » : la hiérarchie d'erreurs.

Vérifie que chaque sous-classe de HexaSecError :
- est instanciable avec un message + contexte,
- expose `.message` et `.context` (le contrat de la couche),
- reste bien un HexaSecError (substitution de Liskov),
- et que les erreurs de **propagation** (adapter → domaine) ne portent jamais
  une valeur secrète en clair.
"""

from __future__ import annotations

import pytest

from hexa_sec.domain.errors import (
    CorrelationError,
    HexaSecError,
    MandateExpiredError,
    MandateLevelError,
    MandateNotFoundError,
    MandateScopeError,
    ReportStoreError,
    ScannerAuthError,
    ScannerParseError,
    ScannerTimeoutError,
    ScannerUnavailableError,
    TenantIsolationError,
)


def _all_subclasses(cls: type[HexaSecError]) -> list[type[HexaSecError]]:
    result: list[type[HexaSecError]] = []
    for subclass in cls.__subclasses__():
        result.append(subclass)
        result.extend(_all_subclasses(subclass))
    return result


def test_every_error_is_instancable_with_context() -> None:
    for error_type in _all_subclasses(HexaSecError):
        error = error_type("boom", {"tenant": "acme"})
        assert isinstance(error, HexaSecError)
        assert error.message == "boom"
        assert error.context == {"tenant": "acme"}
        assert str(error) == "boom"


def test_every_error_without_context_defaults_to_empty() -> None:
    for error_type in _all_subclasses(HexaSecError):
        error = error_type("boom")
        assert error.context == {}


def test_all_known_errors_are_hexa_sec_errors() -> None:
    known = [
        MandateNotFoundError,
        MandateScopeError,
        MandateExpiredError,
        MandateLevelError,
        ScannerUnavailableError,
        ScannerAuthError,
        ScannerTimeoutError,
        ScannerParseError,
        CorrelationError,
        ReportStoreError,
        TenantIsolationError,
    ]
    for error_type in known:
        assert issubclass(error_type, HexaSecError)


def test_mandate_errors_carry_scope_context() -> None:
    error = MandateScopeError("target out of scope", {"target": "10.0.0.99"})
    assert "target" in error.context
    assert error.context["target"] == "10.0.0.99"


def test_auth_error_never_carries_a_secret() -> None:
    error = ScannerAuthError("missing or invalid key", {"vendor": "nessus"})
    # le message reste générique : il ne révèle jamais la clé elle-même
    assert error.message == "missing or invalid key"
    assert "sk-" not in error.message
    assert "AKIA" not in error.message
    # le contexte porte le vendor, jamais la valeur du secret
    assert error.context == {"vendor": "nessus"}
