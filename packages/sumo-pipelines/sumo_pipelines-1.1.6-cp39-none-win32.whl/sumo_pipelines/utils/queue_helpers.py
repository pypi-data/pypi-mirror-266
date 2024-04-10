from copy import deepcopy
from typing import Generator
from sumo_pipelines.config import PipelineConfig
from ray.util.queue import Queue, Empty
from omegaconf import OmegaConf


def unpack_queue(
    q: Queue,
    config: PipelineConfig,
) -> Generator[PipelineConfig, None, None]:
    
    while (not q.empty()):
        try:
            item = q.get_nowait()
        except Empty():
            print("Queue is empty")
            break
        
        # copy the config
        new_config = deepcopy(config)

        for dp, val in item[1:]:
            # set the value
            OmegaConf.update(new_config, dp, val)

        yield new_config

