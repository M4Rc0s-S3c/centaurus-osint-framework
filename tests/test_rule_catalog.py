from centaurus.rules.catalog import DEFAULT_RULES


def test_default_rule_catalog_contains_all_productive_rules_once():
    ids = [rule.id for rule in DEFAULT_RULES]

    assert ids == [
        "RL-001",
        "RL-002",
        "RL-003",
        "RL-004",
        "RL-005",
        "RL-006",
        "RL-007",
        "RL-008",
        "RL-009",
        "RL-010",
        "RL-014",
    ]
    assert len(ids) == len(set(ids)) == 11
