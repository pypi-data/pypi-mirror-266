"""client.py."""

import base64
import importlib.metadata
import os
from functools import singledispatchmethod, wraps
from typing import Any, Callable, Dict, List, Optional, Union

import dill
from strangeworks_core.platform.gql import API, APIInfo
from strangeworks_core.types.resource import Resource

from strangeworks.core.client import auth, file, jobs, resource, workspace
from strangeworks.core.client.backends import Backend, get_backend, get_backends
from strangeworks.core.client.experiments import (
    Experiment,
    ExperimentConfiguration,
    ExperimentInput,
    Trial,
    TrialSubmission,
    get_experiment,
)
from strangeworks.core.client.experiments import run as experiment_run
from strangeworks.core.client.experiments import upload_exp_file
from strangeworks.core.client.file import File
from strangeworks.core.client.jobs import Job
from strangeworks.core.client.rest_client import StrangeworksRestClient
from strangeworks.core.client.workspace import Workspace
from strangeworks.core.config.base import ConfigSource
from strangeworks.core.errors.error import StrangeworksError
from strangeworks.core.utils import fix_str_attr
from strangeworks.platform.gql import SDKAPI

__version__ = importlib.metadata.version("strangeworks")


class SWClient:
    """Strangeworks client object."""

    def __init__(
        self,
        cfg: ConfigSource,
        headers: Optional[Dict[str, str]] = None,
        rest_client: Optional[StrangeworksRestClient] = None,
        **kwargs,
    ) -> None:
        """Strangeworks client.

        Implements the Strangeworks API and provides core functionality for cross-vendor
        applications.

        Parameters
        ----------
        cfg: ConfigSource
            Source for retrieving SDK configuration values.
        headers : Optional[Dict[str, str]]
            Headers that are sent as part of the request to Strangeworks.
        rest_client : Optional[StrangeworksRestClient]
        **kwargs
            Other keyword arguments to pass to tools like ``requests``.
        """
        self.cfg = cfg
        self.kwargs = kwargs

        self.headers = (
            os.getenv("STRANGEWORKS_HEADERS", default=None)
            if headers is None
            else headers
        )

        self.rest_client = rest_client
        self._key = cfg.get("api_key")
        self._url = cfg.get("url")

    def authenticate(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        profile: Optional[str] = None,
        store_credentials: bool = True,
        overwrite: bool = False,
        **kwargs,
    ) -> None:
        """Authenticate with Strangeworks.

        Obtains an authorization token from the platform using the api_key. The auth
        token is used to make calls to the platform. Access to platform interfaces
        are initialized.

        Parameters
        ----------
        api_key : Optional[str]
            The API key.
        url: Optional[str]
            The base URL to the Strangeworks API.
        profile: Optional[str]
            The profile name to use for configuration.
        store_credentials: bool
            Indicates whether credentials (api key an url)  should be saved. Defaults
            to True.
        overwrite: bool
            Indicates whether to overwrite credentials if they already exist. Defaults
            to False.
        **kwargs
            Additional arguments.
        """
        _key = api_key or (
            self.cfg.get("api_key", profile=profile) if profile else self._key
        )

        if _key is None:
            raise StrangeworksError.authentication_error(
                message=(
                    "Unable to retrieve api key from a previous configuration. "
                    "Please provide your api_key."
                )
            )
        _url = url or (self.cfg.get("url", profile=profile) if profile else self._url)

        _auth_token = auth.get_token(_key, _url)
        # successfully obtained an auth token.
        # first set, url
        self._key = _key
        self._url = _url
        # might as well try to use it.
        self.rest_client = StrangeworksRestClient(
            api_key=_key, host=_url, auth_token=_auth_token
        )

        # get the workspace info
        workspace: Workspace = self.workspace_info()
        self.cfg.set_active_profile(active_profile=workspace.slug)

        # if we made it this far, lets go ahead and try to save the configuration to a
        # file. But only if an api_key was provided.
        if api_key and api_key != self.cfg.get("api_key") and store_credentials:
            self.cfg.set(
                profile=workspace.slug,
                overwrite=overwrite,
                api_key=api_key,
                url=_url,
            )

    def get_sdk_api(self) -> SDKAPI:
        """Return SDK API instance."""
        if not self._key:
            raise StrangeworksError.authentication_error()
        return SDKAPI(
            api_key=self._key,
            base_url=self._url,
        )

    def resources(self, slug: Optional[str] = None) -> Optional[List[Resource]]:
        """Retrieve list of resources that are available for this workspace account.

        Parameters
        ----------
        slug: Optional[str]
            Identifier for a specific resource. Defaults to None.

        Return
        ------
        Optional[List[Resource]]
            List of resources for the current workspace account or None if no resources
            have been created.
        """
        return resource.get(client=self.get_sdk_api(), resource_slug=slug)

    def jobs(
        self,
        slug: Optional[str] = None,
        resource_slugs: Optional[List[str]] = None,
        product_slugs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Job:
        """Retrieve list of jobs associated with the current workspace account.

        Parameters
        ----------
        slug : Optional[str] = None
            Identifier for a specific job. Defaults to None.
        resource_slugs: Optional[List[str]]
            List of resource identifiers. Only jobs whose resources match will be
            returned. Defaults to None.
        product_slugs: Optional[List[str]]
            List of product identifiers. Only jobs whose product slugs match will be
            returned. Defaults to None.
        statuses: Optional[List[str]]
            List of job statuses. Only obs whose statuses match will be returned.
            Defaults to None.

        Return
        -------
        : Optional[List[Job]]
            List of jobs or None if there are no jobs that match selection criteria.
        """
        return jobs.get(
            client=self.get_sdk_api(),
            job_slug=slug,
            product_slugs=product_slugs or [],
            resource_slugs=resource_slugs or [],
            statuses=statuses or [],
            tags=tags or [],
        )

    def workspace_info(self) -> Workspace:
        """Retrieve information about the current workspace."""
        return workspace.get(self.get_sdk_api())

    def execute(
        self,
        res: Resource,
        payload: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
    ):
        """Execute a job request.

        Parameters
        ----------
        res: Resource
            the resource that has the function to call.
        payload: Optiona;[Dict[str, Any]]
            the payload to send with the request.
        endpoint:
            additional endpoint to append to the proxy path for the resource.

        """
        if payload:
            return self.rest_client.post(
                url=res.proxy_url(endpoint),
                json=payload,
            )

        return self.rest_client.get(url=res.proxy_url(endpoint))

    def execute_post(
        self,
        product_slug: str,
        payload: Optional[Dict[str, Any]] = None,
        json: Optional[dict] = None,
        data: Optional[any] = None,
        endpoint: Optional[str] = None,
    ):
        """Execute a job request.

        Parameters
        ----------
        product_slug: str
            string used to identify a product entry on the platform.
        payload:
            same as json
        json:
            A JSON serializable Python object to send in the body of the Request.
        data:
            Dictionary, list of tuples, bytes, or file-like object to send in the body
            of the Request. Typically a string.
        endpoint: str | None = None
            additional path that denotes a service/product endpoint.

        Returns
        -------
            Result of the request, typically a dictionary.
        """
        resource = self.get_resource_for_product(product_slug)
        return self.rest_client.post(
            url=resource.proxy_url(path=endpoint), json=payload or json, data=data
        )

    def execute_get(self, product_slug: str, endpoint: Optional[str] = None):
        """Execute GET.

        Parameters
        ----------
        product_slug: str
            string used to identify a product entry on the platform.
        endpoint: str | None = None
            additional path that denotes a service/product endpoint.

        Returns
        -------
            Result of the request, typically a JSON serializable object like a
            dictionary.
        """
        resource = self.get_resource_for_product(product_slug)
        return self.rest_client.get(url=resource.proxy_url(endpoint))

    def get_backends(
        self,
        product_slugs: List[str] = None,
        backend_type_slugs: List[str] = None,
        backend_statuses: List[str] = None,
        backend_tags: List[str] = None,
    ) -> List[Backend]:
        """Return a list of backends available based on the filters provided.

        Replaces the deprecated BackendsService.
        """
        return get_backends(
            client=self.get_sdk_api(),
            product_slugs=product_slugs,
            backend_type_slugs=backend_type_slugs,
            backend_statuses=backend_statuses,
            backend_tags=backend_tags,
        )

    def get_backend(self, backend_slug: str) -> Backend:
        """Return a single backend by the slug.

        Replaces the deprecated BackendsService.
        """
        return get_backend(self.get_sdk_api(), backend_slug)

    def upload_file(self, file_path: str) -> File:
        """Upload a file to strangeworks.

        File.url is how you can download the file.

        raises StrangeworksError if any issues arise while attempting to upload the
        file.
        """
        w = workspace.get(self.get_sdk_api())
        f, signedUrl = file.upload(self.get_sdk_api(), w.slug, file_path)
        try:
            fd = open(file_path, "rb")
        except IOError as e:
            raise StrangeworksError(f"unable to open {file_path}: {str(e)}")
        else:
            with fd:
                self.rest_client.put(signedUrl, data=fd)
        return f

    @singledispatchmethod
    def download_job_files(
        self,
        file_paths: Union[str, list],
        resource_slugs: Optional[List[str]] = None,
        product_slugs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[File]:
        """Download files associated with a job.

        Parameters
        ----------
        file_paths: Union[str, list]
            either the job slug (str) or a list of URLs associated with a Job object.

        Return
        ------
        A List of File objects.
        """
        raise NotImplementedError("files must either be a string or a List of strings")

    @download_job_files.register
    def _(
        self,
        file_paths: str,
        resource_slugs: Optional[List[str]] = None,
        product_slugs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[File]:
        sw_job = jobs.get(
            client=self.get_sdk_api(),
            job_slug=file_paths,
            product_slugs=product_slugs,
            resource_slugs=resource_slugs,
            statuses=statuses,
        )

        file_paths = [f.url for f in sw_job[0].files]

        files_out = [self.rest_client.get(url=f) for f in file_paths]

        return files_out

    @download_job_files.register
    def _(
        self,
        file_paths: list,
        resource_slugs: Optional[List[str]] = None,
        product_slugs: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[File]:
        files_out = [self.rest_client.get(url=f) for f in file_paths]

        return files_out

    def set_resource_for_product(
        self,
        resource_slug: str,
        product_slug: str,
    ) -> None:
        """Set which resource to use for a given product.

        Users can have multiple resources set up for the same product. When this is the
        case, they can set which resource to use with this call.

        Parameters
        ----------
        resource: str
            Resource identifier (currently the slug).
        product_slug:
         str
            product identifier.
        """
        res = self.resources(slug=resource_slug)
        if len(res) == 0:
            raise StrangeworksError(
                message=(
                    f"Unable to retrieve resource (slug: {resource}) "
                    f"for workspace {self.cfg.get_active_profile()}"
                )
            )
        if len(res) > 1:
            raise StrangeworksError(
                message=(
                    f"More than one resource with slug: {resource}"
                    f" for workspace {self.cfg.get_active_profile()}"
                )
            )
        if res[0].product.slug != product_slug:
            raise StrangeworksError(
                message=(
                    f"Resource (slug: {res[0].slug}, product: {res[0].product.slug} is "
                    f"for a different product {product_slug}"
                )
            )
        kwargs = {product_slug: resource_slug}
        self.cfg.set(**kwargs)

    def get_resource_for_product(
        self,
        product_slug: str,
    ) -> Resource:
        """Get resource to use when using product.

        If the user has a resource allready configured and that resource still exists,
        that resource will be returned. If the user-configured resource no longer
        exists, an error will be raised.

        If user does not have a resource identified for the product and there is only
        a single resouce for the product available in the users workspace, that resource
        will be returned.

        If there are multiple resources for the given product slug and the user hasn't
        already selected one, they will be asked to do so.

        If there are no resources configured for the product slug, an error will be
        raised asking the user to create one.

        Parameters
        ----------
        product_slug: str
            product identifier.

        Return
        ------
        : Resource
            a resource object which maps to the product.

        Raises
        ------
        :StrangeworksError
            if no resource is found or there are multiple resource and none selected.
        """
        _product_slug = fix_str_attr(product_slug)
        resources = self.resources()
        resource_slug = self.cfg.get(_product_slug)
        if resource_slug:
            resource_as_list = [res for res in resources if res.slug == resource_slug]
            if len(resource_as_list) != 1:
                raise StrangeworksError(
                    f"Resource (slug: {resource_slug}) no longer exists on the system"
                )
            else:
                return resource_as_list[0]
        # we dont have a resource slug. lets see how many resources we can find in this
        # workspace with matching product slug.
        candidates = [res for res in resources if res.product.slug == _product_slug]
        if len(candidates) > 1:
            resources_list = [
                f"  resource_slug: {r.slug}, product_slug: {r.product.slug}"
                for r in candidates
            ]

            resources_string = "\n".join(resources_list)

            raise StrangeworksError(
                message=f"More than one matching resource found for "
                f"{product_slug}. Please select one:\n"
                f"{resources_string}\n Then call "
                "strangeworks.set_resource_for_product"
                "(resource_slug, product_slug)"
            )
        if len(candidates) == 0:
            raise StrangeworksError(
                message=f"No matching resource found for {product_slug}. "
                "Please create one."
            )

        return candidates[0]

    def get_error_messages(
        self,
        job_slug: str,
    ) -> Dict[str, List[File]]:
        sw_job = jobs.get(
            client=self.get_sdk_api(),
            job_slug=job_slug,
        )

        if len(sw_job) == 0:
            raise StrangeworksError(f"Job with slug {job_slug} not found in workspace.")
        else:
            sw_job = sw_job[0]

        # Check parent job for error messages
        parent_files = []
        child_files = []
        for f in sw_job.files:
            if "error" in f.file_name:
                parent_files.append(self.rest_client.get(url=f.url))

        # Check child job for error messages
        if sw_job.child_jobs:
            for child_job in sw_job.child_jobs:
                for f in child_job.files:
                    if "error" in f.file_name:
                        child_files.append(self.rest_client.get(url=f.url))

        # For svc-from-callable jobs, error message is in results file
        for f in sw_job.files:
            if "result" in f.file_name:
                result = self.rest_client.get(url=f.url)
                if isinstance(result, dict) and any(
                    "error" in r for r in result.keys()
                ):
                    parent_files.append(result)

        if sw_job.child_jobs:
            for child_job in sw_job.child_jobs:
                for f in child_job.files:
                    if "result" in f.file_name:
                        result = self.rest_client.get(url=f.url)
                        if any("error" in r for r in result.keys()):
                            child_files.append(result)

        return {"parent_job": parent_files, "child_jobs": child_files}

    def run(
        self,
        func: Callable[..., Any],
        input: Union[ExperimentInput, list[ExperimentInput]],
        cfg: ExperimentConfiguration = ExperimentConfiguration(),
        **kwargs,
    ) -> dict[str, TrialSubmission]:
        """
        Run an experiment.

        Parameters
        ----------
        func: Callable[..., Any]
            The function to run.
        input: Union[ExperimentInput, list[ExperimentInput]]
            The input to the function.
        cfg: ExperimentConfiguration
            The configuration for the experiment.

        Returns
        -------
        dict[str, TrialSubmission]
            The results of the experiment.
        """
        a = API(self._url, APIInfo.SDK, api_key=self._key)
        return experiment_run(a, func, input, cfg, **kwargs)

    def experiment(self, cfg: ExperimentConfiguration = ExperimentConfiguration()):
        """Generate Callable for running an experiment.

        Parameters
        ----------
        cfg: ExperimentConfiguration
            The configuration for the experiment.

        Returns
        -------
        Callable[..., Any]
            The decorated function.

        Examples
        --------
        >>> @sw.experiment()
        ... def my_experiment():
        ...     return 42
        ... my_experiment()

        """

        def decorator(func):
            @wraps(func)
            def wrapper(*fargs, **fkwargs):
                experiment_name = (
                    cfg.experiment_name if cfg.experiment_name else func.__name__
                )
                trial_name = cfg.trial_name if cfg.trial_name else func.__name__
                return self.run(
                    func,
                    ExperimentInput(experiment_name, trial_name, fargs, fkwargs),
                    cfg,
                )

            wrapper.sw_exp_og_func = func
            return wrapper

        return decorator

    def experiment_download(
        self,
        experiment_name: str,
        trials: Union[int, list[str]],
        files: Union[str, list[str]],
        jobs: Union[bool, list[str]],
    ) -> Experiment:
        """Download an Experiment.

        This gives you the flexiblity to download any number of trials.
        Particular files or jobs can be downloaded for each trial.

        Parameters
        ----------
        experiment_name: str
            The name of the experiment.
        trials: Union[int, list[str]]
            The trials to download.
            If an int is provided, then the last n trials will be downloaded.
            If a list of str is provided, then the named trials will be downloaded.
            The list of str are expected to be trial_name values.
        files: Union[str, list[str]]
            The files to download.
            The str or list of str are expected to be file_name values.
            If a str is provided, then the file will be downloaded.
            If a list of str is provided, then the files will be downloaded.
        jobs: Union[bool, list[str]]
            The jobs to download.
            If a bool is provided,
                then the all jobs related with the trial will be downloaded.
            If a list of str is provided, then the jobs will be downloaded.

        Returns
        -------
        Experiment
            The experiment.

        Examples
        --------
        >>> # Download the last 3 trials of the 'heavy_computation' experiment.
        >>> # Download the 'user_program_stdout.txt' file for each trial.
        >>> # Do not include any related jobs.
        >>> import strangeworks as sw
        >>> sw.authenticate(...) # update with your api key.
        >>> sw.experiment_download(
        ...     "heavy_computation", 3, "user_program_stdout.txt", False
        ... )
        Experiment(
            name='heavy_computation',
            trials=[
                Trial(
                    name='siete_ocho_207',
                    files=[
                        File(
                            id=None,
                            slug='evtstr5wp',
                            label=None,
                            file_name='user_program_stdout.txt',
                            url='https://api.strangeworks.com/files/experiments/lucky-badger-8981-krjdisf9d/trial/snarling-roe-0728-t0k8btudx/evtstr5wp',
                            content='The answer is 42.',
                        )
                    ],
                    jobs=None,
                ),
                Trial(
                    name='siete_ocho_206',
                    files=[
                        File(
                            id=None,
                            slug='9kemsahmh',
                            label=None,
                            file_name='user_program_stdout.txt',
                            url='https://api.strangeworks.com/files/experiments/lucky-badger-8981-krjdisf9d/trial/glistening-river-1629-5pjcb0r9j/9kemsahmh',
                            content='sent request to strangeworks optimization.',
                            )
                    ],
                    jobs=None,
                ),
                Trial(
                    name='siete_ocho_205',
                    files=[
                        File(
                            id=None,
                            slug='rbm85i4wy',
                            label=None,
                            file_name='user_program_stdout.txt',
                            url='https://api.strangeworks.com/files/experiments/lucky-badger-8981-krjdisf9d/trial/winding-water-8578-giugxm4gd/rbm85i4wy',
                            content='',
                        )
                    ],
                    jobs=None,
                )])

        >>> # Download a list of named trials of the 'heavy_computation' experiment.
        >>> # Download the 'result.pickle' and 'user_program_stdout.txt'
        >>> #   files for each trial.
        >>> # If the trial has the files you requested
        >>> #   then they will be included in the Trial object.
        >>> # Include any related jobs.
        >>> # If no jobs are related to any of the trials,
        >>> #   then the jobs attribute will be None.
        >>> import strangeworks as sw
        >>> sw.authenticate(...) # update with your api key.
        >>> sw.experiment_download(
        ...     "heavy_computation",
        ...     ["siete_ocho", "siete_ocho_9"],
        ...     ["result.pickle", "user_program_stdout.txt"],
        ...     True,
        ... )
        Experiment(
            name='heavy_computation',
            trials=[
                Trial(
                    name='siete_ocho_9',
                    files=[
                        File(
                            id=None,
                            slug='hseuqyjd7',
                            label=None,
                            file_name='result.pickle',
                            url='https://api.strangeworks.com/files/experiments/lucky-badger-8981-krjdisf9d/trial/bold-whale-5839-5yhcpjuhz/hseuqyjd7',
                            content='gASVBAAAAAAAAABNagQu'
                        ),
                        File(
                            id=None,
                            slug='ey5szvabe',
                            label=None,
                            file_name='user_program_stdout.txt',
                            url='https://api.strangeworks.com/files/experiments/lucky-badger-8981-krjdisf9d/trial/bold-whale-5839-5yhcpjuhz/ey5szvabe',
                            content=''),
                    ],
                    jobs=[
                        Job(
                            slug='straight-mountain-3370',
                            child_jobs=[],
                            external_identifier='',
                            resource=None,
                            status='COMPLETED',
                            is_terminal_state=None,
                            remote_status=None,
                            job_data_schema=None,
                            job_data=None,
                            files=[
                                File(
                                    id=None,
                                    slug='7ab5s545s',
                                    label=None,
                                    file_name='result.json',
                                    url='https://api.strangeworks.com/files/jobs/straight-mountain-3370/7ab5s545s/result.json',
                                    content=None,
                                )
                            ],
                        )
                    ]),
                Trial(name='siete_ocho', files=[], jobs=None)
            ],
        )



        """
        a = API(self._url, APIInfo.SDK, api_key=self._key)
        exp = get_experiment(a, experiment_name, trials, files, jobs)

        ts = []
        for t in exp.trials:
            fs = []
            for f in t.files:
                try:
                    content = self.rest_client.get(url=f.url)
                    if (
                        f.file_name == "result.pickle"
                        and f.data_schema_slug == "sw-result-pickle"
                    ):
                        content = dill.loads(base64.b64decode(content))
                except Exception as e:
                    content = e
                fs.append(
                    File(
                        id=f.id,
                        slug=f.slug,
                        label=f.label,
                        file_name=f.file_name,
                        url=f.url,
                        content=content,
                    )
                )
            ts.append(Trial(name=t.name, status=t.status, files=fs, jobs=t.jobs))

        return Experiment(
            exp.name,
            ts,
        )

    def experiment_upload(
        self,
        experiment_name: str,
        trial_name: str,
        file_path: str,
    ) -> File:
        """
        experiment_upload allows you to upload a file to a trial.

        Parameters
        ----------
        experiment_name: str
            The name of the experiment.
        trial_name: str
            The name of the trial.
        file_path: str
            The path to the file to upload.

        Returns
        -------
        File
            The file that was uploaded.

        Examples
        --------
        >>> import strangeworks as sw
        >>> sw.authenticate(...)
        >>> sw.experiment_upload(
        ...     "heavy_computation",
        ...     "siete_ocho_9",
        ...     "./post_processed_result.json",
        ... )

        """
        a = API(self._url, APIInfo.SDK, api_key=self._key)
        f, url = upload_exp_file(a, experiment_name, trial_name, file_path)
        try:
            fd = open(file_path, "rb")
        except IOError as e:
            raise StrangeworksError(f"unable to open {file_path}: {str(e)}")
        else:
            with fd:
                self.rest_client.put(url, data=fd)
        return f

    def experiment_get_result(self, name: str, trial: Optional[str] = None) -> Any:
        """Get Experiment Result.

        Allows you to download the result of an experiment.

        Assumes that your current environment has the same modules loaded / installed
        as the environment which you submitted the experiment.

        Parameters
        ----------
        name: str
            The name of the experiment.
        trial: Optional[str]
            The name of the trial. Defaults to the last trial in the experiment.

        Returns
        -------
        Any
            The result of the experiment.
            This is the value that you returned from your experiment function.

        Examples
        --------
        >>> import strangeworks as sw
        >>> sw.authenticate(...)
        >>> sw.experiment_get_result("heavy_computation", "siete_ocho_9")
        42
        >>> sw.experiment_get_result("heavy_computation")
        42

        Raises
        ------
        StrangeworksError
            If we are unable to download the result.
        StrangeworksError
            If we are unable to get one trial from the experiment.
        StrangeworksError
            If the trial is not in a COMPLETED state.
        StrangeworksError
            If we are unable to get the one result file from the trial.
        """
        t = [trial] if trial else 1
        exp = self.experiment_download(name, t, "result.pickle", False)
        if len(exp.trials) != 1:
            raise StrangeworksError(
                f"we are unable to grab the {t} trial from the experiment"
            )

        exp_trial = exp.trials[0]
        if not exp_trial.status or (exp_trial.status != "COMPLETED"):
            raise StrangeworksError(
                f"Trial {exp_trial.name} is not in a COMPLETED state. "
                f"Current state is {exp_trial.status}."
            )
        if len(exp_trial.files) != 1:
            raise StrangeworksError(
                f"Trial {exp_trial.name} does not have exactly one file. "
                f"Current number of files is {len(exp_trial.files)}."
            )

        return exp_trial.files[0].content
