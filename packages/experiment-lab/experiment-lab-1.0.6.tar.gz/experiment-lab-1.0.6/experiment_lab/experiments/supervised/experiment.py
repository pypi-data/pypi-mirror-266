"""The supervised learning experiment file."""

from json import load
import logging
from typing import Any, Dict
import os
import hydra
import torch
from torch import nn, optim
import torch.utils.data
import wandb

from experiment_lab.common.utils import default
from experiment_lab.core.base_experiment import BaseExperiment
from experiment_lab.experiments.supervised.config import IntervalType, SupervisedConfig


logger = logging.getLogger(__name__)


class SupervisedExperiment(BaseExperiment):
    """The supervised learning experiment class."""

    def __init__(self, cfg: SupervisedConfig) -> None:
        """The constructor for the supervised learning experiment."""
        self.cfg = cfg
        self.initialize_experiment()

    def initialize_experiment(self) -> None:
        """Initializes the supervised experiment config."""
        super().initialize_experiment()

        self.dataset: torch.utils.data.Dataset = hydra.utils.instantiate(
            self.cfg.dataset
        )
        self.device: torch.device = torch.device(self.cfg.device)
        self.data_loader_kwargs: Dict[str, Any] = default(
            self.cfg.data_loader_kwargs, {}
        )

    def apply_model_on_epoch(
        self,
        model: nn.Module,
        loader: torch.utils.data.DataLoader,
        optimizer: optim.Optimizer,
        scheduler: optim.lr_scheduler.LRScheduler | None,
        loss: nn.Module,
        train_with: bool = False,
        epoch: int = 0,
    ):
        model.train()
        losses = []
        num_batches = len(loader)
        for batch_idx, (input_data, target_data) in enumerate(loader):
            batch_idx += 1
            input_data, target_data = (
                input_data.to(self.device),
                target_data.to(self.device),
            )
            if train_with:
                optimizer.zero_grad()
                output_data = model(input_data)
                loss_val = loss(output_data, target_data)
                loss_val.backward()
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
                if (
                    (
                        self.cfg.logging_schedule.log_type == IntervalType.batches
                        or self.cfg.logging_schedule.log_type
                        == IntervalType.batches_and_epochs
                    )
                    and self.cfg.logging_schedule.log_freq > 0
                    and batch_idx % self.cfg.logging_schedule.log_freq == 0
                ):
                    logging.info(
                        f"epoch {epoch} / {self.cfg.num_epochs}; batch {batch_idx} / {num_batches} - train loss: {loss_val.item()};"
                    )
                if (
                    (
                        self.cfg.logging_schedule.wandb_log_type == IntervalType.batches
                        or self.cfg.logging_schedule.wandb_log_type
                        == IntervalType.batches_and_epochs
                    )
                    and self.cfg.logging_schedule.wandb_log_freq > 0
                    and batch_idx % self.cfg.logging_schedule.wandb_log_freq == 0
                ):
                    wandb.log(
                        {
                            "epoch": epoch,
                            "batch_idx": batch_idx,
                            "train_loss": loss_val.item(),
                        }
                    )
                losses.append(loss_val.item())
            else:
                with torch.no_grad():
                    output_data = model(input_data)
                    loss_val = loss(output_data, target_data)
                    losses.append(loss_val.item())
        return torch.Tensor(losses).to(self.device).mean()

    def single_run(
        self, run_id: str, run_output_path: str, seed: int | None = None
    ) -> Any:
        """A single run of the supervised learning experiment.

        Args:
            run_id (str): The run id.
            run_output_path (str): The run output path.
            seed (int | None, optional): The initial random seed. Defaults to None.

        Returns:
            Any: The post processed results.
        """
        # Setup the device to train on
        if self.cfg.gpu_idx is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(self.cfg.gpu_idx)

        if seed is not None:
            torch.manual_seed(seed=seed)

        # Setting up data
        train_dataset, validation_dataset, test_dataset = torch.utils.data.random_split(
            dataset=self.dataset,
            lengths=[self.cfg.train_ratio, self.cfg.val_ratio, self.cfg.test_ratio],
        )

        train_dataloader, validation_dataloader, test_dataloader = (
            torch.utils.data.DataLoader(
                dataset=train_dataset, **self.data_loader_kwargs
            ),
            torch.utils.data.DataLoader(
                dataset=validation_dataset, **self.data_loader_kwargs
            ),
            torch.utils.data.DataLoader(
                dataset=test_dataset, **self.data_loader_kwargs
            ),
        )

        # Setting up model
        model: nn.Module = hydra.utils.instantiate(self.cfg.model).to(self.device)
        if self.cfg.load_model_path is not None:
            model.load_state_dict(torch.load(self.cfg.load_model_path))

        # Setting up optimizer
        optimizer: optim.Optimizer = hydra.utils.instantiate(
            self.cfg.optimizer, model.parameters()
        )
        scheduler: optim.lr_scheduler.LRScheduler | None = (
            None
            if self.cfg.scheduler is None
            else hydra.utils.instantiate(self.cfg.scheduler, optimizer)
        )

        # Setting up loss
        loss = hydra.utils.instantiate(self.cfg.loss)

        os.makedirs(f"{run_output_path}/models", exist_ok=True)

        for epoch in range(0, self.cfg.num_epochs + 1):
            train_loss = self.apply_model_on_epoch(
                model=model,
                loader=train_dataloader,
                optimizer=optimizer,
                scheduler=scheduler,
                loss=loss,
                train_with=epoch > 0,
                epoch=epoch,
            )
            validation_loss = self.apply_model_on_epoch(
                model=model,
                loader=validation_dataloader,
                optimizer=optimizer,
                scheduler=scheduler,
                loss=loss,
                train_with=False,
                epoch=epoch,
            )
            test_loss = self.apply_model_on_epoch(
                model=model,
                loader=test_dataloader,
                optimizer=optimizer,
                scheduler=scheduler,
                loss=loss,
                train_with=False,
                epoch=epoch,
            )

            if self.cfg.save_model_freq > 0 and epoch % self.cfg.save_model_freq == 0:
                torch.save(
                    model.state_dict(),
                    f"{run_output_path}/models/model_epoch_{epoch}.pl",
                )

            if (
                (
                    self.cfg.logging_schedule.log_type == IntervalType.epochs
                    or self.cfg.logging_schedule.log_type
                    == IntervalType.batches_and_epochs
                )
                and self.cfg.logging_schedule.log_freq > 0
                and epoch % self.cfg.logging_schedule.log_freq == 0
            ):
                logging.info(
                    f"epoch {epoch} / {self.cfg.num_epochs}; - train loss: {train_loss.item()}; val_loss: {validation_loss.item()}; test_loss: {test_loss.item()}"
                )
            if (
                (
                    self.cfg.logging_schedule.wandb_log_type == IntervalType.epochs
                    or self.cfg.logging_schedule.wandb_log_type
                    == IntervalType.batches_and_epochs
                )
                and self.cfg.logging_schedule.wandb_log_freq > 0
                and epoch % self.cfg.logging_schedule.wandb_log_freq == 0
            ):
                wandb.log(
                    {
                        "epoch": epoch,
                        "train_loss": train_loss.item(),
                        "val_loss": validation_loss.item(),
                        "test_loss": test_loss.item(),
                    }
                )

        torch.save(
            model.state_dict(),
            f"{run_output_path}/models/final_model_epoch_{self.cfg.num_epochs}.pl",
        )
