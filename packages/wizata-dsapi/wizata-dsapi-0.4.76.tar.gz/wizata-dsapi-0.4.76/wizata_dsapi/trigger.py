import uuid
import json
from .api_dto import ApiDto


class Trigger(ApiDto):
    """
    Trigger defines how pipelines are automatically executed.
    """

    @classmethod
    def route(cls):
        return "triggers"

    @classmethod
    def from_dict(cls, data):
        obj = Trigger()
        obj.from_json(data)
        return obj

    def __init__(self,
                 trigger_id: uuid.UUID = None,
                 interval: int = None,
                 delay: int = None,
                 pipeline_id: uuid.UUID = None,
                 template_id: uuid.UUID = None,
                 properties: dict = None,
                 twin_ids: list = None):
        """
        create an instance of trigger class. use api() to create/update/delete
        :param trigger_id: existing uuid or forced uuid.
        :param interval: interval in ms between two execution.
        :param delay: set a delay from 00:00:00.000ms interval alignment as ms.
        :param pipeline_id: set a pipeline id to trigger.
        :param template_id: set a template id to trigger.
        :param properties: set a dict of properties to pass when triggering the pipeline.
        :param twin_ids: set a list of twin ids on which executed the pipelines (must be registered on the pipeline).
        """
        if trigger_id is None:
            trigger_id = uuid.uuid4()
        self.trigger_id = trigger_id
        self.interval = interval
        self.delay = delay
        self.pipeline_id = pipeline_id
        self.template_id = template_id
        self.properties = properties
        self.twin_ids = twin_ids
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        """
        id
        :return: string formatted UUID.
        """
        return str(self.trigger_id).upper()

    def endpoint(self) -> str:
        """
        backend endpoint name.
        :return: Endpoint name.
        """
        return "ExecutionTriggers"

    def from_json(self, obj):
        """
        load from JSON dictionary representation
        """
        if "id" in obj.keys():
            self.trigger_id = uuid.UUID(obj["id"])

        if "interval" in obj.keys() and obj["interval"] is not None:
            self.interval = int(obj["interval"])
        if "delay" in obj.keys() and obj["delay"] is not None:
            self.delay = int(obj["delay"])

        if "pipelineId" in obj.keys() and obj["pipelineId"] is not None:
            self.pipeline_id = uuid.UUID(obj["pipelineId"])
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])

        if "jsonProperties" in obj.keys():
            if isinstance(obj["jsonProperties"], str) and obj["jsonProperties"] != "":
                self.properties = json.loads(obj["jsonProperties"])
            else:
                self.properties = obj["jsonProperties"]

        if "twinIds" in obj.keys() and isinstance(obj["twinIds"], list):
            self.twin_ids = []
            for twinId in obj["twinIds"]:
                self.twin_ids.append(uuid.UUID(twinId))

        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

    def to_json(self, target: str = None):
        """
        Convert to a json version of Execution definition.
        By default, use DS API format.
        """
        obj = {
            "id": str(self.trigger_id)
        }

        if self.interval is not None:
            obj["interval"] = self.interval
        if self.delay is not None:
            obj["delay"] = self.delay

        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self.pipeline_id is not None:
            obj["pipelineId"] = str(self.pipeline_id)

        if self.properties is not None:
            obj["jsonProperties"] = json.dumps(self.properties)

        if self.twin_ids is not None and len(self.twin_ids) > 0:
            obj["twinIds"] = []
            for twin_id in self.twin_ids:
                obj["twinIds"].append(str(twin_id))

        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)

        return obj
