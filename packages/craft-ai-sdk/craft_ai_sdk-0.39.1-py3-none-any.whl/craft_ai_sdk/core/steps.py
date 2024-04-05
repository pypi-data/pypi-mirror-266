import time

from ..sdk import BaseCraftAiSdk
from ..io import Input, Output
from ..exceptions import SdkException
from ..utils import (
    log_func_result,
    log_action,
    map_container_config_step_parameter,
    remove_none_values,
)
from ..experimental_warnings import experimental, UPDATE_STEP_WARNING_MESSAGE
from ..constants import CREATION_REQUESTS_RETRY_INTERVAL


def _log_step_with_io(sdk: BaseCraftAiSdk, step):
    parameters = step.get("parameters", {})
    if not {"step_name", "inputs", "outputs"} <= parameters.keys():
        return

    inputs, outputs = parameters["inputs"], parameters["outputs"]
    msg = f'Step "{parameters["step_name"]}" created'
    if inputs:
        msg += "\n  Inputs: "
        for inp in inputs:
            required_str = ", required" if inp.get("is_required", False) else ""
            msg += f'\n    - {inp["name"]} ({inp["data_type"]}{required_str})'

    if outputs:
        msg += "\n  Outputs: "
        for output in outputs:
            msg += f'\n    - {output["name"]} ({output["data_type"]})'

    log_action(sdk, msg)


@log_func_result("Steps creation")
def create_step(
    sdk: BaseCraftAiSdk,
    step_name,
    function_path=None,
    function_name=None,
    description=None,
    container_config=None,
    inputs=None,
    outputs=None,
    timeout_s=3 * 60,
):
    """Create pipeline step from a function located on a remote repository.

    Use :obj:`STEP_PARAMETER` to explicitly set a value to null or fall back on
    project information.
    You can also use :obj:`container_config.included_folders` to specify the files and
    folders required for the step execution. This is useful if your repository
    contains large files that are not required for the step execution, such as
    documentation or test files. Indeed there is a maximum limit of 5MB for the
    total size of the content specified with :obj:`included_folders`.

    Args:
        step_name (:obj:`str`): Step name.
        function_path (:obj:`str`, optional): Path to the file that contains the
            function. This parameter is required if parameter "dockerfile_path"
            is not specified.
        function_name (:obj:`str`, optional): Name of the function in that file.
            This parameter is required if parameter "dockerfile_path" is not
            specified.
        description (:obj:`str`, optional): Description. Defaults to None.
        container_config (:obj:`dict[str, str]`, optional): Some step configuration,
            with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the step.
              Defaults to falling back on project information. The accepted formats
              are "python:3.X-slim", where "3.X" is a supported version of Python,
              and "python-cuda:3.X-Y.Z" for GPU environments, where "Y.Z" is a
              supported version of CUDA. The list of supported versions is available
              on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
              Defaults to falling back on project information.
            * ``"repository_branch"`` (:obj:`str`): Branch name. Defaults to falling
              back on project information.
            * ``"repository_deploy_key"`` (:obj:`str`): Private SSH key of the
              repository.
              Defaults to falling back on project information, can be set to null.
              The key should retain the header/footer beacon with : "BEGIN/END RSA
              PRIVATE KEY".
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file. Environment variables created through
              :func:`create_or_update_environment_variable` can be used
              in requirements.txt, as in ``"${ENV_VAR}"``.
              Defaults to falling back on project information, can be set to null.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and files
              in the repository required for the step execution.
              Defaults to falling back on project information, can be set to null.
              Total size of included_folders must be less than 5MB.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
              Defaults to falling back on project information, can be set to null.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile. This
              parameter should only be used as a last resort and for advanced use.
              When specified, the following parameters should be set to null:
              ``"function_path"``, ``"function_name"``, ``"language"``,
              ``"requirements_path"`` and ``"system_dependencies"``.

        inputs(`list` of instances of :class:`Input`): List of inputs. Each
            parameter of the step function should be specified as an instance of
            :class:`Input` via this parameter `inputs`.
            During the execution of the step, the value of the inputs would be
            passed as function arguments.
        outputs(`list` of instances of :class:`Output`): List of the step
            outputs. For the step to have outputs, the function should return a
            :obj:`dict` with the name of the output as keys and the value of the
            output as values. Each output should be specified as an instance
            of :class:`Output` via this parameter `outputs`.
        timeout_s (:obj:`int`): Maximum time (in seconds) to wait for the step to
            be created. 3min (180s) by default, and at least 2min (120s).

    Returns:
        :obj:`dict`: Created step represented as a :obj:`dict` with the following
        keys:

        * ``"parameters"`` (:obj:`dict`): Information used to create the step with
          the following keys:

          * ``"step_name"`` (:obj:`str`): Name of the step.
          * ``"function_path"`` (:obj:`str`): Path to the file that contains the
            function.
          * ``"function_name"`` (:obj:`str`): Name of the function in that file.
          * ``"repository_branch"`` (:obj:`str`): Branch name.
          * ``"description"`` (:obj:`str`): Description.
          * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of inputs represented
            as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Input name.
            * ``"data_type"`` (:obj:`str`): Input data type.
            * ``"is_required"`` (:obj:`bool`): Whether the input is required.
            * ``"default_value"`` (:obj:`str`): Input default value.

          * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of outputs
            represented as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Output name.
            * ``"data_type"`` (:obj:`str`): Output data type.
            * ``"description"`` (:obj:`str`): Output description.

          * ``"container_config"`` (:obj:`dict[str, str]`): Some step
            configuration, with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the step.
              The accepted formats are "python:3.X-slim", where "3.X" is a supported
              version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
              where "Y.Z" is a supported version of CUDA. The list of supported
              versions is available on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and
              files in the repository required for the step execution.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file.

        * ``"creation_info"`` (:obj:`dict`): Information about the step creation:

          * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
          * ``"updated_at"`` (:obj:`str`): The last update date in ISO format.
          * ``"commit_id"`` (:obj:`str`): The commit id on which the step was
            built.
          * ``"status"`` (:obj:`str`): The step status, always ``"Ready"`` when
            this function returns.
    """

    container_config = {} if container_config is None else container_config.copy()

    data = remove_none_values(
        {
            "step_name": step_name,
            "function_path": function_path,
            "function_name": function_name,
            "description": description,
            "container_config": map_container_config_step_parameter(container_config),
        }
    )

    if inputs is not None:
        if any([not isinstance(input_, Input) for input_ in inputs]):
            raise ValueError("'inputs' must be a list of instances of Input.")
        data["inputs"] = [inp.to_dict() for inp in inputs]

    if outputs is not None:
        if any([not isinstance(output_, Output) for output_ in outputs]):
            raise ValueError("'outputs' must be a list of instances of Output.")
        data["outputs"] = [output.to_dict() for output in outputs]

    if timeout_s < 120:
        raise ValueError("The timeout must be at least 2 minutes (120 seconds).")

    url = f"{sdk.base_environment_api_url}/steps"

    log_action(
        sdk,
        "Please wait while step is being created. This may take a while...",
    )

    start_time = sdk._get_time()
    created_step, response = sdk._post(url, json=data, get_response=True)

    if response.status_code != 206:
        _log_step_with_io(sdk, created_step)
        return created_step

    # The step is still building. Keep checking its status until it is ready
    elapsed_time = sdk._get_time() - start_time
    step_status = "Pending"
    while step_status != "Ready" and elapsed_time < timeout_s:
        time.sleep(CREATION_REQUESTS_RETRY_INTERVAL)
        created_step = get_step(sdk, step_name)

        if created_step is None:
            raise SdkException(
                f'The creation of step "{step_name}" has failed. Please try creating '
                "the step again. If this error keeps happening, please contact the "
                "support team.",
                name="UnexpectedError",
            )

        step_status = created_step.get("creation_info", {}).get("status", None)
        elapsed_time = sdk._get_time() - start_time

    if step_status != "Ready":
        raise SdkException(
            'The step was not ready in time. It is still being created but \
this function stopped trying. Please check its status with "get_step".',
            name="TimeoutException",
        )
    return created_step


def get_step(sdk: BaseCraftAiSdk, step_name):
    """Get a single step if it exists.

    Args:
        step_name (:obj:`str`): The name of the step to get.

    Returns:
        :obj:`dict`: ``None`` if the step does not exist; otherwise
        the step information, with the following keys:

        * ``"parameters"`` (:obj:`dict`): Information used to create the step with
          the following keys:

          * ``"step_name"`` (:obj:`str`): Name of the step.
          * ``"function_path"`` (:obj:`str`): Path to the file that contains the
            function.
          * ``"function_name"`` (:obj:`str`): Name of the function in that file.
          * ``"description"`` (:obj:`str`): Description.
          * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of inputs represented
            as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Input name.
            * ``"data_type"`` (:obj:`str`): Input data type.
            * ``"is_required"`` (:obj:`bool`): Whether the input is required.
            * ``"default_value"`` (:obj:`str`): Input default value.

          * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of outputs
            represented as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Output name.
            * ``"data_type"`` (:obj:`str`): Output data type.
            * ``"description"`` (:obj:`str`): Output description.

          * ``"container_config"`` (:obj:`dict[str, str]`): Some step
            configuration, with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the step.
              The accepted formats are "python:3.X-slim", where "3.X" is a supported
              version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
              where "Y.Z" is a supported version of CUDA. The list of supported
              versions is available on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
            * ``"repository_branch"`` (:obj:`str`): Branch name.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and
              files in the repository required for the step execution.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file.

        * ``"creation_info"`` (:obj:`dict`): Information about the step creation:

          * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
          * ``"updated_at"`` (:obj:`str`): The last update date in ISO format.
          * ``"commit_id"`` (:obj:`str`): The commit id on which the step was
            built.
          * ``"status"`` (:obj:`str`): either ``"Pending"`` or ``"Ready"``.
    """
    url = f"{sdk.base_environment_api_url}/steps/{step_name}"
    try:
        step = sdk._get(url)
    except SdkException as error:
        if error.status_code == 404:
            log_action(
                sdk,
                "If you are waiting for the step to be created, its creation "
                "has failed. Please try creating the step again. "
                "If this error keeps happening, please contact the support team.",
            )
            return None
        raise error
    return step


def list_steps(sdk: BaseCraftAiSdk):
    """Get the list of all steps.

    Returns:
        :obj:`list` of :obj:`dict`: List of steps represented as :obj:`dict` with
        the following keys:

        * ``"step_name"`` (:obj:`str`): Name of the step.
        * ``"status"`` (:obj:`str`): either ``"Pending"`` or ``"Ready"``.
        * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
        * ``"updated_at"`` (:obj:`str`): The last update date in ISO format.
        * ``"repository_branch"`` (:obj:`str`): The branch of the
          repository where the step was built.
        * ``"repository_url"`` (:obj:`str`): The url of the repository
          where the step was built.
        * ``"commit_id"`` (:obj:`str`): The commit id on which the step was
          built.
    """
    url = f"{sdk.base_environment_api_url}/steps"

    return sdk._get(url)


@experimental(UPDATE_STEP_WARNING_MESSAGE)
@log_func_result("Step update")
def update_step(
    sdk: BaseCraftAiSdk,
    step_name,
    function_path=None,
    function_name=None,
    description=None,
    container_config=None,
):
    """Update a pipeline step from a source code located on a remote repository.

    The current step configuration will be **replaced** by the provided options.
    Use :obj:`STEP_PARAMETER` to explicitly set a value to null or fall back on
    project information.

    Args:
        step_name (:obj:`str`): Name of the step to update.
        function_path (:obj:`str`, optional): Path to the file that contains the
            function. This parameter is required if parameter "dockerfile_path"
            is not specified.
        function_name (:obj:`str`, optional): Name of the function in that file.
            This parameter is required if parameter "dockerfile_path" is not
            specified.
        repository_branch (:obj:`str`, optional): Branch name. Defaults to falling
            back on project information.
        description (:obj:`str`, optional): Description. Defaults to None.
        container_config (:obj:`dict[str, str]`, optional): Some step configuration,
            with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the step.
              Defaults to falling back on project information. The accepted formats
              are "python:3.X-slim", where "3.X" is a supported version of Python,
              and "python-cuda:3.X-Y.Z" for GPU environments, where "Y.Z" is a
              supported version of CUDA. The list of supported versions is available
              on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
              Defaults to falling back on project information.
            * ``"repository_deploy_key"`` (:obj:`str`): Private SSH key of the
              repository.
              Defaults to falling back on project information, can be set to null.
              The key should retain the header/footer beacon with : "BEGIN/END RSA
              PRIVATE KEY".
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file. Environment variables created through
              :func:`create_or_update_environment_variable` can be used
              in requirements.txt, as in ``"${ENV_VAR}"``.
              Defaults to falling back on project information, can be set to null.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and files
              in the repository required for the step execution.
              Defaults to falling back on project information, can be set to null.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
              Defaults to falling back on project information, can be set to null.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile. This
              parameter should only be used as a last resort and for advanced use.
              When specified, the following parameters should be set to null:
              ``"function_path"``, ``"function_name"``, ``"language"``,
              ``"requirements_path"`` and ``"system_dependencies"``.

    Returns:
        :obj:`dict`: The updated step represented as a :obj:`dict` with
        the following keys:

        * ``"parameters"`` (:obj:`dict`): Information used to create the step with
          the following keys:

          * ``"step_name"`` (:obj:`str`): Name of the step.
          * ``"function_path"`` (:obj:`str`): Path to the file that contains the
            function.
          * ``"function_name"`` (:obj:`str`): Name of the function in that file.
          * ``"description"`` (:obj:`str`): Description.
          * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of inputs represented
            as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Input name.
            * ``"data_type"`` (:obj:`str`): Input data type.
            * ``"is_required"`` (:obj:`bool`): Whether the input is required.
            * ``"default_value"`` (:obj:`str`): Input default value.

          * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of outputs
            represented as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Output name.
            * ``"data_type"`` (:obj:`str`): Output data type.
            * ``"description"`` (:obj:`str`): Output description.

          * ``"container_config"`` (:obj:`dict[str, str]`): Some step
            configuration, with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the step.
              The accepted formats are "python:3.X-slim", where "3.X" is a supported
              version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
              where "Y.Z" is a supported version of CUDA. The list of supported
              versions is available on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
            * ``"repository_branch"`` (:obj:`str`): Branch name.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and
              files in the repository required for the step execution.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file.

        * ``"creation_info"`` (:obj:`dict`): Information about the step creation:

          * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
          * ``"updated_at"`` (:obj:`str`): The last update date in ISO format.
          * ``"commit_id"`` (:obj:`str`): The commit id on which the step was
            built.
          * ``"status"`` (:obj:`str`): either ``"Pending"`` or ``"Ready"``.

    """

    url = f"{sdk.base_environment_api_url}/steps/{step_name}"

    container_config = {} if container_config is None else container_config.copy()
    data = remove_none_values(
        {
            "function_path": function_path,
            "function_name": function_name,
            "description": description,
            "container_config": map_container_config_step_parameter(container_config),
        }
    )

    log_action(
        sdk,
        "Please wait while step is being updated. This may take a while...",
    )
    return sdk._put(url, json=data)


@log_func_result("Step deletion")
def delete_step(sdk: BaseCraftAiSdk, step_name, force_dependents_deletion=False):
    """Delete one step.

    Args:
        step_name (:obj:`str`): Name of the step to delete
            as defined in the ``config.yaml`` configuration file.
        force_dependents_deletion (:obj:`bool`, optional): if True the associated
            step's dependencies will be deleted too (pipeline, pipeline executions,
            deployments). Defaults to False.

    Returns:
        :obj:`dict[str, str]`: The deleted step represented as a :obj:`dict` with
        the following keys:

        * ``"step_name"`` (:obj:`str`): Name of the step.
    """
    url = f"{sdk.base_environment_api_url}/steps/{step_name}"
    params = {
        "force_dependents_deletion": force_dependents_deletion,
    }
    return sdk._delete(url, params=params)
