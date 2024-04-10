# coding=utf-8
# Copyright 2022 The Pax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Interfaces for AutoML for PAX."""

from __future__ import annotations

import abc
import dataclasses
import enum
import inspect
import re
from typing import Any, Callable, Sequence, Type

from praxis import base_hyperparams
from praxis import pax_fiddle
import pyglove as pg


MetricAggregationFn = Callable[[Sequence[float]], float]


class BaseAlgorithm(
    base_hyperparams.FiddleBaseParameterizable, metaclass=abc.ABCMeta
):
  """Base class for search algorithms."""

  @abc.abstractmethod
  def __call__(self) -> pg.DNAGenerator:
    """Returns a PyGlove DNAGenerator."""


class BaseEarlyStoppingPolicy(
    base_hyperparams.FiddleBaseParameterizable, metaclass=abc.ABCMeta
):
  """Base class for population-wise early stopping policy."""

  @abc.abstractmethod
  def __call__(self) -> pg.tuning.EarlyStoppingPolicy:
    """Returns a PyGlove early stopping policy."""


class BaseReward(
    base_hyperparams.FiddleBaseParameterizable, metaclass=abc.ABCMeta
):
  """Base class for reward functions."""

  @abc.abstractmethod
  def __call__(self, metrics_dict: dict[str, float], global_step: int) -> float:
    """Returns a float value as reward from a dict of metrics."""

  @property
  @abc.abstractmethod
  def used_metrics(self) -> Sequence['Metric']:
    """Returns `automl.Metric` objects used for computing current reward."""

  @property
  def needs_train(self) -> bool:
    """Returns True if current reward needs training metrics."""
    return any(m.is_train_metric for m in self.used_metrics)

  @property
  def needs_eval(self) -> bool:
    """Returns True if current reward needs eval metrics."""
    return any(m.is_eval_metric for m in self.used_metrics)

  @property
  def needs_decode(self) -> bool:
    """Returns True if current reward needs decoding metrics."""
    return any(m.is_decode_metric for m in self.used_metrics)


class CrossStepMetricAggregator(
    base_hyperparams.FiddleBaseParameterizable, metaclass=abc.ABCMeta
):
  """Aggregator for gathering metrics across multiple steps."""

  @abc.abstractmethod
  def __call__(
      self, metrics_across_steps: Sequence[tuple[int, dict[str, float]]]
  ) -> dict[str, float]:
    """Aggregates metrics across multiple steps.

    Args:
      metrics_across_steps: A sequence of tuple (step, metrics).

    Returns:
      An aggregated metric dict used for final reward computing.
    """


# To avoid introducing dependency on base_experiment,
# we use Any as its PyType annotation for now.
BaseExperiment = Any


@dataclasses.dataclass
class SearchHParams:
  """Hyperparameters for an AutoML search.

  Attributes:
    search_algorithm: Hyperparameters for search algorithm.
    search_reward: Hyperparameters for search reward. If None, 0 will be used as
      objective, which shall be used only for grid search or random search.
    early_stopping: An optional population-wise early stopping policy. If None,
      no population-wise early stopping policy will be used, though users still
      can raise `automl.EarlyStoppingError` to early terminate a a single trial
      during training/evaluation.
    cross_step_metric_aggregator: Hyperparameters for cross-step metric
      aggregator. If None, `automl.LastReportedMetricValues` will be used.
    max_num_trials: Max number of trials for the search.
    errors_to_skip: An optional field to specify on what errors the trial should
      be skipped. It's in the form of a list of (ExceptionType) or
      (ExceptionType, regexForError). For example, if users specify:
      `[RuntimeError, (Exception, 'XLACompilation.*')]`, the trails that
      RuntimeError or errors that match 'XLACompilation.*' will be treated as to
      skip.
    prior_study_ids: An optional list of Vizier study GUIDs to warm up current
      search. All completed trials from previous studies will be feedback to the
      controller via the `pg.DNAGenerator.recover` interface.
    add_prior_trials: If True, trials from previous studies will be copied to
      current study. Effective only when `prior_study_ids` is set.
    add_experiment_config_to_metadata: If True (default), serialized experiment
      config will be added to trial metadata for helping meta-learning later. If
      the study will be very large and users don't want to store the experiment
      config, set it to False.
    treats_early_stopped_trials_as_done: If True, early stopped trials will be
      treated as done, whose rewards will be fed back to the controller, except
      for those trials who haven't added any measurements.
    train_to_end: If True, training will not be stopped until it reaches
      `num_train_steps`. If False, training will be stopped when there is no
      further eval/decode steps.
    enable_dataset_tuning: If True, include the training data pipeline in search
      space inspection.
    enable_partitioner_tuning: If True, include the partitioner in search space
      inspection.
    enable_train_programs_tuning: If True, include the train programs in search
      space inspection.
    vizier_service_endpoint: Vizier service endpoint. This is used for debugging
      only.
  """
  search_algorithm: pax_fiddle.Config[BaseAlgorithm] | None = None
  search_reward: pax_fiddle.Config[BaseReward] | None = None
  early_stopping: pax_fiddle.Config[BaseEarlyStoppingPolicy] | None = None
  cross_step_metric_aggregator: pax_fiddle.Config[
      CrossStepMetricAggregator
  ] | None = None
  max_num_trials: int = 1000000
  errors_to_skip: list[Type[Exception] | tuple[Type[Exception], str]] | None = (
      None
  )
  prior_study_ids: list[int] | None = None
  add_prior_trials: bool = False
  add_experiment_config_to_metadata: bool = True
  treats_early_stopped_trials_as_done: bool = False
  train_to_end: bool = False
  enable_dataset_tuning: bool = False
  enable_partitioner_tuning: bool = False
  enable_train_programs_tuning: bool = False
  vizier_service_endpoint: str | None = None


class MetricType(enum.Enum):
  """Metric type for AutoML search."""
  CUSTOM = 0
  TRAIN_METRICS = 1
  EVAL_TRAIN_METRICS = 2
  EVAL_METRICS = 3
  EVAL_SCORING_METRICS = 4
  DECODE_METRICS = 5

  @classmethod
  def metric_schema(cls, metric_type: 'MetricType'):
    """Returns the metric schema in tuple (category, section)."""
    if metric_type == MetricType.CUSTOM:
      return ('', '')
    elif metric_type == MetricType.TRAIN_METRICS:
      return ('train', '')
    elif metric_type == MetricType.EVAL_TRAIN_METRICS:
      return ('eval_train', 'metrics')
    elif metric_type == MetricType.EVAL_METRICS:
      return ('eval_test', 'metrics')
    elif metric_type == MetricType.EVAL_SCORING_METRICS:
      return ('eval_test', 'scoring_eval')
    elif metric_type == MetricType.DECODE_METRICS:
      return ('decode_test', '')
    else:
      assert False, 'Should never happen'

  @classmethod
  def applies_to_multiple_datasets(cls, metric_type: 'MetricType'):
    """Returns True if a metric can be applied to multiple datasets."""
    return metric_type in _MULTI_DATASET_METRIC_TYPES


_MULTI_DATASET_METRIC_TYPES = frozenset([
    MetricType.EVAL_METRICS,
    MetricType.EVAL_SCORING_METRICS,
    MetricType.DECODE_METRICS,
])


class MetricAggregator(str, enum.Enum):
  """Builtin metric aggregator."""
  MAX = 0
  MIN = 1
  AVERAGE = 2
  SUM = 3


@dataclasses.dataclass
class Metric:
  """Representing a metric for tuning.

  Attributes:
    metric_type: Type of the tuning metric.
    metric_name: Name of the metric.
    dataset_name: Dataset name. If None, the metric is either not
      dataset-specific or there is only one dataset for that metric type so the
      name can be omitted.
    sub_experiment_id: Sub-experiment ID. If None, the metric will match
      all metrics from all sub-experiments.
    aggregator: Optional metric aggregation at a single step, which
      will be used to obtain a single value from multiple matched metric items
      based on current Metric specification. It can be a value from enum
      `MetricAggregator` or a callable object. If None, `Metric.get_value` will
      raise error when there are multiple matched items.
  """
  metric_name: str
  metric_type: MetricType = MetricType.CUSTOM
  dataset_name: str | None = None
  sub_experiment_id: str | None = None
  aggregator: MetricAggregator | Callable[[Sequence[float]], float] | None = (
      None
  )

  def __post_init__(self):
    self._metric_key_regex = re.compile(self.pattern, re.IGNORECASE)
    if self.aggregator is None:
      self._aggregator = None
    elif self.aggregator == MetricAggregator.MAX:
      self._aggregator = max
    elif self.aggregator == MetricAggregator.MIN:
      self._aggregator = min
    elif self.aggregator == MetricAggregator.AVERAGE:
      self._aggregator = lambda xs: sum(xs) / len(xs)
    elif self.aggregator == MetricAggregator.SUM:
      self._aggregator = sum
    elif callable(self.aggregator):
      self._aggregator = self.aggregator
    else:
      raise ValueError(
          f'Unsupported aggregator {self.aggregator}. '
          f'Expecting a value from `automl.MetricAggregator` enum'
          f'or Callable[[Sequence[float]], float].')

  @property
  def pattern(self):
    """Returns key pattern."""
    category, section = MetricType.metric_schema(self.metric_type)
    prefix = ''
    if MetricType.applies_to_multiple_datasets(self.metric_type):
      dataset_pattern = self.dataset_name or '[^/]+'
      assert category, category
      prefix = f'{category}_{dataset_pattern}/'
    elif category:
      prefix = f'{category}/'
    if section:
      prefix = f'{prefix}{section}/'

    if self.sub_experiment_id is None:
      suffix = '(:.+)?'
    else:
      suffix = f':{self.sub_experiment_id}'
    return f'^{prefix}{self.metric_name}{suffix}$'

  @property
  def is_train_metric(self) -> bool:
    """Returns True if current metric is train metric."""
    p = self.pattern
    return p.startswith(('^train', '^num_params'))

  @property
  def is_eval_train_metric(self) -> bool:
    """Returns True if current metric is eval train metric."""
    return self.pattern.startswith('^eval_train')

  @property
  def is_eval_metric(self) -> bool:
    """Returns True if current metric is eval metric."""
    p = self.pattern
    return p.startswith(('^eval_test', '^eval_steps'))

  @property
  def is_decode_metric(self) -> bool:
    """Returns True if current metric is decode metric."""
    p = self.pattern
    return p.startswith(('^decode_test', '^decode_steps'))

  @property
  def applies_to_multiple_datasets(self):
    """Returns True if current metric is dataset specific."""
    return (MetricType.applies_to_multiple_datasets(self.metric_type) and
            self.dataset_name is None)

  def match_items(
      self, metric_dict: dict[str, float]
  ) -> list[tuple[str, float]]:
    """Gets matched items of current metric from a metric dict."""
    return [(k, v)
            for k, v in metric_dict.items()
            if self._metric_key_regex.match(k)]

  def get_values(self, metric_dict: dict[str, float]) -> list[float]:
    """Gets the value of current metric from a metric dict."""
    return [v for k, v in self.match_items(metric_dict)]

  def get_value(self, metric_dict: dict[str, float]) -> float:
    """Gets the only value for current metric from a metric dict."""
    items = list(self.match_items(metric_dict))
    if not items:
      raise KeyError(
          f'Metric {self.pattern!r} does not match with any metrics. '
          f'Available metrics are: {list(metric_dict.keys())}.')
    if len(items) != 1:
      if self._aggregator is not None:
        return self._aggregator([m[1] for m in items])
      raise ValueError(
          f'Found multiple metrics that match {self.pattern!r} while '
          f'aggregator is not specified: {items}.')
    return items[0][1]

  # Class method for creating custom metric types.
  @classmethod
  def train_steps_per_second(
      cls,
      sub_experiment_id: str | None = None,
      aggregator: str | Callable[[Sequence[float]], float] | None = None,
  ) -> 'Metric':
    """Returns metric for training steps per second."""
    return Metric('train_steps_per_sec',
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)

  @classmethod
  def eval_steps_per_second(
      cls,
      sub_experiment_id: str | None = None,
      aggregator: str | Callable[[Sequence[float]], float] | None = None,
  ) -> 'Metric':
    """Returns metric for evaluation steps per second."""
    return Metric('eval_steps_per_sec',
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)

  @classmethod
  def decode_steps_per_second(
      cls,
      sub_experiment_id: str | None = None,
      aggregator: str | MetricAggregationFn | None = None,
  ) -> 'Metric':
    """Returns metric for `decode_steps_per_second`."""
    return Metric('decode_steps_per_sec',
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)

  @classmethod
  def num_params(
      cls,
      sub_experiment_id: str | None = None,
      aggregator: str | MetricAggregationFn | None = None,
  ) -> 'Metric':
    """Returns metric for `num_params`."""
    return Metric('num_params',
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)

  # Class methods for creating eval metric types.
  @classmethod
  def train(
      cls,
      metric_name: str,
      sub_experiment_id: str | None = None,
      aggregator: str | MetricAggregationFn | None = None,
  ) -> 'Metric':
    """Returns a metric from evaluation on the training dataset."""
    return Metric(metric_name,
                  MetricType.TRAIN_METRICS,
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)

  @classmethod
  def eval_train(
      cls,
      metric_name: str,
      sub_experiment_id: str | None = None,
      aggregator: str | MetricAggregationFn | None = None,
  ) -> 'Metric':
    """Returns a metric from evaluation on the training dataset."""
    return Metric(metric_name,
                  MetricType.EVAL_TRAIN_METRICS,
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)

  @classmethod
  def eval(
      cls,
      metric_name: str,
      dataset_name: str | None = None,
      sub_experiment_id: str | None = None,
      aggregator: str | MetricAggregationFn | None = None,
  ) -> 'Metric':
    """Returns a metric from evaluation on the test dataset."""
    return Metric(metric_name,
                  MetricType.EVAL_METRICS,
                  dataset_name,
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)

  @classmethod
  def eval_scoring(
      cls,
      metric_name: str,
      dataset_name: str | None = None,
      sub_experiment_id: str | None = None,
      aggregator: str | MetricAggregationFn | None = None,
  ) -> 'Metric':
    """Returns a metric from evaluation on the test dataset."""
    return Metric(metric_name,
                  MetricType.EVAL_SCORING_METRICS,
                  dataset_name,
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)

  @classmethod
  def decode(
      cls,
      metric_name: str,
      dataset_name: str | None = None,
      sub_experiment_id: str | None = None,
      aggregator: str | MetricAggregationFn | None = None,
  ) -> 'Metric':
    """Returns a metric or processed metric from a decode dataset."""
    return Metric(metric_name,
                  MetricType.DECODE_METRICS,
                  dataset_name,
                  sub_experiment_id=sub_experiment_id,
                  aggregator=aggregator)


def enable_class_level_hyper_primitives(cls: Type[Any]) -> None:
  """Enable class-level hypers for a BaseExperiment subclass."""

  def create_hyper_property(name: str, hyper: pg.hyper.HyperPrimitive):
    attr_name = f'_PROPERTY_{name}'
    hyper_kwargs = dict(hyper.sym_init_args)
    if 'name' not in hyper_kwargs or hyper_kwargs['name'] is None:
      hyper_kwargs['name'] = name

    def getter(x):
      if hasattr(x, attr_name):
        return getattr(x, attr_name)
      return hyper.__class__(**hyper_kwargs)  # pytype: disable=not-instantiable

    def setter(x, v):
      setattr(x, attr_name, v)

    return property(getter, setter)

  for name, hyper in inspect.getmembers(
      cls, lambda x: isinstance(x, pg.hyper.HyperPrimitive)
  ):
    setattr(cls, name, create_hyper_property(name, hyper))
