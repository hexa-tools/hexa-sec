"""SecretType — the kinds of committed secrets (context: secret_risk, SEC-12).

Classification of a leaked credential. Normalization never invents a type: an
unknown or malformed label is rejected at parse time, never guessed — this is
what lets the checker demand an exact type instead of assuming.
"""

from __future__ import annotations

from enum import Enum


class SecretType(Enum):
    """The family a committed secret belongs to."""

    APIKEY = "api_key"
    PRIVATEKEY = "private_key"
    PASSWORD = "password"
    TOKEN = "token"
    AWSKEY = "aws_key"
    CIPHERTEXT = "ciphertext"

    @classmethod
    def normalize(cls, raw: str) -> SecretType:
        """Map a raw label to a ``SecretType``; unknown values are rejected.

        Accepts case/space/hyphen variations of the canonical values and raises
        ``ValueError`` for anything else — the checker never guesses a type.
        """
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown secret type: {raw}") from error
