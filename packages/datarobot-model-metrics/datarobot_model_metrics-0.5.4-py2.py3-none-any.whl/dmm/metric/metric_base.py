#
# Copyright 2022-2024 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import numpy as np
import pandas as pd


class MetricBase(object):
    def __init__(
        self,
        name: str,
        description: str = None,
        need_predictions: bool = False,
        need_actuals: bool = False,
        need_scoring_data: bool = False,
        need_training_data: bool = False,
    ):
        self.name = name
        self.description = description
        self._need_predictions = need_predictions
        self._need_actuals = need_actuals
        self._need_scoring_data = need_scoring_data
        self._need_training_data = need_training_data

    def __str__(self):
        s = "name: {}, description: {}".format(self.name, self.description)
        s += "\nneed_training_data: {}".format(self._need_training_data)
        s += "\nneed_scoring_data:  {}".format(self._need_scoring_data)
        s += "\nneed_predictions:   {}".format(self._need_predictions)
        s += "\nneed_actuals:       {}".format(self._need_actuals)
        return s

    def need_predictions(self) -> bool:
        """
        Should return True if this metric need predictions
        :return bool:
        """
        return self._need_predictions

    def need_actuals(self) -> bool:
        """
        Should return True if this metric need actuals. If true, both predictions and acutals
        will be provided
        :return bool:
        """
        return self._need_actuals

    def need_scoring_data(self) -> bool:
        """
        Should return True if this metric need scoring data.
        :return bool:
        """
        return self._need_scoring_data

    def need_training_data(self) -> bool:
        """
        Should return True if this metric need training data.
        :return bool:
        """
        return self._need_training_data

    def fit(self, training_data: pd.DataFrame = None) -> object:
        """
        This method get access to the training data and is able to generate a context object
        which is passed to each call to the transform method.
        :param training_data:
        :return:
        """
        return None

    def score(
        self,
        scoring_data: pd.DataFrame,
        predictions: np.array,
        actuals: np.array,
        fit_ctx=None,
        metadata=None,
    ) -> float:
        raise NotImplemented

    def reduce_func(self) -> callable:
        return np.mean


class ModelMetricBase(MetricBase):
    def __init__(
        self, name: str, description: str = None, need_training_data: bool = False
    ):
        super().__init__(
            name=name,
            description=description,
            need_scoring_data=False,
            need_predictions=True,
            need_actuals=True,
            need_training_data=need_training_data,
        )

    def score(
        self,
        predictions: np.array,
        actuals: np.array,
        fit_context=None,
        metadata=None,
        scoring_data=None,
    ) -> float:
        raise NotImplemented


class DataMetricBase(MetricBase):
    def __init__(
        self, name: str, description: str = None, need_training_data: bool = False
    ):
        super().__init__(
            name=name,
            description=description,
            need_scoring_data=True,
            need_predictions=False,
            need_actuals=False,
            need_training_data=need_training_data,
        )

    def score(
        self,
        scoring_data: pd.DataFrame,
        fit_ctx=None,
        metadata=None,
        predictions=None,
        actuals=None,
    ) -> float:
        raise NotImplemented


class LLMMetricBase(MetricBase):
    def __init__(
        self, name: str, description: str = None, need_training_data: bool = False
    ):
        super().__init__(
            name=name,
            description=description,
            need_scoring_data=True,
            need_predictions=True,
            need_actuals=False,
            need_training_data=need_training_data,
        )

    def score(
        self,
        scoring_data: pd.DataFrame,
        predictions: np.array,
        fit_ctx=None,
        metadata=None,
        actuals=None,
    ) -> float:
        raise NotImplemented
