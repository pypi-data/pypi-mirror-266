from ..exceptions import SdkException
from ..sdk import BaseCraftAiSdk
from ..utils import log_func_result


@log_func_result("Pipeline creation")
def create_pipeline(sdk: BaseCraftAiSdk, pipeline_name, step_name):
    """Create a pipeline containing a single step.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline to be created.
        step_name (:obj:`str`): Name of the step to be included in the pipeline.
            Note that the step should have the status ``"Ready"`` to create the
            pipeline.

    Returns:
        :obj:`dict`: Created pipeline represented as :obj:`dict` with the following
        keys:

        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
        * ``"created_at"`` (:obj:`str`): Pipeline date of creation.
        * ``"steps"`` (:obj:`list[str]`): List of step names included in the
          pipeline.
        * ``"open_inputs"`` (:obj:`list` of :obj:`dict`): List of open inputs
          of the pipeline. Each open input is represented as a :obj:`dict` with the
          following keys:

          * ``"input_name"`` (:obj:`str`): Name of the open input.
          * ``"step_name"`` (:obj:`str`): Name of the step that provides the open
            input.
          * ``"data_type"`` (:obj:`str`): Data type of the open input.
          * ``"description"`` (:obj:`str`): Description of the open input.
          * ``"default_value"`` (:obj:`str`): Default value of the open input.
          * ``"is_required"`` (:obj:`bool`): Whether the open input is required or
            not.

        * ``"open_outputs"`` (:obj:`list` of :obj:`dict`): List of open outputs
          of the pipeline. Each open output is represented as a :obj:`dict` with the
          following keys:

          * ``"output_name"`` (:obj:`str`): Name of the open output.
          * ``"step_name"`` (:obj:`str`): Name of the step that provides the open
            output.
          * ``"data_type"`` (:obj:`str`): Data type of the open output.
          * ``"description"`` (:obj:`str`): Description of the open output.
    """
    url = f"{sdk.base_environment_api_url}/pipelines"
    body = {
        "pipeline_name": pipeline_name,
        "step_names": [step_name],
    }

    resp = sdk._post(url, json=body)
    return resp


def get_pipeline(sdk: BaseCraftAiSdk, pipeline_name):
    """Get a single pipeline if it exists.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline to get.

    Returns:
        None if the pipeline does not exist, otherwise pipeline information, with
        the following keys:

        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
        * ``"created_at"`` (:obj:`str`): Pipeline date of creation.
        * ``"created_by"`` (:obj:`str`): ID of the user who created the deployment.
        * ``"last_execution_id"`` (:obj:`str`): ID of the last execution of the
          pipeline.
        * ``"steps"`` (:obj:`list[str]`): List of step names included in the
          pipeline.
        * ``"open_inputs"`` (:obj:`list` of :obj:`dict`): List of open inputs
          of the pipeline. Each open input is represented as a :obj:`dict` with the
          following keys:

          * ``"input_name"`` (:obj:`str`): Name of the open input.
          * ``"step_name"`` (:obj:`str`): Name of the step that provides the open
            input.
          * ``"data_type"`` (:obj:`str`): Data type of the open input.
          * ``"description"`` (:obj:`str`): Description of the open input.
          * ``"default_value"`` (:obj:`str`): Default value of the open input.
          * ``"is_required"`` (:obj:`bool`): Whether the open input is required or
            not.

        * ``"open_outputs"`` (:obj:`list` of :obj:`dict`): List of open outputs
          of the pipeline. Each open output is represented as a :obj:`dict` with the
          following keys:

          * ``"output_name"`` (:obj:`str`): Name of the open output.
          * ``"step_name"`` (:obj:`str`): Name of the step that provides the open
            output.
          * ``"data_type"`` (:obj:`str`): Data type of the open output.
          * ``"description"`` (:obj:`str`): Description of the open output.
    """
    try:
        url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}"
        pipeline = sdk._get(url)
    except SdkException as error:
        if error.status_code == 404:
            return None
        raise error

    latest_execution = sdk._get(
        f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}/executions/latest"
    )
    pipeline["last_execution_id"] = (
        latest_execution.get("execution_id", None)
        if latest_execution is not None
        else None
    )
    return pipeline


def list_pipelines(sdk: BaseCraftAiSdk):
    """Get the list of all pipelines.

    Returns:
        :obj:`list` of :obj:`dict`: List of pipelines represented as :obj:`dict`
        with the following keys:

        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
        * ``"created_at"`` (:obj:`str`): Pipeline date of creation.
    """
    url = f"{sdk.base_environment_api_url}/pipelines"

    return sdk._get(url)


@log_func_result("Pipeline deletion")
def delete_pipeline(
    sdk: BaseCraftAiSdk, pipeline_name, force_deployments_deletion=False
):
    """Delete a pipeline identified by its name.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline.
        force_deployments_deletion (:obj:`bool`, optional): if True the associated
            endpoints will be deleted too. Defaults to False.

    Returns:
        :obj:`dict`: The deleted pipeline and its associated deleted deployments
        represented as a :obj:`dict` with the following keys:

            * ``"pipeline"`` (:obj:`dict`): Deleted pipeline represented as
              :obj:`dict` with the following keys:

              * ``"name"`` (:obj:`str`): Name of the deleted pipeline.

            * ``"deployments"`` (:obj:`list`): List of deleted deployments
              represented as :obj:`dict` with the following keys:

              * ``"name"`` (:obj:`str`): Name of the deleted deployments.
              * ``"execution_rule"`` (:obj:`str`): Execution rule of the deleted
                deployments.
    """
    url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}"
    params = {
        "force_deployments_deletion": force_deployments_deletion,
    }
    return sdk._delete(url, params=params)
