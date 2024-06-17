from pathlib import Path

import hydra
from hydra.utils import instantiate
from loguru import logger
from omegaconf import DictConfig

from entity.taxonomy import Taxonomy
from processing import CycleRemovalProcessing
from processing.normalize import NormalizeTermsProcessing


@hydra.main(version_base='1.3', config_path="../conf", config_name="patch_taxonomy")
def patch(cfg: DictConfig):
    print(f"Config: {cfg}")
    method = instantiate(cfg.completion)
    path_taxonomy(cfg.taxonomy_path, method, cfg)


def path_taxonomy(taxonomy_path, completion_method, cfg):
    name = completion_method.name
    params = "_".join(["_".join(x) for x in completion_method.params.items()])
    path = Path(f'{cfg.result}/taxonomy/{cfg.ensemble}/{cfg.best}')
    path.mkdir(parents=True, exist_ok=True)
    print(path)
    out_path = path / f'patched_gitranking_ensemble_patched.json'
    if out_path.with_suffix('.json').exists() or cfg.redo:
        logger.info(f"Skipping {out_path} - already exists or redo is set to True")
        return

    taxonomy = Taxonomy().load(taxonomy_path)

    taxonomy = completion_method.complete(taxonomy)
    taxonomy = taxonomy.update()
    normalize = NormalizeTermsProcessing(embedding_model='all-mpnet-base-v2')
    taxonomy = normalize.process(taxonomy)
    cycle = CycleRemovalProcessing()
    taxonomy = cycle.process(taxonomy)
    taxonomy = taxonomy.update()
    data = taxonomy.model_dump_json(indent=4)
    with open(out_path, 'w') as f:
        f.write(data)


if __name__ == '__main__':
    patch()
