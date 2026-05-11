from synthaml import extract_typology, generate_guided_transactions
from synthaml.evaluate import validate_fund_conservation


def test_extract_typology_from_sample_text():
    config = extract_typology(
        "Solar export invoices mention shell companies in Hong Kong and Singapore. "
        "Payments split from $4,000 to $45,000 on Friday afternoons."
    )
    assert "solar" in config.industry
    assert config.amount_max == 45000
    assert "Hong Kong" in config.origin_regions + config.destination_regions


def test_guided_generator_has_required_columns_and_labels():
    config = extract_typology("Online gaming wallet top-ups split and consolidate late-night.")
    frame = generate_guided_transactions(config, n_records=120, seed=3)
    assert len(frame) == 120
    assert {"tx_id", "amount", "label", "risk_signal", "chain_id"}.issubset(frame.columns)
    assert {"legitimate", "suspicious"}.issubset(set(frame["label"]))


def test_suspicious_chains_conserve_funds():
    config = extract_typology("Shell companies split invoice payments between $3,000 and $30,000.")
    frame = generate_guided_transactions(config, n_records=180, seed=4)
    checks = validate_fund_conservation(frame)
    assert not checks.empty
    assert checks["passes"].all()
    assert (frame["amount"] > 0).all()
