import copy
import json
import tempfile
import time
from typing import Any, List, Optional

import strangeworks as sw
import yaml
from strangeworks.core.client.backends import Backend
from strangeworks.core.client.jobs import Job
from strangeworks.core.client.resource import Resource
from strangeworks.core.errors.error import StrangeworksError
from strangeworks_core.types.job import Status
from strangeworks_optimization_models.parameter_models import (
    AquilaParameterModel,
    DwaveLeapParameterModel,
    DwaveSamplerParameterModel,
    FujitsuParameterModel,
    GurobiParameterModel,
    HitachiParameterModel,
    JijLeapHybridCQMParameterModel,
    JijSAParameterModel,
    JijSQAParameterModel,
    NECParameterModel,
    QuantagoniaParameterModel,
    ToshibaParameterModel,
)
from strangeworks_optimization_models.problem_models import (
    RemoteFile,
    StrangeworksModel,
    StrangeworksModelFactory,
)
from strangeworks_optimization_models.solution_models import (
    StrangeworksSolution,
    StrangeworksSolutionFactory,
)
from strangeworks_optimization_models.solver_models import (
    StrangeworksSolver,
    StrangeworksSolverFactory,
)
from strangeworks_optimization_models.strangeworks_models import (
    StrangeworksOptimizationJob,
    StrangeworksOptimizationModel,
    StrangeworksOptimizationSolution,
    StrangeworksOptimizationSolver,
)


def _get_product_slug(label_name: str) -> str:
    if label_name in ["jij"]:
        return "jijzept"
    elif label_name in ["azure"]:
        return "azure-quantum"
    elif label_name in ["braket"]:
        return "amazon-braket"
    return label_name


class StrangeworksOptimizer:
    """Strangeworks optimization controller."""

    model: StrangeworksModel | None = None
    solver: StrangeworksSolver | None = None
    solution: StrangeworksSolution | None = None
    job: Job | None = None
    tags: List[str] | None = None

    def __init__(
        self,
        model: Any | None = None,
        solver: Any | None = None,
        options: (
            AquilaParameterModel
            | DwaveLeapParameterModel
            | DwaveSamplerParameterModel
            | FujitsuParameterModel
            | GurobiParameterModel
            | HitachiParameterModel
            | JijLeapHybridCQMParameterModel
            | JijSAParameterModel
            | JijSQAParameterModel
            | NECParameterModel
            | QuantagoniaParameterModel
            | ToshibaParameterModel
            | None
        ) = None,
        solution: Any | None = None,
        resource_slug: str | None = None,
        tags: List[str] | None = None,
    ) -> None:
        """Initialize the StrangeworksOptimizer.

        If a resource slug is provided, confirm it exists and set is as resource for
        its product. If there is no resource associated with the given slug, raise
        error.

        If no resource slug is provided, try retrieving a resource slug for the
        optimization service. If the user does not have a resource configured, raise
        error.

        Parameters
        ----------
        model: Any | None
            The model that will be used by the optimizer.
        solver: Any | None
            The solver to use for optimization.
        options: dict | None
            Options to pass to the optimizer.
        solution: Any | None
            Solution to be used.
        resource_slug: str | None
            Allows user to specify a specific resource to use.
        tags: List[str] | None
            List of user specified tags that will be associated with the job.
        """
        self.model = StrangeworksModelFactory.from_model(model) if model else None

        if solver:
            self.solver = StrangeworksSolverFactory.from_solver(solver)
            self._init_solver()

        if tags:
            self.tags = tags
        else:
            self.tags = None

        self.options = options
        self.solution = StrangeworksSolutionFactory.from_solution(solution)

        if resource_slug:
            sw.set_resource_for_product(resource_slug=resource_slug, product_slug="optimization")
        self.resource: Resource = sw.get_resource_for_product("optimization")

    def _init_solver(self):
        if self.solver:
            product_slug = _get_product_slug(self.solver.provider)
            self.sub_rsc = sw.get_resource_for_product(product_slug)

            self.solver.strangeworks_parameters = {
                "sub_product_slug": self.sub_rsc.product.slug,
                "sub_resource_slug": self.sub_rsc.slug,
            }

    def run(self) -> Job | None:
        full_solver = self.solver.provider + "." + self.solver.solver
        if not self.check_parameter_model_compatability(self.solver.provider, full_solver, self.options):
            raise StrangeworksError(f"Parameter option {self.options} is not compatible with {full_solver}")

        solver = StrangeworksOptimizationSolver.from_solver(self.solver)

        if self.tags:
            for tag in self.tags:
                if len(tag) > 35:
                    raise StrangeworksError("Tag length cannot be greater than 35 characters")

            sw_params = json.loads(solver.strangeworks_parameters)
            sw_params["tags"] = self.tags
            solver.strangeworks_parameters = json.dumps(sw_params)

        if self.options:
            # Transform options class to dict and remove entries that are None
            options = copy.deepcopy(self.options.__dict__)
            for k, v in self.options.__dict__.items():
                if v is None:
                    options.pop(k)
        solver.solver_options = json.dumps(options) if self.options else json.dumps(None)

        strangeworks_optimization_job = StrangeworksOptimizationJob(
            model=StrangeworksOptimizationModel.from_model(self.model),
            solver=solver,
            solution=StrangeworksOptimizationSolution.from_solution(self.solution) if self.solution else None,
        )
        res = sw.execute(self.resource, payload=strangeworks_optimization_job.model_dump(), endpoint="run")

        job_slug = json.loads(res["solution"]["strangeworks_parameters"])["job_slug"]
        self.job = sw.jobs(slug=job_slug)[0]
        return self.job

    def run_batch(self, batch_file: str) -> dict[str, Job]:
        with open(batch_file) as stream:
            yam = yaml.safe_load(stream)

        tagbatch = yam["job_name"]

        # Make sure run names are unique. Becuase we are using the run names as keys for the returned dict
        if len(yam["runs"]) != len(set([job["run"] for job in yam["runs"]])):
            raise ValueError("Run names must be unique")

        sw_jobs = {}
        for job in yam["runs"]:
            tagjob = job["run"]
            problem_params = job["problem_parameters"]

            remote_model = RemoteFile(model_url=problem_params["model_url"], model_type=problem_params["model_type"])

            provider = problem_params["solver"].split(".", 1)[0]

            options = self.get_options(provider, problem_params["solver"], problem_params["solver_options"])

            optimizer = StrangeworksOptimizer(
                model=remote_model,
                solver=problem_params["solver"],
                options=options,
                resource_slug=self.resource.slug,
                tags=[tagbatch, tagjob],
            )

            sw_jobs[tagjob] = optimizer.run()

        return sw_jobs

    def check_parameter_model_compatability(self, provider: str, solver: str, parameter_model: Any) -> bool:
        if provider == "dwave":
            if (
                solver == "dwave.hybrid_binary_quadratic_model_version2p"
                or solver == "dwave.hybrid_constrained_quadratic_model_version1p"
                or solver == "dwave.hybrid_discrete_quadratic_model_version1p"
            ):
                return isinstance(parameter_model, DwaveLeapParameterModel)
            else:
                return isinstance(parameter_model, DwaveSamplerParameterModel)
        elif provider == "gurobi":
            return isinstance(parameter_model, GurobiParameterModel)
        elif provider == "quantagonia":
            return isinstance(parameter_model, QuantagoniaParameterModel)
        elif provider == "hitachi":
            return isinstance(parameter_model, HitachiParameterModel)
        elif provider == "toshiba" or provider == "toshiba-p3-16xl":
            return isinstance(parameter_model, ToshibaParameterModel)
        elif provider == "fujitsu":
            return isinstance(parameter_model, FujitsuParameterModel)
        elif provider == "nec":
            return isinstance(parameter_model, NECParameterModel)
        elif provider == "jij":
            if solver == "jij.SQA":
                return isinstance(parameter_model, JijSQAParameterModel)
            elif solver == "jij.SA":
                return isinstance(parameter_model, JijSAParameterModel)
            elif solver == "jij.LeapHybridCQM":
                return isinstance(parameter_model, JijLeapHybridCQMParameterModel)
            else:
                raise ValueError("Invalid solver")
        elif provider == "braket":
            return isinstance(parameter_model, AquilaParameterModel)
        else:
            raise StrangeworksError(
                f"Parameter model compatability check failed due to non-existent provider {provider}"
            )

    def get_options(
        self, provider: str, solver: str, solver_options: dict[str, Any]
    ) -> (
        AquilaParameterModel
        | DwaveLeapParameterModel
        | DwaveSamplerParameterModel
        | FujitsuParameterModel
        | GurobiParameterModel
        | HitachiParameterModel
        | JijLeapHybridCQMParameterModel
        | JijSAParameterModel
        | JijSQAParameterModel
        | NECParameterModel
        | QuantagoniaParameterModel
        | ToshibaParameterModel
    ):
        if provider == "dwave":
            if (
                solver == "dwave.hybrid_binary_quadratic_model_version2p"
                or solver == "dwave.hybrid_constrained_quadratic_model_version1p"
                or solver == "dwave.hybrid_discrete_quadratic_model_version1p"
            ):
                return DwaveLeapParameterModel(**solver_options)
            else:
                return DwaveSamplerParameterModel(**solver_options)
        elif provider == "gurobi":
            return GurobiParameterModel(**solver_options)
        elif provider == "quantagonia":
            return QuantagoniaParameterModel(**solver_options)
        elif provider == "hitachi":
            return HitachiParameterModel(**solver_options)
        elif provider == "toshiba":
            return ToshibaParameterModel(**solver_options)
        elif provider == "fujitsu":
            return FujitsuParameterModel(**solver_options)
        elif provider == "nec":
            return NECParameterModel(**solver_options)
        elif provider == "jij":
            if solver == "jij.SQA":
                return JijSQAParameterModel(**solver_options)
            elif solver == "jij.SA":
                return JijSAParameterModel(**solver_options)
            elif solver == "jij.LeapHybridCQM":
                return JijLeapHybridCQMParameterModel(**solver_options)
            else:
                raise ValueError("Invalid solver")
        elif provider == "aquila":
            return AquilaParameterModel(**solver_options)
        else:
            raise ValueError("Invalid provider")

    def results(self, sw_job_slug):
        endpoint = f"results/{sw_job_slug}"
        solution = sw.execute(self.resource, endpoint=endpoint)
        solution = StrangeworksOptimizationSolution(**solution)

        if solution.solution == "running":
            status = self.status(sw_job_slug)

            while not status.is_terminal_state:  # COMPLETED, CANCELLED, or FAILED
                time.sleep(10)
                status = self.status(sw_job_slug)

            if status == Status.COMPLETED:
                solution = sw.execute(self.resource, endpoint=endpoint)
                solution = StrangeworksOptimizationSolution(**solution)
            else:
                raise StrangeworksError(f"Cannot get results, Job status is {status.value}")

        return solution.deserialize()

    def status(self, sw_job_slug) -> Status:
        endpoint = f"status/{sw_job_slug}"
        resp = sw.execute(self.resource, endpoint=endpoint)
        return Status(resp)

    def jobs_by_tag(self, tags: List[str], andor: str = "AND"):
        """
        Return all of the jobs with the given tags

        Parameters
        ----------
        tags: List[str]
            List of tags to filter the jobs by.

        andor: str
            The logical operator to use for the tags. Can be either "AND" or "OR".

        """

        if andor == "AND":
            job_list = [sw.jobs(tags=t) for t in tags]
            slug_list = [[j.slug for j in jobset] for jobset in job_list]

            commonalities = set(slug_list[0])
            for ii in range(1, len(slug_list)):
                commonalities = commonalities - (commonalities - set(slug_list[ii]))

            return [sw.jobs(slug=sl) for sl in list(commonalities)]
        elif andor == "OR":
            return sw.jobs(tags=tags)
        else:
            raise ValueError("andor must be either 'AND' or 'OR'")

    def upload_model(self, model, filename: str | None = None, description: str | None = None) -> RemoteFile:
        """
        Uploads the model to Strangeworks and returns the slug of the uploaded file.

        Parameters
        ----------
        model: Any
            The model to be uploaded. This will be parsed into a StrangeworksOptimizationModel.
            To ensure that we support the type, and to make it easy to work with the model on the service side.

        To-Do:
        filename: str (optional)
            The filename to use for the uploaded file. If not provided, a random filename will be used. This will
            make it easier for users to understand what their workspace files are.
        description: str (optional)
            A description of the file to be uploaded. This will be used to help users understand what the file is
            for, and to help them understand what the file is for.

        """
        strangeworks_optimization_model = StrangeworksOptimizationModel.from_model(model=model or self.model)
        with tempfile.NamedTemporaryFile(mode="w+") as t:
            t.write(strangeworks_optimization_model.model_dump_json())
            t.flush()

            # To-DO: Add filename, description and info to the upload_file method
            # f = sw.upload_file(
            #     file_path=t.name,
            #     name=filename,
            #     description=description,
            #     info={"model_type": strangeworks_optimization_model.model_type},
            # )
            f = sw.upload_file(t.name)

        remote_file = RemoteFile(
            model_url=f.url,
            model_type=strangeworks_optimization_model.model_type,
            # model_type=f.info["model_type"],
            # filename=f.file_name,
            # description=f.description,
        )
        return remote_file

    # def get_workspace_files(self, file_slug: str | None = None) -> List[RemoteFile]:
    #     """
    #     Returns a list of all files in the workspace.

    #     if file_slug:
    #         then create RemoteFile object for that file
    #     else:
    #         list all files in workspace with names and descriptions.
    #     """
    #     pass

    def backends(self) -> Optional[Backend]:
        """List of optimization backends."""
        # get resources associated with this workspace
        resources = sw.resources()
        # if workspace has no resources, return an empty list.
        if not resources:
            return []
        # generate list of product slugs to use for filtering backends.
        product_slugs = [x.product.slug for x in resources]
        backends = sw.backends(
            product_slugs=product_slugs,
            backend_type_slugs=["optimization"],
        )

        return backends

    def download_input_file(self, sw_job_slug) -> StrangeworksOptimizationJob:
        # Returns the entire OptimizationJob object/payload
        # If the job has completed, the solution should also be included.

        sw_job = sw.jobs(slug=sw_job_slug)[0]

        for file in sw_job.files:
            if file.file_name == "OptimizationJob.json":
                return StrangeworksOptimizationJob(**sw.download_job_files([file.url])[0])

        raise StrangeworksError("OptimizationJob.json not found in job files")

    def download_input_model(self, sw_job_slug, download_remote=False):
        # Parses the OptimizationJob.json and returns the deserialized model
        # If download_remote is True, and the model is a RemoteFile type
        # then the model will be downloaded from the remote URL

        OptimizationJob = self.download_input_file(sw_job_slug)
        OptimizationModel = OptimizationJob.model.deserialize().model

        if isinstance(OptimizationModel, RemoteFile) and download_remote:
            return (
                StrangeworksOptimizationModel(**sw.download_job_files([OptimizationModel.model_url])[0])
                .deserialize()
                .model
            )

        return OptimizationModel

    @property
    def resource_slug(self):
        return self.resource.slug
