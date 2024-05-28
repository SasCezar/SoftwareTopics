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
    models = cfg.ensemble_models
    name = cfg.best.name
    taxonomy_a_path = Path(cfg.best.best_models[models[0]])
    print(taxonomy_a_path)
    taxonomy_b_path = Path(cfg.best.best_models[models[1]])
    print(taxonomy_b_path)

    taxonomy_a = Taxonomy.load(taxonomy_a_path)
    taxonomy_b = Taxonomy.load(taxonomy_b_path)

    logger.info(f"Taxonomy A: {models[0]} - {taxonomy_a_path}")
    logger.info(f"Taxonomy B: {models[1]} - {taxonomy_b_path}")

    ensemble: AbstractEnsemble = instantiate(cfg.ensemble)
    res = ensemble.complete(taxonomy_a, taxonomy_b)

    output = Path(cfg.output) / ensemble.name / name
    output.mkdir(parents=True, exist_ok=True)
    output = output / f'{taxonomy_a_path.stem}_{taxonomy_b_path.stem}.json'
    data = res.model_dump_json(indent=4)
    with open(output, 'w') as f:
        f.write(data)


if __name__ == '__main__':
    complete()
