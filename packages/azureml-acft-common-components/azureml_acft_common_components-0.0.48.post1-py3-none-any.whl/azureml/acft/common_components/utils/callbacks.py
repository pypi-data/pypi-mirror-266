# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common callbacks for all vetricals."""

import os
import json
import shutil
from pathlib import Path

from dataclasses import asdict
from transformers.trainer_callback import TrainerCallback, TrainerControl, TrainerState
from transformers.trainer import TrainingArguments, get_last_checkpoint

from azureml.acft.accelerator.constants import SaveFileConstants
from azureml.acft.common_components.model_selector.constants import ModelSelectorDefaults, ModelSelectorConstants


class SaveExtraFilesToCheckpoints(TrainerCallback):
    """save extrafiles to checkpoint folder for image/multimodal verticals."""

    def __init__(self, metadata: str,
                 model_selector_output: str,
                 optimization_args: dict,
                 io_args: dict) -> None:
        """
        :param metadata: dict containg the meta information
        :type metadata: dict
        :param model_selector_output: path of the input model
        :type model_selector_output: str
        :param optimization_args: dict of optimization args
        :type optimization_args: dict
        :param io_args: dict of io args
        :type io_args: dict

        :return: None
        :rtype: None
        """
        super().__init__()
        self.io_args = asdict(io_args)
        self.optimization_args = asdict(optimization_args)
        model_name = self.optimization_args.get(ModelSelectorConstants.MODEL_NAME)
        self.metadata = metadata
        input_model_path = os.path.join(model_selector_output, ModelSelectorDefaults.MLFLOW_MODEL_DIRECTORY)
        if not os.path.isdir(input_model_path):
            input_model_path = os.path.join(model_selector_output, ModelSelectorDefaults.MLFLOW_MODEL_DIRECTORY)
        if not os.path.isdir(input_model_path):
            input_model_path = os.path.join(model_selector_output, model_name)
        self.input_model_defaults_path = os.path.join(input_model_path, ModelSelectorDefaults.MODEL_DEFAULTS_PATH)

    def save_files(self, output_dir: str) -> None:
        """Save required files in the folder specified.

        :param output_dir: path of the directory for dumping files
        :type output_dir: str

        :return: None
        :rtype: None
        """
        op_metadata_path = os.path.join(output_dir, ModelSelectorDefaults.MODEL_METADATA_PATH)
        with open(op_metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)

        op_modeldefaults_path = os.path.join(output_dir, ModelSelectorDefaults.MODEL_DEFAULTS_PATH)
        if os.path.isfile(self.input_model_defaults_path):
            shutil.copy(self.input_model_defaults_path, op_modeldefaults_path)

        optimization_args_save_path = os.path.join(output_dir, SaveFileConstants.OPTIMIZATION_ARGS_SAVE_PATH)
        with open(optimization_args_save_path, 'w') as fp:
            json.dump(self.optimization_args, fp, indent=2)

        io_args_save_path = os.path.join(output_dir, SaveFileConstants.IO_ARGS_SAVE_PATH)
        with open(io_args_save_path, 'w') as fp:
            json.dump(self.io_args, fp, indent=2)

    def on_save(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs) -> None:
        """Callback called after saving each checkpoint.
        :param args: training arguments
        :type args: TrainingArguments (transformers.TrainingArguments)
        :param state: trainer state
        :type state: TrainerState (transformers.TrainerState)
        :param control: trainer control
        :type control: TrainerControl (transformers.TrainerControl)
        :param kwargs: keyword arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """
        last_checkpoint_folder = get_last_checkpoint(args.output_dir)
        if args.should_save:  # save only on rank-0
            self.save_files(last_checkpoint_folder)
            # checkpoint_done.txt will be saved at the end after all checkpoint related files, like global_step*,
            # trainer_state.json, etc., have been saved. If it exists in a checkpoint folder, the checkpoint can
            # be considered valid.
            checkpoint_done_path = os.path.join(last_checkpoint_folder, SaveFileConstants.CHECKPOINT_DONE_PATH)
            Path(checkpoint_done_path).touch()

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs) -> None:
        """Callback called at the end of training.
        :param args: training arguments
        :type args: TrainingArguments (transformers.TrainingArguments)
        :param state: trainer state
        :type state: TrainerState (transformers.TrainerState)
        :param control: trainer control
        :type control: TrainerControl (transformers.TrainerControl)
        :param kwargs: keyword arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        if args.should_save:  # save only on rank-0
            self.save_files(self.io_args["pytorch_model_folder"])
