import concurrent.futures
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Union

from strangeworks_core.batch.utils import submit
from strangeworks_core.platform.gql import API, Operation
from strangeworks_core.types.func import Func

from strangeworks.core.client.file import File
from strangeworks.core.client.jobs import Job
from strangeworks.core.errors.error import StrangeworksError


@dataclass
class ExperimentConfiguration:
    """
    Configuration for the experiment.

    Attributes
    ----------
    experiment_name: Optional[str], optional
        Name of the experiment, by default None.
        If None, the experiment name will be the name of the function.
    trial_name : Optional[str], optional
        Name of the trial, by default None
        If None, the trial name will be the name of the function.
    requirements_path : Optional[str], optional
        Path to a requirements.txt file, by default None
        The requirements.txt defines the dependencies required to run
        the experiment.
    local_run : bool, optional
        If True, run the experiment locally, by default False
        This allows you to test the experiment locally before submitting.
    """

    experiment_name: Optional[str] = None
    trial_name: Optional[str] = None
    requirements_path: Optional[str] = None
    local_run: bool = False


@dataclass
class ExperimentInput:
    """
    Input to the experiment.

    Attributes
    ----------
    experiment_name : str
        Name of the experiment.
    trial_name : str
        Name of the trial.
    fargs : tuple[any], optional
        Positional arguments to the function, by default ()
    fkwargs : dict[str, any], optional
        Keyword arguments to the function, by default {}
    """

    experiment_name: str
    trial_name: str
    fargs: tuple[any] = ()
    fkwargs: dict[str, any] = field(default_factory=dict)


@dataclass
class TrialSubmission:
    """
    Output of the experiment.

    Attributes
    ----------
    success : bool
        Whether the experiment was successfully submitted.
    message : str
        Message about the experiment.
    output : Optional[any], optional
        Output of the experiment, by default None
        This output is only available if the experiment was run locally.
    """

    success: bool
    message: str
    output: Optional[any] = None


def run(
    api: API,
    func: Callable[..., any],
    input: Union[ExperimentInput, list[ExperimentInput]],
    cfg: ExperimentConfiguration = ExperimentConfiguration(),
    **kwargs,
) -> dict[str, TrialSubmission]:
    """
    Run a function as a batch job on the Strangeworks platform.

    Parameters
    ----------
    api : API
        Strangeworks API object.
    func : Callable[..., any]
        The function to run.
    input : Union[ExperimentInput, list[ExperimentInput]]
        The input to the function. If a list is provided, each element will be
        run as a separate batch job.
    cfg : ExperimentConfiguration, optional
        Configuration for the experiment, by default ExperimentConfiguration()

    Returns
    -------
    dict[str, TrialSubmission]
        A dictionary of trial names to TrialSubmission objects.

    """
    if not isinstance(input, list):
        input = [input]

    if cfg.local_run:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    func, *inp.fargs, **inp.fkwargs
                ): f"trial_{inp.trial_name}"
                for i, inp in enumerate(input)
            }

            msg = "locally executed. result from function call are in output field."
            return {
                futures[future]: TrialSubmission(
                    success=True,
                    message=msg,
                    output=future.result(),
                )
                for future in concurrent.futures.as_completed(futures)
            }

    init_batch_job = Operation(
        query="""
        mutation batchJobInitiateCreate(
            $init: InitiateBatchJobCreateInput!
            $experiment_name: String!
            $trial_name: String
        ){
            batchJobInitiateCreate(
                input: {
                    initiate: $init
                    experimentName: $experiment_name
                    trialName: $trial_name
                }
            ) {
                batchJobSlug
                signedURL
            }
        }
        """
    )

    out = {}
    for inp in input:
        try:
            submit(
                api,
                init_batch_job,
                Func(func, inp.fargs, inp.fkwargs, cfg.requirements_path),
                experiment_name=inp.experiment_name,
                trial_name=inp.trial_name,
            )
        except Exception as e:
            # todo: for now, let's not enumerate the trials
            # it's confusing to the user as there might be more trials in the portal
            # at the moment,
            #   this won't be a problem as we are not giving them access to run
            # multiple trials at once
            out[f"trial_{inp.trial_name}"] = TrialSubmission(
                success=False,
                message="failed to submit. exception in output field.",
                output=e,
            )
        else:
            # todo: for now, let's not enumerate the trials
            # it's confusing to the user as there might be more trials in the portal
            # at the moment,
            #   this won't be a problem as we are not giving them access to run
            # multiple trials at once
            out[f"trial_{inp.trial_name}"] = TrialSubmission(
                success=True, message="successfully submitted"
            )

    return out


@dataclass
class Trial:
    """
    An experiment trial.

    Attributes
    ----------
    name : str
        Name of the trial.
    status: Optional[str]
        Trial status.
    files : list[File]
        List of files associated with the trial.
    jobs : Optional[list[Job]], optional
        List of jobs associated with the trial, by default None

    """

    name: str
    status: Optional[str]
    files: list[File]
    jobs: Optional[list[Job]] = None


@dataclass
class Experiment:
    """
    An experiment.

    Attributes
    ----------
    name : str
        Name of the experiment.
    trials : list[Trial]
        List of trials associated with the experiment.

    """

    name: str
    trials: list[Trial]


def get_experiment(
    api: API,
    name: str,
    trials: Union[int, list[str]],
    files: Union[str, list[str]],
    jobs: Union[bool, list[str]],
) -> Experiment:
    """
    get_experiment returns an experiment object.

    Parameters
    ----------
    api : API
        Strangeworks API object.
    name : str
        Name of the experiment.
    trials : Union[int, list[str]]
        Number of trials to return or a list of trial names.
    files : Union[str, list[str]]
        Name of the file or a list of file names.
    jobs : Union[bool, list[str]]
        If True, return jobs associated with the trials. If a list of job slugs is
        provided, return only those jobs.

    Returns
    -------
    Experiment
        An experiment object.
        Filled with the trials requested.
        Each trial will have the files requested (if the particular trial has them).
        Each trial will have the jobs requested (if the particular trial has them).
    """

    if isinstance(files, str):
        files = [files]

    vv = {
        "experiment_name": name,
        "file_names": files,
    }

    if isinstance(trials, int):
        query = _last_n_trials_query(jobs)
        vv["n"] = trials
    elif isinstance(trials, list):
        query = _trials_query(jobs)
        vv["trial_list"] = trials
    else:
        raise TypeError("trials must be an int or a list of strings")

    if isinstance(jobs, list):
        vv["job_slugs"] = jobs

    op = Operation(query=query)

    out = api.execute(op, **vv)

    workspace_experiment = out["workspace"]["experiment"]
    experiment_trials = workspace_experiment["trials"]
    ts = []
    for trial in experiment_trials:
        sw_files = trial.get("files")
        js = trial.get("jobs", None)
        ts.append(
            Trial(
                name=trial.get("name"),
                status=trial.get("status"),
                files=[File.from_dict(f) for f in sw_files],
                jobs=[Job.from_dict(j) for j in js] if js else None,
            )
        )

    return Experiment(workspace_experiment["name"], ts)


def upload_exp_file(
    api: API,
    experiment_name: str,
    trial_name: str,
    path: str,
    is_public: bool = False,
    name: Optional[str] = None,
    json_schema: Optional[str] = None,
    label: Optional[str] = None,
    content_type: Optional[str] = None,
) -> tuple[File, str]:
    """
    upload_exp_file uploads a file to an experiment.

    Parameters
    ----------
    api : API
        Strangeworks API object.
    experiment_name : str
        Name of the experiment.
    trial_name : str
        Name of the trial.
    path : str
        Path to the file.
    is_public : bool, optional
        Whether the file is public, by default False
    name : Optional[str], optional
        Name of the file, by default None
    json_schema : Optional[str], optional
        JSON schema of the file, by default None
    label : Optional[str], optional
        Label of the file, by default None
    content_type : Optional[str], optional
        Content type of the file, by default None

    Returns
    -------
    tuple[File, str]
        A tuple of the File object and the signed URL.
        The signed URL is where the file can be uploaded.
    """

    p = Path(path)
    stats = p.stat()
    meta_size = stats.st_size
    meta_create_date = datetime.fromtimestamp(
        stats.st_ctime, tz=timezone.utc
    ).isoformat()
    meta_modified_date = datetime.fromtimestamp(
        stats.st_mtime, tz=timezone.utc
    ).isoformat()
    meta_type = p.suffix[1:]  # suffix without the .
    if meta_type == "" and name:
        # maybe the user provided file name has the correct extension
        _, ext = os.path.splitext(name)
        meta_type = ext[1:]  # again, without the .
    file_name = name or p.name
    ct = content_type or "application/x-www-form-urlencoded"
    upload_file_query = _upload_file_to_experiment_query()
    op = Operation(query=upload_file_query)
    res = api.execute(
        op=op,
        experiment_name=experiment_name,
        trial_name=trial_name,
        file_name=file_name,
        content_type=ct,
        is_public=is_public,
        json_schema=json_schema,
        label=label,
        meta_file_create_date=meta_create_date,
        meta_file_modified_date=meta_modified_date,
        meta_file_size=meta_size,
        meta_file_type=meta_type,
    ).get("experimentUploadFile")
    if not res:
        raise StrangeworksError(message="unable to get valid response from platform")

    if "error" in res:
        raise StrangeworksError(message=res.get("error"))

    f = res.get("file")
    url = res.get("signedURL")
    if not f or not url:
        raise StrangeworksError(
            message="unable to obtain file details or a place to upload the file"
        )
    return (File.from_dict(f), url)


def _last_n_trials_query(include_jobs: Union[bool, list[str]]) -> str:
    files_fragment = _trial_files_fragment()
    query_vars = "$experiment_name: String!, $n: Int, $file_names: [String!]!"

    jobs_frag_def, jobs_frag, additional_query_vars = _get_job_fragment(include_jobs)
    if additional_query_vars:
        query_vars += additional_query_vars

    return f"""

    query experiment_trials({query_vars}) {{
        workspace {{
            experiment(name: $experiment_name) {{
                name
                trials(n: $n) {{
                    name
                    status
                    ...trialFiles
                    {jobs_frag}
                }}
            }}
        }}
    }}

    {files_fragment}

    {jobs_frag_def}

    """


def _trials_query(include_jobs: Union[bool, list[str]]) -> str:
    files_fragment = _trial_files_fragment()
    query_vars = (
        "$experiment_name: String!, $trial_list: [String!], $file_names: [String!]!"
    )

    jobs_frag_def, jobs_frag, additional_query_vars = _get_job_fragment(include_jobs)
    if additional_query_vars:
        query_vars += additional_query_vars

    return f"""

    query experiment_trials({query_vars}) {{
        workspace {{
            experiment(name: $experiment_name) {{
                name
                trials(names: $trial_list) {{
                    name
                    status
                    ...trialFiles
                    {jobs_frag}
                }}
            }}
        }}
    }}

    {files_fragment}

    {jobs_frag_def}

    """


def _get_job_fragment(
    include_jobs: Union[bool, list[str]]
) -> tuple[str, str, Optional[str]]:
    if isinstance(include_jobs, list):
        jobs_frag_def = _trial_jobs_with_slugs_fragment()
        jobs_frag = "...trialJobsWithSlugs"
        query_vars = ", $job_slugs: [String!]"
    elif isinstance(include_jobs, bool) and include_jobs:
        jobs_frag_def = _trail_jobs_fragment()
        jobs_frag = "...trialJobs"
        query_vars = None
    else:
        jobs_frag_def = ""
        jobs_frag = ""
        query_vars = None

    return (jobs_frag_def, jobs_frag, query_vars)


def _trial_files_fragment() -> str:
    return """

    fragment trialFiles on Trial {
        files(names: $file_names) {
            fileName
            slug
            url
            dataSchemaSlug
        }
    }

    """


def _trial_jobs_with_slugs_fragment() -> str:
    exp_job_frag = _experiment_job_fragment()
    return f"""

    fragment trialJobsWithSlugs on Trial {{
        jobs(slugs: $job_slugs) {{
            ...experimentJobFragment
        }}
    }}

    {exp_job_frag}

    """


def _trail_jobs_fragment() -> str:
    exp_job_frag = _experiment_job_fragment()
    return f"""

    fragment trialJobs on Trial {{
        jobs {{
            ...experimentJobFragment
        }}
    }}

    {exp_job_frag}

    """


def _experiment_job_fragment() -> str:
    return """

    fragment experimentJobFragment on Job {
        slug
        externalIdentifier
        status
        files {
            file {
                slug
                fileName
                url
            }
        }
    }

    """


def _upload_file_to_experiment_query() -> str:
    return """
    mutation experimentUploadFile(
        $experiment_name: String!
        $trial_name: String!
        $file_name: String!
        $content_type: String!
        $is_public: Boolean! = false
        $json_schema: String
        $label: String
        $meta_file_create_date: Time
        $meta_file_modified_date: Time
        $meta_file_size: Int
        $meta_file_type: String
    ) {
    experimentUploadFile(
        input: {
            experimentName: $experiment_name
            trialName: $trial_name
            fileName: $file_name
            contentType: $content_type
            isPublic: $is_public
            jsonSchema: $json_schema
            label: $label
            metaFileCreateDate: $meta_file_create_date
            metaFileModifiedDate: $meta_file_modified_date
            metaFileSize: $meta_file_size
            metaFileType: $meta_file_type
        }
    ) {
        signedURL
        file {
            id
            slug
            label
            fileName
            url
            metaFileType
            metaDateCreated
            metaDateModified
            metaSizeBytes
            dataSchemaSlug
            dateCreated
            dateUpdated
        }
    }
    }
    """
