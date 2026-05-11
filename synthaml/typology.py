"""Typology extraction for SynthAML.

The LLM path turns a plain-language AML warning into a compact scenario
configuration. The heuristic path keeps the demo and evaluation reproducible
when an API key is not available.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
import re
from typing import Any


@dataclass(frozen=True)
class TypologyConfig:
    name: str
    industry: str
    origin_regions: list[str]
    destination_regions: list[str]
    suspicious_methods: list[str]
    narrative_terms: list[str]
    amount_min: float
    amount_max: float
    split_count_min: int
    split_count_max: int
    time_window_hours: int
    risk_summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_CONFIG = TypologyConfig(
    name="Cross-border trade-based laundering",
    industry="import/export services",
    origin_regions=["United States", "United Kingdom"],
    destination_regions=["Hong Kong", "Singapore", "United Arab Emirates"],
    suspicious_methods=[
        "rapid splitting of inbound funds",
        "payments to newly formed counterparties",
        "invoice narratives with repeated generic descriptions",
    ],
    narrative_terms=["consulting invoice", "import services", "equipment deposit"],
    amount_min=2500.0,
    amount_max=48000.0,
    split_count_min=3,
    split_count_max=7,
    time_window_hours=36,
    risk_summary=(
        "Funds arrive in medium-sized deposits, then quickly split across related "
        "cross-border counterparties with vague trade narratives."
    ),
)


REGION_KEYWORDS = {
    "hong kong": "Hong Kong",
    "singapore": "Singapore",
    "united arab emirates": "United Arab Emirates",
    "uae": "United Arab Emirates",
    "china": "China",
    "mexico": "Mexico",
    "panama": "Panama",
    "cyprus": "Cyprus",
    "malta": "Malta",
    "united kingdom": "United Kingdom",
    "uk": "United Kingdom",
    "united states": "United States",
    "us": "United States",
}


INDUSTRY_KEYWORDS = {
    "solar": "solar equipment exports",
    "gaming": "online gaming and virtual assets",
    "crypto": "virtual assets",
    "virtual asset": "virtual assets",
    "invoice": "trade invoicing",
    "import": "import/export services",
    "export": "import/export services",
    "real estate": "real estate services",
}


METHOD_KEYWORDS = {
    "shell": "use of shell-company counterparties",
    "split": "structured splitting of transfers",
    "smurf": "structured splitting of transfers",
    "invoice": "false or vague invoice narratives",
    "round": "round-dollar transaction amounts",
    "friday": "activity clustered near Friday cutoff windows",
    "late-night": "off-hours transaction timing",
    "night": "off-hours transaction timing",
    "gaming": "small top-ups followed by consolidation",
    "crypto": "conversion through virtual-asset channels",
}


def extract_typology(
    text: str,
    use_llm: bool = False,
    model: str = "gpt-4o-mini",
    provider: str = "openai",
    api_key: str | None = None,
) -> TypologyConfig:
    """Extract a structured typology from a warning report.

    Args:
        text: Warning report or case description.
        use_llm: If true and an API key is present, use OpenAI for extraction.
        model: Model name for the selected provider.
        provider: "openai" or "deepseek".
        api_key: Optional runtime key. If omitted, reads provider env var.
    """

    cleaned = _normalize_text(text)
    provider = provider.lower().strip()
    if use_llm and _provider_key(provider, api_key):
        try:
            config = _extract_with_openai_compatible(cleaned, model, provider, api_key)
            return _correct_region_roles(config, cleaned)
        except Exception:
            return _correct_region_roles(_extract_with_heuristics(cleaned), cleaned)
    return _correct_region_roles(_extract_with_heuristics(cleaned), cleaned)


def _normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text[:12000]


def _extract_with_heuristics(text: str) -> TypologyConfig:
    lowered = text.lower()

    industry = next(
        (label for key, label in INDUSTRY_KEYWORDS.items() if key in lowered),
        DEFAULT_CONFIG.industry,
    )

    regions = []
    for key, label in REGION_KEYWORDS.items():
        if re.search(rf"\b{re.escape(key)}\b", lowered) and label not in regions:
            regions.append(label)

    origin_regions = regions[:2] or DEFAULT_CONFIG.origin_regions
    destination_regions = regions[2:5] or DEFAULT_CONFIG.destination_regions

    suspicious_methods = [
        label for key, label in METHOD_KEYWORDS.items() if key in lowered
    ]
    if not suspicious_methods:
        suspicious_methods = DEFAULT_CONFIG.suspicious_methods

    amount_min, amount_max = _extract_amount_range(lowered)
    terms = _extract_narrative_terms(lowered, industry)

    name = _make_name(industry, suspicious_methods)
    summary = (
        f"The warning describes {industry} activity where funds are moved through "
        f"{', '.join(suspicious_methods[:3])}. The generator should create noisy "
        "legitimate traffic plus labeled suspicious chains that preserve timing and "
        "fund-flow consistency."
    )

    return TypologyConfig(
        name=name,
        industry=industry,
        origin_regions=origin_regions,
        destination_regions=destination_regions,
        suspicious_methods=suspicious_methods[:5],
        narrative_terms=terms,
        amount_min=amount_min,
        amount_max=amount_max,
        split_count_min=3,
        split_count_max=7,
        time_window_hours=48 if "friday" in lowered else 36,
        risk_summary=summary,
    )


def _extract_amount_range(text: str) -> tuple[float, float]:
    amounts = []
    for match in re.finditer(r"\$?\s?([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.\d+)?", text):
        value = float(match.group(1).replace(",", ""))
        if value >= 100:
            amounts.append(value)
    if len(amounts) >= 2:
        return max(100.0, min(amounts)), max(amounts)
    if len(amounts) == 1:
        return max(100.0, amounts[0] * 0.4), amounts[0] * 1.4
    return DEFAULT_CONFIG.amount_min, DEFAULT_CONFIG.amount_max


def _extract_narrative_terms(text: str, industry: str) -> list[str]:
    candidates = []
    for phrase in [
        "consulting invoice",
        "equipment deposit",
        "solar panel shipment",
        "gaming credits",
        "wallet top-up",
        "import services",
        "logistics fee",
        "software services",
        "marketing retainer",
    ]:
        if any(token in text for token in phrase.split()):
            candidates.append(phrase)

    if "gaming" in industry:
        candidates.extend(["gaming credits", "wallet top-up", "player settlement"])
    elif "solar" in industry:
        candidates.extend(["solar panel shipment", "equipment deposit", "logistics fee"])
    elif "virtual" in industry:
        candidates.extend(["wallet top-up", "asset conversion", "platform settlement"])
    else:
        candidates.extend(DEFAULT_CONFIG.narrative_terms)

    deduped = []
    for term in candidates:
        if term not in deduped:
            deduped.append(term)
    return deduped[:5]


def _make_name(industry: str, methods: list[str]) -> str:
    method = methods[0].split(" of ")[-1] if methods else "rapid fund movement"
    return f"{industry.title()} Typology: {method.title()}"


def _correct_region_roles(config: TypologyConfig, text: str) -> TypologyConfig:
    lowered = text.lower()
    origin_regions = _regions_in_role_span(
        lowered,
        [
            r"originate(?:s|d)? in (?P<span>[^.]+?)(?:,?\s+then|\.)",
            r"originat(?:e|es|ed) from (?P<span>[^.]+?)(?:,?\s+then|\.)",
            r"payments? from (?P<span>[^.]+?)(?:,?\s+then|\.)",
        ],
    )
    destination_regions = _regions_in_role_span(
        lowered,
        [
            r"to counterparties in (?P<span>[^.]+)(?:\.)",
            r"split (?:quickly )?to (?P<span>[^.]+)(?:\.)",
            r"sent (?:quickly )?to (?P<span>[^.]+)(?:\.)",
            r"moved (?:quickly )?to (?P<span>[^.]+)(?:\.)",
        ],
    )
    if not origin_regions and not destination_regions:
        return config

    return TypologyConfig(
        name=config.name,
        industry=config.industry,
        origin_regions=origin_regions or config.origin_regions,
        destination_regions=destination_regions or config.destination_regions,
        suspicious_methods=config.suspicious_methods,
        narrative_terms=config.narrative_terms,
        amount_min=config.amount_min,
        amount_max=config.amount_max,
        split_count_min=config.split_count_min,
        split_count_max=config.split_count_max,
        time_window_hours=config.time_window_hours,
        risk_summary=config.risk_summary,
    )


def _regions_in_role_span(text: str, patterns: list[str]) -> list[str]:
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        span = match.group("span")
        hits = []
        for key, label in REGION_KEYWORDS.items():
            match_for_region = re.search(rf"\b{re.escape(key)}\b", span)
            if match_for_region:
                hits.append((match_for_region.start(), label))
        regions = []
        for _position, label in sorted(hits, key=lambda item: item[0]):
            if label not in regions:
                regions.append(label)
        if regions:
            return regions
    return []


def _provider_key(provider: str, api_key: str | None = None) -> str | None:
    if api_key:
        return api_key
    if provider == "deepseek":
        return os.getenv("DEEPSEEK_API_KEY")
    return os.getenv("OPENAI_API_KEY")


def _provider_base_url(provider: str) -> str | None:
    if provider == "deepseek":
        return "https://api.deepseek.com"
    return None


def _extract_with_openai_compatible(
    text: str,
    model: str,
    provider: str,
    api_key: str | None = None,
) -> TypologyConfig:
    from openai import OpenAI

    client = OpenAI(api_key=_provider_key(provider, api_key), base_url=_provider_base_url(provider))
    schema = {
        "name": "string",
        "industry": "string",
        "origin_regions": ["string"],
        "destination_regions": ["string"],
        "suspicious_methods": ["string"],
        "narrative_terms": ["string"],
        "amount_min": 1000.0,
        "amount_max": 50000.0,
        "split_count_min": 3,
        "split_count_max": 7,
        "time_window_hours": 36,
        "risk_summary": "string",
    }

    prompt = (
        "Extract only defensive AML synthetic-data generation constraints from this "
        "warning. Avoid tactical evasion advice. Return strict JSON matching this "
        f"shape: {json.dumps(schema)}\n\n"
        "Important role rules: origin_regions are where payments or funds originate. "
        "destination_regions are where funds are sent, split, consolidated, or moved to. "
        "For example, if text says payments originate in A and split to B, A belongs "
        "in origin_regions and B belongs in destination_regions.\n\n"
        f"Warning:\n{text}"
    )
    request = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You help compliance teams convert AML warnings into safe, "
                    "high-level synthetic test-data constraints."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    if provider == "deepseek":
        request["extra_body"] = {"thinking": {"type": "disabled"}}
    response = client.chat.completions.create(**request)
    payload = json.loads(response.choices[0].message.content or "{}")
    merged = DEFAULT_CONFIG.to_dict() | payload
    return TypologyConfig(
        name=str(merged["name"]),
        industry=str(merged["industry"]),
        origin_regions=list(merged["origin_regions"])[:5],
        destination_regions=list(merged["destination_regions"])[:5],
        suspicious_methods=list(merged["suspicious_methods"])[:6],
        narrative_terms=list(merged["narrative_terms"])[:6],
        amount_min=float(merged["amount_min"]),
        amount_max=float(merged["amount_max"]),
        split_count_min=int(merged["split_count_min"]),
        split_count_max=int(merged["split_count_max"]),
        time_window_hours=int(merged["time_window_hours"]),
        risk_summary=str(merged["risk_summary"]),
    )
