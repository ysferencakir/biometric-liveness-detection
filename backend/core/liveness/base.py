from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import numpy as np


@dataclass
class ModuleResult:
    module_name: str
    passed: bool
    score: float
    details: dict = field(default_factory=dict)


class LivenessModule(ABC):
    @abstractmethod
    def process_frame(self, landmarks: np.ndarray, timestamp_ms: int) -> None: ...

    @abstractmethod
    def result(self) -> ModuleResult: ...

    @abstractmethod
    def reset(self) -> None: ...
