# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AzureMLTranslationDAO class."""
from azureml.metrics.common._validation import _check_seq2seq_bool, _check_seq2seq_tokenizer, \
    _check_seq2seq_list_of_list_of_str, _check_seq2seq_list_of_str
from azureml.metrics.constants import ReferenceCodes
from azureml.metrics.tasks.base.dao.azureml_dao import AzureMLDAO
from functools import cached_property


class AzureMLTranslationDAO(AzureMLDAO):

    def __init__(self, y_test, y_pred, **kwargs):
        super().__init__(y_test, y_pred, **kwargs)

    @property
    def reference_validation_str(self):
        """Returns reference validation string for Translation."""
        return ReferenceCodes.VALIDATE_TRANSLATION

    @cached_property
    def smoothing(self):
        smoothing = self.kwargs.get('smoothing', False)
        _check_seq2seq_bool(smoothing, 'smoothing', reference_code=self.reference_validation_str)
        return smoothing

    @cached_property
    def tokenizer(self):
        tokenizer = self.kwargs.get('tokenizer', None)
        if tokenizer is not None:
            _check_seq2seq_tokenizer(tokenizer, 'tokenizer', reference_code=self.reference_validation_str)
        return tokenizer

    @cached_property
    def use_static_script(self):
        use_static_script = self.kwargs.get('use_static_script', False)
        _check_seq2seq_bool(use_static_script, 'use_static_script', reference_code=self.reference_validation_str)
        return use_static_script

    def _prep_y_pred(self, y_pred):
        _check_seq2seq_list_of_str(y_pred, 'y_pred', reference_code=self.reference_validation_str)
        return y_pred

    def _prep_y_test(self, y_test):
        _check_seq2seq_list_of_list_of_str(y_test, 'y_test', reference_code=self.reference_validation_str)
        return y_test
