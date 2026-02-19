"""In-memory training status for API (single job at a time)."""
import threading
from dataclasses import dataclass, field
from typing import Optional

_state_lock = threading.Lock()


@dataclass
class TrainingState:
    status: str = "idle"  # idle | running | completed | failed
    task_type: str = ""
    kaggle_slug: str = ""
    current_epoch: int = 0
    total_epochs: int = 0
    message: str = ""
    error: Optional[str] = None
    best_metric: Optional[float] = None


_training_state = TrainingState()


def get_state() -> TrainingState:
    with _state_lock:
        return TrainingState(
            status=_training_state.status,
            task_type=_training_state.task_type,
            kaggle_slug=_training_state.kaggle_slug,
            current_epoch=_training_state.current_epoch,
            total_epochs=_training_state.total_epochs,
            message=_training_state.message,
            error=_training_state.error,
            best_metric=_training_state.best_metric,
        )


def set_state(
    status: str = None,
    task_type: str = None,
    kaggle_slug: str = None,
    current_epoch: int = None,
    total_epochs: int = None,
    message: str = None,
    error: str = None,
    best_metric: float = None,
):
    with _state_lock:
        if status is not None:
            _training_state.status = status
        if task_type is not None:
            _training_state.task_type = task_type
        if kaggle_slug is not None:
            _training_state.kaggle_slug = kaggle_slug
        if current_epoch is not None:
            _training_state.current_epoch = current_epoch
        if total_epochs is not None:
            _training_state.total_epochs = total_epochs
        if message is not None:
            _training_state.message = message
        if error is not None:
            _training_state.error = error
        if best_metric is not None:
            _training_state.best_metric = best_metric
