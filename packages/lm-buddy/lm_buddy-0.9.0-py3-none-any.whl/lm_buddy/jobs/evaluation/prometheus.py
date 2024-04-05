"""
lm-buddy entrypoint to run evaluations using a Prometheus inference server
see https://github.com/kaistAI/prometheus/blob/main/evaluation/benchmark/run_absolute_scoring.py
"""

import copy
import json
from dataclasses import dataclass
from pathlib import Path

from datasets import load_dataset
from fastchat.conversation import get_conv_template
from openai import Completion, OpenAI, OpenAIError
from tqdm import tqdm

from lm_buddy.configs.huggingface import AutoTokenizerConfig
from lm_buddy.configs.jobs.prometheus import PrometheusJobConfig
from lm_buddy.jobs.asset_loader import HuggingFaceAssetLoader
from lm_buddy.jobs.common import EvaluationResult
from lm_buddy.preprocessing import format_dataset_with_prompt
from lm_buddy.tracking.artifact_utils import (
    ArtifactType,
    build_directory_artifact,
    default_artifact_name,
)


@dataclass
class BadResponseError(Exception):
    def __init__(self, message, error=None):
        self.message = message
        self.error = error


def openai_completion(config: PrometheusJobConfig, client: OpenAI, prompt: str) -> Completion:
    """Connects to a remote OpenAI-API-compatible Prometheus endpoint
    and returns a Completion holding the model's response.
    """

    return client.completions.create(
        model=config.prometheus.inference.engine,
        prompt=prompt,
        best_of=config.prometheus.best_of,
        max_tokens=config.prometheus.max_tokens,
        frequency_penalty=config.prometheus.frequency_penalty,
        temperature=config.prometheus.temperature,
        top_p=config.prometheus.top_p,
    )


def parse_response(config: PrometheusJobConfig, response: Completion) -> tuple[str, str]:
    """Given a Prometheus eval response as returned by the OpenAI API
    endpoint (i.e. in Completion format), extract feedback
    and score.
    """

    if response is None:
        raise BadResponseError("Server returned an empty response")

    try:
        response_text = response.choices[0].text
        # note: this can raise a ValueError if the message is malformed
        feedback, score = response_text.split("[RESULT]")
        feedback = feedback.strip()
        score = score.strip()
        if score not in [str(s) for s in config.evaluation.scores]:
            raise BadResponseError(f"Score {score} is not in range")
    except (ValueError, BadResponseError) as e:
        raise BadResponseError(f"Server returned a malformed response ({e})", e)

    return feedback, score


def instruction_to_prompt(config: PrometheusJobConfig, instruction: str) -> str:
    """Given some text containing Prometheus instructions, a conversation
    template (e.g. "llama-2") and a system message (e.g. "You are a
    fair evaluator language model"), generate an actual prompt.
    """
    conv = get_conv_template(config.evaluation.conversation_template)
    conv.set_system_message(config.evaluation.conversation_system_message)
    conv.append_message(conv.roles[0], instruction)
    conv.append_message(conv.roles[1], None)
    return conv.get_prompt()


def get_response_with_retries(
    config: PrometheusJobConfig, client: OpenAI, prompt: str, max_retries: int
) -> tuple[str, str]:
    current_retry_attempt = 1
    while current_retry_attempt <= config.evaluation.max_retries:
        try:
            response = openai_completion(config, client, prompt)
            feedback, score = parse_response(config, response)
            break
        except (OpenAIError, BadResponseError) as e:
            print(
                f"[w] {e.message}, "
                f"retrying ({current_retry_attempt}/{config.evaluation.max_retries})"
            )
            current_retry_attempt += 1
            if current_retry_attempt > config.evaluation.max_retries:
                raise e
    return (feedback, score)


def run_eval(config: PrometheusJobConfig) -> Path:
    # Instantiate OpenAI client to speak with the vLLM endpoint
    client = OpenAI(base_url=config.prometheus.inference.base_url)

    # load dataset from W&B artifact
    hf_loader = HuggingFaceAssetLoader()
    dataset = hf_loader.load_dataset(config.dataset)
    if config.dataset.prompt_template is not None:
        dataset = format_dataset_with_prompt(
            dataset, config.dataset.prompt_template, config.dataset.text_field
        )

    # get the tokenizer
    tokenizer_config = AutoTokenizerConfig(path=config.prometheus.inference.engine)
    tokenizer = hf_loader.load_pretrained_tokenizer(tokenizer_config)

    # enable / disable tqdm
    dataset_iterable = tqdm(dataset) if config.evaluation.enable_tqdm else dataset

    # open the output file for writing and iterate on samples
    tracking_name = config.tracking.name if config.tracking is not None else "output.json"
    output_fname = Path(config.evaluation.output_folder) / tracking_name
    with output_fname.open("w") as file:
        for sample in dataset_iterable:
            # convert instructions from the dataset (`text_field` in a dict) to
            # prompts that prometheus accepts
            prompt = instruction_to_prompt(config, sample[config.dataset.text_field])

            # skip those examples which are too long
            tokenized_prompt = tokenizer(prompt, truncation=False)
            if len(tokenized_prompt["input_ids"]) > 3072:
                continue

            # prepare output
            result = copy.deepcopy(sample)
            result["prometheus_output"] = []
            result["prometheus_score"] = []

            for _ in range(config.evaluation.num_answers):
                (feedback, score) = get_response_with_retries(
                    config, client, prompt, config.evaluation.max_retries
                )
                result["prometheus_output"].append(feedback)
                result["prometheus_score"].append(score)

            # dump sample results incrementally
            file.write(json.dumps(result) + "\n")

    # convert plain json dataset in HF format
    output_dataset_path = Path(config.evaluation.output_folder) / "hf" / tracking_name
    ds = load_dataset("json", data_files=str(output_fname), split="train")
    ds.save_to_disk(output_dataset_path)

    return output_dataset_path


def run_prometheus(config: PrometheusJobConfig) -> EvaluationResult:
    # Run eval and store output in local filename
    output_dataset_path = run_eval(config)
    print(f"Prometheus evaluation dataset stored at {output_dataset_path}")

    # Create a directory artifact for the HF dataset
    artifact_name = default_artifact_name(config.name, artifact_type=ArtifactType.DATASET)
    dataset_artifact = build_directory_artifact(
        artifact_name=artifact_name,
        artifact_type=ArtifactType.DATASET,
        dir_path=output_dataset_path,
        reference=False,
    )

    return EvaluationResult(
        artifacts=[dataset_artifact],
        dataset_path=output_dataset_path,
        tables={},
    )
