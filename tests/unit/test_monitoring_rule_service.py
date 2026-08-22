import pytest

from app.core.exceptions import (
    ResourceNotFoundError,
    RuleLimitExceededError,
)
from app.database.session import SessionLocal
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_task import MonitoringTask
from app.services.monitoring_rule_service import MonitoringRuleService


@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def task(db):
    monitoring_task = MonitoringTask(
        user_id=41,
        name="Test Monitoring Task",
        description="Test monitoring task",
        target_url="https://example.com",
        check_interval=60,
        is_active=True,
    )

    db.add(monitoring_task)
    db.commit()
    db.refresh(monitoring_task)

    try:
        yield monitoring_task

    finally:
        db.query(MonitoringRule).filter(
            MonitoringRule.task_id == monitoring_task.id
        ).delete(synchronize_session=False)

        db.delete(monitoring_task)
        db.commit()


def test_create_rule(db, task):
    service = MonitoringRuleService(db)

    rule = service.create_rule(
        task_id=task.id,
        user_id=41,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    assert rule.id is not None
    assert rule.task_id == task.id
    assert rule.rule_type == "PRICE"
    assert rule.operator == "<"
    assert rule.target_value == "50000"
    assert rule.is_enabled is True


def test_list_rules(db, task):
    service = MonitoringRuleService(db)

    rule_1 = service.create_rule(
        task_id=task.id,
        user_id=41,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    rule_2 = service.create_rule(
        task_id=task.id,
        user_id=41,
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions Open",
    )

    rules = service.list_rules(
        task_id=task.id,
        user_id=41,
    )

    rule_ids = {rule.id for rule in rules}

    assert rule_1.id in rule_ids
    assert rule_2.id in rule_ids


def test_get_rule_returns_owned_rule(db, task):
    service = MonitoringRuleService(db)

    rule = service.create_rule(
        task_id=task.id,
        user_id=41,
        rule_type="AVAILABILITY",
        operator="==",
        target_value="IN_STOCK",
    )

    found_rule = service.get_rule(
        rule_id=rule.id,
        task_id=task.id,
        user_id=41,
    )

    assert found_rule.id == rule.id
    assert found_rule.task_id == task.id


def test_get_rule_rejects_other_user(db, task):
    service = MonitoringRuleService(db)

    rule = service.create_rule(
        task_id=task.id,
        user_id=41,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Monitoring task not found",
    ):
        service.get_rule(
            rule_id=rule.id,
            task_id=task.id,
            user_id=999999,
        )


def test_update_rule(db, task):
    service = MonitoringRuleService(db)

    rule = service.create_rule(
        task_id=task.id,
        user_id=41,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    updated_rule = service.update_rule(
        rule_id=rule.id,
        task_id=task.id,
        user_id=41,
        rule_type="PRICE",
        operator="<=",
        target_value="45000",
        is_enabled=False,
    )

    assert updated_rule.id == rule.id
    assert updated_rule.rule_type == "PRICE"
    assert updated_rule.operator == "<="
    assert updated_rule.target_value == "45000"
    assert updated_rule.is_enabled is False


def test_delete_rule(db, task):
    service = MonitoringRuleService(db)

    rule = service.create_rule(
        task_id=task.id,
        user_id=41,
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions Open",
    )

    rule_id = rule.id

    service.delete_rule(
        rule_id=rule_id,
        task_id=task.id,
        user_id=41,
    )

    found_rule = db.get(MonitoringRule, rule_id)

    assert found_rule is None


def test_create_price_rule_rejects_invalid_operator(db, task):
    service = MonitoringRuleService(db)

    with pytest.raises(
        ValueError,
        match="Invalid operator for PRICE rule",
    ):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="PRICE",
            operator="CONTAINS",
            target_value="50000",
        )


def test_create_price_rule_rejects_invalid_target(db, task):
    service = MonitoringRuleService(db)

    with pytest.raises(
        ValueError,
        match="Price target must be a positive integer",
    ):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="PRICE",
            operator="<",
            target_value="0",
        )


def test_create_availability_rule_rejects_invalid_target(db, task):
    service = MonitoringRuleService(db)

    with pytest.raises(
        ValueError,
        match="Invalid availability target",
    ):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="AVAILABILITY",
            operator="==",
            target_value="AVAILABLE",
        )


def test_create_keyword_rule_rejects_empty_target(db, task):
    service = MonitoringRuleService(db)

    with pytest.raises(
        ValueError,
        match="Keyword target cannot be empty",
    ):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="KEYWORD",
            operator="CONTAINS",
            target_value=" ",
        )


def test_create_rule_rejects_invalid_rule_type(db, task):
    service = MonitoringRuleService(db)

    with pytest.raises(
        ValueError,
        match="Invalid rule type",
    ):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="UNKNOWN",
            operator="==",
            target_value="test",
        )


def test_create_availability_rule_rejects_invalid_operator(db, task):
    service = MonitoringRuleService(db)

    with pytest.raises(
        ValueError,
        match="Invalid operator for AVAILABILITY rule",
    ):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="AVAILABILITY",
            operator="<",
            target_value="IN_STOCK",
        )


def test_create_keyword_rule_rejects_invalid_operator(db, task):
    service = MonitoringRuleService(db)

    with pytest.raises(
        ValueError,
        match="Invalid operator for KEYWORD rule",
    ):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="KEYWORD",
            operator="==",
            target_value="Admissions Open",
        )


def test_create_rule_rejects_fourth_rule(db, task):
    service = MonitoringRuleService(db)

    for _ in range(3):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="KEYWORD",
            operator="CONTAINS",
            target_value="sale",
        )

    with pytest.raises(
        RuleLimitExceededError,
        match="maximum of 3 rules",
    ):
        service.create_rule(
            task_id=task.id,
            user_id=41,
            rule_type="KEYWORD",
            operator="CONTAINS",
            target_value="offer",
        )