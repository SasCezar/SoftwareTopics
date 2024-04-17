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
    method = instantiate(cfg.completion)
    make_taxonomy(cfg.gitranking_path, method, cfg)


def make_taxonomy(gitranking_path, completion_method, cfg):
    gitranking = GitRanking(gitranking_path)
    name = completion_method.name
    params = "_".join(["_".join(x) for x in completion_method.params.items()])
    path = Path(f'{cfg.interim_data}/taxonomy/{name}')
    path.mkdir(parents=True, exist_ok=True)
    print(path)
    out_path = path / f'gitranking_{name}_{params}.json'
    if out_path.with_suffix('.json').exists() or cfg.redo:
        logger.info(f"Skipping {out_path} - already exists or redo is set to True")
        return
    taxonomy = Taxonomy(name=f'gitranking_{name}')
    taxonomy.terms = list(gitranking.terms.keys())
    taxonomy.missing = copy.deepcopy(taxonomy.terms)
    taxonomy.gitranking_qid = gitranking.terms
    taxonomy.gitranking_aliases = gitranking.aliases

    taxonomy = completion_method.complete(taxonomy)
    taxonomy = Taxonomy.compute_stats(taxonomy)
    data = taxonomy.model_dump_json(indent=4)
    with open(out_path, 'w') as f:
        f.write(data)


if __name__ == '__main__':
    complete()
