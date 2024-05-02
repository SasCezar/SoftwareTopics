import copy
from pathlib import Path

import hydra
from hydra.utils import instantiate
from loguru import logger
from omegaconf import DictConfig

from entity.gitranking import GitRanking
from entity.taxonomy import Taxonomy


@hydra.main(version_base='1.3', config_path="../conf", config_name="complete_taxonomy")
def complete(cfg: DictConfig):
    print(f"Config: {cfg}")
    taxonomies = []
    for taxo in cfg.ensemble:
        method = Taxonomy.load(taxo)
        taxonomies.append(method)





if __name__ == '__main__':
    complete()
