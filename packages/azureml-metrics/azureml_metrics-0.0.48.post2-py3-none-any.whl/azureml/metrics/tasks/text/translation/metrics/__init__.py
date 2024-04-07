# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.metrics import constants
from azureml.metrics.common.metrics_registry import MetricsRegistry
from azureml.metrics.tasks.text.translation.metrics import _seq2seq_translation
from azureml.metrics.tasks.text.translation.dao.azureml_translation_dao import AzureMLTranslationDAO


def register_translation_metrics():
    MetricsRegistry.register(constants.Metric.TranslationBleu_1, _seq2seq_translation.Bleu,
                             AzureMLTranslationDAO)
    MetricsRegistry.register(constants.Metric.TranslationBleu_2, _seq2seq_translation.Bleu,
                             AzureMLTranslationDAO)
    MetricsRegistry.register(constants.Metric.TranslationBleu_3, _seq2seq_translation.Bleu,
                             AzureMLTranslationDAO)
    MetricsRegistry.register(constants.Metric.TranslationBleu_4, _seq2seq_translation.Bleu,
                             AzureMLTranslationDAO)


register_translation_metrics()
