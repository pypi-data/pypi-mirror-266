# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Intercept boto to ensure that HTTPS is reported correctly.

"""

from __future__ import unicode_literals
from . import HTTPConnectionInterceptor
import appdynamics.agent.interceptor.utils.openai_utils as openai_utils
from appdynamics.agent.interceptor.utils.openai_utils import OpenaiConstants
from abc import ABC, abstractmethod


class ApiModel(ABC):
    @abstractmethod
    def report_metrics(self, response, reporting_values, model_name):
        pass

    @abstractmethod
    def create_metrics(self, model_name=None):
        pass


class CompletionApiModel(ApiModel):
    def __init__(self, agent):
        self.agent = agent
        self.tier_model_metrics_mapping = dict()
        self.app_model_metrics_mapping = dict()

    def report_metrics(self, response, reporting_values, model_name):
        # Reporting completion api's metrics
        modified_response = None
        try:
            # modifying response class to dict if execption not raised
            if OpenaiConstants.ERROR_METRIC_NAME not in reporting_values:
                modified_response = openai_utils.convert_to_dict(agent=self.agent, response=response)

            if modified_response:
                reporting_values.update(openai_utils.get_reporting_values_per_request(
                    model_name=model_name,
                    agent=self.agent,
                    endpoint_response=modified_response
                ))

            # Reporting indiviual tier level performance metrics
            for metrics in (self.tier_model_metrics_mapping, self.app_model_metrics_mapping):
                openai_utils.report_metrics(
                    metrics_dict=metrics[model_name],
                    reporting_values=reporting_values,
                    agent=self.agent
                )
            # Reporting indiviual app level performance metrics
            for metrics in (self.tier_all_models_metrics_mapping, self.application_all_models_metrics_mapping):
                openai_utils.report_metrics(
                    metrics_dict=metrics,
                    reporting_values=reporting_values,
                    agent=self.agent
                )

        except Exception as exec:
            self.agent.logger.error(f"""Error in sending metrics.{str(exec)} \n
            Please check completion's report_metrics method""")
            raise

    def create_metrics(self, model_name=None):
        if model_name and model_name not in self.tier_model_metrics_mapping:
            self.tier_model_metrics_mapping[model_name] = openai_utils.initialize_metrics(
                metric_prefix_path=OpenaiConstants.TIER_METRIC_PATH +
                OpenaiConstants.METRIC_PATH_SEGREGATOR + model_name,
                metric_dict=openai_utils.METRICS_DICT
            )
        if model_name and model_name not in self.app_model_metrics_mapping:
            self.app_model_metrics_mapping[model_name] = openai_utils.initialize_metrics(
                metric_prefix_path=OpenaiConstants.APPLICATION_METRIC_PATH,
                metric_prefix=OpenaiConstants.OPENAI_PREFIX,
                metric_suffix=OpenaiConstants.METRIC_NAME_SEGREGATOR + model_name,
                metric_dict=openai_utils.METRICS_DICT
            )
        self.tier_all_models_metrics_mapping = openai_utils.initialize_metrics(
            metric_prefix_path=OpenaiConstants.TIER_METRIC_PATH,
            metric_suffix=OpenaiConstants.METRIC_NAME_SEGREGATOR + OpenaiConstants.ALL_MODELS_STRING,
            metric_dict=openai_utils.METRICS_DICT,
        )
        self.application_all_models_metrics_mapping = openai_utils.initialize_metrics(
            metric_prefix_path=OpenaiConstants.APPLICATION_METRIC_PATH,
            metric_prefix=OpenaiConstants.OPENAI_PREFIX,
            metric_suffix=OpenaiConstants.METRIC_NAME_SEGREGATOR + OpenaiConstants.ALL_MODELS_STRING,
            metric_dict=openai_utils.METRICS_DICT,
        )


class ModerationApiModel(ApiModel):
    def __init__(self, agent):
        self.agent = agent
        self.moderation_model_metrics_mapping = dict()

    def report_metrics(self, response, reporting_values, model_name):
        # Reporting completion api's metrics
        modified_response = None
        try:
            # modifying response class to dict
            if OpenaiConstants.ERROR_METRIC_NAME not in reporting_values:
                modified_response = openai_utils.convert_to_dict(agent=self.agent, response=response)

            if modified_response:
                reporting_values[OpenaiConstants.FLAGGED_QUERIES_METRIC_NAME] = openai_utils.prompt_flagged_counter(
                    agent=self.agent,
                    response=modified_response.get('results')
                )
                reporting_values[OpenaiConstants.TOTAL_QUERIES_METRIC_NAME] = len(modified_response.get('results', []))
                reporting_values.update(openai_utils.get_moderation_category_values(
                    input_response=modified_response,
                    agent=self.agent
                ))
            # Reporting moderation api metrics tier level
            openai_utils.report_metrics(
                metrics_dict=self.moderation_model_metrics_mapping[model_name],
                reporting_values=reporting_values,
                agent=self.agent
            )
            openai_utils.report_metrics(
                metrics_dict=self.moderartion_all_tier_metrics_mapping,
                reporting_values=reporting_values,
                agent=self.agent
            )

            # Reporting moderation api metrics application level
            openai_utils.report_metrics(
                metrics_dict=self.moderation_app_level_metrics_mapping,
                reporting_values=reporting_values,
                agent=self.agent
            )
        except Exception as exec:
            self.agent.logger.error(f"""Error in sending metrics. {str(exec)} \n
            Please check moderation's report_metrics method""")
            raise

    def create_metrics(self, model_name=None):
        if model_name and model_name not in self.moderation_model_metrics_mapping:
            self.moderation_model_metrics_mapping[model_name] = openai_utils.initialize_metrics(
                metric_prefix_path=OpenaiConstants.MODERATION_METRIC_PATH,
                metric_dict=openai_utils.MODERATION_METRIC_DICT,
            )
            self.moderation_model_metrics_mapping[model_name].update(
                openai_utils.initialize_metrics(
                    metric_prefix_path=OpenaiConstants.MODERATION_TIER_LEVEL_PREFIX,
                    metric_dict=openai_utils.MODERATION_CATEGORY_METRICS,
                )
            )

        self.moderation_app_level_metrics_mapping = openai_utils.initialize_metrics(
            metric_prefix_path=OpenaiConstants.APPLICATION_METRIC_PATH,
            metric_prefix=OpenaiConstants.OPENAI_PREFIX,
            metric_suffix=OpenaiConstants.METRIC_NAME_SEGREGATOR + OpenaiConstants.MODERATION,
            metric_dict=openai_utils.MODERATION_METRIC_DICT,
        )
        self.moderation_app_level_metrics_mapping.update(
            openai_utils.initialize_metrics(
                metric_prefix_path=OpenaiConstants.APPLICATION_METRIC_PATH,
                metric_prefix=OpenaiConstants.MODERATION_APPLICATION_LEVEL_PREFIX,
                metric_suffix=OpenaiConstants.METRIC_NAME_SEGREGATOR + OpenaiConstants.MODERATION,
                metric_dict=openai_utils.MODERATION_CATEGORY_METRICS,
            )
        )
        self.moderartion_all_tier_metrics_mapping = openai_utils.initialize_metrics(
            metric_prefix_path=OpenaiConstants.TIER_METRIC_PATH,
            metric_suffix=OpenaiConstants.METRIC_NAME_SEGREGATOR + OpenaiConstants.ALL_MODELS_STRING,
            metric_dict=openai_utils.METRICS_DICT,
        )


class OpenAiMethodInstrumentor(HTTPConnectionInterceptor):
    def __init__(self, agent, cls):
        super(OpenAiMethodInstrumentor, self).__init__(agent, cls)
        self.completionApiModelInstance = CompletionApiModel(self.agent)
        self.moderationApiModelInstance = ModerationApiModel(self.agent)
        self.completionApiModelInstance.create_metrics()
        self.moderationApiModelInstance.create_metrics()

    def make_exit_call(self):
        exit_call = None
        base_url = None
        with self.log_exceptions():
            bt = self.bt
            if bt:
                """
                For getting the openai endpoint in openai >= 1
                we are getting the openai class instance in 0th index of
                any create api, from where we are fetching the base_url or the
                endpoint its calling to. Below in self.openai_client which
                stores the openai client instance during interception
                """
                # pylint: disable=E1101
                if self.openai_major_version >= 1 and self.openai_client \
                        and hasattr(self.openai_client, '_client') \
                        and hasattr(self.openai_client._client, 'base_url'):
                    base_url = self.openai_client._client.base_url
                host, port, scheme, url = openai_utils.get_backend_details(
                    base_url=base_url
                )
                backend = self.get_backend(
                    host=host,
                    port=port,
                    scheme=scheme,
                    url=url
                )
                if backend:
                    exit_call = self.start_exit_call(bt, backend)
        self.end_exit_call(exit_call=exit_call)


class AsyncCreateInstrumentor(OpenAiMethodInstrumentor):
    def __init__(self, agent, cls, openai_major_version):
        self.openai_major_version = openai_major_version
        super().__init__(agent, cls)

    async def _moderation_acreate(self, acreate, *args, **kwargs):
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        moderation_acreate_response = dict()
        reporting_values[OpenaiConstants.CALLS_METRIC_NAME] = 1
        self.moderationApiModelInstance.create_metrics(model_name=OpenaiConstants.MODERATION)
        try:
            moderation_acreate_response = await acreate(*args, **kwargs)
        except:
            reporting_values[OpenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            self.make_exit_call()
            try:
                self.moderationApiModelInstance.report_metrics(
                    response=moderation_acreate_response,
                    reporting_values=reporting_values,
                    model_name=OpenaiConstants.MODERATION
                )
            except:
                return moderation_acreate_response
            reporting_values.clear()
            # returning response
        return moderation_acreate_response

    async def _create(self, create, *args, **kwargs):
        create_response = await self._acreate(create, *args, **kwargs)
        return create_response

    async def _acreate(self, acreate, *args, **kwargs):
        if 'moderation' in acreate.__module__.lower():
            acreate_response = await self._moderation_acreate(acreate, *args, **kwargs)
            return acreate_response
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        acreate_response = dict()
        reporting_values[OpenaiConstants.CALLS_METRIC_NAME] = 1
        model = kwargs.get('model') or kwargs.get('engine')
        # creating model specfic metrics
        self.completionApiModelInstance.create_metrics(model_name=model)

        try:
            acreate_response = await acreate(*args, **kwargs)
        except:
            reporting_values[OpenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            self.make_exit_call()
            try:
                self.completionApiModelInstance.report_metrics(
                    response=acreate_response,
                    reporting_values=reporting_values,
                    model_name=model
                )
            except:
                return acreate_response
            reporting_values.clear()
        # returning response
        return acreate_response


class SyncCreateInstrumentor(OpenAiMethodInstrumentor):
    def __init__(self, agent, cls, openai_major_version):
        self.openai_major_version = openai_major_version
        super().__init__(agent, cls)

    def _moderation_create(self, create, *args, **kwargs):
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        moderation_create_response = dict()
        reporting_values[OpenaiConstants.CALLS_METRIC_NAME] = 1
        self.moderationApiModelInstance.create_metrics(model_name=OpenaiConstants.MODERATION)
        try:
            moderation_create_response = create(*args, **kwargs)
        except:
            reporting_values[OpenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            self.make_exit_call()
            try:
                self.moderationApiModelInstance.report_metrics(
                    response=moderation_create_response,
                    reporting_values=reporting_values,
                    model_name=OpenaiConstants.MODERATION
                )
            except:
                return moderation_create_response
            reporting_values.clear()
            # returning response
        return moderation_create_response

    def _create(self, create, *args, **kwargs):
        if 'moderation' in create.__module__.lower():
            return self._moderation_create(create, *args, **kwargs)
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        create_response = dict()
        reporting_values[OpenaiConstants.CALLS_METRIC_NAME] = 1
        model = kwargs.get('model') or kwargs.get('engine')
        # creating model specfic metrics
        self.completionApiModelInstance.create_metrics(model_name=model)
        try:
            create_response = create(*args, **kwargs)
        except:
            reporting_values[OpenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            self.make_exit_call()
            try:
                self.completionApiModelInstance.report_metrics(
                    response=create_response,
                    reporting_values=reporting_values,
                    model_name=model
                )
            except:
                return create_response
        reporting_values.clear()
        # returning response
        return create_response


def intercept_openai(agent, mod):
    openai_major_version = int(mod.VERSION.split(".")[0])
    # for openai version 0.x or lower
    if openai_major_version <= 0:
        # create instrumentation
        SyncCreateInstrumentor(agent, mod.Completion, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.ChatCompletion, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.Moderation, openai_major_version).attach("create")

        # async create instrumentation
        AsyncCreateInstrumentor(agent, mod.Completion, openai_major_version).attach("acreate")
        AsyncCreateInstrumentor(agent, mod.ChatCompletion, openai_major_version).attach("acreate")
        AsyncCreateInstrumentor(agent, mod.Moderation, openai_major_version).attach("acreate")

    else:
        # create instrumentation
        SyncCreateInstrumentor(agent, mod.resources.Completions, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.resources.chat.Completions, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.resources.Moderations, openai_major_version).attach("create")

        # async create instrumentation
        AsyncCreateInstrumentor(agent, mod.resources.AsyncCompletions, openai_major_version).attach("create")
        AsyncCreateInstrumentor(agent, mod.resources.chat.AsyncCompletions, openai_major_version).attach("create")
        AsyncCreateInstrumentor(agent, mod.resources.AsyncModerations, openai_major_version).attach("create")
