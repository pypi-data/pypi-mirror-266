"""Pretraining API"""
from __future__ import annotations

from concurrent.futures import Future
from typing import Any, Dict, List, Optional, Union, overload

from typing_extensions import Literal

from mcli.api.engine.engine import get_return_response, run_singular_mapi_request
from mcli.api.model.run import Run
from mcli.models.pretrain_config import PretrainConfig, TokenizerConfig
from mcli.utils.utils_config import ComputeConfig, ExperimentTrackerConfig

QUERY_FUNCTION = 'createPretrain'
VARIABLE_DATA_NAME = 'createPretrainData'
# This returns the same data that the create_run function returns
# for consistency when rendering the describe output
QUERY = f"""
mutation CreatePretrain(${VARIABLE_DATA_NAME}: CreatePretrainInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
    id
    name
    createdByEmail
    status
    createdAt
    updatedAt
    reason
    priority
    maxRetries
    preemptible
    retryOnSystemFailure
    isDeleted
    runType
    resumptions {{
        clusterName
        cpus
        gpuType
        gpus
        nodes
        executionIndex
        startTime
        endTime
        status
        estimatedEndTime
    }}
    details {{
        originalRunInput
        metadata
        lastExecutionId
    }}
  }}
}}"""


@overload
def create_pretraining_run(
    model: str,
    train_data: Union[List[str], Dict[str, Any]],
    save_folder: str,
    *,
    compute: Optional[Union[ComputeConfig, Dict[str, Any]]] = None,
    tokenizer: Optional[Union[TokenizerConfig, Dict[str, Any]]] = None,
    training_duration: Optional[str] = None,
    parameters: Optional[Dict[str, str]] = None,
    eval: Optional[Dict[str, str]] = None,  #pylint: disable=redefined-builtin
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Run:
    ...


@overload
def create_pretraining_run(
    model: str,
    train_data: Union[List[str], Dict[str, Any]],
    save_folder: str,
    *,
    compute: Optional[Union[ComputeConfig, Dict[str, Any]]] = None,
    tokenizer: Optional[Union[TokenizerConfig, Dict[str, Any]]] = None,
    training_duration: Optional[str] = None,
    parameters: Optional[Dict[str, str]] = None,
    eval: Optional[Dict[str, str]] = None,  #pylint: disable=redefined-builtin
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Future[Run]:
    ...


def create_pretraining_run(
    model: str,
    train_data: Union[List[str], Dict[str, Any]],
    save_folder: str,
    *,
    compute: Optional[Union[ComputeConfig, Dict[str, Any]]] = None,
    tokenizer: Optional[Union[TokenizerConfig, Dict[str, Any]]] = None,
    training_duration: Optional[str] = None,
    parameters: Optional[Dict[str, str]] = None,
    eval: Optional[Dict[str, str]] = None,  #pylint: disable=redefined-builtin
    experiment_tracker: Optional[ExperimentTrackerConfig] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Union[Run, Future[Run]]:
    """Create a pretraining run.

    Required args:
        model: The name of the Hugging Face model to use.
        train_data: Either a list of paths to the training data or a mapping of dataset names to the path and
            proportion of the dataset to use. For example, if you have two datasets, ``dataset1`` and ``dataset2``,
            and you want to use 80% of ``dataset1`` and 50% of ``dataset2``, you can pass in
            ``{"dataset1": {"path": "path/to/dataset1", "proportion": 8}, "dataset2": {"path": "path/to/dataset2",
            "proportion": 5}}``.
        save_folder: The remote location to save the checkpoints. For example,
            if your ``save_folder`` is ``s3://my-bucket/my-checkpoints``, the Composer checkpoints
            will be saved to ``s3://my-bucket/my-checkpoints/<run-name>/checkpoints``, and Hugging Face formatted
            checkpoints will be saved to ``s3://my-bucket/my-checkpoints/<run-name>/hf_checkpoints``. The supported
            cloud provider prefixes are ``s3://``, ``gs://``, and ``oci://``.
        compute: The compute configuration to use. Required for now

    Optional args:
        tokenizer: Tokenizer configuration to use. If not provided, the default tokenizer for the model will be used.
        training_duration: The total duration of your run. This can be specified in batches
            (e.g. ``100ba``), epochs (e.g. ``10ep``), or tokens (e.g. ``1_000_000tok``). Default is ``1ep``.
        parameters: Additional parameters to pass to the model
            learning_rate: The peak learning rate to use. Default is ``5e-7``. The optimizer used
                is DecoupledLionW with betas of 0.90 and 0.95 and no weight decay, and the learning rate scheduler 
                used is LinearWithWarmupSchedule with a warmup of 2% of the total training duration and a final 
                learning rate multiplier of 0.
            context_length: The maximum sequence length to use. This will be used to truncate any data that is too long. 
                The default is the default for the provided Hugging Face model. We do not support extending the context
                length beyond each model's default.
        experiment_tracker: The configuration for an experiment tracker. For example, to add Weights and Biases
            tracking, you can pass in ``{"wandb": {"project": "my-project", "entity": "my-entity"}}``. To add in mlflow
            tracking, you can pass in ``{"mlflow": {"experiment_path": "my-experiment", "model_registry_path: 
            "catalog.schema.model_name"}}``.
        eval: Configuration for evaluation
        timeout: Time, in seconds, in which the call should complete. If the run creation
            takes too long, a TimeoutError will be raised. If ``future`` is ``True``, this
            value will be ignored.
        future: Return the output as a :class:`~concurrent.futures.Future`. If True, the
            call to `create_pretraining_run` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the :type Run: output, use ``return_value.result()``
            with an optional ``timeout`` argument.

    Returns:
        A :type Run: object containing the pretraining run information.
    """
    config = PretrainConfig.from_dict({
        'model': model,
        'train_data': train_data,
        'save_folder': save_folder,
        'compute': compute or {},
        'tokenizer': tokenizer,
        'training_duration': training_duration,
        'parameters': parameters,
        'eval': eval,
        'experiment_tracker': experiment_tracker,
    })
    pretraining_config = config.to_create_pretraining_api_input()
    variables = {
        VARIABLE_DATA_NAME: pretraining_config,
    }

    response = run_singular_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=Run,
        variables=variables,
    )
    return get_return_response(response, future=future, timeout=timeout)
