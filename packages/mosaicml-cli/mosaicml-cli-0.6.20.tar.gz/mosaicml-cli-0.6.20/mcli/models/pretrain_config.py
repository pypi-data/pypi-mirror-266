""" Pretraining config """
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union

import yaml
from typing_extensions import TypedDict

from mcli.api.exceptions import MCLIConfigError
from mcli.utils.utils_config import (BaseSubmissionConfig, ComputeConfig, ComputeTranslation, ExperimentTrackerConfig,
                                     ExperimentTrackerTranslation, Translation, strip_nones)
from mcli.utils.utils_logging import WARN
from mcli.utils.utils_string_functions import camel_case_to_snake_case, snake_case_to_camel_case

logger = logging.getLogger(__name__)


class PretrainingParameters(TypedDict, total=False):
    """Typed dictionary for pretraining parameters"""
    learning_rate: Optional[float]
    context_length: Optional[int]


class TokenizerConfig(TypedDict, total=False):
    """Typed dictionary for tokenizer parameters"""
    name: Optional[str]
    trust_remote_code: Optional[bool]

    model_max_length: Optional[int]
    model_input_names: Optional[List[str]]


class EvalParameters(TypedDict, total=False):
    """Typed dictionary for evaluation parameters"""
    data_path: Optional[str]
    prompts: Optional[str]


class PretrainingParametersTranslation(Translation[PretrainingParameters, Dict[str, Any]]):
    """Translate parameters configs to and from MAPI"""

    translations = {
        "learningRate": "learning_rate",
        "contextLength": "context_length",
    }

    @classmethod
    def from_mapi(cls, value: Dict[str, Any]) -> PretrainingParameters:
        extracted = PretrainingParameters(**{cls.translations.get(k, k): v for k, v in value.items()})
        return extracted

    @classmethod
    def to_mapi(cls, value: PretrainingParameters) -> Dict[str, Any]:
        inv = {v: k for k, v in cls.translations.items()}
        processed = {inv.get(k, k): v for k, v in value.items() if v is not None}
        return processed


class TokenizerConfigTranslation(Translation[TokenizerConfig, Dict[str, Any]]):
    """Translate tokenizer configs to and from MAPI"""

    translations = {
        "name": "name",
        "modelMaxLength": "model_max_length",
        "modelInputNames": "model_input_names",
        "trustRemoteCode": "trust_remote_code",
    }

    @classmethod
    def from_mapi(cls, value: Dict[str, Any]) -> TokenizerConfig:
        extracted = TokenizerConfig(**{cls.translations.get(k, k): v for k, v in value.items()})
        return extracted

    @classmethod
    def to_mapi(cls, value: TokenizerConfig) -> Dict[str, Any]:
        inv = {v: k for k, v in cls.translations.items()}
        processed = {inv.get(k, k): v for k, v in value.items() if v is not None}
        return processed


class EvalParametersTranslation(Translation[EvalParameters, Dict[str, Any]]):
    """Translate scheduling configs to and from MAPI"""

    translations = {
        "dataPath": "data_path",
        "prompts": "prompts",
    }

    @classmethod
    def from_mapi(cls, value: Dict[str, Any]) -> EvalParameters:
        extracted = EvalParameters(**{cls.translations.get(k, k): v for k, v in value.items()})
        return extracted

    @classmethod
    def to_mapi(cls, value: EvalParameters) -> Dict[str, Any]:
        inv = {v: k for k, v in cls.translations.items()}
        processed = {inv.get(k, k): v for k, v in value.items() if v is not None}
        return processed


@dataclass
class PretrainConfig(BaseSubmissionConfig):
    """Input for pretraining run

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
    """

    model: str
    train_data: Union[List[str], Dict[str, Any]]
    save_folder: str
    compute: ComputeConfig

    tokenizer: Optional[TokenizerConfig] = None
    training_duration: Optional[str] = None
    parameters: PretrainingParameters = field(default_factory=PretrainingParameters)
    eval: EvalParameters = field(default_factory=EvalParameters)
    experiment_tracker: Optional[ExperimentTrackerConfig] = None

    _required_properties = {'model', 'train_data', 'save_folder', 'compute'}
    _pretrain_properties = {
        'model',
        'train_data',
        'compute',
        'save_folder',
        'tokenizer',
        'training_duration',
        'parameters',
        'eval',
        'experiment_tracker',
    }

    def __str__(self) -> str:
        return yaml.safe_dump(asdict(self))

    @classmethod
    def validate_dict(cls, dict_to_use: Dict, show_unused_warning: bool = True) -> Dict:
        """Load the config from the provided dictionary.
        """
        config_dict = strip_nones(dict_to_use)
        unused_keys = set(dict_to_use) - cls._pretrain_properties
        for key in unused_keys:
            del config_dict[key]
        if {'name', 'image', 'command'}.issubset(unused_keys):
            logger.info(f'{WARN} You specified a name, image, and command. Did you mean to use `mcli run`?')
        missing = cls._required_properties - set(dict_to_use)
        if missing:
            raise MCLIConfigError(f'Missing required fields: {", ".join(missing)}',)
        if len(unused_keys) > 0 and show_unused_warning:
            raise MCLIConfigError(f'Encountered unknown fields in pretraining config: {", ".join(unused_keys)}.')
        return config_dict

    @classmethod
    def from_dict(cls, dict_to_use: Dict[str, Any], show_unused_warning: bool = True):
        """Load the config from the provided dictionary.
        """
        config_dict = cls.validate_dict(dict_to_use, show_unused_warning)
        return cls(**config_dict)

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]):
        """Load the config from mapi response.
        """
        data = {}
        for key, value in response.items():
            if key == "experimentTracker":
                value = ExperimentTrackerTranslation.from_mapi(value)
            elif key == "eval":
                value = EvalParametersTranslation.from_mapi(value)
            elif key == "parameters":
                value = PretrainingParametersTranslation.from_mapi(value)
            elif key == "compute":
                value = ComputeTranslation.from_mapi(value)
            elif key == "tokenizer":
                value = TokenizerConfigTranslation.from_mapi(value)

            data[camel_case_to_snake_case(key)] = value
        return cls.from_dict(data)

    def to_create_pretraining_api_input(self) -> Dict[str, Dict[str, Any]]:
        """Converts the PretrainConfig object to the config used in mapi
        """
        pretrain = {}
        config_dict = strip_nones(self.__dict__)
        for key, val in config_dict.items():
            if key == 'experiment_tracker':
                val = ExperimentTrackerTranslation.to_mapi(val)
            elif key == "eval":
                val = EvalParametersTranslation.to_mapi(val)
            elif key == "parameters":
                val = PretrainingParametersTranslation.to_mapi(val)
            elif key == "compute":
                val = ComputeTranslation.to_mapi(val)
            elif key == "tokenizer":
                val = TokenizerConfigTranslation.to_mapi(val)

            translated_key = snake_case_to_camel_case(key)
            if key in self._pretrain_properties:
                pretrain[translated_key] = val

        return pretrain

    def to_yaml(self) -> str:
        """Converts the PretrainConfig object to a yaml string with only used keys
        """
        filtered_config = {k: v for k, v in self.__dict__.items() if v}
        return yaml.safe_dump(filtered_config)
