import pytest

from app.core.exceptions import ResourceNotFoundError
from app.database.session import SessionLocal
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_task import MonitoringTask
from app.monitoring.engine import MonitoringEngineService
from unittest.mock import Mock
from app.monitoring.extractor import ExtractedData
from app.monitoring.retriever import RetrievedPage

from app.monitoring.evaluator import (
    RuleEvaluationResult,
)

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
        name="Engine Test Task",
        description="Testing monitoring engine",
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


def test_get_executable_rules_returns_enabled_rules(db, task):
    service = MonitoringEngineService(db)

    enabled_rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=True,
    )

    db.add(enabled_rule)
    db.commit()
    db.refresh(enabled_rule)

    rules = service.get_executable_rules(
        task_id=task.id,
        user_id=41,
    )

    assert len(rules) == 1
    assert rules[0].id == enabled_rule.id


def test_get_executable_rules_ignores_disabled_rules(db, task):
    service = MonitoringEngineService(db)

    enabled_rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=True,
    )

    disabled_rule = MonitoringRule(
        task_id=task.id,
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="sale",
        is_enabled=False,
    )

    db.add_all([
        enabled_rule,
        disabled_rule,
    ])
    db.commit()

    rules = service.get_executable_rules(
        task_id=task.id,
        user_id=41,
    )

    rule_ids = {rule.id for rule in rules}

    assert enabled_rule.id in rule_ids
    assert disabled_rule.id not in rule_ids


def test_get_executable_rules_returns_empty_for_paused_task(db, task):
    service = MonitoringEngineService(db)

    task.is_active = False
    db.commit()

    rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=True,
    )

    db.add(rule)
    db.commit()

    rules = service.get_executable_rules(
        task_id=task.id,
        user_id=41,
    )

    assert rules == []


def test_get_executable_rules_returns_empty_when_no_rules_exist(db, task):
    service = MonitoringEngineService(db)

    rules = service.get_executable_rules(
        task_id=task.id,
        user_id=41,
    )

    assert rules == []


def test_get_executable_rules_rejects_nonexistent_task(db):
    service = MonitoringEngineService(db)

    with pytest.raises(
        ResourceNotFoundError,
        match="Monitoring task not found",
    ):
        service.get_executable_rules(
            task_id=999999,
            user_id=41,
        )


def test_get_executable_rules_rejects_other_user(db, task):
    service = MonitoringEngineService(db)

    with pytest.raises(
        ResourceNotFoundError,
        match="Monitoring task not found",
    ):
        service.get_executable_rules(
            task_id=task.id,
            user_id=999999,
        )

def test_prepare_execution_returns_context(db, task):
    retriever = Mock()
    extractor = Mock()
    evaluator = Mock()

    retriever.retrieve.return_value = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="<html>Example</html>",
    )

    extracted_data = ExtractedData(
        text="Example",
    )

    extractor.extract.return_value = extracted_data

    rule = MonitoringRule(
        task_id=task.id,
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Example",
        is_enabled=True,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    evaluation = RuleEvaluationResult(
        rule=rule,
        matched=True,
    )

    evaluator.evaluate_all.return_value = [
        evaluation
    ]

    service = MonitoringEngineService(
        db,
        retriever=retriever,
        extractor=extractor,
        evaluator=evaluator,
    )

    context = service.prepare_execution(
        task_id=task.id,
        user_id=41,
    )

    assert context is not None

    assert context.task.id == task.id

    assert len(context.rules) == 1
    assert context.rules[0].id == rule.id

    assert context.page.status_code == 200
    assert context.page.html == "<html>Example</html>"

    assert context.data is extracted_data

    assert len(context.evaluations) == 1
    assert context.evaluations[0] is evaluation
    assert context.evaluations[0].matched is True

    retriever.retrieve.assert_called_once_with(
        task.target_url
    )

    extractor.extract.assert_called_once_with(
        page=retriever.retrieve.return_value,
        rules=[rule],
    )

    evaluator.evaluate_all.assert_called_once_with(
        rules=[rule],
        data=extracted_data,
    )


def test_prepare_execution_returns_none_for_paused_task(
    db,
    task,
):
    retriever = Mock()

    task.is_active = False
    db.commit()

    service = MonitoringEngineService(
        db,
        retriever=retriever,
    )

    context = service.prepare_execution(
        task_id=task.id,
        user_id=41,
    )

    assert context is None
    retriever.retrieve.assert_not_called()


def test_prepare_execution_returns_none_without_enabled_rules(
    db,
    task,
):
    retriever = Mock()

    disabled_rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=False,
    )

    db.add(disabled_rule)
    db.commit()

    service = MonitoringEngineService(
        db,
        retriever=retriever,
    )

    context = service.prepare_execution(
        task_id=task.id,
        user_id=41,
    )

    assert context is None
    retriever.retrieve.assert_not_called()

def test_execute_creates_snapshot_for_successful_execution(
    db,
    task,
):
    retriever = Mock()
    extractor = Mock()
    evaluator = Mock()

    retriever.retrieve.return_value = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="<html>Example</html>",
    )

    extracted_data = ExtractedData(
        price="45000",
        availability="IN_STOCK",
        text="Example product",
    )

    extractor.extract.return_value = extracted_data

    rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=True,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    evaluator.evaluate_all.return_value = [
        RuleEvaluationResult(
            rule=rule,
            matched=True,
        )
    ]

    service = MonitoringEngineService(
        db,
        retriever=retriever,
        extractor=extractor,
        evaluator=evaluator,
    )

    context = service.execute(
        task_id=task.id,
        user_id=41,
    )

    assert context is not None

    snapshot = service.snapshot_service.repository.find_by_id(
        1
    )

    snapshots = service.snapshot_service.list_snapshots(
        task_id=task.id,
        user_id=41,
    )

    assert len(snapshots) == 1

    snapshot = snapshots[0]

    assert snapshot.task_id == task.id
    assert snapshot.snapshot_data == {
        "price": "45000",
        "availability": "IN_STOCK",
        "text": "Example product",
    }
    assert snapshot.execution_status == "SUCCESS"
    assert snapshot.content_hash is not None
    assert len(snapshot.content_hash) == 64

def test_execute_does_not_create_history_event_when_rule_does_not_match(
    db,
    task,
):
    retriever = Mock()
    extractor = Mock()
    evaluator = Mock()

    retriever.retrieve.return_value = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="<html>Example</html>",
    )

    extracted_data = ExtractedData(
        price="60000",
    )

    extractor.extract.return_value = extracted_data

    rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=True,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    evaluator.evaluate_all.return_value = [
        RuleEvaluationResult(
            rule=rule,
            matched=False,
        )
    ]

    service = MonitoringEngineService(
        db,
        retriever=retriever,
        extractor=extractor,
        evaluator=evaluator,
    )

    service.execute(
        task_id=task.id,
        user_id=41,
    )

    snapshots = service.snapshot_service.list_snapshots(
        task_id=task.id,
        user_id=41,
    )

    assert len(snapshots) == 1

    events = service.history_event_service.list_events(
        task.id
    )

    assert events == []

def test_execute_creates_history_event_when_rule_matches(
    db,
    task,
):
    retriever = Mock()
    extractor = Mock()
    evaluator = Mock()

    retriever.retrieve.return_value = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="<html>Example</html>",
    )

    extracted_data = ExtractedData(
        price="45000",
    )

    extractor.extract.return_value = extracted_data

    rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=True,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    evaluator.evaluate_all.return_value = [
        RuleEvaluationResult(
            rule=rule,
            matched=True,
        )
    ]

    service = MonitoringEngineService(
        db,
        retriever=retriever,
        extractor=extractor,
        evaluator=evaluator,
    )

    service.execute(
        task_id=task.id,
        user_id=41,
    )

    snapshots = service.snapshot_service.list_snapshots(
        task_id=task.id,
        user_id=41,
    )

    assert len(snapshots) == 1

    events = service.history_event_service.list_events(
        task.id
    )

    assert len(events) == 1

    event = events[0]

    assert event.task_id == task.id
    assert event.rule_id == rule.id
    assert event.snapshot_id == snapshots[0].id
    assert event.event_type == "PRICE_DROP"
    assert event.previous_value is None
    assert event.current_value == "45000"
    assert event.event_message == "Price condition triggered."