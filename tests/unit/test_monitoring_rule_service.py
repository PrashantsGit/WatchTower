import pytest

from app.core.exceptions import ResourceNotFoundError
from app.database.session import SessionLocal
from app.models.monitoring_rule import MonitoringRule
from app.services.monitoring_rule_service import MonitoringRuleService



def test_create_rule():
    db = SessionLocal()

    rule = None

    try:
        service = MonitoringRuleService(db)

        rule = service.create_rule(
            task_id=7,
            user_id=41,
            rule_type="PRICE",
            operator="<",
            target_value="50000",
        )

        assert rule.id is not None
        assert rule.task_id == 7
        assert rule.rule_type == "PRICE"
        assert rule.operator == "<"
        assert rule.target_value == "50000"
        assert rule.is_enabled is True

    finally:
        if rule is not None:
            db.delete(rule)
            db.commit()

        db.close()


def test_list_rules():
    db = SessionLocal()

    rule_1 = None
    rule_2 = None

    try:
        service = MonitoringRuleService(db)

        rule_1 = service.create_rule(
            task_id=7,
            user_id=41,
            rule_type="PRICE",
            operator="<",
            target_value="50000",
        )

        rule_2 = service.create_rule(
            task_id=7,
            user_id=41,
            rule_type="KEYWORD",
            operator="CONTAINS",
            target_value="Admissions Open",
        )

        rules = service.list_rules(
            task_id=7,
            user_id=41,
        )

        rule_ids = {rule.id for rule in rules}

        assert rule_1.id in rule_ids
        assert rule_2.id in rule_ids

    finally:
        if rule_1 is not None:
            db.delete(rule_1)

        if rule_2 is not None:
            db.delete(rule_2)

        db.commit()
        db.close()


def test_get_rule_returns_owned_rule():
    db = SessionLocal()

    rule = None

    try:
        service = MonitoringRuleService(db)

        rule = service.create_rule(
            task_id=7,
            user_id=41,
            rule_type="AVAILABILITY",
            operator="==",
            target_value="IN_STOCK",
        )

        found_rule = service.get_rule(
            rule_id=rule.id,
            task_id=7,
            user_id=41,
        )

        assert found_rule.id == rule.id
        assert found_rule.task_id == 7

    finally:
        if rule is not None:
            db.delete(rule)
            db.commit()

        db.close()


def test_get_rule_rejects_other_user():
    db = SessionLocal()

    rule = None

    try:
        service = MonitoringRuleService(db)

        rule = service.create_rule(
            task_id=7,
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
                task_id=7,
                user_id=999999,
            )

    finally:
        if rule is not None:
            db.delete(rule)
            db.commit()

        db.close()

def test_update_rule():
    db = SessionLocal()

    rule = None

    try:
        service = MonitoringRuleService(db)

        rule = service.create_rule(
            task_id=7,
            user_id=41,
            rule_type="PRICE",
            operator="<",
            target_value="50000",
        )

        updated_rule = service.update_rule(
            rule_id=rule.id,
            task_id=7,
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

    finally:
        if rule is not None:
            db.delete(rule)
            db.commit()

        db.close()


def test_delete_rule():
    db = SessionLocal()

    rule = None

    try:
        service = MonitoringRuleService(db)

        rule = service.create_rule(
            task_id=7,
            user_id=41,
            rule_type="KEYWORD",
            operator="CONTAINS",
            target_value="Admissions Open",
        )

        rule_id = rule.id

        service.delete_rule(
            rule_id=rule_id,
            task_id=7,
            user_id=41,
        )

        rule = None

        found_rule = db.get(MonitoringRule, rule_id)

        assert found_rule is None

    finally:
        if rule is not None:
            db.delete(rule)
            db.commit()

        db.close()

def test_create_price_rule_rejects_invalid_operator():
    db = SessionLocal()

    try:
        service = MonitoringRuleService(db)

        with pytest.raises(
            ValueError,
            match="Invalid operator for PRICE rule",
        ):
            service.create_rule(
                task_id=7,
                user_id=41,
                rule_type="PRICE",
                operator="CONTAINS",
                target_value="50000",
            )

    finally:
        db.close()


def test_create_price_rule_rejects_invalid_target():
    db = SessionLocal()

    try:
        service = MonitoringRuleService(db)

        with pytest.raises(
            ValueError,
            match="Price target must be a positive integer",
        ):
            service.create_rule(
                task_id=7,
                user_id=41,
                rule_type="PRICE",
                operator="<",
                target_value="0",
            )

    finally:
        db.close()


def test_create_availability_rule_rejects_invalid_target():
    db = SessionLocal()

    try:
        service = MonitoringRuleService(db)

        with pytest.raises(
            ValueError,
            match="Invalid availability target",
        ):
            service.create_rule(
                task_id=7,
                user_id=41,
                rule_type="AVAILABILITY",
                operator="==",
                target_value="AVAILABLE",
            )

    finally:
        db.close()


def test_create_keyword_rule_rejects_empty_target():
    db = SessionLocal()

    try:
        service = MonitoringRuleService(db)

        with pytest.raises(
            ValueError,
            match="Keyword target cannot be empty",
        ):
            service.create_rule(
                task_id=7,
                user_id=41,
                rule_type="KEYWORD",
                operator="CONTAINS",
                target_value="   ",
            )

    finally:
        db.close()

def test_create_rule_rejects_invalid_rule_type():
    db = SessionLocal()

    try:
        service = MonitoringRuleService(db)

        with pytest.raises(
            ValueError,
            match="Invalid rule type",
        ):
            service.create_rule(
                task_id=7,
                user_id=41,
                rule_type="UNKNOWN",
                operator="==",
                target_value="test",
            )

    finally:
        db.close()


def test_create_availability_rule_rejects_invalid_operator():
    db = SessionLocal()

    try:
        service = MonitoringRuleService(db)

        with pytest.raises(
            ValueError,
            match="Invalid operator for AVAILABILITY rule",
        ):
            service.create_rule(
                task_id=7,
                user_id=41,
                rule_type="AVAILABILITY",
                operator="<",
                target_value="IN_STOCK",
            )

    finally:
        db.close()


def test_create_keyword_rule_rejects_invalid_operator():
    db = SessionLocal()

    try:
        service = MonitoringRuleService(db)

        with pytest.raises(
            ValueError,
            match="Invalid operator for KEYWORD rule",
        ):
            service.create_rule(
                task_id=7,
                user_id=41,
                rule_type="KEYWORD",
                operator="==",
                target_value="Admissions Open",
            )

    finally:
        db.close()