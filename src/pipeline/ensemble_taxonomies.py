import copy
from pathlib import Path

import hydra
from hydra.utils import instantiate
from loguru import logger
from omegaconf import DictConfig

from ensemble.ensemble import AbstractEnsemble
from entity.gitranking import GitRanking
from entity.taxonomy import Taxonomy


@hydra.main(version_base='1.3', config_path="../conf", config_name="ensemble")
def complete(cfg: DictConfig):
    print(f"Config: {cfg}")
    taxonomy_a = Taxonomy.load(Path(cfg.taxonomy_a))
    taxonomy_b = Taxonomy.load(Path(cfg.taxonomy_b))

    logger.info(f"Taxonomy A: {cfg.taxonomy_a}")
    logger.info(f"Taxonomy B: {cfg.taxonomy_b}")

    ensemble: AbstractEnsemble = instantiate(cfg.ensemble)
    res = ensemble.complete(taxonomy_a, taxonomy_b)

    data = res.model_dump_json(indent=4)
    with open(Path(cfg.output), 'w') as f:
        f.write(data)


if __name__ == '__main__':
    complete()
