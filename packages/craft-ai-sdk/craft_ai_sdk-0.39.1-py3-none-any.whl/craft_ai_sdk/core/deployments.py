import time

from ..constants import (
    DEPLOYMENT_EXECUTION_RULES,
    DEPLOYMENT_MODES,
    DEPLOYMENT_UPDATE_STATUS,
    CREATION_REQUESTS_RETRY_INTERVAL,
)
from ..io import InputSource, OutputDestination
from ..sdk import BaseCraftAiSdk
from ..exceptions import SdkException
from ..utils import (
    _datetime_to_timestamp_in_ms,
    log_func_result,
    log_action,
)


@log_func_result("Deployment creation")
def create_deployment(
    sdk: BaseCraftAiSdk,
    pipeline_name,
    deployment_name,
    execution_rule,
    deployment_mode=DEPLOYMENT_MODES.ELASTIC,
    schedule=None,
    inputs_mapping=None,
    outputs_mapping=None,
    description=None,
    timeout_s=3 * 60,
):
    """Create a custom deployment associated to a given pipeline.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline.
        deployment_name (:obj:`str`): Name of the deployment.
        execution_rule(:obj:`str`): Execution rule of the deployment. Must
            be "endpoint" or "periodic". For convenience, members of the enumeration
            :class:`DEPLOYMENT_EXECUTION_RULES` could be used too.
        deployment_mode (:obj:`str`): Mode of the deployment.
            Can be "elastic" or "low_latency". Defaults to "elastic". For convenience,
            members of the enumeration :class:`DEPLOYMENT_MODES` could be used too.
        schedule (:obj:`str`, optional): Schedule of the deployment. Only
            required if ``execution_rule`` is "periodic". Must be a valid
            `cron expression <https://www.npmjs.com/package/croner>`.
            The deployment will be executed periodically according to this schedule.
            The schedule must follow this format:
            ``<minute> <hour> <day of month> <month> <day of week>``.
            Note that the schedule is in UTC time zone.
            '*' means all possible values.
            Here are some examples:

                * ``"0 0 * * *"`` will execute the deployment every day at
                  midnight.
                * ``"0 0 5 * *"`` will execute the deployment every 5th day of
                  the month at midnight.

        inputs_mapping(:obj:`list` of instances of :class:`InputSource`):
            List of input mappings, to map pipeline inputs to different
            sources (such as constant values, endpoint inputs, or environment
            variables). See :class:`InputSource` for more details.
            For endpoint rules, if an input of the step in the pipeline is not
            explicitly mapped, it will be automatically mapped to an endpoint
            input with the same name.
            For periodic rules, all inputs of the step in the pipeline must be
            explicitly mapped.
        outputs_mapping(:obj:`list` of instances of :class:`OutputDestination`):
            List of output mappings, to map pipeline outputs to different
            destinations. See :class:`OutputDestination` for more details.
            For endpoint rules, if an output of the step in the pipeline is not
            explicitly mapped, it will be automatically mapped to an endpoint
            output with the same name.
            For periodic rules, all outputs of the step in the pipeline must be
            explicitly mapped.
        description (:obj:`str`, optional): Description of the deployment.
        timeout_s (:obj:`int`): Maximum time (in seconds) to wait for the deployment to
            be ready. 3min (180s) by default, and at least 2min (120s).

    Returns:
        :obj:`dict[str, str]`: Created deployment represented as a dict with the
        following keys:

        * ``"name"`` (:obj:`str`): Name of the deployment.
        * ``"endpoint_token"`` (:obj:`str`): Token of the endpoint used to
          trigger the deployment. Note that this token is only returned if
          ``execution_rule`` is "endpoint".
        * ``"schedule"`` (:obj:`str`): Schedule of the deployment. Note that
          this schedule is only returned if ``execution_rule`` is "periodic".
        * ``"human_readable_schedule"`` (:obj:`str`): Human readable schedule
          of the deployment. Note that this schedule is only returned if
          ``execution_rule`` is "periodic".

    Note:
      Note those particularities when ``execution_rule`` is "endpoint":

        * Only one step input can be mapped to an endpoint as an "endpoint_input_name"
          if it is of type "file".
        * Only one step output can be mapped to an endpoint as an "endpoint_output_name"
          if it is of type "file".
        * When the endpoint deployment is created, it creates an HTTP endpoint which can
          be called at ``POST {environment_url}/endpoints/{endpoint_name}``. You can get
          `environment_url` with `sdk.base_environment_url`.

      | An endpoint token is required to call the HTTP endpoint. This token is different
        from the SDK token, you can find it in the result of this function as
        "endpoint_token". Use it to set the "Authorization" header as "EndpointToken
        {endpoint_token}".
      | Input can be passed to the endpoint either:

        * When there is no input file mapped to the endpoint, in the body in JSON with
          the `application/json` content type and with the format

          .. code-block:: json

              {
                "{input_name}": "{input_value}"
              }

        * When a file input is mapped to the endpoint, as a file with a
          `multipart/form-data` content type.

      This will return the output as:

        * When there is no output file, in the body in JSON in the format

          .. code-block:: json

              {
                "output": {
                  "{output_name}": "{output_value}"
                }
              }

        * When a file output is mapped, it will return the file as a response with the
          `application/octet-stream` content type.

      | A successful call will return results with a status code 200 after redirections.
      | If your HTTP clients does not follow redirection automatically, redirections are
        indicated by a status code between 300 and 399, and the redirection URL is in
        the `Location` header. Keep calling the redirection URL until you get a
        non-redirection status code.
      | If an endpoint deployment's execution encounters an error, it will return a
        status code between 400 and 599, and an error message in the body at the
        property `message`.
      | Here is an example of a successful call with curl:

      .. code-block:: bash

        curl -L "{environment_url}/endpoints/{endpoint_name}" \\
          -H "Authorization: EndpointToken {endpoint_token}" \\
          -H "Content-Type: application/json; charset=utf-8" \\
          -d @- << EOF
        {"input_string": "value_1", "input_number": 0}
        EOF

        # The response will be:
        # {"output": {"output_string": "returned_value_1", "output_number": 1}}

    """

    if deployment_mode not in set(DEPLOYMENT_MODES):
        raise ValueError(
            "Invalid 'deployment_mode', must be in ['elastic', 'low_latency']."
        )

    if execution_rule not in set(DEPLOYMENT_EXECUTION_RULES):
        raise ValueError(
            "Invalid 'execution_rule', must be in ['endpoint', 'periodic']."
        )

    if timeout_s < 120:
        raise ValueError("The timeout must be at least 2 minutes (120 seconds).")

    url = (
        f"{sdk.base_environment_api_url}/endpoints"
        if execution_rule == "endpoint"
        else f"{sdk.base_environment_api_url}/periodic-deployment"
    )

    data = {
        "pipeline_name": pipeline_name,
        "name": deployment_name,
        "description": description,
        "mode": deployment_mode,
    }

    if schedule is not None:
        if execution_rule != "periodic":
            raise ValueError(
                "'schedule' can only be specified if 'execution_rule' is \
'periodic'."
            )
        else:
            data["schedule"] = schedule

    if inputs_mapping is not None:
        if any(
            [
                not isinstance(input_mapping_, InputSource)
                for input_mapping_ in inputs_mapping
            ]
        ):
            raise ValueError("'inputs' must be a list of instances of InputSource.")
        data["inputs_mapping"] = [
            input_mapping_.to_dict() for input_mapping_ in inputs_mapping
        ]

    if outputs_mapping is not None:
        if any(
            [
                not isinstance(output_mapping_, OutputDestination)
                for output_mapping_ in outputs_mapping
            ]
        ):
            raise ValueError(
                "'outputs' must be a list of instances of OutputDestination."
            )
        data["outputs_mapping"] = [
            output_mapping_.to_dict() for output_mapping_ in outputs_mapping
        ]

    # filter optional parameters
    data = {k: v for k, v in data.items() if v is not None}

    log_action(
        sdk,
        "Please wait while deployment is being created. This may take a while...",
    )

    start_time = sdk._get_time()
    created_deployment, response = sdk._post(url, json=data, get_response=True)

    if response.status_code != 206:
        return created_deployment

    # The deployment is not ready. Keep checking its status until it is ready
    elapsed_time = sdk._get_time() - start_time
    deployment_update_status = DEPLOYMENT_UPDATE_STATUS.CREATING

    while (
        deployment_update_status
        not in [DEPLOYMENT_UPDATE_STATUS.SUCCESS, DEPLOYMENT_UPDATE_STATUS.FAILED]
        and elapsed_time < timeout_s
    ):
        time.sleep(CREATION_REQUESTS_RETRY_INTERVAL)
        created_deployment = get_deployment(sdk, deployment_name)

        if created_deployment is None:
            raise SdkException(
                f'The creation of deployment "{deployment_name}" has failed. '
                "Please try creating the step again. If this error keeps happening, "
                "please contact the support team.",
                name="UnexpectedError",
            )

        deployment_update_status = created_deployment.get("update_status", None)
        elapsed_time = sdk._get_time() - start_time

    if deployment_update_status != DEPLOYMENT_UPDATE_STATUS.SUCCESS:
        raise SdkException(
            'The deployment was not ready in time. It is still being created but \
this function stopped trying. Please check its status with "get_deployment".',
            name="TimeoutException",
        )
    return created_deployment


def get_deployment(sdk: BaseCraftAiSdk, deployment_name):
    """Get information of a deployment.

    Args:
        deployment_name (:obj:`str`): Name of the deployment.

    Returns:
        :obj:`dict`: Deployment information represented as :obj:`dict` with the
        following keys:

        * ``"name"`` (:obj:`str`): Name of the deployment.
        * ``"mode"`` (:obj:`str`): The deployment mode. Can be
          "elastic" or "low_latency".
        * ``"pipeline"`` (:obj:`dict`): Pipeline associated to the deployment
          represented as :obj:`dict` with the following keys:

          * ``"name"`` (:obj:`str`): Name of the pipeline.

        * ``"inputs_mapping"`` (:obj:`list` of :obj:`dict`): List of inputs
          mapping represented as :obj:`dict` with the following keys:

          * ``"step_input_name"`` (:obj:`str`): Name of the step input.
          * ``"data_type"`` (:obj:`str`): Data type of the step input.
          * ``"description"`` (:obj:`str`): Description of the step input.
          * ``"constant_value"`` (:obj:`str`): Constant value of the step input.
            Note that this key is only returned if the step input is mapped to a
            constant value.
          * ``"environment_variable_name"`` (:obj:`str`): Name of the environment
            variable. Note that this key is only returned if the step input is
            mapped to an environment variable.
          * ``"endpoint_input_name"`` (:obj:`str`): Name of the endpoint input.
            Note that this key is only returned if the step input is mapped to an
            endpoint input.
          * ``"is_null"`` (:obj:`bool`): Whether the step input is mapped to null.
            Note that this key is only returned if the step input is mapped to
            null.
          * ``"datastore_path"`` (:obj:`str`): Datastore path of the step input.
            Note that this key is only returned if the step input is mapped to the
            datastore.
          * ``"is_required"`` (:obj:`bool`): Whether the step input is required.
            Note that this key is only returned if the step input is required.
          * ``"default_value"`` (:obj:`str`): Default value of the step input.
            Note that this key is only returned if the step input has a default
            value.

        * ``"outputs_mapping"`` (:obj:`list` of :obj:`dict`): List of outputs
          mapping represented as :obj:`dict` with the following keys:

          * ``"step_output_name"`` (:obj:`str`): Name of the step output.
          * ``"data_type"`` (:obj:`str`): Data type of the step output.
          * ``"description"`` (:obj:`str`): Description of the step output.
          * ``"endpoint_output_name"`` (:obj:`str`): Name of the endpoint output.
            Note that this key is only returned if the step output is mapped to an
            endpoint output.
          * ``"is_null"`` (:obj:`bool`): Whether the step output is mapped to null.
            Note that this key is only returned if the step output is mapped to
            null.
          * ``"datastore_path"`` (:obj:`str`): Datastore path of the step output.
            Note that this key is only returned if the step output is mapped to
            the datastore.

        * ``"endpoint_token"`` (:obj:`str`): Token of the endpoint. Note that this
          key is only returned if the deployment is an endpoint.
        * ``"schedule"`` (:obj:`str`): Schedule of the deployment. Note that this
          key is only returned if the deployment is a periodic deployment.
        * ``"human_readable_schedule"`` (:obj:`str`): Human readable schedule of
          the deployment. Note that this key is only returned if the deployment is
          a periodic deployment.
        * ``"created_at"`` (:obj:`str`): Date of creation of the deployment.
        * ``"created_by"`` (:obj:`str`): ID of the user who created the deployment.
        * ``"updated_at"`` (:obj:`str`): Date of last update of the deployment.
        * ``"updated_by"`` (:obj:`str`): ID of the user who last updated the
          deployment.
        * ``"last_execution_id"`` (:obj:`str`): ID of the last execution of the
          deployment.
        * ``"is_enabled"`` (:obj:`bool`): Whether the deployment is enabled.
        * ``"description"`` (:obj:`str`): Description of the deployment.
        * ``"execution_rule"`` (:obj:`str`): Execution rule of the deployment.
        * ``"update_status"`` (:obj:`str`): The deployment status. Can be
          "creating","updating","success" or "failed".
        * ``"pods"`` (:obj:`list` of :obj:`dict`): List of pods associated to the
          low latency deployment. Note that this key is only returned if the
          deployment is in low latency mode. Each pod is represented as :obj:`dict`
          with the following keys:

          * ``pod_id`` (:obj:`str`): ID of the pod.
          * ``status`` (:obj:`str`): Status of the pod.
    """

    url = f"{sdk.base_environment_api_url}/deployments/{deployment_name}"
    deployment = sdk._get(url)
    if deployment is not None:
        latest_execution = sdk._get(
            f"\
{sdk.base_environment_api_url}/deployments/{deployment_name}/executions/latest"
        )
        deployment["last_execution_id"] = (
            latest_execution.get("execution_id", None)
            if latest_execution is not None
            else None
        )
    return deployment


def get_deployment_logs(
    sdk: BaseCraftAiSdk,
    deployment_name,
    from_datetime=None,
    to_datetime=None,
    limit=None,
):
    """Get the logs of a deployment with "low_latency" mode.

    Args:
        deployment_name (:obj:`str`): Name of the deployment.
        from_datetime (:obj:`datetime.time`, optional): Datetime from which the logs
            are collected. If not specified, logs are collected from the beginning.
        to_datetime (:obj:`datetime.time`, optional): Datetime until which the logs
            are collected. If not specified, logs are collected until the end.
        limit (:obj:`int`, optional): Maximum number of logs that are collected.
            If not specified, all logs are collected.

    Returns:
        :obj:`list` of :obj:`dict`: List of logs represented as :obj:`dict` with
        the following keys:

        * ``"timestamp"`` (:obj:`str`): Timestamp of the log.
        * ``"message"`` (:obj:`str`): Message of the log.
        * ``"pod_id"`` (:obj:`str`): ID of the pod.
        * ``"type"`` (:obj:`str`): Type of the log. Can be "deployment".
    """
    url = f"{sdk.base_environment_api_url}/deployments/{deployment_name}/logs"
    data = {}
    if from_datetime is not None:
        data["from"] = _datetime_to_timestamp_in_ms(from_datetime)
    if to_datetime is not None:
        data["to"] = _datetime_to_timestamp_in_ms(to_datetime)
    if limit is not None:
        data["limit"] = limit

    log_action(
        sdk,
        "Please wait while logs are being fetched. This may take a while...",
    )
    return sdk._post(url, json=data)


def list_deployments(sdk: BaseCraftAiSdk):
    """Get the list of all deployments.

    Returns:
        :obj:`list` of :obj:`dict`: List of deployments represented as :obj:`dict`
        with the following keys:

        * ``"name"`` (:obj:`str`): Name of the deployment.
        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline associated to
          the deployment.
        * ``"version"`` (:obj:`str`): Version of the pipeline associated to the
          deployment.
        * ``"execution_rule"`` (:obj:`str`): Execution rule of the deployment. Can be
          "endpoint", "run" or "periodic".
        * ``"is_enabled"`` (:obj:`bool`): Whether the deployment is enabled.
        * ``"created_at"`` (:obj:`str`): Date of creation of the deployment.
    """
    url = f"{sdk.base_environment_api_url}/deployments"
    return sdk._get(url)


@log_func_result("Deployment deletion")
def delete_deployment(sdk: BaseCraftAiSdk, deployment_name):
    """Delete a deployment identified by its name.

    Args:
        deployment_name (:obj:`str`): Name of the deployment.

    Returns:
        :obj:`dict`: Deleted deployment represented as dict with the following
        keys:

        * ``"name"`` (:obj:`str`): Name of the deployment.
        * ``"execution_rule"`` (:obj:`str`): Execution rule of the deployment. Can be
          "endpoint", "run" or "periodic".
    """
    url = f"{sdk.base_environment_api_url}/deployments/{deployment_name}"
    return sdk._delete(url)
