from app.database.session import SessionLocal
from app.models.monitoring_rule import MonitoringRule
from app.repositories.monitoring_rule_repository import MonitoringRuleRepository


def test_monitoring_rule_repository():
    db = SessionLocal()

    rule = None

    try:
        repository = MonitoringRuleRepository(db)

        rule = MonitoringRule(
            task_id=7,
            rule_type="PRICE",
            operator="<",
            target_value="50000",
            is_enabled=True,
        )

        created_rule = repository.create(rule)

        assert created_rule.id is not None
        assert created_rule.task_id == 7
        assert created_rule.rule_type == "PRICE"
        assert created_rule.operator == "<"
        assert created_rule.target_value == "50000"
        assert created_rule.is_enabled is True

        found_rule = repository.find_by_id(created_rule.id)

        assert found_rule is not None
        assert found_rule.id == created_rule.id

        rules = repository.list_by_task(7)

        rule_ids = {item.id for item in rules}

        assert created_rule.id in rule_ids

    finally:
        if rule is not None:
            db.delete(rule)
            db.commit()

        db.close()

def test_monitoring_rule_repository_updates_rule():
    db = SessionLocal()

    rule = None

    try:
        repository = MonitoringRuleRepository(db)

        rule = MonitoringRule(
            task_id=7,
            rule_type="PRICE",
            operator="<",
            target_value="50000",
            is_enabled=True,
        )

        rule = repository.create(rule)

        rule.operator = "<="
        rule.target_value = "45000"

        updated_rule = repository.update(rule)

        assert updated_rule.id == rule.id
        assert updated_rule.operator == "<="
        assert updated_rule.target_value == "45000"

    finally:
        if rule is not None:
            db.delete(rule)
            db.commit()

        db.close()


def test_monitoring_rule_repository_deletes_rule():
    db = SessionLocal()

    rule = None

    try:
        repository = MonitoringRuleRepository(db)

        rule = MonitoringRule(
            task_id=7,
            rule_type="KEYWORD",
            operator="CONTAINS",
            target_value="Admissions Open",
            is_enabled=True,
        )

        rule = repository.create(rule)
        rule_id = rule.id

        repository.delete(rule)
        db.commit()

        found_rule = repository.find_by_id(rule_id)

        assert found_rule is None

        rule = None

    finally:
        if rule is not None:
            db.delete(rule)
            db.commit()

        db.close()