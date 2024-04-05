from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional, Dict, Tuple, Any, Union

import yaml
from pydantic import BaseModel, Field, validator, PrivateAttr
from tabulate import tabulate

from predibase._errors import PredibaseError
from predibase.resource.llm.prompt import PromptTemplate
from predibase.resources.datasets import Datasets
from predibase.resources.model import PretrainedHuggingFaceLLM, FinetunedLLMAdapter
from predibase.util import log_info, get_url

if TYPE_CHECKING:
    from predibase import Predibase
    from predibase.resource.model import ModelRepo

_PATH_HERE = os.path.abspath(os.path.dirname(__file__))
_TEMPLATE_DIR = os.path.join(_PATH_HERE, "../resource/llm/templates")
_CONFIG_FILENAME = "config.yaml"  # Name of config file for loading templates.


class Adapters:
    def __init__(self, client: Predibase):
        self._client = client
        self._session = client._session  # Directly using the session in the short term as we transition to v2.

    def create(
        self,
        config: Union[FinetuneConfig, Dict[str, Any]],
        *,
        description: str | None = None,
        repo: str | ModelRepo | None = None,
        wait: bool = True,
        show_tensorboard: bool = True,
    ) -> FinetunedLLMAdapter:
        """
        Triggers training of a fine-tuned adapter.

        :param config: A config object for the training run. Determines, among other parameters, the base LLM to
            fine-tune and the dataset to fine-tune on.
        :param description: (Optional) A human-readable description for this model.
        :param repo: (Optional) The repository to associate this model with. If not provided, one will be automatically
            created.
        :param wait: If True, the `create` call will block until training has completed.
        :param show_tensorboard: If True, training metrics will be streamed and displayed via a local Tensorboard
            instance. Requires `wait` to be True.
        :return: A FinetunedLLMAdapter object representing the (possible still training) adapter.
        """

        if show_tensorboard and not wait:
            raise RuntimeError("`show_tensorboard` is a blocking option and thus requires `wait` to be True.")

        if isinstance(config, dict):
            config = FinetuneConfig(**config)

        if repo is None:
            # If no repo is specified, automatically construct the repo name from the dataset and model name.
            dataset_name = config.dataset
            if "/" in dataset_name:
                _, dataset_name = dataset_name.split("/")

            model_name = config.base_model.name
            if "/" in model_name:
                _, model_name = model_name.split("/")

            repo = f"{model_name}-{dataset_name}"

        if isinstance(repo, str):
            if "/" in repo:
                repo = repo.replace("/", "-")
            repo = self._client.repos.create(repo, exists_ok=True)

        # TODO: this could move to server-side to reduce round trips.
        dataset = Datasets(self._session).get(config.dataset)

        train_req = {
            "config": config.render(),
            "datasetID": dataset.id,
            "repoID": repo.id,
            "description": description,
        }

        resp = self._session.post_json("/models/train", train_req)
        model_id = resp["model"]["id"]

        # Output link to UI model page
        endpoint = f"models/version/{model_id}"
        url = get_url(self._session, endpoint)
        log_info(f"Check Status of Model Training Here: [link={url}]{url}")

        adapter = FinetunedLLMAdapter(self._client, repo.name, model_id)
        if wait:
            return adapter.wait_ready(show_tensorboard=show_tensorboard)
        return adapter

    @staticmethod
    def FinetuneConfig(*args, **kwargs) -> FinetuneConfig:
        return FinetuneConfig(*args, **kwargs)

    def get(self, resource_id: str) -> FinetunedLLMAdapter:
        """
        Retrieve a FinetunedLLMAdapter given its name or URI.
        :param resource_id: A string of the form [pb://adapters/]<repo_name>/<version> identifying the adapter to fetch.
        :return: A FinetunedLLMAdapter object.
        """
        if resource_id.startswith("pb://adapters/"):
            resource_id = resource_id[len("pb://adapters/") :]

        tokens = resource_id.split("/")
        if len(tokens) < 2:
            raise PredibaseError(f"expected a URI of the form [pb://adapters/]<repo_name>/<version>")

        resp = self._session.get_json(f"/models/version/name/{tokens[0]}?version={tokens[1]}")
        if not resp.get("llmBaseModelName", ""):
            raise PredibaseError(f"resource ID {resource_id} does not point to a fine-tuned LLM adapter")

        return FinetunedLLMAdapter(self._client, tokens[0], resp["id"])


# TODO: remove `arbitrary_types_allowed` after moving more classes to Pydantic models
class FinetuneConfig(BaseModel, validate_assignment=True, arbitrary_types_allowed=True):
    base_model: Union[str, PretrainedHuggingFaceLLM] = Field(
        description="The model to fine-tune, expressed either as a string ("
        "e.g., `meta-llama/Llama-2-7b-hf`) or as a "
        "PretrainedHuggingFaceLLM instance."
    )
    # TODO: improve passing dataset by name once we get rid of connection namespacing
    dataset: str = Field(
        description="The dataset to fine-tune on. Accepts a string of the form <connection>/<name> referencing data "
        "uploaded to Predibase."
    )
    prompt_template: Union[str, PromptTemplate] = Field(
        description="The text template used to format each training example. Column data "
        "will be interpolated via `{column_name}` placeholders. A "
        "PromptTemplate object can be used instead in cases where curly "
        "braces are difficult to escape, such as when working with JSON-like "
        "prompts."
    )
    target: str = Field(
        description="The name of the dataset column containing outputs that the model should learn to " "generate."
    )
    finetune_template: FinetuneTemplate = Field(
        default_factory=lambda: FinetuneTemplateCollection().default,
        description="(Optional) A base configuration template that this " "config should take default values from.",
    )
    epochs: Optional[int] = Field(
        default=None,
        description="(Optional) The number of epochs to train for. If not set, "
        "a default value will be used. At most one of this parameter and "
        "`train_steps` may be set.",
    )
    train_steps: Optional[int] = Field(
        default=None,
        description="(Optional) The number of steps to train for. If not set, "
        "a default value will be used. At most one of this parameter and "
        "`epochs` may be set.",
    )
    learning_rate: Optional[float] = Field(
        default=None,
        description="(Optional) The learning rate of the model. If not set, " "a default value will be used.",
    )

    @classmethod
    @validator("train_steps")
    def check_train_steps(cls, v, values):
        if values.get("epochs") is not None:
            raise ValueError("only one of `epochs` and `train_steps` may be set")

    def __init__(self, **data):
        super().__init__(**data)

        if isinstance(self.base_model, str):
            self.base_model = PretrainedHuggingFaceLLM(self.base_model)

    def render(self) -> Dict:
        prompt_template = self.prompt_template
        if isinstance(prompt_template, PromptTemplate):
            prompt_template = prompt_template.render()

        config = self.finetune_template.to_config(self.base_model, prompt_template, self.target)

        # HACK(Arnav): Temporary hack to inject the right target_modules into the config for mixtral and
        # mixtral instruct. This should be removed once the Mixtral models have a default PEFT mapping for LoRA
        # target_modules. See MLX-1680: https://linear.app/predibase/issue/MLX-1680/remove-peftlora-mixtral-hack-in
        # -the-predibase-sdk # noqa
        if (
            config.get("base_model", "") in {"mistralai/Mixtral-8x7B-v0.1", "mistralai/Mixtral-8x7B-Instruct-v0.1"}
            and "adapter" in config
            and config.get("adapter", {}).get("target_modules", None) is None
        ):
            config["adapter"]["target_modules"] = ["q_proj", "v_proj"]

        # Apply first-class training parameters.
        if self.train_steps is not None:
            config["trainer"]["train_steps"] = self.train_steps
        if self.epochs is not None:
            config["trainer"]["epochs"] = self.epochs
        if self.learning_rate is not None:
            config["trainer"]["learning_rate"] = self.learning_rate

        return config


class FinetuneTemplateCollection(dict):
    def __init__(self):
        super().__init__()

        for filename in os.listdir(_TEMPLATE_DIR):
            if not filename.endswith(".yaml"):
                continue

            if filename == _CONFIG_FILENAME:
                with open(os.path.join(_TEMPLATE_DIR, _CONFIG_FILENAME)) as config_file:
                    self._config = yaml.safe_load(config_file)
            else:
                tmpl = FinetuneTemplate(filename=os.path.join(_TEMPLATE_DIR, filename))
                self[tmpl.name] = tmpl

    @property
    def default(self) -> FinetuneTemplate:
        default_name = self._config.get("default", "")
        tmpl = self.get(default_name, None)
        if tmpl is None:
            raise RuntimeError(f"the default template '{default_name}' was not found")

        return tmpl

    def compare(self):
        print(self)

    def __str__(self):
        def make_row(key) -> Tuple[str, str, str]:
            tmpl = self[key]
            default_indicator = "------>" if tmpl.name == self._config["default"] else ""
            return default_indicator, key, tmpl.description

        return tabulate(
            (make_row(k) for k in sorted(self.keys())),
            tablefmt="simple_grid",
            headers=["Default", "Name", "Description"],
            colalign=["center"],
        )


class FinetuneTemplate(BaseModel):
    filename: str
    _meta: Optional[dict] = PrivateAttr(default=None)
    _raw_template_str: Optional[str] = PrivateAttr(default=None)

    @property
    def name(self) -> str:
        if self._meta is None:
            self._load()
        return self._meta["name"]

    @property
    def description(self) -> str:
        if self._meta is None:
            self._load()
        return self._meta["description"]

    def to_config(
        self,
        model: str | PretrainedHuggingFaceLLM,
        prompt_template: str = "__PROMPT_TEMPLATE_PLACEHOLDER__",
        target: str = "__TARGET_PLACEHOLDER__",
    ) -> dict:
        if self._raw_template_str is None:
            self._load()

        if isinstance(model, PretrainedHuggingFaceLLM):
            model = model.name

        cfg = yaml.safe_load(
            self._raw_template_str.format(
                base_model=model,
                prompt_template=prompt_template,
                target=target,
            ),
        )
        del cfg["template_meta"]
        return cfg

    def _load(self):
        with open(os.path.join(_TEMPLATE_DIR, self.filename)) as f:
            self._raw_template_str = f.read()

        self._meta = yaml.safe_load(self._raw_template_str)["template_meta"]
