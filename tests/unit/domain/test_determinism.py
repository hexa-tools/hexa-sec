"""Edge cases — catégorie « déterminisme / reproductibilité ».

Le domaine est pur et déterministe ; on verrouille pourtant le contrat :
un prédicat appelé deux fois sur les mêmes données produit toujours la même
sortie. Une instabilité ne se voit jamais sur une sortie isolée — seulement en
comparant deux exécutions à entrées identiques.
"""

from __future__ import annotations

from datetime import date

from hexa_sec.domain.api_risk.api_endpoint import ApiEndpoint
from hexa_sec.domain.api_risk.api_finding import ApiFinding
from hexa_sec.domain.api_risk.owasp_category import OwaspApiCategory
from hexa_sec.domain.asset.asset import Asset
from hexa_sec.domain.asset.asset_type import AssetType
from hexa_sec.domain.asset_inventory.inventory import AssetInventory, InventoryEntry
from hexa_sec.domain.asset_inventory.port import Application, Port, Version
from hexa_sec.domain.cloud_risk.cloud_finding import CloudFinding
from hexa_sec.domain.cloud_risk.cloud_provider import CloudProvider
from hexa_sec.domain.cloud_risk.cloud_resource import CloudResource
from hexa_sec.domain.consent.mandate import Mandate, MandateId, MandateLevel
from hexa_sec.domain.container_risk.container_finding import ContainerFinding
from hexa_sec.domain.container_risk.image_ref import ImageRef
from hexa_sec.domain.dns_risk.dns_finding import DnsFinding
from hexa_sec.domain.dns_risk.subdomain import Subdomain
from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus
from hexa_sec.domain.email_risk.email_finding import EmailFinding
from hexa_sec.domain.email_risk.email_record import EmailRecord
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.mobile_risk.mobile_finding import MobileFinding
from hexa_sec.domain.mobile_risk.mobile_platform import MobilePlatform
from hexa_sec.domain.report.priority_action import PriorityAction
from hexa_sec.domain.report.report import Report, ReportId
from hexa_sec.domain.scan.scan import Scan, ScanId
from hexa_sec.domain.scan.scan_depth import ScanDepth
from hexa_sec.domain.scan.scan_parameters import ScanParameters
from hexa_sec.domain.scan.scan_status import ScanStatus
from hexa_sec.domain.scoring.risk_score import RiskScore
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


def _scan() -> Scan:
    mandate = Mandate(
        mandate_id=MandateId("mnd_0001"),
        client="Acme Corp",
        targets=("10.0.0.1",),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        level=MandateLevel.STANDARD,
        signature="REF-2026-0001",
    )
    return Scan.create(
        ScanId("scan_0001"),
        mandate,
        (Asset(name="10.0.0.1", type=AssetType.HOST),),
        ("nessus",),
        ScanParameters(depth=ScanDepth.COMPLETE),
        as_of=date(2026, 6, 1),
    )


def _inventory() -> AssetInventory:
    return AssetInventory(
        host="10.0.0.1",
        entries=(
            InventoryEntry(host="10.0.0.1", port=Port(443), application=Application("https"), version=Version("1.24")),
        ),
    )


def test_asset_inventory_is_deterministic() -> None:
    # catégorie 7 — des données identiques produisent toujours le même inventaire
    assert _inventory() == _inventory()
    assert _inventory().open_ports() == _inventory().open_ports()


def test_asset_inventory_with_entry_is_reproducible() -> None:
    # catégorie 7 — l'ajout (with_entry) est stable et reproductible
    a = _inventory().with_entry(InventoryEntry(host="10.0.0.1", port=Port(22), application=Application("ssh")))
    b = _inventory().with_entry(InventoryEntry(host="10.0.0.1", port=Port(22), application=Application("ssh")))
    assert a == b
    assert a.count() == 2


def _report() -> Report:
    return Report(
        report_id=ReportId("rep_0001"),
        title="Audit report",
        global_score=RiskScore.from_value(62.0),
        top_actions=(_priority_action(),),
    )


def _priority_action() -> PriorityAction:
    return PriorityAction(
        finding_id=FindingId("fnd_0001"),
        issue="Exposed API key",
        why="Account takeover risk",
        fix="Rotate the key",
        effort="5 min",
        risk_score=RiskScore.from_value(95.0),
    )


def test_report_is_deterministic() -> None:
    # catégorie 7 — un rapport identique produit des sections identiques, dans
    # l'ordre, entre deux constructions.
    first = _report()
    second = _report()
    assert first == second
    assert first.sections() == second.sections()
    assert first.top_actions == second.top_actions


def test_priority_action_is_deterministic() -> None:
    # catégorie 7 — la même action produite deux fois est identique et son
    # score de priorité est stable.
    assert _priority_action() == _priority_action()
    assert _priority_action().risk_score.value == 95.0


def test_scan_creation_is_deterministic() -> None:
    # catégorie 7 — des entrées identiques produisent toujours le même scan
    assert _scan() == _scan()


def test_scan_predicate_is_reproducible() -> None:
    # catégorie 7 — la machine à états (with_status) est reproductible
    first = _scan().with_status(ScanStatus.RUNNING)
    second = _scan().with_status(ScanStatus.RUNNING)
    assert first == second
    assert first.status is ScanStatus.RUNNING
    assert first.with_status(ScanStatus.DONE) == second.with_status(ScanStatus.DONE)
