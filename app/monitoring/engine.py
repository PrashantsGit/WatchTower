
import hashlib
import json
import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_task import MonitoringTask
from app.monitoring.evaluator import (
    MonitoringRuleEvaluator,
    RuleEvaluationResult,
)
from app.monitoring.extractor import (
    ExtractedData,
    MonitoringExtractor,
)
from app.monitoring.retriever import (
    RetrievedPage,
    WebRetriever,
)
from app.repositories.monitoring_rule_repository import (
    MonitoringRuleRepository,
)
from app.monitoring.trigger import MonitoringTriggerService
from app.services.history_event_service import HistoryEventService
from app.services.monitoring_snapshot_service import (
    MonitoringSnapshotService,
)
from app.services.notification_decision_service import (
    NotificationDecisionService,
)

logger = logging.getLogger(__name__)


@dataclass
class MonitoringExecutionContext:
    task: MonitoringTask
    rules: list[MonitoringRule]
    page: RetrievedPage
    data: ExtractedData
    evaluations: list[RuleEvaluationResult]


class MonitoringEngineService:

    def __init__(
        self,
        db: Session,
        retriever: WebRetriever | None = None,
        extractor: MonitoringExtractor | None = None,
        evaluator: MonitoringRuleEvaluator | None = None,
    ):
        self.db = db
        self.rule_repository = MonitoringRuleRepository(db)
        self.retriever = retriever or WebRetriever()
        self.extractor = extractor or MonitoringExtractor()
        self.evaluator = evaluator or MonitoringRuleEvaluator()
        self.trigger = MonitoringTriggerService()
        self.snapshot_service = MonitoringSnapshotService(db)
        self.history_event_service = HistoryEventService(db)
        self.notification_decision_service = (
            NotificationDecisionService(db)
        )

    def _get_owned_task(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringTask:
        task = self.db.get(MonitoringTask, task_id)

        if task is None or task.user_id != user_id:
            raise ResourceNotFoundError(
                "Monitoring task not found."
            )

        return task

    def get_executable_rules(
        self,
        task_id: int,
        user_id: int,
    ) -> list[MonitoringRule]:
        task = self._get_owned_task(task_id, user_id)

        if not task.is_active:
            return []

        rules = self.rule_repository.list_by_task(task_id)
        return [rule for rule in rules if rule.is_enabled]

    def prepare_execution(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringExecutionContext | None:
        task = self._get_owned_task(task_id, user_id)

        if not task.is_active:
            return None

        rules = self.rule_repository.list_by_task(task_id)
        executable_rules = [
            rule for rule in rules if rule.is_enabled
        ]

        if not executable_rules:
            return None

        page = self.retriever.retrieve(task.target_url)
        data = self.extractor.extract(
            page=page,
            rules=executable_rules,
        )
        evaluations = self.evaluator.evaluate_all(
            rules=executable_rules,
            data=data,
        )

        return MonitoringExecutionContext(
            task=task,
            rules=executable_rules,
            page=page,
            data=data,
            evaluations=evaluations,
        )

    def execute(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringExecutionContext | None:
        try:
            context = self.prepare_execution(
                task_id=task_id,
                user_id=user_id,
            )
        except ResourceNotFoundError:
            raise
        except Exception:
            # Retrieval, extraction, or evaluation failures create
            # a failed snapshot, but never a history event.
            task = self._get_owned_task(task_id, user_id)
            self.snapshot_service.create_snapshot(
                task_id=task.id,
                user_id=user_id,
                snapshot_data={},
                content_hash=self._calculate_content_hash({}),
                execution_status="FAILED",
            )
            logger.exception(
                "Monitoring preparation failed for task %s",
                task_id,
            )
            return None

        if context is None:
            return None

        previous_snapshot = (
            self.snapshot_service.get_latest_successful_snapshot(
                task_id=context.task.id,
                user_id=user_id,
            )
        )

        snapshot_data = {
            "price": context.data.price,
            "availability": context.data.availability,
            "text": context.data.text,
        }

        snapshot = self.snapshot_service.create_snapshot(
            task_id=context.task.id,
            user_id=user_id,
            snapshot_data=snapshot_data,
            content_hash=self._calculate_content_hash(
                snapshot_data
            ),
            execution_status="SUCCESS",
        )

        # The first successful snapshot establishes the baseline.
        # It does not create a history event or notification.
        if previous_snapshot is None:
            return context

        triggered = self.trigger.get_triggered_rules(
            context.evaluations
        )

        for evaluation in triggered:
            previous_value = self._get_previous_value(
                rule=evaluation.rule,
                snapshot_data=previous_snapshot.snapshot_data,
            )
            current_value = self._get_current_value(
                rule=evaluation.rule,
                data=context.data,
            )

            if not self._has_meaningful_change(
                rule=evaluation.rule,
                previous_value=previous_value,
                current_value=current_value,
            ):
                continue

            event = self.history_event_service.create_event(
                task_id=context.task.id,
                rule_id=evaluation.rule.id,
                snapshot_id=snapshot.id,
                event_type=self._get_event_type(
                    rule_type=evaluation.rule.rule_type,
                    previous_value=previous_value,
                    current_value=current_value,
                ),
                previous_value=previous_value,
                current_value=current_value,
                event_message=self._get_event_message(
                    evaluation.rule.rule_type,
                    context.data,
                ),
            )

            # Notification persistence must not invalidate a
            # successfully-created history event.
            try:
                self.notification_decision_service.create_notifications_for_event(
                    event=event,
                    user_id=user_id,
                )
            except Exception:
                logger.exception(
                    "Could not create notifications for history "
                    "event %s (task %s)",
                    event.id,
                    context.task.id,
                )

        return context

    @staticmethod
    def _calculate_content_hash(snapshot_data: dict) -> str:
        serialized = json.dumps(
            snapshot_data,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _get_previous_value(
        rule: MonitoringRule,
        snapshot_data: dict,
    ) -> str | None:
        rule_type = rule.rule_type.upper()

        if rule_type == "PRICE":
            return snapshot_data.get("price")

        if rule_type == "AVAILABILITY":
            value = snapshot_data.get("availability")
            return None if value is None else value.upper()

        if rule_type == "KEYWORD":
            text = snapshot_data.get("text")
            if text is None:
                return None

            keyword_present = (
                rule.target_value.lower() in text.lower()
            )
            return "PRESENT" if keyword_present else "ABSENT"

        return None

    @staticmethod
    def _get_current_value(
        rule: MonitoringRule,
        data: ExtractedData,
    ) -> str | None:
        rule_type = rule.rule_type.upper()

        if rule_type == "PRICE":
            return data.price

        if rule_type == "AVAILABILITY":
            value = data.availability
            return None if value is None else value.upper()

        if rule_type == "KEYWORD":
            if data.text is None:
                return None

            keyword_present = (
                rule.target_value.lower() in data.text.lower()
            )
            return "PRESENT" if keyword_present else "ABSENT"

        return None

    @staticmethod
    def _has_meaningful_change(
        rule: MonitoringRule,
        previous_value: str | None,
        current_value: str | None,
    ) -> bool:
        if previous_value is None or current_value is None:
            return False

        return previous_value != current_value

    @staticmethod
    def _get_event_type(
        rule_type: str,
        previous_value: str | None = None,
        current_value: str | None = None,
    ) -> str:
        rule_type = rule_type.upper()

        if rule_type == "PRICE":
            return "PRICE_DROP"

        if rule_type == "AVAILABILITY":
            if (
                previous_value == "OUT_OF_STOCK"
                and current_value == "IN_STOCK"
            ):
                return "STOCK_AVAILABLE"

            if (
                previous_value == "IN_STOCK"
                and current_value == "OUT_OF_STOCK"
            ):
                return "STOCK_UNAVAILABLE"

            return "AVAILABILITY_CHANGED"

        if rule_type == "KEYWORD":
            return "KEYWORD_DETECTED"

        return "RULE_TRIGGERED"

    @staticmethod
    def _get_event_message(
        rule_type: str,
        data: ExtractedData,
    ) -> str:
        rule_type = rule_type.upper()

        if rule_type == "PRICE":
            return "Price condition triggered."

        if rule_type == "AVAILABILITY":
            return "Availability condition triggered."

        if rule_type == "KEYWORD":
            return "Keyword condition triggered."

        return "Monitoring rule triggered."
