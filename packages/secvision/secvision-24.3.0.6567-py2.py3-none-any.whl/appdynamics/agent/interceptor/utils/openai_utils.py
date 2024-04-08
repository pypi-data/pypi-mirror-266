import appdynamics.agent.models.custom_metrics as custom_metrics_mod
from appdynamics.lang import items, urlparse
from collections import defaultdict


class OpenaiConstants():
    COST_METRIC_NAME = "Cost"
    TOKENS_METRIC_NAME = "Tokens"
    CALLS_METRIC_NAME = "Calls per minute"
    ERROR_METRIC_NAME = "Errors per minute"
    FLAGGED_QUERIES_METRIC_NAME = "Flagged queries"
    TOTAL_QUERIES_METRIC_NAME = "Total queries"
    ALL_MODELS_STRING = "All Models"
    OPENAI = "OpenAI"
    METRIC_NAME_SEGREGATOR = " - "
    OPENAI_PREFIX = OPENAI + METRIC_NAME_SEGREGATOR
    TIER_METRIC_PATH = "Agent|OpenAI"
    APPLICATION_METRIC_PATH = "BTM|Application Summary"
    RESPONSE_PROMPT_STRING = "prompt_tokens"
    RESPONSE_COMPLETION_STRING = "completion_tokens"
    RESPONSE_TOTAL_TOKEN_STRING = "total_tokens"
    TIME_ROLLUP_STRING = "time_rollup_type"
    CLUSTER_ROLLUP_STRING = "cluster_rollup_type"
    HOLE_HANDLING_STRING = "hole_handling_type"
    METRIC_PATH_SEGREGATOR = "|"
    DEFAULT_HOST = "api.openai.com"
    DEFAULT_OPENAI_ENDPOINT = "https://api.openai.com/v1"
    MODERATION = "moderations"
    MODERATION_METRIC_PATH = TIER_METRIC_PATH + METRIC_PATH_SEGREGATOR + MODERATION
    MODERATION_CATERGORY_FOLDER_NAME = "Flagged Calls by category"
    MODERATION_APPLICATION_LEVEL_PREFIX = OPENAI_PREFIX + MODERATION_CATERGORY_FOLDER_NAME + METRIC_NAME_SEGREGATOR
    MODERATION_TIER_LEVEL_PREFIX = TIER_METRIC_PATH + METRIC_PATH_SEGREGATOR + MODERATION + \
        METRIC_PATH_SEGREGATOR + MODERATION_CATERGORY_FOLDER_NAME


METRICS_DICT = {
    OpenaiConstants.COST_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    OpenaiConstants.CALLS_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    OpenaiConstants.ERROR_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    OpenaiConstants.TOKENS_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
}

MODEL_COST_MAP = {
    "babbage": {'prompt_cost': 5, 'completion_cost': 5},
    "curie": {'prompt_cost': 20, 'completion_cost': 20},
    "davinci": {'prompt_cost': 200, 'completion_cost': 200},
    "text-ada-001": {'prompt_cost': 4, 'completion_cost': 4},
    "text-babbage-001": {'prompt_cost': 5, 'completion_cost': 5},
    "text-curie-001": {'prompt_cost': 20, 'completion_cost': 20},
    "gpt-3.5-turbo": {'prompt_cost': 15, 'completion_cost': 20},
    "gpt-3.5-turbo-0613": {'prompt_cost': 30, 'completion_cost': 40},
    "gpt-3.5-turbo-16k": {'prompt_cost': 30, 'completion_cost': 40},
    "gpt-3.5-turbo-16k-0613": {'prompt_cost': 30, 'completion_cost': 40},
    "text-davinci-001": {'prompt_cost': 200, 'completion_cost': 200},
    "text-davinci-002": {'prompt_cost': 200, 'completion_cost': 200},
    "text-davinci-003": {'prompt_cost': 200, 'completion_cost': 200},
    "code-davinci-002": {'prompt_cost': 0, 'completion_cost': 0},
    "gpt-4": {'prompt_cost': 300, 'completion_cost': 600},
    "gpt-4-0613": {'prompt_cost': 300, 'completion_cost': 600},
    "gpt-4-32k": {'prompt_cost': 600, 'completion_cost': 1200},
    "gpt-4-32k-0613": {'prompt_cost': 600, 'completion_cost': 1200},
    "gpt-4-1106-preview": {'prompt_cost': 100, 'completion_cost': 300},
    "gpt-3.5-turbo-1106": {'prompt_cost': 10, 'completion_cost': 20},
    "gpt-3.5-turbo-instruct": {'prompt_cost': 15, 'completion_cost': 20},
    "davinci-002": {'prompt_cost': 20, 'completion_cost': 20},
    "babbage-002": {'prompt_cost': 4, 'completion_cost': 4},

    # cisco chat-ai
    "gpt-35-turbo": {'prompt_cost': 15, 'completion_cost': 20},
}

MODERATION_CATEGORY = {
    "sexual": "sexual",
    "hate": "hate",
    "harassment": "harassment",
    "self-harm": "selfHarm",
    "sexual/minors": "sexualMinors",
    "hate/threatening": "hateThreatening",
    "violence/graphic": "violenceGraphic",
    "self-harm/intent": "selfHarmIntent",
    "self-harm/instructions": "selfHarmInstructions",
    "harassment/threatening": "harassmentThreatening",
    "violence": "violence",
}


MODERATION_METRIC_DICT = {
    OpenaiConstants.CALLS_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    OpenaiConstants.FLAGGED_QUERIES_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    OpenaiConstants.TOTAL_QUERIES_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    OpenaiConstants.ERROR_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
}

MODERATION_CATEGORY_METRICS = {
    value: MODERATION_METRIC_DICT[OpenaiConstants.FLAGGED_QUERIES_METRIC_NAME]
    for key, value in items(MODERATION_CATEGORY)
}


def get_tokens_per_request(method_response, token_type=OpenaiConstants.RESPONSE_PROMPT_STRING):
    try:
        return method_response['usage'][token_type]
    except Exception as exec:
        raise UnsupportedResponseException(f"""UnsupportedResponseException: create method response struct changed.
                    Please contact admin or use the latest agent for updates \n [Error]:
                    {str(exec)}""")


def get_cost_per_request(model_name=None, prompt_tokens=0, completion_tokens=0):
    if model_name and model_name in MODEL_COST_MAP:
        return (prompt_tokens * MODEL_COST_MAP[model_name]['prompt_cost']) + \
            (completion_tokens * MODEL_COST_MAP[model_name]['completion_cost'])
    else:
        raise UnsupportedModelException(f" unsupported model {model_name} is \
        not supported by current agent.\
        Please update the python agent or contact admin")


def initialize_metrics(metric_prefix_path="", metric_prefix="", metric_suffix="", metric_dict=dict()):
    model_metrics_dict = dict()
    for metric_name, metric_attr in items(metric_dict):
        model_metrics_dict[metric_name] = custom_metrics_mod.CustomMetric(
            name=metric_prefix_path + OpenaiConstants.METRIC_PATH_SEGREGATOR +
            metric_prefix + metric_name + metric_suffix,
            time_rollup_type=metric_attr[OpenaiConstants.TIME_ROLLUP_STRING],
            hole_handling_type=metric_attr[OpenaiConstants.HOLE_HANDLING_STRING])
    return model_metrics_dict


def get_backend_details(base_url=None) -> tuple:
    backend_details = None
    try:
        # importing openai package since api's hostname
        # change will different api's getting hostname
        # on every exitcall
        if base_url and hasattr(base_url, 'host') and hasattr(base_url, 'port') and hasattr(base_url, 'scheme'):
            port = base_url.port or ('443' if base_url.scheme == 'https' else '80')
            backend_details = (base_url.host, port, base_url.scheme, base_url.host)
        else:
            from openai import api_base
            parsed_url = urlparse(api_base)
            port = parsed_url.port or ('443' if parsed_url.scheme == 'https' else '80')
            backend_details = (parsed_url.hostname, port, parsed_url.scheme, api_base)
    except:
        backend_details = (
            OpenaiConstants.DEFAULT_HOST,
            '443', 'https',
            OpenaiConstants.DEFAULT_OPENAI_ENDPOINT
        )
    finally:
        return backend_details


def prompt_flagged_counter(agent=None, response=None) -> int:
    flagged_calls = 0
    try:
        if not response:
            response = list()
        flagged_calls = sum([int(moderation_data.get("flagged", False)) for moderation_data in response])
    except Exception as e:
        agent.logger.error(f"Moderation API response changed. {str(e)} \n. Please raise a bug")
    finally:
        return flagged_calls


def get_moderation_category_values(input_response=None, agent=None) -> dict:
    output_response = defaultdict(int)
    try:
        for prompts in input_response.get('results'):
            for category, is_flagged in items(prompts.get("categories", {})):
                if category in MODERATION_CATEGORY:
                    if is_flagged:
                        output_response[MODERATION_CATEGORY[category]] += 1
                else:
                    agent.logger.warning(
                        "Category not support {0}".format(category))
    except Exception as e:
        agent.logger.error("Moderation API response changed. Please raise a bug" + str(e))
    finally:
        return output_response


def report_metrics(metrics_dict=None, reporting_values=None, agent=None):
    if not metrics_dict or not reporting_values:
        raise MissingReportingValuesExcepion(" Metric Reporting\
           values not found .Please provide proper method arguments\
        ")
    try:
        for metric_name, metric_value in items(reporting_values):
            if metric_name in metrics_dict:
                agent.report_custom_metric(
                    metrics_dict[metric_name],
                    metric_value
                )
    except Exception as exec:
        agent.logger.error("MetricReportingError: " + str(exec))
        pass


def convert_to_dict(agent=None, response=None):
    modified_response = response
    try:
        if hasattr(response, 'model_dump') and not isinstance(response, dict):
            modified_response = response.model_dump(exclude_unset=True)
    except Exception as exc:
        agent.logger.error("Cannot convert api class to dict " + str(exc))
    finally:
        return modified_response


def get_reporting_values_per_request(model_name=None, agent=None, endpoint_response=None):
    reporting_values = dict()
    # Calculating current request tokens
    try:
        reporting_values[OpenaiConstants.TOKENS_METRIC_NAME] = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=OpenaiConstants.RESPONSE_TOTAL_TOKEN_STRING
        )
        prompt_tokens = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=OpenaiConstants.RESPONSE_PROMPT_STRING
        )
        completion_tokens = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=OpenaiConstants.RESPONSE_COMPLETION_STRING
        )
    except UnsupportedResponseException as exec:
        agent.logger.error(str(exec))
        raise

    # Calculating current request cost per model
    try:
        if prompt_tokens and completion_tokens:
            reporting_values[OpenaiConstants.COST_METRIC_NAME] = get_cost_per_request(
                model_name=model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
    except UnsupportedModelException as exec:
        agent.logger.error(str(exec))
    finally:
        return reporting_values


class UnsupportedModelException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UnsupportedModelException: {self.message}"


class UnsupportedResponseException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UnsupportedResponseException: {self.message}"


class MissingReportingValuesExcepion(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"MissingReportingValuesExcepion: {self.message}"
