from __future__ import annotations

import asyncio
import json
import time
from functools import singledispatch
from typing import Any, Dict, Optional, Tuple, Union

import strangeworks as sw
from braket.ahs.analog_hamiltonian_simulation import AnalogHamiltonianSimulation
from braket.annealing.problem import Problem
from braket.circuits import Circuit
from braket.circuits.serialization import IRType
from braket.ir.openqasm import Program as OpenQasmProgram
from braket.schema_common import BraketSchemaBase
from braket.tasks.annealing_quantum_task_result import AnnealingQuantumTaskResult
from braket.tasks.gate_model_quantum_task_result import GateModelQuantumTaskResult
from braket.tasks.quantum_task import QuantumTask
from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.types.job import Job, Status

from strangeworks_braket.utils.serializer import pickle_serializer


class StrangeworksQuantumTask(QuantumTask):
    _product_slug = "amazon-braket"

    def __init__(self, job: Job, *args, **kwargs):
        self.job: Job = job

    @property
    def id(self) -> str:
        """The id of the task.

        Returns
        -------
        id: str
            The id of the task. This is the id of the job in Strangeworks.
        """
        return self.job.slug

    def cancel(self) -> None:
        """Cancel the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.

        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )

        resource = sw.get_resource_for_product(StrangeworksQuantumTask._product_slug)
        cancel_url = f"{resource.proxy_url()}/jobs/{self.job.external_identifier}"
        # todo: strangeworks-python is rest_client an optional thing. i dont think it should be # noqa: E501
        # this is something we should discuss
        sw.client.rest_client.delete(url=cancel_url)

    def state(self) -> str:
        """Get the state of the task.

        Returns
        -------
        state: str
            The state of the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.
            Or if we find are not able to find the status.
        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )

        res = sw.execute_get(
            StrangeworksQuantumTask._product_slug,
            f"jobs/{self.job.external_identifier}",
        )
        self.job = StrangeworksQuantumTask._transform_dict_to_job(res)

        if not self.job.remote_status:
            raise StrangeworksError("Job has no status")
        return self.job.remote_status

    def result(self) -> Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]:
        """Get the result of the task.

        Returns
        -------
        result: Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]
            The result of the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.
            Or if the task did not complete successfully.
            Or unable to fetch the results for the task.
        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )
        while self.job.status not in {
            Status.COMPLETED,
            Status.FAILED,
            Status.CANCELLED,
        }:
            res = sw.execute_get(
                StrangeworksQuantumTask._product_slug,
                f"jobs/{self.job.external_identifier}",
            )
            self.job = StrangeworksQuantumTask._transform_dict_to_job(res)
            time.sleep(2.5)

        if self.job.status != Status.COMPLETED:
            raise StrangeworksError("Job did not complete successfully")
        # sw.jobs will return type errors until it updates their type hints
        # todo: update strangeworks-python job type hints
        # todo: at this point in time, sw.jobs returns a different type than sw.execute
        jobs = sw.jobs(slug=self.job.slug)
        if not jobs:
            raise StrangeworksError("Job not found.")
        if len(jobs) != 1:
            raise StrangeworksError("Multiple jobs found.")
        job: Job = jobs[0]
        if not job.files:
            raise StrangeworksError("Job has no files.")
        # for now the strangeworks-python library still returns the Job.files as Files not JobFiles # noqa: E501
        files = list(
            filter(lambda f: f.file_name == "job_results_braket.json", job.files)
        )
        if len(files) != 1:
            raise StrangeworksError("Job has multiple files")

        file = files[0]
        if not file.url:
            raise StrangeworksError("Job file has no url")
        # why does this say it returns a list of files?
        # did it not just download the file?
        # is the contents not some dictionary?
        # todo probably have to update this in strangeworks-python
        contents = sw.download_job_files([file.url])
        if not contents:
            raise StrangeworksError("Unable to download result file.")
        if len(contents) != 1:
            raise StrangeworksError("Unable to download result file.")
        bsh = BraketSchemaBase.parse_raw_schema(json.dumps(contents[0]))

        if (
            bsh.taskMetadata.deviceId
            != "arn:aws:braket:us-east-1::device/qpu/quera/Aquila"
            and bsh.taskMetadata.deviceId
            != "arn:aws:braket:us-east-1::device/qpu/xanadu/Borealis"
        ):
            task_result = GateModelQuantumTaskResult.from_object(bsh)
        else:
            task_result = bsh
        return task_result

    def async_result(self) -> asyncio.Task:
        raise NotImplementedError

    def metadata(self, use_cached_value: bool = False) -> Dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def from_strangeworks_slug(id: str) -> StrangeworksQuantumTask:
        """Get a task from a strangeworks id.

        Parameters
        ----------
        id: str
            The strangeworks id of the task.

        Returns
        -------
        task: StrangeworksQuantumTask
            The task.

        Raises
        ------
        StrangeworksError
            If no task is found for the id.
            Or if multiple tasks are found for the id.
        """
        # todo: at this point in time, sw.jobs returns a different type than sw.execute
        jobs = sw.jobs(slug=id)
        if not jobs:
            raise StrangeworksError("No jobs found for slug")
        if len(jobs) != 1:
            raise StrangeworksError("Multiple jobs found for slug")
        job = jobs[0]
        return StrangeworksQuantumTask(job)

    @staticmethod
    def create(
        device_arn: str,
        task_specification: Union[
            Circuit, Problem, OpenQasmProgram, AnalogHamiltonianSimulation
        ],
        shots: int,
        device_parameters: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        *args,
        **kwargs,
    ) -> StrangeworksQuantumTask:
        """Create a task.

        Parameters
        ----------
        device_arn: str
            The name of the device to run the task on.
        task_specification: Union[Circuit, Problem, OpenQasmProgram]
            The task specification.
        shots: int
            The number of shots to run the task for.
        device_parameters: Optional[Dict[str, Any]]
            The device parameters.
        tags: Optional[Dict[str, str]]
            The tags to add to the strangeworks job.

        Returns
        -------
        task: StrangeworksQuantumTask
            The task.

        Raises
        ------
        StrangeworksError
            If the task specification is not a circuit, or openqasm program.

        """
        circuit_type, circuit = _sw_task_specification(task_specification)
        payload = {
            "circuit_type": circuit_type,
            "circuit": circuit,
            "aws_device_arn": device_arn,
            "device_parameters": device_parameters if device_parameters else {},
            "shots": shots,
        }

        res = sw.execute_post(StrangeworksQuantumTask._product_slug, payload, "jobs")
        sw_job = StrangeworksQuantumTask._transform_dict_to_job(res)
        # todo: can i use sw to create tags ?
        return StrangeworksQuantumTask(sw_job)

    # create a method that transforms the dict into a job
    # first it must convert the json keys from snake_case to camelCase
    # then it must create a job from the dict
    @staticmethod
    def _transform_dict_to_job(d: Dict[str, Any]) -> Job:
        # todo: this is unfortunate. dont like that we need to do this.
        def to_camel_case(snake_str):
            components = snake_str.split("_")
            # We capitalize the first letter of each component except the first one
            # with the 'title' method and join them together.
            return components[0] + "".join(x.title() for x in components[1:])

        remix = {to_camel_case(key): value for key, value in d.items()}
        return Job.from_dict(remix)


@singledispatch
def _sw_task_specification(
    task_specification: Union[
        Circuit, Problem, OpenQasmProgram, AnalogHamiltonianSimulation
    ]
) -> Tuple[str, str]:
    raise NotImplementedError


# register a function for each type
@_sw_task_specification.register
def _sw_task_specification_circuit(task_specification: Circuit) -> Tuple[str, str]:
    return "qasm", task_specification.to_ir(ir_type=IRType.OPENQASM).json()


@_sw_task_specification.register
def _sw_task_specification_problem(task_specification: Problem) -> Tuple[str, str]:
    raise NotImplementedError


@_sw_task_specification.register
def _sw_task_specification_openqasm(
    task_specification: OpenQasmProgram,
) -> Tuple[str, str]:
    return "qasm", task_specification.json()


@_sw_task_specification.register
def _sw_task_specification_aquila(
    task_specification: AnalogHamiltonianSimulation,
) -> Tuple[str, str]:
    task_new_specification = json.dumps(pickle_serializer(task_specification, "json"))
    return "aquila", task_new_specification
