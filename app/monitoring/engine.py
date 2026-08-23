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

    def _get_owned_task(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringTask:

        task = self.db.get(
            MonitoringTask,
            task_id,
        )

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

        task = self._get_owned_task(
            task_id=task_id,
            user_id=user_id,
        )

        if not task.is_active:
            return []

        rules = self.rule_repository.list_by_task(
            task_id
        )

        return [
            rule
            for rule in rules
            if rule.is_enabled
        ]

    def prepare_execution(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringExecutionContext | None:

        task = self._get_owned_task(
            task_id=task_id,
            user_id=user_id,
        )

        if not task.is_active:
            return None

        rules = self.rule_repository.list_by_task(
            task_id
        )

        executable_rules = [
            rule
            for rule in rules
            if rule.is_enabled
        ]

        if not executable_rules:
            return None

        page = self.retriever.retrieve(
            task.target_url
        )

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

        context = None

        try:
            context = self.prepare_execution(
                task_id=task_id,
                user_id=user_id,
            )
        except Exception:
            task = self._get_owned_task(
                task_id=task_id,
                user_id=user_id,
            )

            if task is None:
                return None

            self.snapshot_service.create_snapshot(
                task_id=task.id,
                user_id=user_id,
                snapshot_data={},
                content_hash=self._calculate_content_hash({}),
                execution_status="FAILED",
            )

            return None

        if context is None:
            return None

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

        triggered = self.trigger.get_triggered_rules(
            context.evaluations
        )

        for evaluation in triggered:
            self.history_event_service.create_event(
                task_id=context.task.id,
                rule_id=evaluation.rule.id,
                snapshot_id=snapshot.id,
                event_type=self._get_event_type(
                    evaluation.rule.rule_type
                ),
                previous_value=None,
                current_value=self._get_current_value(
                    evaluation.rule.rule_type,
                    context.data,
                ),
                event_message=self._get_event_message(
                    evaluation.rule.rule_type,
                    context.data,
                ),
            )

        return context
    @staticmethod
    def _calculate_content_hash(
        snapshot_data: dict,
    ) -> str:

        import hashlib
        import json

        serialized = json.dumps(
            snapshot_data,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _get_event_type(
        rule_type: str,
    ) -> str:

        event_types = {
            "PRICE": "PRICE_DROP",
            "AVAILABILITY": "STOCK_AVAILABLE",
            "KEYWORD": "KEYWORD_DETECTED",
        }

        return event_types.get(
            rule_type.upper(),
            "RULE_TRIGGERED",
        )

    @staticmethod
    def _get_current_value(
        rule_type: str,
        data: ExtractedData,
    ) -> str | None:

        rule_type = rule_type.upper()

        if rule_type == "PRICE":
            return data.price

        if rule_type == "AVAILABILITY":
            return data.availability

        if rule_type == "KEYWORD":
            return data.text

        return None

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