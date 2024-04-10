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

"""Tests for summary_utils."""

import math
import os
from typing import Any
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
import jax.numpy as jnp
import numpy as np
from paxml import base_metrics
from paxml import metric_utils
from paxml import summary_utils
import tensorflow.compat.v2 as tf


class MatcherAlmostEqual:

  def __init__(self, value: float, abs_tol: float = 1e-8):
    self._value = value
    self._abs_tol = abs_tol

  def __eq__(self, other: float) -> bool:
    return math.isclose(self._value, other, abs_tol=self._abs_tol)

  def __ne__(self, other: float) -> bool:
    return not self == other


class MatcherArrayAlmostEqual:

  def __init__(self, value: np.ndarray, abs_tol: float = 1e-8):
    self._value = value
    self._abs_tol = abs_tol

  def __eq__(self, other: np.ndarray) -> bool:
    return np.allclose(self._value, other, atol=self._abs_tol)

  def __ne__(self, other: np.ndarray) -> bool:
    return not self == other


class SummaryUtilsTest(parameterized.TestCase):

  def _get_weighted_scalars_and_clu_metrics(
      self,
      use_clu_metrics_instead_of_weighted_scalars: bool,
      values_1: jnp.ndarray,
      weights_1: jnp.ndarray,
      values_2: jnp.ndarray,
      weights_2: jnp.ndarray,
  ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    clu_metrics = None
    weighted_scalars = None
    if use_clu_metrics_instead_of_weighted_scalars:
      clu_metrics = {
          'output_0': base_metrics.WeightedScalarCluMetric.create(
              weight=weights_1, value=values_1
          ),
          'output_1': base_metrics.WeightedScalarCluMetric.create(
              weight=weights_2, value=values_2
          ),
      }
    else:
      weighted_scalars = {
          'output_0': (values_1, weights_1),
          'output_1': (values_2, weights_2),
      }
    return clu_metrics, weighted_scalars

  def _get_weighted_scalars_and_clu_metrics_1(
      self, use_clu_metrics_instead_of_weighted_scalars: bool
  ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    values_1 = jnp.array([5.0, 6.0])
    weights_1 = jnp.array([3, 2])
    values_2 = jnp.array([4.0, 7.0, 8.0])
    weights_2 = jnp.array([1, 1, 1])
    return self._get_weighted_scalars_and_clu_metrics(
        use_clu_metrics_instead_of_weighted_scalars,
        values_1,
        weights_1,
        values_2,
        weights_2,
    )

  def _get_weighted_scalars_and_clu_metrics_2(
      self, use_clu_metrics_instead_of_weighted_scalars: bool
  ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    values_3 = jnp.array([15.0, 16.0])
    weights_3 = jnp.array([13, 12])
    values_4 = jnp.array([14.0, 17.0, 18.0])
    weights_4 = jnp.array([11, 11, 11])
    return self._get_weighted_scalars_and_clu_metrics(
        use_clu_metrics_instead_of_weighted_scalars,
        values_3,
        weights_3,
        values_4,
        weights_4,
    )

  @parameterized.named_parameters(
      ('', False, False),
      ('_async', True, False),
      ('_non_async_with_clu_metrics', False, True),
      ('_async_with_clu_metrics', True, True),
  )
  def test_process_no_accumulation(
      self, is_async: bool, use_clu_metrics_instead_of_weighted_scalars: bool
  ):
    summary_writer = tf.summary.create_file_writer(
        os.path.join(absltest.get_default_test_tmpdir(), 'summary'))
    write_interval_steps = 2
    summary_handler = summary_utils.SummaryHandler(summary_writer,
                                                   write_interval_steps,
                                                   is_async=is_async)

    # We accumulate modulo N, so step 0 is special in a sense that there won't
    # be any accumulation.
    loss_1 = jnp.array([0.1, 0.15, 0.2])
    clu_metrics_1, weighted_scalars_1 = (
        self._get_weighted_scalars_and_clu_metrics_1(
            use_clu_metrics_instead_of_weighted_scalars
        )
    )
    summary_tensors_1 = {
        'summary_a_scalar': jnp.array([9.0, 8.0]),
        'summary_b_image': jnp.ones(shape=[1, 4, 4], dtype=jnp.float32),
        'summary_c_audio': jnp.zeros(shape=[10, 3], dtype=jnp.float32),
        'summary_d_histogram': jnp.array([1, 2, 3]),
    }
    steps_per_sec_1 = 37.

    loss_2 = jnp.array([0.2, 0.25, 0.3])
    clu_metrics_2, weighted_scalars_2 = (
        self._get_weighted_scalars_and_clu_metrics_2(
            use_clu_metrics_instead_of_weighted_scalars
        )
    )
    summary_tensors_2 = {
        'summary_a_scalar': jnp.array([7.0, 6.0]),
        'summary_b_image': 10 * jnp.ones(shape=[2, 3, 4], dtype=jnp.float32),
        'summary_c_audio': jnp.zeros(shape=[12, 1], dtype=jnp.float32),
        'summary_d_histogram': jnp.array([4, 5, 6]),
    }
    steps_per_sec_2 = 35.

    with mock.patch.object(
        tf.summary, 'scalar', return_value=None) as mock_tf_summary_scalar:
      with mock.patch.object(
          tf.summary, 'image', return_value=None) as mock_tf_summary_image:
        with mock.patch.object(
            tf.summary, 'audio', return_value=None) as mock_tf_summary_audio:
          with mock.patch.object(
              tf.summary, 'histogram', return_value=None
          ) as mock_tf_summary_histogram:
            if use_clu_metrics_instead_of_weighted_scalars:
              summary_handler.process(
                  step=1,
                  loss=loss_1,
                  weighted_scalars=None,
                  clu_metrics=clu_metrics_1,
                  summary_tensors=summary_tensors_1,
                  steps_per_sec=steps_per_sec_1,
              )
              summary_handler.process(
                  step=2,
                  loss=loss_2,
                  weighted_scalars=None,
                  clu_metrics=clu_metrics_2,
                  summary_tensors=summary_tensors_2,
                  steps_per_sec=steps_per_sec_2,
              )
            else:
              summary_handler.process(
                  step=1,
                  loss=loss_1,
                  weighted_scalars=weighted_scalars_1,
                  summary_tensors=summary_tensors_1,
                  steps_per_sec=steps_per_sec_1,
              )
              summary_handler.process(
                  step=2,
                  loss=loss_2,
                  weighted_scalars=weighted_scalars_2,
                  summary_tensors=summary_tensors_2,
                  steps_per_sec=steps_per_sec_2,
              )
            summary_handler.close()
    # In this test all summaries use the latest values from step 2.
    expected_loss = np.mean(loss_2).item()
    mock_tf_summary_scalar.assert_any_call('loss',
                                           MatcherAlmostEqual(expected_loss), 2)
    mock_tf_summary_scalar.assert_any_call('Steps/sec', steps_per_sec_2, 2)
    if use_clu_metrics_instead_of_weighted_scalars:
      expected_metrics_output_0 = clu_metrics_2['output_0'].compute().item()
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_0',
          MatcherAlmostEqual(expected_metrics_output_0, 1e-6),
          2,
      )
      expected_metrics_output_1 = clu_metrics_2['output_1'].compute().item()
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_1',
          MatcherAlmostEqual(expected_metrics_output_1, 1e-6),
          2,
      )
    else:
      expected_metrics_output_0_weight = np.sum(
          weighted_scalars_2['output_0'][1]
      ).item()
      expected_metrics_output_0 = (
          np.sum(
              weighted_scalars_2['output_0'][0]
              * weighted_scalars_2['output_0'][1]
          ).item()
          / expected_metrics_output_0_weight
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_0',
          MatcherAlmostEqual(expected_metrics_output_0, 1e-6),
          2,
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_0-weight',
          MatcherAlmostEqual(expected_metrics_output_0_weight),
          2,
      )
      expected_metrics_output_1_weight = np.sum(
          weighted_scalars_2['output_1'][1]
      ).item()
      expected_metrics_output_1 = (
          np.sum(
              weighted_scalars_2['output_1'][0]
              * weighted_scalars_2['output_1'][1]
          ).item()
          / expected_metrics_output_1_weight
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_1',
          MatcherAlmostEqual(expected_metrics_output_1, 1e-6),
          2,
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_1-weight',
          MatcherAlmostEqual(expected_metrics_output_1_weight),
          2,
      )

    mock_tf_summary_scalar.assert_any_call(
        'summary_a_scalar',
        MatcherAlmostEqual(
            np.mean(summary_tensors_2['summary_a_scalar']).item()
        ),
        2,
    )
    mock_tf_summary_image.assert_any_call(
        'summary_b_image/0',
        MatcherArrayAlmostEqual(np.array(summary_tensors_2['summary_b_image'])),
        2)
    mock_tf_summary_audio.assert_any_call(
        'summary_c_audio/0',
        MatcherArrayAlmostEqual(np.array(summary_tensors_2['summary_c_audio'])),
        44000, 2)
    mock_tf_summary_histogram.assert_any_call(
        'summary_d_histogram',
        MatcherArrayAlmostEqual(np.array([4, 5, 6])),
        2,
    )

  @parameterized.named_parameters(
      ('', False, False),
      ('_async', True, False),
      ('_non_async_with_clu_metrics', False, True),
      ('_async_with_clu_metrics', True, True),
  )
  def test_process_with_accumulation(
      self, is_async: bool, use_clu_metrics_instead_of_weighted_scalars: bool
  ):
    summary_writer = tf.summary.create_file_writer(
        os.path.join(absltest.get_default_test_tmpdir(), 'summary'))
    write_interval_steps = 2
    accumulate_interval_steps = 1
    summary_handler = summary_utils.SummaryHandler(summary_writer,
                                                   write_interval_steps,
                                                   accumulate_interval_steps,
                                                   is_async)

    # We accumulate modulo N, so step 0 is special in a sense that there won't
    # be any accumulation.
    loss_1 = jnp.array([0.1, 0.15, 0.2])
    clu_metrics_1, weighted_scalars_1 = (
        self._get_weighted_scalars_and_clu_metrics_1(
            use_clu_metrics_instead_of_weighted_scalars
        )
    )
    summary_tensors_1 = {
        'summary_a_scalar': jnp.array([9., 8.]),
        'summary_b_image': jnp.ones(shape=[2, 3, 4], dtype=jnp.float32),
        'summary_c_audio': jnp.zeros(shape=[10, 3], dtype=jnp.float32),
    }
    steps_per_sec_1 = 37.

    loss_2 = jnp.array([0.2, 0.25, 0.3])
    clu_metrics_2, weighted_scalars_2 = (
        self._get_weighted_scalars_and_clu_metrics_2(
            use_clu_metrics_instead_of_weighted_scalars
        )
    )
    summary_tensors_2 = {
        'summary_a_scalar': jnp.array([7., 6.]),
        'summary_b_image': 10 * jnp.ones(shape=[2, 3, 4], dtype=jnp.float32),
        'summary_c_audio': 5 * jnp.zeros(shape=[10, 3], dtype=jnp.float32),
    }
    steps_per_sec_2 = 35.

    with mock.patch.object(
        tf.summary, 'scalar', return_value=None) as mock_tf_summary_scalar:
      with mock.patch.object(
          tf.summary, 'image', return_value=None) as mock_tf_summary_image:
        with mock.patch.object(
            tf.summary, 'audio', return_value=None) as mock_tf_summary_audio:
          if use_clu_metrics_instead_of_weighted_scalars:
            summary_handler.process(
                step=1,
                loss=loss_1,
                weighted_scalars=None,
                clu_metrics=clu_metrics_1,
                summary_tensors=summary_tensors_1,
                steps_per_sec=steps_per_sec_1,
            )
            summary_handler.process(
                step=2,
                loss=loss_2,
                weighted_scalars=None,
                clu_metrics=clu_metrics_2,
                summary_tensors=summary_tensors_2,
                steps_per_sec=steps_per_sec_2,
            )
          else:
            summary_handler.process(
                step=1,
                loss=loss_1,
                weighted_scalars=weighted_scalars_1,
                summary_tensors=summary_tensors_1,
                steps_per_sec=steps_per_sec_1,
            )
            summary_handler.process(
                step=2,
                loss=loss_2,
                weighted_scalars=weighted_scalars_2,
                summary_tensors=summary_tensors_2,
                steps_per_sec=steps_per_sec_2,
            )
          summary_handler.close()
    # In this test all summaries use accumulated values over steps 1 and 2.
    expected_loss = np.mean([np.array(l) for l in [loss_1, loss_2]])
    mock_tf_summary_scalar.assert_any_call('loss',
                                           MatcherAlmostEqual(expected_loss), 2)
    expected_steps_per_sec = np.mean([steps_per_sec_1, steps_per_sec_2])
    mock_tf_summary_scalar.assert_any_call('Steps/sec', expected_steps_per_sec,
                                           2)
    if use_clu_metrics_instead_of_weighted_scalars:
      merged_clu_metrics = metric_utils.merge_clu_metrics(
          clu_metrics_1, clu_metrics_2
      )
      expected_metrics_output_0 = merged_clu_metrics['output_0'].compute()
      expected_metrics_output_1 = merged_clu_metrics['output_1'].compute()
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_0',
          MatcherAlmostEqual(expected_metrics_output_0, 1e-6),
          2,
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_1',
          MatcherAlmostEqual(expected_metrics_output_1, 1e-6),
          2,
      )
    else:
      expected_metrics_output_0_weight = np.sum(
          weighted_scalars_1['output_0'][1] + weighted_scalars_2['output_0'][1]
      ).item()
      expected_metrics_output_0 = (
          np.sum(
              weighted_scalars_1['output_0'][0]
              * weighted_scalars_1['output_0'][1]
              + weighted_scalars_2['output_0'][0]
              * weighted_scalars_2['output_0'][1]
          ).item()
          / expected_metrics_output_0_weight
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_0',
          MatcherAlmostEqual(expected_metrics_output_0, 1e-6),
          2,
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_0-weight',
          MatcherAlmostEqual(expected_metrics_output_0_weight),
          2,
      )
      expected_metrics_output_1_weight = np.sum(
          weighted_scalars_1['output_1'][1] + weighted_scalars_2['output_1'][1]
      ).item()
      expected_metrics_output_1 = (
          jnp.sum(
              weighted_scalars_1['output_1'][0]
              * weighted_scalars_1['output_1'][1]
              + weighted_scalars_2['output_1'][0]
              * weighted_scalars_2['output_1'][1]
          ).item()
          / expected_metrics_output_1_weight
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_1',
          MatcherAlmostEqual(expected_metrics_output_1, 1e-6),
          2,
      )
      mock_tf_summary_scalar.assert_any_call(
          'Metrics/output_1-weight',
          MatcherAlmostEqual(expected_metrics_output_1_weight),
          2,
      )

    summary_a_scalars = [
        summary_tensors_1['summary_a_scalar'],
        summary_tensors_2['summary_a_scalar'],
    ]
    expected_summary_a_scalar = np.mean(
        [np.array(s) for s in summary_a_scalars]
    ).item()
    mock_tf_summary_scalar.assert_any_call(
        'summary_a_scalar', MatcherAlmostEqual(expected_summary_a_scalar), 2)
    mock_tf_summary_image.assert_any_call(
        'summary_b_image/0',
        MatcherArrayAlmostEqual(np.array(summary_tensors_1['summary_b_image'])),
        2)
    mock_tf_summary_image.assert_any_call(
        'summary_b_image/0',
        MatcherArrayAlmostEqual(np.array(summary_tensors_2['summary_b_image'])),
        2)
    mock_tf_summary_audio.assert_any_call(
        'summary_c_audio/0',
        MatcherArrayAlmostEqual(np.array(summary_tensors_1['summary_c_audio'])),
        44000, 2)
    mock_tf_summary_audio.assert_any_call(
        'summary_c_audio/0',
        MatcherArrayAlmostEqual(np.array(summary_tensors_2['summary_c_audio'])),
        44000, 2)


if __name__ == '__main__':
  absltest.main()
