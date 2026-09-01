"""Edge cases — catégorie « déterminisme / reproductibilité ».

Le domaine est pur et déterministe ; on verrouille pourtant le contrat :
un prédicat appelé deux fois sur les mêmes données produit toujours la même
sortie. Une instabilité ne se voit jamais sur une sortie isolée — seulement en
comparant deux exécutions à entrées identiques.
"""

from __future__ import annotations

from hexa_sec.domain.api_risk.api_endpoint import ApiEndpoint
from hexa_sec.domain.api_risk.api_finding import ApiFinding
from hexa_sec.domain.api_risk.owasp_category import OwaspApiCategory
from hexa_sec.domain.cloud_risk.cloud_finding import CloudFinding
from hexa_sec.domain.cloud_risk.cloud_provider import CloudProvider
from hexa_sec.domain.cloud_risk.cloud_resource import CloudResource
from hexa_sec.domain.container_risk.container_finding import ContainerFinding
from hexa_sec.domain.container_risk.image_ref import ImageRef
from hexa_sec.domain.dns_risk.dns_finding import DnsFinding
from hexa_sec.domain.dns_risk.subdomain import Subdomain
from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus
from hexa_sec.domain.email_risk.email_finding import EmailFinding
from hexa_sec.domain.email_risk.email_record import EmailRecord
from hexa_sec.domain.mobile_risk.mobile_finding import MobileFinding
from hexa_sec.domain.mobile_risk.mobile_platform import MobilePlatform
from hexa_sec.domain.secret_risk.secret_type import SecretType
from hexa_sec.domain.wifi_risk.ssid import Ssid
from hexa_sec.domain.wifi_risk.wifi_finding import WifiFinding
from hexa_sec.domain.wifi_risk.wifi_security import WifiSecurity


def test_wifi_predicate_is_deterministic() -> None:
    finding = WifiFinding(ssid=Ssid("Office"), security=WifiSecurity.WEP, clients=3)
    assert finding.weak is True
    assert finding.weak is True


def test_email_predicate_is_deterministic() -> None:
    finding = EmailFinding(record=EmailRecord(domain="acme.example"), dmarc=DmarcStatus.MISSING)
    assert finding.spoofable() is True
    assert finding.spoofable() is True


def test_dns_predicate_is_deterministic() -> None:
    finding = DnsFinding(
        domain="acme.example", subdomains=(Subdomain(name="admin", resolved=True),)
    )
    assert finding.exposed() is True
    assert finding.exposed() is True
    assert finding.has_zone_transfer() is False


def test_cloud_predicate_is_deterministic() -> None:
    resource = CloudResource(provider=CloudProvider.AWS, resource_id="x", resource_type="y", public=True)
    finding = CloudFinding(resource=resource, issue="public bucket")
    assert finding.exposed() is True
    assert finding.exposed() is True


def test_container_predicate_is_deterministic() -> None:
    finding = ContainerFinding(image=ImageRef("acme/payment", "1.0"), cve="CVE-2024-1")
    assert finding.severe() is False
    assert finding.severe() is False


def test_mobile_predicate_is_deterministic() -> None:
    finding = MobileFinding(
        package="com.acme.app", platform=MobilePlatform.ANDROID, issue="secret", secret_type=SecretType.API_KEY
    )
    assert finding.embeds_secret() is True
    assert finding.embeds_secret() is True


def test_api_predicate_is_deterministic() -> None:
    endpoint = ApiEndpoint(method="get", path="/v1/payments", auth_required=True)
    finding = ApiFinding(
        endpoint=endpoint, category=OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION
    )
    assert finding.endpoint.requires_auth() is True
    assert finding.endpoint.requires_auth() is True
