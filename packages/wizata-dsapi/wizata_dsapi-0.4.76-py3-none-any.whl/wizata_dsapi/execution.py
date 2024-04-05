import json
import uuid
from enum import Enum

from .api_dto import ApiDto
from .pipeline import Pipeline
from .experiment import Experiment


class AbortedException(Exception):
    pass


class ExecutionStatus(Enum):
    RECEIVED = "received"
    QUEUED = "queued"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ABORT_REQUESTED = "abortrequested"


class ExecutionStepLog(ApiDto):
    """
    Execution Step Log defining an results and status of pipeline step execution.
    """

    def __init__(self, execution_step_log_id=None, step_id=None, execution_id=None, content=None, status=None):
        if execution_step_log_id is None:
            execution_step_log_id = uuid.uuid4()
        self.execution_step_log_id = execution_step_log_id
        self.execution_id = execution_id
        self.step_id = step_id
        self.content = content
        self.status = status
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        """
        Id of the execution (execution_step_log_id)
        :return: string formatted UUID of the Execution.
        """
        return str(self.execution_step_log_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate execution.
        :return: Endpoint name.
        """
        return "ExecutionStepLogs"

    def to_json(self, target: str = None):
        """
        Convert to a json version of Execution definition.
        By default, use DS API format.
        """
        obj = {
            "id": str(self.execution_step_log_id)
        }
        if self.execution_id is not None:
            obj["executionId"] = str(self.execution_id)
        if self.step_id is not None:
            obj["stepId"] = str(self.step_id)
        if self.content is not None:
            obj["content"] = json.dumps(self.content)
        if self.createdById is not None:
            obj["createdById"] = self.createdById
        if self.createdDate is not None:
            obj["createdDate"] = self.createdDate
        if self.updatedById is not None:
            obj["updatedById"] = self.updatedById
        if self.updatedDate is not None:
            obj["updatedDate"] = self.updatedDate
        if self.status is not None and isinstance(self.status, ExecutionStatus):
            obj["status"] = self.status.value
        return obj

    def from_json(self, obj):
        """
        Load an execution from a stored JSON model.
        :param obj: dictionary representing an execution.
        """
        if "id" in obj.keys():
            self.execution_step_log_id = uuid.UUID(obj["id"])
        if "executionId" in obj.keys() and obj["executionId"] is not None:
            self.execution_id = uuid.UUID(obj["executionId"])
        if "stepId" in obj.keys() and obj["stepId"] is not None:
            self.step_id = uuid.UUID(obj["stepId"])
        if "content" in obj.keys() and obj["content"] is not None:
            if isinstance(obj["content"], str):
                self.content = json.loads(obj["content"])
            else:
                self.content = obj["content"]
        if "status" in obj.keys():
            self.status = ExecutionStatus(str(obj["status"]))
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]


class Execution(ApiDto):
    """

    Execution defines a pipeline execution log done in production or as an experimentation.

    :ivar execution_id: UUID of the Execution (alternatively use 'experiment').

    :ivar warnings: Warning about the Execution.
    :ivar status: ExecutionStatus of the Execution.

    :ivar queued_date: = timestamp on which execution is queued, if none use createdDate
    :ivar started_date: = timestamp on which execution is started.
    :ivar execution_time: = duration of the execution from started.
    :ivar waiting_time: = duration of the waiting time in the queue.

    :ivar pipeline_id: pipeline to execute (alternatively use 'pipeline').
    :ivar properties: configuration, parameters and variables (only accessible from front-end to DS api).

    :ivar experiment_id: UUID of the Experiment of a manual test run.
    :ivar trigger_id: UUID of the Trigger of an automatic run.
    :ivar template_id: UUID of the Template linked to the pipeline used.
    :ivar twin_id: UUID of the Twin linked to the twin used.

    """

    @classmethod
    def route(cls):
        return "execute"

    @classmethod
    def from_dict(cls, data):
        obj = Execution()
        obj.from_json(data)
        return obj

    def __init__(self,
                 execution_id=None,
                 properties: dict = None,
                 pipeline: Pipeline = None,
                 pipeline_id: uuid.UUID = None,
                 experiment: Experiment = None,
                 experiment_id: uuid.UUID = None,
                 twin_id: uuid.UUID = None,
                 template_id: uuid.UUID = None,
                 trigger_id: uuid.UUID = None):

        # Id
        if execution_id is None:
            execution_id = uuid.uuid4()
        self.execution_id = execution_id

        # Experiment
        if experiment is not None:
            self.experiment_id = experiment.experiment_id
        else:
            self.experiment_id = experiment_id

        # Trigger
        self.trigger_id = trigger_id
        self.twin_id = twin_id
        self.template_id = template_id

        # Pipeline
        if pipeline is not None:
            self.pipeline_id = pipeline.pipeline_id
        else:
            self.pipeline_id = pipeline_id

        # Status and info
        self.status = None
        self.queued_date = None
        self.started_date = None
        self.execution_time = None
        self.waiting_time = None
        self.warnings = None

        # Only accessible between Front-End and DS API (not backend)
        if properties is None:
            properties = {}
        self.properties = properties

        # created/updated
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

        # outputs (only accessible within runners)
        self.models = []
        self.plots = []
        self.dataframes = []

    def api_id(self) -> str:
        """
        Id of the execution (execution_id)

        :return: string formatted UUID of the Execution.
        """
        return str(self.execution_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate execution.
        :return: Endpoint name.
        """
        return "Executions"

    def to_json(self, target: str = None):
        """
        get a dict representation of execution.
        """
        obj = {
            "id": str(self.execution_id)
        }

        # Experiment
        if self.experiment_id is not None:
            obj["experimentId"] = str(self.experiment_id)

        # Pipeline
        if self.pipeline_id is not None:
            obj["pipelineId"] = str(self.pipeline_id)

        # Trigger , Twin & Template
        if self.trigger_id is not None:
            obj["executionTriggerId"] = str(self.trigger_id)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)

        # Status and info
        if self.queued_date is not None:
            obj["queuedDate"] = self.queued_date
        if self.started_date is not None:
            obj["startedDate"] = self.started_date
        if self.execution_time is not None:
            obj["executionTime"] = self.execution_time
        if self.waiting_time is not None:
            obj["waitingTime"] = self.waiting_time
        if self.warnings is not None:
            obj["warnings"] = self.warnings
        if self.status is not None and isinstance(self.status, ExecutionStatus):
            obj["status"] = self.status.value

        # Properties (DS API/Front-End only)
        if self.properties is not None and target is None:
            obj["properties"] = json.dumps(self.properties)

        # created/updated
        if self.createdById is not None:
            obj["createdById"] = self.createdById
        if self.createdDate is not None:
            obj["createdDate"] = self.createdDate
        if self.updatedById is not None:
            obj["updatedById"] = self.updatedById
        if self.updatedDate is not None:
            obj["updatedDate"] = self.updatedDate

        return obj

    def from_json(self, obj):
        """
        Load an execution from a stored JSON model.
        :param obj: dictionnary representing an execution.
        """
        if "id" in obj.keys():
            self.execution_id = uuid.UUID(obj["id"])

        # Experiment
        if "experimentId" in obj.keys() and obj["experimentId"] is not None:
            self.experiment_id = uuid.UUID(obj["experimentId"])

        # Pipeline
        if "pipelineId" in obj.keys() and obj["pipelineId"] is not None:
            self.pipeline_id = uuid.UUID(obj["pipelineId"])

        # Trigger , Twin & Template
        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])
        if "executionTriggerId" in obj.keys() and obj["executionTriggerId"] is not None:
            self.trigger_id = uuid.UUID(obj["executionTriggerId"])

        # Status and Info
        if "queuedDate" in obj.keys() and obj["queuedDate"] is not None:
            self.queued_date = int(obj["queuedDate"])
        if "startedDate" in obj.keys() and obj["startedDate"] is not None:
            self.started_date = int(obj["startedDate"])
        if "waitingTime" in obj.keys() and obj["waitingTime"] is not None:
            self.waiting_time = int(obj["waitingTime"])
        if "executionTime" in obj.keys() and obj["executionTime"] is not None:
            self.execution_time = int(obj["executionTime"])
        if "warnings" in obj.keys() and obj["warnings"] is not None:
            self.warnings = obj["warnings"]
        if "status" in obj.keys():
            self.status = ExecutionStatus(str(obj["status"]))

        # Properties
        if "properties" in obj.keys() and obj["properties"] is not None:
            if isinstance(obj["properties"], str):
                if obj["properties"] == '':
                    self.properties = {}
                self.properties = json.loads(obj["properties"])
            else:
                self.properties = obj["properties"]

        # created/updated
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

