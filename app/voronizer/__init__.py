
from dataclasses import dataclass

from . import main

@dataclass
class PipelineConfig:
    MAT_DENSITY: float = 1.25
    MODEL: bool = True
    SUPPORT: bool = False
    SEPARATE_SUPPORTS: bool = True
    PERFORATE: bool = False
    IMG_STACK: bool = False
    AESTHETIC: bool = False
    INVERSE: bool = False
    NET: bool = False
    SMOOTH: bool = True
    NET_THICKNESS: int = 4
    BUFFER: int = 4
    TPB: int = 8
    RESOLUTION: int = 300
    MODEL_THRESH: float = 0.1
    MODEL_SHELL: int = 3
    MODEL_CELL: float = 0.9
    SUPPORT_THRESH: float = 0.2
    SUPPORT_CELL: float = 0.7
    FILE_NAME: str = ""
    PRIMITIVE_TYPE: str = ""


def run_pipeline(config: PipelineConfig) -> None:
    """Execute the voronizer pipeline with ``config``."""
    main.main(config)
