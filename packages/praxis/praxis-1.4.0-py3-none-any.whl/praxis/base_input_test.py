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

"""Tests for base_input."""

import dataclasses
import itertools
import os
import pickle
import typing
from typing import Any, Type
from unittest import mock

from absl import flags
from absl.testing import absltest
from absl.testing import parameterized
import fiddle as fdl
import jax
from lingvo.core import base_input_generator
from lingvo.core import generic_input
from lingvo.core import py_utils as tf_py_utils
import numpy as np
from praxis import base_hyperparams
from praxis import base_input
from praxis import pax_fiddle
from praxis import py_utils
from praxis import test_utils
import tensorflow.compat.v2 as tf

FLAGS = flags.FLAGS
instantiate = base_hyperparams.instantiate


class TestInput(base_input.BaseInput):
  _iter: Any = dataclasses.field(init=False, repr=False)
  shuffle: bool = True
  dataset_with_undef_dimension: bool = False

  def __post_init__(self):
    super().__post_init__()
    self.dataset = self._get_dataset()  # Updates BaseInput.dataset.
    self._iter = iter(self.dataset)

  def get_next(self) -> py_utils.NestedMap:
    assert tf.compat.v1.executing_eagerly()
    ret = self._iter.get_next()
    return tf.nest.map_structure(lambda x: x.numpy(), ret)

  def reset(self):
    if self.reset_for_eval:
      self._iter = iter(self.dataset)

  def _to_nested_map(self, x) -> py_utils.NestedMap:
    t = tf.ones(shape=[4], dtype=tf.int32) * tf.cast(x, dtype=tf.int32)
    return py_utils.NestedMap(data=t)

  def _get_dataset(self):
    if self.dataset_with_undef_dimension:
      # Creates a TF dataset with undefined (None) dimension.
      def data_generator():
        for i in range(10):
          yield [[i]]

      return tf.data.Dataset.from_generator(
          data_generator,
          output_signature=tf.TensorSpec(shape=(None, 1), dtype=tf.int32),
      )

    d = tf.data.Dataset.range(10)
    d = d.shard(self.num_infeed_hosts, self.infeed_host_index)
    if self.shuffle:
      d = d.shuffle(10, seed=self.input_random_seed).repeat(-1)
    if self.reset_for_eval:
      d = d.take(self.batch_size * 2)
    d = d.map(self._to_nested_map)

    # Sets drop_remainder=True to fix the batch dimension size, to be used in
    # the shape validation test. Otherwise the batch dimension will be non-fixed
    # because the last batch could have a smaller size.
    d = d.batch(self.batch_size, drop_remainder=True)
    return d


class TestInputCheckpointable(TestInput):

  def __post_init__(self):
    super().__post_init__()
    self._state = 0

  def get_next(self) -> py_utils.NestedMap:
    self._state += 1
    return super().get_next()

  def reset(self):
    if self.reset_for_eval:
      self._iter = iter(self.dataset)
      self._state = 0

  def _get_state_internal(self) -> bytes:
    return str(self._state).encode()

  def _set_state_internal(self, state: bytes):
    self._state = int(state.decode())
    self._iter = iter(self.dataset.skip(self._state))


class LingvoInput(base_input_generator.BaseInputGeneratorFromFiles):

  def _DataSourceFromFilePattern(
      self,
      file_pattern,
      input_source_weights=None,
      input_source_id_offset=0,
      **extra_input_kwargs,
  ):
    p = self.params
    assert not tf.compat.v1.executing_eagerly()
    assert tf.compat.v1.executing_eagerly_outside_functions()

    def _process(source_id, record):
      del source_id
      num = tf.strings.to_number(record, tf.int32)
      if not tf_py_utils.use_tpu():
        num = num * num
      return py_utils.NestedMap(num=num), 1

    batch_size = p.batch_size or 2
    inputs, _ = generic_input.GenericInput(
        processor=_process,
        file_pattern=file_pattern,
        file_random_seed=p.file_random_seed,
        require_sequential_order=bool(
            self.cluster.require_sequential_input_order),
        repeat_count=p.repeat_count,
        file_buffer_size=32,
        file_parallelism=1,
        bucket_upper_bound=[10],
        bucket_batch_limit=[batch_size])
    return inputs


def _get_test_dataset(num: int) -> tf.data.Dataset:

  def to_map(i: int):
    return {'a': {'b': [i]}, 'data': [i]}

  return tf.data.Dataset.range(num).map(to_map)


TestDataset = base_input_generator.DefineTFDataInput('TestDataset',
                                                     _get_test_dataset)


class TestDatasetOverride(TestDataset):

  def GetPreprocessedInputBatch(self) -> py_utils.NestedMap:
    batch = super().GetPreprocessedInputBatch()
    assert isinstance(batch, py_utils.NestedMap)
    batch.data2 = batch.data * 2 + 1
    return batch


class InputTest(test_utils.TestCase):

  def test_lingvo_input(self):
    tmp = os.path.join(FLAGS.test_tmpdir, 'tmptest')
    batch_size = 2
    num_batches = 10
    num_data = batch_size * num_batches
    with tf.io.TFRecordWriter(tmp) as w:
      for i in range(num_data):
        w.write(('%04d' % i).encode('utf-8'))

    p = pax_fiddle.Config(base_input.LingvoInputAdaptor)
    p.input = LingvoInput.Params()
    p.input.file_pattern = 'tfrecord:' + tmp
    p.input.file_random_seed = 0
    p.input.repeat_count = 1
    p.reset_for_eval = True
    # To set require_sequential_input_order to True
    p.is_training = False
    p.cluster_do_eval = True
    inp = instantiate(p)
    for i in range(num_batches):
      batch = inp.get_next()
      self.assertArraysEqual(
          np.array([2 * i, 2 * i + 1], dtype=np.int32), batch.num)
    with self.assertRaisesRegex(tf.errors.OutOfRangeError,
                                'SequentialRecordYielder reached 1 repeat'):
      inp.get_next()
    inp.reset()
    for i in range(num_batches):
      batch = inp.get_next()
      self.assertArraysEqual(
          np.array([2 * i, 2 * i + 1], dtype=np.int32), batch.num)
    del inp

    # Test that we can force a raise earlier manually.
    smaller_num_batches = 4
    p2 = p.clone().set(num_batches=smaller_num_batches)
    inp2 = instantiate(p2)
    for i in range(smaller_num_batches):
      batch = inp2.get_next()
      self.assertArraysEqual(
          np.array([2 * i, 2 * i + 1], dtype=np.int32), batch.num)
    with self.assertRaisesRegex(tf.errors.OutOfRangeError,
                                f'num_batches exceeding {smaller_num_batches}'):
      inp2.get_next()
    inp2.reset()
    batch = inp2.get_next()
    self.assertArraysEqual(np.array([0, 1], dtype=np.int32), batch.num)

  def test_lingvo_input_change_batch_size(self):
    tmp = os.path.join(FLAGS.test_tmpdir, 'tmptest2')
    batch_size = 2
    num_batches = 6
    num_data = batch_size * num_batches
    with tf.io.TFRecordWriter(tmp) as w:
      for i in range(num_data):
        w.write(('%04d' % i).encode('utf-8'))

    p = pax_fiddle.Config(base_input.LingvoInputAdaptorNewBatchSize)
    p.input = LingvoInput.Params()
    p.input.file_pattern = 'tfrecord:' + tmp
    p.input.file_random_seed = 0
    p.input.repeat_count = 1
    p.batch_size = 1
    p.reset_for_eval = True
    # To set require_sequential_input_order to True
    p.is_training = False
    p.cluster_do_eval = True
    inp = instantiate(p)
    for i in range(num_batches * 2):
      batch = inp.get_next()
      self.assertArraysEqual(np.array([i], dtype=np.int32), batch.num)
    with self.assertRaises(tf.errors.OutOfRangeError):
      inp.get_next()

  def test_lingvo_input_change_batch_size_tfdata(self):
    input_p = TestDataset.Params()
    input_p.args.num = 6
    p = pax_fiddle.Config(
        base_input.LingvoInputAdaptorNewBatchSize,
        batch_size=1,
        input=input_p,
        is_training=True,
    )
    inp = instantiate(p)
    for i in range(input_p.args.num):
      batch = inp.get_next()
      self.assertArraysEqual(np.array([i], dtype=np.int32), batch.a.b)
      self.assertArraysEqual(np.array([i], dtype=np.int32), batch.data)

  def test_lingvo_tfdata_input(self):
    num_batches = 10
    input_p = TestDataset.Params()
    input_p.args.num = num_batches
    p = pax_fiddle.Config(
        base_input.LingvoInputAdaptor,
        input=input_p,
        is_training=True,
        cluster_do_eval=True,
    )
    inp = instantiate(p)
    # When used for training data, cluster.do_eval is never set.
    # The input repeats the data indefinitely.
    for i in range(int(num_batches * 2.5)):
      x = inp.get_next()
      self.assertEqual(x.data, i % num_batches)
      self.assertEqual(x.data.shape, (1,))
      self.assertEqual(x.eval_sample_weights, np.array([1.0], dtype=np.float32))
      self.assertEqual(x.eval_sample_weights.shape, (1,))
    # Resets the input to begin from the first element again.
    inp.reset()
    x = inp.get_next()
    self.assertEqual(x.data, 0)

  def test_lingvo_tfdata_input_eval(self):
    num_batches = 10
    input_p = TestDataset.Params()
    input_p.args.num = num_batches
    # We have two versions of the input, with different values for
    # cluster.do_eval.
    p_eval = pax_fiddle.Config(
        base_input.LingvoInputAdaptor,
        input=input_p,
        is_training=False,
        cluster_do_eval=True,
    )
    p_noeval = pax_fiddle.Config(
        base_input.LingvoInputAdaptor,
        input=input_p,
        is_training=False,
        cluster_do_eval=False,
    )
    inp_eval = instantiate(p_eval)
    inp_noeval = instantiate(p_noeval)
    for i in range(num_batches):
      self.assertEqual(inp_eval.get_next().data, i)
      self.assertEqual(inp_noeval.get_next().data, i)
    # When cluster.do_eval is set, the input exhausts one epoch and raises.
    with self.assertRaisesRegex(tf.errors.OutOfRangeError, 'End of sequence'):
      inp_eval.get_next()
    # When cluster.do_eval is not set (the default), the input repeats.
    self.assertEqual(inp_noeval.get_next().data, 0)
    # Resets the input to begin from the first element again.
    inp_eval.reset()
    self.assertEqual(inp_eval.get_next().data, 0)

  def test_lingvo_tfdata_override(self):
    num_batches = 10
    input_p = TestDatasetOverride.Params()
    input_p.args.num = num_batches
    p = pax_fiddle.Config(
        base_input.LingvoInputAdaptor, input=input_p, is_training=True
    )
    inp = instantiate(p)
    for i in range(int(num_batches * 2.5)):
      x = inp.get_next()
      self.assertEqual(x.data, i % num_batches)
      self.assertEqual(x.data2, (i % num_batches) * 2 + 1)
    inp.reset()
    x = inp.get_next()
    self.assertEqual(x.data, 0)
    self.assertEqual(x.data2, 1)

  def test_tfdata_input(self):
    p = pax_fiddle.Config(TestInput)
    p.num_infeed_hosts = 3
    p.input_random_seed = 345
    p.batch_size = 2
    train = []
    test = []
    for i in range(p.num_infeed_hosts):
      train_p = p.clone().set(infeed_host_index=i)
      test_p = train_p.clone().set(reset_for_eval=True)
      train.append(instantiate(train_p))
      test.append(instantiate(test_p))

    num_train_batches = 10
    for _ in range(num_train_batches):
      for i in range(p.num_infeed_hosts):
        batch = train[i].get_next()
        self.assertTrue(np.all(batch.data % p.num_infeed_hosts == i))

    num_test_batches = 2
    for _ in range(num_test_batches):
      for i in range(p.num_infeed_hosts):
        batch = test[i].get_next()
        self.assertTrue(np.all(batch.data % p.num_infeed_hosts == i))
    for i in range(p.num_infeed_hosts):
      with self.assertRaisesRegex(tf.errors.OutOfRangeError, 'End of sequence'):
        unused_batch = test[i].get_next()

    # input works again after reset().
    for i in range(p.num_infeed_hosts):
      test[i].reset()
      batch = test[i].get_next()
      self.assertEqual(batch.data[0, 0] % p.num_infeed_hosts, i)

  # A variant of test_tfdata_input() with pickling-unpickling cycles between
  # operations to verify that restorable input objects can be saved & restored
  # correctly.
  def test_tfdata_input_save_restore(self):
    p = pax_fiddle.Config(TestInputCheckpointable)
    p.num_infeed_hosts = 3
    p.input_random_seed = 345
    p.batch_size = 2
    train = []
    test = []
    for i in range(p.num_infeed_hosts):
      train_p = p.clone().set(infeed_host_index=i)
      test_p = train_p.clone().set(reset_for_eval=True)
      train.append(instantiate(train_p))
      test.append(instantiate(test_p))

    for i in range(p.num_infeed_hosts):
      train[i] = pickle.loads(pickle.dumps(train[i]))
      test[i] = pickle.loads(pickle.dumps(test[i]))

    num_train_batches = 10
    for _ in range(num_train_batches):
      for i in range(p.num_infeed_hosts):
        train[i] = pickle.loads(pickle.dumps(train[i]))
        batch = train[i].get_next()
        self.assertTrue(np.all(batch.data % p.num_infeed_hosts == i))

    num_test_batches = 2
    for _ in range(num_test_batches):
      for i in range(p.num_infeed_hosts):
        test[i] = pickle.loads(pickle.dumps(test[i]))
        batch = test[i].get_next()
        self.assertTrue(np.all(batch.data % p.num_infeed_hosts == i))
    for i in range(p.num_infeed_hosts):
      with self.assertRaisesRegex(tf.errors.OutOfRangeError, 'End of sequence'):
        unused_batch = test[i].get_next()

    # input works again after reset().
    for i in range(p.num_infeed_hosts):
      test[i].reset()
      test[i] = pickle.loads(pickle.dumps(test[i]))
      batch = test[i].get_next()
      self.assertEqual(batch.data[0, 0] % p.num_infeed_hosts, i)

  @parameterized.parameters(
      itertools.product([True, False], [True, False], [True, False])
  )
  def test_peek(
      self, before_first: bool, after_first: bool, checkpointable: bool
  ):
    """Using peek_padded() doesn't change results of get_next_padded()."""
    if checkpointable:
      pipeline_p = pax_fiddle.Config(TestInputCheckpointable)
    else:
      pipeline_p = pax_fiddle.Config(TestInput)
    pipeline_p.batch_size = 2
    pipeline_p.shuffle = False
    pipeline = instantiate(pipeline_p)
    batch1 = [[0, 0, 0, 0], [1, 1, 1, 1]]
    batch2 = [[2, 2, 2, 2], [3, 3, 3, 3]]
    batch3 = [[4, 4, 4, 4], [5, 5, 5, 5]]
    if before_first:
      self.assertAllClose(pipeline.peek_padded()['data'], batch1)
    self.assertAllClose(pipeline.get_next_padded()['data'], batch1)
    if after_first:
      self.assertAllClose(pipeline.peek_padded()['data'], batch2)
    self.assertAllClose(pipeline.get_next_padded()['data'], batch2)
    self.assertAllClose(pipeline.get_next_padded()['data'], batch3)

  def test_peek_does_not_use_get_state(self):
    with mock.patch.object(
        TestInput, 'get_state', autospec=True
    ) as mock_get_state:
      pipeline_p = pax_fiddle.Config(TestInput)
      pipeline_p.batch_size = 2
      pipeline = instantiate(pipeline_p)
      pipeline.peek_padded()
      mock_get_state.assert_not_called()

  @parameterized.parameters(
      (True, True), (False, False), (True, False), (False, True)
  )
  def test_peek_handles_state(
      self, peek_after_restore: bool, create_new_pipeline: bool
  ):
    """Using peek_padded() works with get_state()/set_state()."""

    def create_pipeline():
      pipeline_p = pax_fiddle.Config(TestInputCheckpointable)
      pipeline_p.batch_size = 2
      pipeline_p.shuffle = False
      return instantiate(pipeline_p)

    pipeline = create_pipeline()
    batch1 = [[0, 0, 0, 0], [1, 1, 1, 1]]
    batch2 = [[2, 2, 2, 2], [3, 3, 3, 3]]
    self.assertAllClose(pipeline.peek_padded()['data'], batch1)
    state: bytes = pipeline.get_state()
    self.assertAllClose(pipeline.peek_padded()['data'], batch1)
    self.assertAllClose(pipeline.get_next_padded()['data'], batch1)
    self.assertAllClose(pipeline.get_next_padded()['data'], batch2)

    if create_new_pipeline:
      pipeline = create_pipeline()
    pipeline.set_state(state)

    if peek_after_restore:
      self.assertAllClose(pipeline.peek_padded()['data'], batch1)
    self.assertAllClose(pipeline.get_next_padded()['data'], batch1)
    self.assertAllClose(pipeline.get_next_padded()['data'], batch2)

  def test_validate_batch_size(self):
    tmp = os.path.join(FLAGS.test_tmpdir, 'tmptest3')
    with tf.io.TFRecordWriter(tmp) as w:
      for i in range(12):
        w.write(('%04d' % i).encode('utf-8'))

    p = pax_fiddle.Config(base_input.LingvoInputAdaptorNewBatchSize)
    p.input = LingvoInput.Params().Set(
        file_pattern='tfrecord:' + tmp, file_random_seed=0)
    with self.assertRaisesRegex(ValueError, 'self.batch_size'):
      instantiate(p)

    p2 = pax_fiddle.Config(base_input.LingvoInputAdaptor, input=p.input)
    p2.batch_size = 2
    with self.assertRaisesRegex(ValueError, 'self.batch_size'):
      instantiate(p2)

    p3 = pax_fiddle.Config(TestInput)
    with self.assertRaisesRegex(ValueError, 'self.batch_size'):
      instantiate(p3)

  def test_lingvo_eval_adaptor_tfdata(self):
    input_p = TestDataset.Params()
    input_p.args.num = 11
    eval_p = pax_fiddle.Config(
        base_input.LingvoEvalAdaptor,
        input=input_p,
        is_training=False,
        cluster_do_eval=True,  # required to not repeat the data.
        reset_for_eval=True,
    )
    eval_p.batch_size = 3
    eval_p.num_infeed_hosts = 3
    input_params = [
        eval_p.clone().set(infeed_host_index=i)
        for i in range(eval_p.num_infeed_hosts)
    ]
    inputs = [instantiate(p) for p in input_params]
    batches = []
    # We have 11 examples and global batch size of 9=3x3, hence 2 batches.
    num_batches = input_p.args.num // (eval_p.batch_size *
                                       eval_p.num_infeed_hosts) + 1
    for i in range(num_batches):
      batches.extend([inp.get_next() for inp in inputs])
    self.assertArraysEqual(batches[0].data, np.array([0, 1, 2], dtype=np.int32))
    self.assertArraysEqual(batches[1].data, np.array([3, 4, 5], dtype=np.int32))
    self.assertArraysEqual(batches[2].data, np.array([6, 7, 8], dtype=np.int32))
    self.assertArraysEqual(batches[3].data, np.array([9, 10, 0],
                                                     dtype=np.int32))
    self.assertArraysEqual(batches[4].data, np.array([0, 0, 0], dtype=np.int32))
    self.assertArraysEqual(batches[5].data, np.array([0, 0, 0], dtype=np.int32))
    self.assertArraysEqual(batches[0].eval_sample_weights,
                           np.array([1., 1., 1.], dtype=np.float32))
    self.assertArraysEqual(batches[1].eval_sample_weights,
                           np.array([1., 1., 1.], dtype=np.float32))
    self.assertArraysEqual(batches[2].eval_sample_weights,
                           np.array([1., 1., 1.], dtype=np.float32))
    # Starts to emit paddings after the 11-th example.
    self.assertArraysEqual(batches[3].eval_sample_weights,
                           np.array([1., 1., 0.], dtype=np.float32))
    self.assertArraysEqual(batches[4].eval_sample_weights,
                           np.array([0., 0., 0.], dtype=np.float32))
    self.assertArraysEqual(batches[5].eval_sample_weights,
                           np.array([0., 0., 0.], dtype=np.float32))
    # After 2 batches, all 3 inputs raise at the same time.
    for i in range(eval_p.num_infeed_hosts):
      with self.assertRaises(StopIteration):
        inputs[i].get_next()
    inputs[0].reset()
    self.assertArraysEqual(inputs[0].get_next().data,
                           np.array([0, 1, 2], dtype=np.int32))

  def test_lingvo_eval_adaptor(self):
    tmp = os.path.join(FLAGS.test_tmpdir, 'eval_adaptor')
    batch_size = 2
    num_batches = 2
    num_data = batch_size * num_batches
    with tf.io.TFRecordWriter(tmp) as w:
      for i in range(num_data):
        w.write(('%04d' % i).encode('utf-8'))

    input_p = LingvoInput.Params().Set(
        file_pattern='tfrecord:' + tmp, file_random_seed=0, repeat_count=1)
    # Set is_training and cluster_do_eval to get sequential input.
    p = pax_fiddle.Config(
        base_input.LingvoEvalAdaptor,
        input=input_p,
        reset_for_eval=True,
        is_training=False,
        cluster_do_eval=True,
    )
    p.batch_size = 3
    inp = instantiate(p)
    batches = []
    num_batches = num_data // p.batch_size + 1
    for i in range(num_batches):
      batches.append(inp.get_next())
    self.assertArraysEqual(batches[0].num, np.array([0, 1, 2], dtype=np.int32))
    self.assertArraysEqual(batches[1].num, np.array([3, 0, 0], dtype=np.int32))
    self.assertArraysEqual(batches[0].eval_sample_weights,
                           np.array([1., 1., 1.], dtype=np.float32))
    self.assertArraysEqual(batches[1].eval_sample_weights,
                           np.array([1., 0., 0.], dtype=np.float32))
    with self.assertRaises(StopIteration):
      inp.get_next()
    inp.reset()
    self.assertArraysEqual(inp.get_next().num,
                           np.array([0, 1, 2], dtype=np.int32))

  def test_lingvo_eval_adaptor_multiple_hosts(self):
    """Tests LingvoEvalAdaptor with multiple hosts."""
    tmp = os.path.join(FLAGS.test_tmpdir, 'eval_adaptor')
    batch_size = 2
    num_batches = 2
    num_data = batch_size * num_batches
    with tf.io.TFRecordWriter(tmp) as w:
      for i in range(num_data):
        w.write(('%04d' % i).encode('utf-8'))

    # Use two hosts in this test. Each host randomly shuffle the data instead of
    # using sequential order to test they generate the data in the same order.
    # Set file_random_seed to a non-zero value.
    input_p = LingvoInput.Params().Set(
        file_pattern='tfrecord:' + tmp, file_random_seed=1, batch_size=1)
    # Set cluster_do_eval=False to not use sequential input.
    adaptor_p = pax_fiddle.Config(
        base_input.LingvoEvalAdaptor,
        input=input_p,
        num_batches=num_data,
        reset_for_eval=True,
        is_training=False,
        num_infeed_hosts=2,
        batch_size=3,
        allow_fixed_file_random_seed=True,
        cluster_do_eval=False,
    )

    input_params = [
        adaptor_p.clone().set(infeed_host_index=i)
        for i in range(adaptor_p.num_infeed_hosts)
    ]
    inputs = [instantiate(p) for p in input_params]

    # Expect only one batch for each host.
    batches = [inp.get_next() for inp in inputs]
    num_concat = np.concatenate([batch.num for batch in batches])
    weights_concat = np.concatenate(
        [batch.eval_sample_weights for batch in batches])
    # Each host may get input in random order. Remove padded data and sort the
    # results.
    self.assertArraysEqual(
        np.sort(np.extract(weights_concat.astype(np.int32), num_concat)),
        np.array([0, 1, 2, 3], dtype=np.int32))
    for i in range(adaptor_p.num_infeed_hosts):
      with self.assertRaises(StopIteration):
        inputs[i].get_next()

  def test_lingvo_eval_adaptor_get_batch_size(self):
    input_p = base_input_generator.BaseSequenceInputGenerator.Params().Set(
        bucket_batch_limit=[1])
    adaptor_p = pax_fiddle.Config(
        base_input.LingvoEvalAdaptor,
        input=input_p,
        batch_size=2,
        num_infeed_hosts=3,
    )
    adaptor_cls = typing.cast(Type, fdl.get_callable(adaptor_p))
    self.assertEqual(adaptor_cls.get_batch_size(adaptor_p), 2)
    self.assertEqual(adaptor_cls.get_global_batch_size(adaptor_p), 6)

  def test_lingvo_lazy_eval_adaptor(self):
    tmp = os.path.join(FLAGS.test_tmpdir, 'lazy_eval_adaptor')
    num_data = 13
    with tf.io.TFRecordWriter(tmp) as w:
      for i in range(num_data):
        w.write(('%04d' % i).encode('utf-8'))

    input_p = LingvoInput.Params().Set(
        file_pattern='tfrecord:' + tmp, file_random_seed=301, repeat_count=-1)
    input_p.batch_size = 3
    input_p.num_samples = num_data
    input_p.file_buffer_size = 1
    input_p.file_parallelism = 1
    eval_p = pax_fiddle.Config(
        base_input.LingvoLazyEvalAdaptor,
        input=input_p,
        is_training=False,
        cluster_do_eval=True,
        reset_for_eval=True,
        num_infeed_hosts=3,
        allow_fixed_file_random_seed=True,
    )
    input_params = [
        eval_p.clone().set(infeed_host_index=i)
        for i in range(eval_p.num_infeed_hosts)
    ]
    inputs = [instantiate(p) for p in input_params]
    num_samples = [input.num_samples for input in inputs]
    self.assertArraysEqual(num_samples, [6, 4, 3])
    batches = []
    # We have 13 examples and global batch size of 9=3x3, hence 2 batches.
    num_batches = input_p.num_samples // (input_p.batch_size *
                                          eval_p.num_infeed_hosts) + 1
    for i in range(num_batches):
      batches.extend([inp.get_next() for inp in inputs])
    self.assertArraysEqual(batches[0].num, np.array([0, 1, 2], dtype=np.int32))
    self.assertArraysEqual(batches[1].num, np.array([3, 4, 5], dtype=np.int32))
    self.assertArraysEqual(batches[2].num, np.array([6, 7, 8], dtype=np.int32))
    self.assertArraysEqual(batches[3].num, np.array([9, 10, 11],
                                                    dtype=np.int32))
    self.assertArraysEqual(batches[4].num, np.array([12, 0, 1], dtype=np.int32))
    self.assertArraysEqual(batches[5].num, np.array([9, 10, 11],
                                                    dtype=np.int32))
    self.assertArraysEqual(batches[0].eval_sample_weights,
                           np.array([1., 1., 1.], dtype=np.float32))
    self.assertArraysEqual(batches[1].eval_sample_weights,
                           np.array([1., 1., 1.], dtype=np.float32))
    self.assertArraysEqual(batches[2].eval_sample_weights,
                           np.array([1., 1., 1.], dtype=np.float32))
    self.assertArraysEqual(batches[3].eval_sample_weights,
                           np.array([1., 1., 1.], dtype=np.float32))
    # Starts to emit paddings after the 13-th example.
    self.assertArraysEqual(batches[4].eval_sample_weights,
                           np.array([1., 0., 0.], dtype=np.float32))
    self.assertArraysEqual(batches[5].eval_sample_weights,
                           np.array([0., 0., 0.], dtype=np.float32))
    # After 2 batches, all 3 inputs raise at the same time.
    for i in range(eval_p.num_infeed_hosts):
      with self.assertRaisesRegex(tf.errors.OutOfRangeError,
                                  '2 batches have been exhausted.'):
        inputs[i].get_next()
    inputs[0].reset()
    self.assertArraysEqual(inputs[0].get_next().num,
                           np.array([0, 1, 2], dtype=np.int32))

  def test_lingvo_lazy_eval_adaptor_set_num_batches(self):
    tmp = os.path.join(FLAGS.test_tmpdir, 'lazy_eval_adaptor')
    num_data = 13
    with tf.io.TFRecordWriter(tmp) as w:
      for i in range(num_data):
        w.write(('%04d' % i).encode('utf-8'))

    input_p = LingvoInput.Params().Set(
        file_pattern='tfrecord:' + tmp, file_random_seed=301, repeat_count=-1
    )
    input_p.batch_size = 3
    input_p.num_samples = num_data
    input_p.file_buffer_size = 1
    input_p.file_parallelism = 1
    eval_p = pax_fiddle.Config(
        base_input.LingvoLazyEvalAdaptor,
        input=input_p,
        is_training=False,
        cluster_do_eval=True,
        reset_for_eval=True,
        num_infeed_hosts=3,
        allow_fixed_file_random_seed=True,
        num_batches=1,
    )
    input_params = [
        eval_p.clone().set(infeed_host_index=i)
        for i in range(eval_p.num_infeed_hosts)
    ]
    inputs = [instantiate(p) for p in input_params]
    num_samples = [input.num_samples for input in inputs]
    self.assertArraysEqual(num_samples, [6, 4, 3])
    batches = []
    # We have 13 examples and global batch size of 9=3x3, hence 2 batches.
    num_batches = 1
    for i in range(num_batches):
      batches.extend([inp.get_next() for inp in inputs])
    self.assertArraysEqual(batches[0].num, np.array([0, 1, 2], dtype=np.int32))
    self.assertArraysEqual(batches[1].num, np.array([3, 4, 5], dtype=np.int32))
    self.assertArraysEqual(batches[2].num, np.array([6, 7, 8], dtype=np.int32))
    self.assertArraysEqual(
        batches[0].eval_sample_weights,
        np.array([1.0, 1.0, 1.0], dtype=np.float32),
    )
    self.assertArraysEqual(
        batches[1].eval_sample_weights,
        np.array([1.0, 1.0, 1.0], dtype=np.float32),
    )
    self.assertArraysEqual(
        batches[2].eval_sample_weights,
        np.array([1.0, 1.0, 1.0], dtype=np.float32),
    )
    # After 1 batch, all 3 inputs raise at the same time.
    for i in range(eval_p.num_infeed_hosts):
      with self.assertRaisesRegex(
          tf.errors.OutOfRangeError, '1 batches have been exhausted.'
      ):
        inputs[i].get_next()
    inputs[0].reset()
    self.assertArraysEqual(
        inputs[0].get_next().num, np.array([0, 1, 2], dtype=np.int32)
    )

  def test_multi_input(self):
    tmp_1 = os.path.join(FLAGS.test_tmpdir, 'tmptest_1')
    tmp_2 = os.path.join(FLAGS.test_tmpdir, 'tmptest_2')
    batch_size_1 = 2
    # Different batch sizes work with the input generator, but are not enabled
    # for trainer due to conflict with pmap.
    batch_size_2 = 1
    num_batches = 10
    num_data_1 = batch_size_1 * num_batches
    with tf.io.TFRecordWriter(tmp_1) as w:
      for i in range(num_data_1):
        w.write(('%04d' % i).encode('utf-8'))

    num_data_2 = batch_size_2 * num_batches
    with tf.io.TFRecordWriter(tmp_2) as w:
      for i in range(num_data_2):
        w.write(('%04d' % (num_data_2 - i)).encode('utf-8'))

    p = pax_fiddle.Config(base_input.LingvoInputAdaptor)
    p.input = LingvoInput.Params()
    p.input.file_pattern = 'tfrecord:' + tmp_1
    p.input.batch_size = batch_size_1
    p.input.file_random_seed = 0
    p.input.repeat_count = 1
    # To set require_sequential_input_order to True
    p.is_training = False
    p.cluster_do_eval = True

    p2 = pax_fiddle.Config(base_input.LingvoInputAdaptor)
    p2.input = LingvoInput.Params()
    p2.input.file_pattern = 'tfrecord:' + tmp_2
    p2.input.batch_size = batch_size_2
    p2.input.file_random_seed = 0
    p2.input.repeat_count = 1
    # To set require_sequential_input_order to True
    p2.is_training = False
    p2.cluster_do_eval = True

    inputs = {
        'input_1': p,
        'input_2': p2,
    }
    multi_p = pax_fiddle.Config(base_input.MultiInput, input_to_params=inputs)
    multi_p.default_input = 'input_1'
    inp = instantiate(multi_p)
    for i in range(num_batches):
      batch = inp.get_next()
      self.assertArraysEqual(
          np.array([[2 * i, 2 * i + 1]], dtype=np.int32), batch.input_1.num)
      self.assertArraysEqual(
          np.array([[num_data_2 - i]], dtype=np.int32), batch.input_2.num)

  def test_multi_input_eval(self):
    tmp_1 = os.path.join(FLAGS.test_tmpdir, 'tmptest_1')
    batch_size_1 = 2
    num_batches = 10
    num_data_1 = batch_size_1 * num_batches
    with tf.io.TFRecordWriter(tmp_1) as w:
      for i in range(num_data_1):
        w.write(('%04d' % i).encode('utf-8'))

    p = pax_fiddle.Config(base_input.LingvoInputAdaptor)
    p.input = LingvoInput.Params()
    p.input.file_pattern = 'tfrecord:' + tmp_1
    p.input.batch_size = batch_size_1
    p.input.file_random_seed = 0
    p.input.repeat_count = 1
    # To set require_sequential_input_order to True
    p.is_training = False
    p.cluster_do_eval = True

    inputs = {
        'input_1': p,
    }
    multi_p = pax_fiddle.Config(base_input.MultiInput, input_to_params=inputs)
    multi_p.default_input = 'input_1'
    multi_p.reset_for_eval = True
    inp = instantiate(multi_p)
    for i in range(num_batches):
      batch = inp.get_next()
      self.assertArraysEqual(
          np.array([[2 * i], [2 * i + 1]], dtype=np.int32), batch.input_1.num)
    with self.assertRaisesRegex(tf.errors.OutOfRangeError,
                                'SequentialRecordYielder reached 1 repeat'):
      inp.get_next()
    inp.reset()
    for i in range(num_batches):
      batch = inp.get_next()
      self.assertArraysEqual(
          np.array([[2 * i], [2 * i + 1]], dtype=np.int32), batch.input_1.num)

  def test_multi_input_get_batch_size(self):
    batch_size_1 = 4
    batch_size_2 = 6

    p = pax_fiddle.Config(base_input.LingvoInputAdaptor)
    p.input = LingvoInput.Params()
    p.input.file_pattern = 'tfrecord:dummy'
    p.input.batch_size = batch_size_1
    p.input.file_random_seed = 0
    p.input.repeat_count = 1
    p.is_training = True

    p2 = pax_fiddle.Config(base_input.LingvoInputAdaptor)
    p2.input = LingvoInput.Params()
    p2.input.file_pattern = 'tfrecord:dummy'
    p2.input.batch_size = batch_size_2
    p2.input.file_random_seed = 0
    p2.input.repeat_count = 1
    p2.is_training = True

    inputs = {
        'input_1': p,
        'input_2': p2,
    }
    multi_p = pax_fiddle.Config(base_input.MultiInput, input_to_params=inputs)
    multi_bs = base_input.MultiInput.get_batch_size(multi_p)
    # Batch size should be greatest common factor of children batch sizes.
    self.assertEqual(multi_bs, 2)


class InputSpecsProviderTest(test_utils.TestCase):

  def test_tf_dataset_input_specs_provider(self):
    input_p = pax_fiddle.Config(
        TestInput,
        num_infeed_hosts=1,
        infeed_host_index=0,
        batch_size=2,
    )
    spec_provider_p = pax_fiddle.Config(
        base_input.DatasetInputSpecsProvider,
        input_p=input_p.clone()
    )
    input_pipeline = instantiate(input_p)
    spec_provider = instantiate(spec_provider_p)
    spec_from_data = jax.tree_map(
        lambda x: jax.ShapeDtypeStruct(x.shape, x.dtype),
        input_pipeline.get_next_padded())
    spec_from_provider = spec_provider.get_input_specs()
    self.assertEqual(spec_from_data, spec_from_provider)

  def test_dataset_input_specs_with_undef_dimension(self):
    input_p = pax_fiddle.Config(
        TestInput,
        num_infeed_hosts=1,
        infeed_host_index=0,
        batch_size=2,
        dataset_with_undef_dimension=True,
    )
    spec_provider_p = pax_fiddle.Config(
        base_input.DatasetInputSpecsProvider, input_p=input_p.clone()
    )
    input_pipeline = instantiate(input_p)
    spec_from_data = jax.tree_map(
        lambda x: jax.ShapeDtypeStruct(x.shape, x.dtype),
        input_pipeline.get_next(),
    )

    spec_provider = instantiate(spec_provider_p)
    spec_from_provider = spec_provider.get_input_specs()
    self.assertEqual(spec_from_data, spec_from_provider)

if __name__ == '__main__':
  absltest.main()
