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

"""Module to manage checkpoint metadata and automatic checkpoint deletion."""

import dataclasses
import typing
from typing import Any, Sequence, Union

from absl import logging
from etils import epath
import orbax.checkpoint as ocp
from paxml import checkpoint_metadata
from paxml import checkpoint_paths
from paxml import checkpoint_types
from paxml import checkpoint_version
from paxml import train_states
from praxis import base_input
from praxis import pytypes


Nested = pytypes.Nested
# TODO(pax-dev): pytyping doesn't like either
# Optional[pytypes.NestedShapeDtypeStruct]
# or pytypes.NestedShapeDtypeStruct | None,
# Switch to the right type hint once pytyping versions are in sync.
OptionalNestedShapeDtypeStruct = Any
TrainState = train_states.TrainState

STATE_ITEM_NAME = checkpoint_paths.STATE_ITEM_NAME
METADATA_ITEM_NAME = checkpoint_metadata.METADATA_ITEM_NAME
INPUT_ITEM_NAME = checkpoint_paths.INPUT_ITEM_NAME
_SUPPORTED_ITEMS = frozenset({STATE_ITEM_NAME, METADATA_ITEM_NAME})
CheckpointType = checkpoint_types.CheckpointType


def _get_checkpoint_version(
    checkpoint_type: CheckpointType,
    directory: epath.Path,
    step: int,
    use_digit_step_subdirectory: bool = False,
) -> float:
  """Gets checkpoint version from saved metadata."""
  checkpoint_step_dir = checkpoint_paths.make_checkpoint_step_dir(
      directory,
      step,
      checkpoint_type=checkpoint_type,
      use_digit_step_subdirectory=use_digit_step_subdirectory,
  )
  version = 0.0
  # Necessary because some checkpoints do not conform to Orbax directory
  # structure. Could rely exclusively on actual version if all checkpoints
  # conformed.
  if checkpoint_metadata.metadata_exists(checkpoint_step_dir):
    version = checkpoint_metadata.restore_metadata(checkpoint_step_dir)[
        checkpoint_version.get_version_key()
    ]
  return version


def _update_args_with_version(item_kwargs, version):
  kwargs = {STATE_ITEM_NAME: {checkpoint_version.get_version_key(): version}}
  if item_kwargs is not None:
    kwargs[STATE_ITEM_NAME].update(item_kwargs)
  return kwargs


def _create_items_dict_with_metadata(
    train_state,
    train_state_unpadded_shape_dtype_struct,
    version,
    tensorstore_use_ocdbt: bool | None = None,
):
  """Returns items dict with metadata."""
  # (padded) train_state
  items = {STATE_ITEM_NAME: train_state}

  if version > 0:
    metadata = checkpoint_metadata.make_metadata(
        version,
        train_state,
        train_state_unpadded_shape_dtype_struct,
        tensorstore_use_ocdbt=tensorstore_use_ocdbt,
    )
    items.update({METADATA_ITEM_NAME: metadata})

  return items


def _has_digit_step_subdirectory(directory) -> bool:
  """Indicates whether the checkpoints have digit-like step subdirectories."""
  return checkpoint_paths.is_tfhub_dir(directory)


@dataclasses.dataclass
class CheckpointManagerOptions(ocp.CheckpointManagerOptions):
  """Options for constructing OrbaxCheckpointManager.

  See superclass.

  Attributes:
    todelete_subdir: If set, checkpoints to be deleted will be only renamed into
      a subdirectory with the provided string. Otherwise, they will be directly
      deleted from the file system. Useful if checkpoint deletion is time
      consuming. By default, delete the checkpoint assets. TODO(b/278901950):
      Remove this option when it is available in Orbax OSS.
    cleanup_tmp_directories: if True, cleans up any existing temporary
      directories on CheckpointManager creation. Set to False by default and
      overridden in select places (like train.py). Otherwise, the
      CheckpointManager is typically a one-off and does not need to concern
      itself with much directory management.
  """

  todelete_subdir: str | None = None
  cleanup_tmp_directories: bool = False


class _CompositeCheckpointHandlerWrapper(ocp.CompositeCheckpointHandler):
  """Wrapper for CompositeCheckpointHandler support version < 1."""

  def _get_state_handler(self) -> ocp.CheckpointHandler:
    for item_name, handler in self._known_handlers.items():
      if item_name == STATE_ITEM_NAME:
        if handler is None:
          raise ValueError(f'Handler for {STATE_ITEM_NAME} was not configured.')
        return handler
    raise ValueError(f'Handler for {STATE_ITEM_NAME} not found.')

  async def async_save(
      self, directory: epath.Path, args: ocp.args.Composite
  ) -> list[ocp.future.Future] | None:
    handler = self._get_state_handler()
    if not isinstance(handler, ocp.AsyncCheckpointHandler):
      raise TypeError(
          f'Handler for {STATE_ITEM_NAME} does not support async save.'
      )
    return await handler.async_save(directory, args=args[STATE_ITEM_NAME])

  def save(self, directory: epath.Path, args: ocp.args.Composite):
    return self._get_state_handler().save(directory, args=args[STATE_ITEM_NAME])

  def restore(
      self,
      directory: epath.Path,
      args: ocp.args.Composite | None = None,
  ) -> ocp.args.Composite:
    result = self._get_state_handler().restore(
        directory, args=args[STATE_ITEM_NAME]
    )
    return ocp.args.Composite(**{STATE_ITEM_NAME: result})

  def metadata(self, directory: epath.Path):
    raise NotImplementedError()

  def finalize(self, directory: epath.Path):
    self._get_state_handler().finalize(directory)

  def close(self):
    self._get_state_handler().close()


# pylint: disable=protected-access
# pytype: disable=attribute-error


def _restore_legacy_flax(directory, handler, restore_fn, *args, **kwargs):
  """Restores legacy Flax checkpoint."""
  handler = typing.cast(
      _CompositeCheckpointHandlerWrapper, handler
  )._known_handlers[STATE_ITEM_NAME]
  if 'LegacyCheckpointHandlerWrapper' in handler.__class__.__name__:
    assert hasattr(handler, '_handler')
    handler = handler._handler
  if handler.__class__.__name__ != 'FlaxCheckpointHandler':
    raise ValueError(
        f'Unsupported handler for Flax restoration of type {type(handler)}.'
    )
  directory = epath.Path(directory)
  original_aggregate_filename = handler._aggregate_filename
  # If is_file, then the checkpoint is in legacy format, not saved with
  # orbax. Orbax checkpoints are directories containing a file\
  # called 'checkpoint'.
  if directory.is_file():
    # The msgpack file is actually the "directory".
    handler._aggregate_filename = directory.name
    directory = directory.parent
  result = restore_fn(directory, *args, **kwargs)
  # Reset aggregate_filename back to normal.
  handler._aggregate_filename = original_aggregate_filename
  return result


# pylint: enable=protected-access
# pytype: enable=attribute-error


class _Checkpointer(ocp.Checkpointer):
  """Override supporting restoring legacy Flax checkpoints."""

  def __init__(self, *args, is_legacy_flax_checkpoint: bool = False, **kwargs):
    super().__init__(*args, **kwargs)
    self._is_legacy_flax_checkpoint = is_legacy_flax_checkpoint

  def restore(
      self, directory: epath.PathLike, *args: Any, **kwargs: Any
  ) -> ocp.args.Composite:
    if self._is_legacy_flax_checkpoint:
      return _restore_legacy_flax(
          directory, self._handler, super().restore, *args, **kwargs
      )
    else:
      return super().restore(directory, *args, **kwargs)


class _AsyncCheckpointer(ocp.AsyncCheckpointer):
  """Override supporting restoring legacy Flax checkpoints."""

  def __init__(self, *args, is_legacy_flax_checkpoint: bool = False, **kwargs):
    super().__init__(*args, **kwargs)
    self._is_legacy_flax_checkpoint = is_legacy_flax_checkpoint

  def restore(
      self, directory: epath.PathLike, *args: Any, **kwargs: Any
  ) -> ocp.args.Composite:
    if self._is_legacy_flax_checkpoint:
      return _restore_legacy_flax(
          directory, self._handler, super().restore, *args, **kwargs
      )
    else:
      return super().restore(directory, *args, **kwargs)


@ocp.args.register_with_handler(
    _CompositeCheckpointHandlerWrapper, for_save=True, for_restore=True
)
class _CompositeWrapperArgs(ocp.args.Composite):
  pass


class _CheckpointManagerImpl(ocp.CheckpointManager):
  """Provides Pax-specific logic for ocp.CheckpointManager.

  Pax only supports a single checkpointable item (TrainState) and checkpoints
  are saved under a different folder name in a flat manner (no per-item
  sub-directories).

  Additionally, Pax supports extra options provided via CheckpointManagerOptions
  (see above).

  An instance of this class can be created on several JAX processes.
  All public APIs may be called by all processes.
  """

  def __init__(
      self,
      directory: epath.PathLike,
      checkpointers: (
          Union[ocp.AbstractCheckpointer, dict[str, ocp.AbstractCheckpointer]]
          | None
      ) = None,
      options: CheckpointManagerOptions | None = None,
      checkpoint_type: CheckpointType = CheckpointType.UNSPECIFIED,
      tensorstore_use_ocdbt: bool | None = None,
  ):
    if checkpoint_type == CheckpointType.UNSPECIFIED:
      raise ValueError('Must specify checkpoint type.')
    self._checkpoint_type = checkpoint_type

    self._version = checkpoint_version.get_version(tensorstore_use_ocdbt)
    # Check for existing checkpoints and retrieve version information. The
    # specific version may impact the checkpoint format, so it must be known in
    # advance of any operations.
    self._directory = epath.Path(directory)
    self._use_digit_step_subdirectory = _has_digit_step_subdirectory(
        self._directory
    )
    if self._directory.exists():
      step = self.any_step()
      if step is not None:
        version = _get_checkpoint_version(
            self._checkpoint_type,
            self._directory,
            step,
            use_digit_step_subdirectory=self._use_digit_step_subdirectory,
        )
        logging.info(
            'Found existing checkpoint with version: %s, step: %s',
            version,
            step,
        )
        if version != self._version:
          logging.warning(
              (
                  'Found existing checkpoints with old version %s, compared to '
                  'latest version %s. Use version of existing checkpoints for '
                  'restoring and saving future checkpoints.'
              ),
              version,
              self._version,
          )
          self._version = version

    options = options or CheckpointManagerOptions()
    # Set to 1 if not provided or set to 0.
    options.save_interval_steps = options.save_interval_steps or 1
    options.step_name_format = checkpoint_paths.PaxStepNameFormat(
        checkpoint_type=self._checkpoint_type,
        use_digit_step_subdirectory=self._use_digit_step_subdirectory,
    )

    super().__init__(directory, checkpointers=checkpointers, options=options)

    if self.version < 1:
      composite_handler = typing.cast(
          ocp.CompositeCheckpointHandler, self._checkpointer._handler  # pylint: disable=protected-access
      )
      original_state_handler = composite_handler._known_handlers[  # pylint: disable=protected-access
          STATE_ITEM_NAME
      ]
      handler = _CompositeCheckpointHandlerWrapper(
          **{STATE_ITEM_NAME: original_state_handler}
      )
      is_legacy_flax_checkpoint = (
          checkpointers[STATE_ITEM_NAME].__class__.__name__
          == 'FlaxCheckpointer'
      )
      if ocp.checkpoint_manager.is_async_checkpointer(self._checkpointer):
        assert hasattr(self._checkpointer, '_async_manager')  # Hint for pytype
        self._checkpointer = _AsyncCheckpointer(
            handler=handler,
            is_legacy_flax_checkpoint=is_legacy_flax_checkpoint,
            timeout_secs=self._checkpointer._async_manager._timeout_secs,  # pylint: disable=protected-access
        )
      else:
        self._checkpointer = _Checkpointer(
            handler=handler,
            is_legacy_flax_checkpoint=is_legacy_flax_checkpoint,
        )

  @property
  def version(self) -> float:
    return self._version

  def all_steps(self, read: bool = False) -> Sequence[int]:
    steps = list(super().all_steps(read=read))
    if read:
      for path in self.directory.iterdir():
        if checkpoint_paths.is_legacy_flax_checkpoint(path):
          steps.append(checkpoint_paths.get_step_from_checkpoint_asset(path))
    return steps

  def any_step(self) -> int | None:
    """Returns any step tracked by the checkpoint manager.

    Returns:
      A step (integer) or None.
    """
    any_step = ocp.utils.any_checkpoint_step(self.directory)
    if any_step is not None:
      return any_step

    for path in self.directory.iterdir():
      if checkpoint_paths.is_legacy_flax_checkpoint(path):
        return checkpoint_paths.get_step_from_checkpoint_asset(path)
    return None

  def _checkpoint_name(self, step: int) -> str:
    assert self._options.step_name_format is not None  # Hint for pytype
    return self._options.step_name_format.build_name(step)

  def should_save(self, step: int) -> bool:
    """Indicates whether there is a need to save a checkpoint."""
    if self._use_digit_step_subdirectory:
      raise NotImplementedError(
          'Checkpoints with digit step subdirectories do not support the '
          'saving mode.'
      )

    # Whether to save an on-demand checkpoint due to preemption
    if self.reached_preemption(step):
      return True
    last_checkpoint_step = self.latest_step()
    # Ensure current step is between the last step and next step (accounting for
    # save interval). The `last_checkpoint_step` may not be initialized, in
    # which case we should save. Otherwise, step must fall on the specified
    # save interval. This condition accounts for the possibility of saving
    # on preemption, in which case we want to maintain the same save period as
    # if preemption had not happened.
    return last_checkpoint_step is None or (
        last_checkpoint_step < step
        and step % self._options.save_interval_steps == 0
    )

  def delete(self, step: int):
    """Deletes a step checkpoint."""
    if self._use_digit_step_subdirectory:
      raise NotImplementedError(
          'Checkpoints with digit step subdirectories do not support deletions.'
      )
    super().delete(step)

  def save(self, *args, **kwargs) -> bool:
    """Saves the provided items."""
    if self._use_digit_step_subdirectory:
      raise NotImplementedError(
          'Checkpoints with digit step subdirectories do not support the '
          'saving mode.'
      )
    return super().save(*args, **kwargs)


class OrbaxCheckpointManager:
  """Wrapper class for overridden _CheckpointManagerImpl."""

  def __init__(
      self,
      directory: epath.Path,
      checkpointer: ocp.AbstractCheckpointer,
      train_input_checkpointer: ocp.Checkpointer | None = None,
      options: CheckpointManagerOptions | None = None,
      checkpoint_type: CheckpointType = CheckpointType.UNSPECIFIED,
      tensorstore_use_ocdbt: bool | None = None,
      aux_checkpointers: dict[str, ocp.AbstractCheckpointer] | None = None,
  ):
    self._checkpoint_type = checkpoint_type
    self._tensorstore_use_ocdbt = tensorstore_use_ocdbt
    checkpointers = {
        STATE_ITEM_NAME: checkpointer,
        METADATA_ITEM_NAME: ocp.Checkpointer(ocp.JsonCheckpointHandler()),
    }
    if aux_checkpointers:
      checkpointers.update(aux_checkpointers)

    if train_input_checkpointer:
      checkpointers[INPUT_ITEM_NAME] = train_input_checkpointer

# Internal Orbax infra configuration

    self._manager = _CheckpointManagerImpl(
        directory,
        checkpointers,
        options=options,
        checkpoint_type=checkpoint_type,
        tensorstore_use_ocdbt=tensorstore_use_ocdbt,
    )

  @property
  def version(self) -> float:
    return self._manager.version

  @property
  def directory(self) -> epath.Path:
    return self._manager.directory

  def all_steps(self) -> Sequence[int]:
    return self._manager.all_steps()

  def latest_step(self) -> int | None:
    return self._manager.latest_step()

  def check_for_errors(self):
    self._manager.check_for_errors()

  def wait_until_finished(self):
    self._manager.wait_until_finished()

  def reached_preemption(self, step: int) -> bool:
    return self._manager.reached_preemption(step)

  def should_save(self, step: int) -> bool:
    return self._manager.should_save(step)

  def _train_checkpoint_exists(self, step: int) -> bool:
    step_dir = checkpoint_paths.make_checkpoint_step_dir(
        self.directory,
        step,
        checkpoint_type=self._checkpoint_type,
        use_digit_step_subdirectory=self._manager._use_digit_step_subdirectory,  # pylint: disable=protected-access
    )
    return (step_dir / INPUT_ITEM_NAME).exists()

  def save(
      self,
      step: int,
      train_state: Any,
      train_state_unpadded_shape_dtype_struct: OptionalNestedShapeDtypeStruct = None,
      train_input_pipeline: base_input.BaseInput | None = None,
      force: bool | None = False,
      aux_items: dict[str, Any] | None = None,
  ) -> bool:
    """See superclass documentation."""
    if self.version > 1.0 and train_state_unpadded_shape_dtype_struct is None:
      raise ValueError(
          """For checkpoint version > 1.0, we require users to provide
          `train_state_unpadded_shape_dtype_struct` during checkpoint
          saving/restoring, to avoid potential silent bugs when loading
          checkpoints to incompatible unpadded shapes of TrainState."""
      )

    # save_kwargs
    save_kwargs = _update_args_with_version(None, self.version)

    # items
    items = _create_items_dict_with_metadata(
        train_state,
        train_state_unpadded_shape_dtype_struct,
        self.version,
        tensorstore_use_ocdbt=self._tensorstore_use_ocdbt,
    )

    if aux_items:
      items.update(aux_items)

    if train_input_pipeline:
      items[INPUT_ITEM_NAME] = train_input_pipeline

    return self._manager.save(step, items, save_kwargs=save_kwargs, force=force)

  def restore(
      self,
      step: int,
      train_state: Any,
      train_state_unpadded_shape_dtype_struct: OptionalNestedShapeDtypeStruct = None,
      train_input_pipeline: base_input.BaseInput | None = None,
      restore_kwargs: Any | None = None,
      aux_items: dict[str, Any] | None = None,
      aux_restore_kwargs: dict[str, Any] | None = None,
  ) -> TrainState | dict[str, Any]:
    """See superclass documentation."""
    uses_transformations = (
        restore_kwargs
        and 'transforms' in restore_kwargs
        and restore_kwargs['transforms'] is not None
    )
    # Propagate version to CheckpointHandler.
    restore_kwargs = _update_args_with_version(restore_kwargs, self.version)

    items = _create_items_dict_with_metadata(
        train_state,
        train_state_unpadded_shape_dtype_struct,
        self.version,
        tensorstore_use_ocdbt=self._tensorstore_use_ocdbt,
    )

    if aux_items:
      items.update(aux_items)

    if aux_restore_kwargs:  # Add aux restore kwargs for aux_items
      restore_kwargs.update(aux_restore_kwargs)

    # Train input checkpoint may not exist if input checkpointing wasn't
    # previously enabled
    if train_input_pipeline and self._train_checkpoint_exists(step):
      items[INPUT_ITEM_NAME] = train_input_pipeline

    restored = self._manager.restore(
        step, items=items, restore_kwargs=restore_kwargs
    )

    # Skip metadata checks if using transformations, since the TrainState may be
    # completely altered.
    if self.version > 1.0 and not uses_transformations:
      # If unpadded shapes were not provided, skip the shape check for now, as
      # there are many callers that need to be changed.
      if train_state_unpadded_shape_dtype_struct is None:
        logging.error(
            """For checkpoint version > 1.0, we require users to provide
          `train_state_unpadded_shape_dtype_struct` during checkpoint
          saving/restoring, to avoid potential silent bugs when loading
          checkpoints to incompatible unpadded shapes of TrainState."""
        )
      else:
        restored_metadata = checkpoint_metadata.PaxMetadata.from_dict(
            restored[METADATA_ITEM_NAME]
        )
        metadata = checkpoint_metadata.PaxMetadata.from_dict(
            items[METADATA_ITEM_NAME]
        )
        if not metadata.is_compatible(restored_metadata):
          raise ValueError(
              'PaxMetadata is not compatible with the restored PaxMetadata. '
              f'expected PaxMetadata = {restored_metadata}. '
              f'actual PaxMetadata = {metadata}.'
          )

    if aux_items:
      return restored
    else:
      return restored[STATE_ITEM_NAME]
