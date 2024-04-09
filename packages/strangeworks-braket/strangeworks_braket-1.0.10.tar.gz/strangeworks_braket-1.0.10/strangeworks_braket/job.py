from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, Optional

import strangeworks as sw
from braket.tasks.quantum_task import QuantumTask
from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.types.job import Job, Status


class StrangeworksQuantumJob(QuantumTask):
    _product_slug = "amazon-braket"

    def __init__(self, job: Job, *args, **kwargs):
        self.job: Job = job

    @property
    def id(self) -> str:
        """The id of the job.

        Returns
        -------
        id: str
            The id of the job. This is the id of the job in Strangeworks.
        """
        return self.job.slug

    def cancel(self) -> None:
        """Cancel the job.

        Raises
        ------
        StrangeworksError
            If the job has not been submitted yet.

        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )

        resource = sw.get_resource_for_product(StrangeworksQuantumJob._product_slug)
        cancel_url = (
            f"{resource.proxy_url()}/hybrid_jobs/{self.job.external_identifier}"
        )
        # todo: strangeworks-python is rest_client an optional thing. i dont think it should be # noqa: E501
        # this is something we should discuss
        sw.client.rest_client.delete(url=cancel_url)

    def state(self) -> str:
        """Get the state of the job.

        Returns
        -------
        state: str
            The state of the job.

        Raises
        ------
        StrangeworksError
            If the job has not been submitted yet.
            Or if we find are not able to find the status.
        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )

        res = sw.execute_get(
            StrangeworksQuantumJob._product_slug,
            f"hybrid_jobs/{self.job.external_identifier}",
        )
        self.job = StrangeworksQuantumJob._transform_dict_to_job(res)

        if not self.job.remote_status:
            raise StrangeworksError("Job has no status")
        return self.job.remote_status

    def result(self) -> Dict[str, Any]:
        """Get the result of the job.

        Returns
        -------
        result: BraketSchemaBase
            The result of the job.

        Raises
        ------
        StrangeworksError
            If the job has not been submitted yet.
            Or if the job did not complete successfully.
            Or unable to fetch the results for the job.
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
                StrangeworksQuantumJob._product_slug,
                f"hybrid_jobs/{self.job.external_identifier}",
            )
            self.job = StrangeworksQuantumJob._transform_dict_to_job(res)
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
        job_result = contents[0]

        return job_result

    def async_result(self) -> asyncio.Task:
        raise NotImplementedError

    def metadata(self, use_cached_value: bool = False) -> Dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def from_strangeworks_slug(id: str) -> StrangeworksQuantumJob:
        """Get a job from a strangeworks id.

        Parameters
        ----------
        id: str
            The strangeworks id of the job.

        Returns
        -------
        job: StrangeworksQuantumJob
            The job.

        Raises
        ------
        StrangeworksError
            If no job is found for the id.
            Or if multiple job are found for the id.
        """
        # todo: at this point in time, sw.jobs returns a different type than sw.execute
        jobs = sw.jobs(slug=id)
        if not jobs:
            raise StrangeworksError("No jobs found for slug")
        if len(jobs) != 1:
            raise StrangeworksError("Multiple jobs found for slug")
        job = jobs[0]
        return StrangeworksQuantumJob(job)

    @staticmethod
    def create_hybrid(
        device_arn: str,
        filepath: str,
        hyperparameters: Dict[str, Any],
        device_parameters: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        *args,
        **kwargs,
    ) -> StrangeworksQuantumJob:
        """Create a job.

        Parameters
        ----------
        device_arn: str
            The name of the device to run the job on.
        filepath: str
            Path to the python file that will be run.
        hyperparameters: Dict[str, Any]
            Dictionary of hyperparameters to pass to the job.
            Must be json serializable.
        device_parameters: Optional[Dict[str, Any]]
            The device parameters.
        tags: Optional[Dict[str, str]]
            The tags to add to the strangeworks job.

        Returns
        -------
        job: StrangeworksQuantumJob
            The job.

        Raises
        ------
        StrangeworksError
            If the job specification is not a circuit, or openqasm program.

        """
        file_list = []
        with open(filepath) as fh:
            for line in fh:
                file_list.append(line)
        json_file = json.dumps(file_list)

        payload = {
            "pythonfile": json_file,
            "hyperparameters": hyperparameters,
            "aws_device_arn": device_arn,
            "device_parameters": device_parameters if device_parameters else {},
        }

        res = sw.execute_post(
            StrangeworksQuantumJob._product_slug, payload, "hybrid_jobs"
        )
        sw_job = StrangeworksQuantumJob._transform_dict_to_job(res)
        # todo: can i use sw to create tags ?
        return StrangeworksQuantumJob(sw_job)

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
