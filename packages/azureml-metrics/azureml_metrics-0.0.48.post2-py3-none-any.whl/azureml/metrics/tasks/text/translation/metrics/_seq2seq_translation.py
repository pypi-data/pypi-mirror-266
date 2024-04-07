# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definitions for Machine Translation metrics."""
import os
import logging

from abc import abstractmethod
from typing import Any

from azureml.metrics.common._metric_base import Metric, ScalarMetric
from azureml.metrics.common.azureml_output_dao import AzureMLOutput
from azureml.metrics.common.utilities import retry
from azureml.metrics import constants
from azureml.metrics.common.import_utilities import load_evaluate
from azureml.metrics.tasks.text.translation.dao.azureml_translation_dao import (
    AzureMLTranslationDAO,
)

logger = logging.getLogger(__name__)


class Seq2SeqTranslationMetric(Metric):
    """Base class for Sequence to Sequence Translation metric"""

    def __init__(self, metrics_data: AzureMLTranslationDAO) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param tokenizer: function that takes input a string, and returns a list of tokens
        :params aggregator: Boolean to indicate whether to aggregate scores
        :params stemmer: Boolean to indicate whether to use Porter stemmer for word suffixes
        """
        self.metrics_data = metrics_data
        super().__init__()

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...


class Bleu(Seq2SeqTranslationMetric, ScalarMetric):
    """Wrapper class for BLEU metric for Sequence to Sequence NLG Tasks"""

    hf_bleu = None

    def compute(self, **kwargs) -> Any:
        """Compute the score for the metric."""
        self.load_bleu()

        output = AzureMLOutput()

        metrics = kwargs.get('metrics', self.metrics_data.metrics)
        for metric in metrics:
            bleu_args = {
                "max_order": constants.Metric.TRANSLATION_NGRAM_MAP[metric],
                "smooth": self.metrics_data.smoothing,
            }
            if self.metrics_data.tokenizer:
                bleu_args.update({"tokenizer": self.metrics_data.tokenizer})
            metrices = Bleu.hf_bleu.compute(
                predictions=self.metrics_data.y_pred,
                references=self.metrics_data.y_test,
                **bleu_args
            )

            output.add_value(metric, metrices['bleu'])
        return output

    @retry(
        max_attempts=constants.RetryConstants.MAX_ATTEMPTS,
        delay=constants.RetryConstants.DELAY_TIME,
    )
    def load_bleu(self):
        evaluate = load_evaluate()
        if Bleu.hf_bleu is None:
            if self.metrics_data.use_static_script is True:
                current_file_path = os.path.abspath(__file__)
                bleu_directory_path = os.path.join(os.path.dirname(current_file_path), 'bleu')
                # get the path to the static script
                Bleu.hf_bleu = evaluate.load(bleu_directory_path)
                logger.info("loading bleu using static script")
            else:
                Bleu.hf_bleu = evaluate.load("bleu")
                logger.info("loading bleu using evaluate library")
