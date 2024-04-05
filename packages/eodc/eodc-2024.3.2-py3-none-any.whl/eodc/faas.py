import asyncio
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urljoin

import requests
from force_processor_bindings.model import ForceParameters, ForceResMergeOptions  # noqa
from hera.exceptions import NotFound, exception_from_server_response
from hera.workflows import Parameter, Workflow, WorkflowsService
from hera.workflows.models import WorkflowStopRequest, WorkflowTemplateRef
from hera.workflows.service import valid_host_scheme
from openeo_executor_bindings.model import OpenEOExecutorParameters
from pystac import Collection, Item
from sen2like_processor_bindings.model import BoundingBox as Sen2LikeBoundingBox  # noqa
from sen2like_processor_bindings.model import (  # noqa
    Sen2LikeParameters,
    sen2like_options,
)
from snap_processor_bindings.model import (  # noqa
    SnapCorrectionCoefficient,
    SnapCorrectionMethod,
    SnapParameters,
)
from vessel_detection_bindings.model import VesselDetectionParameters

from eodc import settings

logger = logging.getLogger(__name__)


@dataclass
class FaasProcessorDetails:
    name: str
    workflow_template_name: str


class FaasProcessor(Enum):
    Force = FaasProcessorDetails("force", "faas-force")
    Sen2Like = FaasProcessorDetails("sen2like", "faas-sen2like")
    OpenEO = FaasProcessorDetails("openeo", "faas-openeo-executor")
    Snap = FaasProcessorDetails("snap", "faas-snap")
    VesselDetection = FaasProcessorDetails("vesseldetection", "faas-vessel-detection")


LABEL_VALIDATION_REGEX = r"(([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?"


class FaasProcessorBase(ABC):
    @classmethod
    def get_instance(cls, processor_details):
        return cls(processor_details=processor_details)

    def __init__(self, processor_details: FaasProcessorDetails) -> None:
        # The URL for hera needs to end with a slash,
        # otherwise urlparse cuts the `/dev` part
        host = (
            settings.FAAS_URL + "/"
            if not settings.FAAS_URL.endswith("/")
            else settings.FAAS_URL
        )
        self.workflows_service = WorkflowsService(
            host=host, verify_ssl=False, namespace=settings.NAMESPACE
        )

        self.processor_details = processor_details
        try:
            self.workflows_service.get_info()
        except ConnectionError:
            raise Exception(
                f"Could not establish connection to argo workflows server "
                f"at {settings.FAAS_URL} in namespace {settings.NAMESPACE}"
            )

        try:
            self.workflows_service.get_workflow_template(
                processor_details.workflow_template_name, namespace=settings.NAMESPACE
            )
        except NotFound:
            raise Exception(
                f"Could not initialise faas module {self.processor_details.name} as the"
                f" workflow template {self.processor_details.workflow_template_name} "
                f"could not be found in namespace {settings.NAMESPACE}"
            )

    def submit_workflow(self, **kwargs):
        if (
            "user_id" in kwargs
            and re.match(LABEL_VALIDATION_REGEX, kwargs["user_id"]) is None
        ):
            raise ValueError("invalid user_id")
        if (
            "job_id" in kwargs
            and re.match(LABEL_VALIDATION_REGEX, kwargs["job_id"]) is None
        ):
            raise ValueError("invalid user_id")

        arguments = [Parameter(name=k, value=v) for k, v in kwargs.items()]

        workflow = Workflow(
            workflow_template_ref=WorkflowTemplateRef(
                name=self.processor_details.workflow_template_name
            ),
            workflows_service=self.workflows_service,
            namespace=settings.NAMESPACE,
            generate_name=f"{self.processor_details.name}-",
            arguments=arguments,
        )

        workflow.create()

        logger.info(
            f"Submitted {self.processor_details.name.upper()} workflow: {workflow.name}"
        )
        return workflow.name

    # Required for OpenEO sync jobs
    async def wait_for_completion(self, workflow_name, poll_interval=30):
        wf = self.workflows_service.get_workflow(
            workflow_name, namespace=settings.NAMESPACE
        )

        # keep polling for workflow status until completed,
        # at the interval dictated by the user
        # While the workflow is still initialising, this comes back as None,
        # so have to accept that here too!
        while wf.status.phase in ("Pending", "Running", None):
            await asyncio.sleep(poll_interval)
            wf = self.workflows_service.get_workflow(
                workflow_name, namespace=settings.NAMESPACE
            )
        return wf

    # Required when we want to halt code and wait.
    def block_wait_for_completion(self, workflow_name, poll_interval=30):
        wf = self.workflows_service.get_workflow(
            workflow_name, namespace=settings.NAMESPACE
        )

        # keep polling for workflow status until completed,
        # at the interval dictated by the user
        # While the workflow is still initialising, this comes back as None,
        # so have to accept that here too!
        while wf.status.phase in ("Pending", "Running", None):
            time.sleep(poll_interval)
            wf = self.workflows_service.get_workflow(
                workflow_name, namespace=settings.NAMESPACE
            )
        return wf

    def get_workflow_status(self, workflow_name: str) -> dict:
        # TODO: Limit this response to only the required fields
        workflow_response = self.workflows_service.get_workflow(
            name=workflow_name, namespace=settings.NAMESPACE
        )
        return dict(workflow_response.status)

    def stop_workflow(self, name):
        req = WorkflowStopRequest(name=name, namespace=settings.NAMESPACE)
        try:
            self.workflows_service.stop_workflow(
                name, req=req, namespace=settings.NAMESPACE
            )
            logger.info(f"Successfully stopped workflow {name}.")
        except NotFound:
            logger.warning(f"Could not stop workflow {name}.")

    def get_logs(self, workflow_name) -> list[str]:
        assert valid_host_scheme(
            self.workflows_service.host
        ), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(
                self.workflows_service.host, "api/v1/workflows/{namespace}/{name}/log"
            ).format(name=workflow_name, namespace=settings.NAMESPACE),
            params={
                "podName": None,
                "logOptions.container": "main",
                "logOptions.follow": None,
                "logOptions.previous": None,
                "logOptions.sinceSeconds": None,
                "logOptions.sinceTime.seconds": None,
                "logOptions.sinceTime.nanos": None,
                "logOptions.timestamps": None,
                "logOptions.tailLines": None,
                "logOptions.limitBytes": None,
                "logOptions.insecureSkipTLSVerifyBackend": None,
                "grep": None,
                "selector": None,
            },
            headers={"Authorization": f"Bearer {self.workflows_service.token}"},
            data=None,
            verify=self.workflows_service.verify_ssl,
        )

        if resp.ok:
            raw_logs = resp.content.decode("utf8").split("\n")
            return [
                json.loads(log)["result"]["content"]
                for log in raw_logs
                if log != "" and "content" in json.loads(log)["result"].keys()
            ]

        raise exception_from_server_response(resp)

    @abstractmethod
    def get_output_stac_items(self):
        raise NotImplementedError()


class Force(FaasProcessorBase):
    @classmethod
    def get_instance(cls):
        return cls(processor_details=FaasProcessor.Force.value)

    def submit_workflow(
        self, force_parameters: ForceParameters, user_id: str, job_id: str
    ):
        return super().submit_workflow(
            force_parameters=force_parameters.json(), user_id=user_id, job_id=job_id
        )

    def get_output_stac_items(self, force_parameters: ForceParameters) -> list[Item]:
        output_path = force_parameters.stac_output_dir

        collection_file = list(output_path.glob("*_collection.json"))[0]
        force_output_collection = Collection.from_file(str(collection_file))
        stac_items = [
            Item.from_file(link.get_absolute_href())
            for link in force_output_collection.get_item_links()
        ]

        return stac_items


class Sen2Like(FaasProcessorBase):
    @classmethod
    def get_instance(cls):
        return cls(processor_details=FaasProcessor.Sen2Like.value)

    def submit_workflow(
        self, sen2like_parameters: Sen2LikeParameters, user_id: str, job_id: str
    ):
        return super().submit_workflow(
            sen2like_parameters=sen2like_parameters.json(),
            user_id=user_id,
            job_id=job_id,
        )

    def get_output_stac_items(
        self, sen2like_parameters: Sen2LikeParameters, target_product: str = "L2F"
    ) -> list[Item]:
        from sen2like_processor_bindings.model import get_output_stac_item_paths

        stac_item_paths = get_output_stac_item_paths(
            sen2like_parameters, target_product=target_product
        )
        stac_items = [Item.from_file(str(path)) for path in stac_item_paths]
        return stac_items


class OpenEO(FaasProcessorBase):
    @classmethod
    def get_instance(cls):
        return cls(processor_details=FaasProcessor.OpenEO.value)

    def submit_workflow(
        self,
        openeo_parameters: OpenEOExecutorParameters,
        openeo_user_id: str,
        openeo_job_id: str,
    ):
        return super().submit_workflow(
            openeo_executor_parameters=openeo_parameters.json(),
            openeo_user_id=openeo_user_id,
            openeo_job_id=openeo_job_id,
        )

    def get_output_stac_items(
        self, openeo_parameters: OpenEOExecutorParameters
    ) -> list[Item]:
        collection_file = list(openeo_parameters.stac_path.glob("*_collection.json"))[0]
        openeo_output_collection = Collection.from_file(str(collection_file))
        stac_items = [
            Item.from_file(link.get_absolute_href())
            for link in openeo_output_collection.get_item_links()
        ]

        return stac_items

    def _get_workflows_for_job_id(
        self, openeo_job_id, filter_workflow_status_phase: Optional[tuple[str]] = None
    ) -> list[Workflow]:
        # filter_workflow_status_phase wants to be an iterable
        # of strings like ("Running", "Pending")
        workflows = self.workflows_service.list_workflows(
            namespace=settings.NAMESPACE,
            label_selector=f"openeo_job_id={openeo_job_id}",
        ).items
        if filter_workflow_status_phase is not None:
            workflows_with_label_filtered = [
                workflow
                for workflow in workflows
                if workflow.status.phase in filter_workflow_status_phase
            ]
        else:
            workflows_with_label_filtered = workflows
        return workflows_with_label_filtered

    def stop_openeo_job(self, openeo_job_id):
        associated_unfinished_workflows = self._get_workflows_for_job_id(
            openeo_job_id=openeo_job_id,
            filter_workflow_status_phase=("Running", "Pending"),
        )
        logger.info(
            f"Stopping OpenEO job {openeo_job_id} with "
            f"{len(associated_unfinished_workflows)} unfinished sub-workflows."
        )

        # Need to stop all sub-jobs too!
        for workflow in associated_unfinished_workflows:
            if workflow.status.phase in ("Running", "Pending"):
                workflow_name = workflow.metadata.name
                super().stop_workflow(workflow_name)
        logger.info(f"Successfully stopped OpenEO job {openeo_job_id}.")


class Snap(FaasProcessorBase):
    @classmethod
    def get_instance(cls):
        return cls(processor_details=FaasProcessor.Snap.value)

    def submit_workflow(
        self,
        snap_parameters: SnapParameters,
        user_id: str,
        job_id: str,
    ):
        return super().submit_workflow(
            snap_parameters=snap_parameters.json(),
            user_id=user_id,
            job_id=job_id,
        )

    def get_output_stac_items(self, snap_parameters: SnapParameters) -> list[Item]:
        collection_file = list(snap_parameters.stac_path.glob("*_collection.json"))[0]
        snap_output_collection = Collection.from_file(str(collection_file))
        stac_items = [
            Item.from_file(link.get_absolute_href())
            for link in snap_output_collection.get_item_links()
        ]

        return stac_items


class VesselDetection(FaasProcessorBase):
    @classmethod
    def get_instance(cls):
        return cls(processor_details=FaasProcessor.VesselDetection.value)

    def submit_workflow(
        self,
        detection_parameters: VesselDetectionParameters,
        vessels_output_dir: str,
        user_id: str,
        job_id: str,
    ):
        return super().submit_workflow(
            detection_parameters=detection_parameters.json(),
            vessels_output_dir=vessels_output_dir,
            user_id=user_id,
            job_id=job_id,
        )

    def get_output_stac_items(
        self, detection_parameters: VesselDetectionParameters
    ) -> list[Item]:
        """Not needed."""
        return None
