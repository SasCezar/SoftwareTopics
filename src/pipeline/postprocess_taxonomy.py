from pathlib import Path
from typing import List

import hydra
from hydra.utils import instantiate
from loguru import logger
from omegaconf import DictConfig
from tqdm import tqdm

from entity import Taxonomy
from processing import AbstractProcessing


def initialize_postprocessing(processing) -> List[AbstractProcessing]:
    return [instantiate(processing.processors[x]) for x in processing.processors] if processing else []


@hydra.main(version_base='1.3', config_path="../conf", config_name="process_taxonomy")
def process_taxonomy(cfg: DictConfig):
    print(cfg)
    path = Path(cfg.taxonomy_folder)
    folders = [x for x in path.iterdir() if 'processed' not in str(x) and x.is_dir()]
    for folder in tqdm(folders):
        files = [x for x in folder.iterdir() if x.suffix == '.json']
        logger.info(f"Processing {folder}")
        for file in tqdm(files, desc=folder.stem):
            post_processing_methods: List[AbstractProcessing] = initialize_postprocessing(cfg.processing)
            processors_name = "_".join(sorted(cfg.processing.processors.keys())) if cfg.processing else ""

            taxonomy = Taxonomy.load(file)
            for method in post_processing_methods:
                logger.info(f"Processing {method}")
                taxonomy = method.process(taxonomy)

            taxonomy.other['post_processing'] = {x: 1 for x in
                                                 cfg.processing.processors.keys()} if cfg.processing else {}
            folder_processed = Path(str(folder) + '_processed')
            folder_processed.mkdir(exist_ok=True)
            out_path = folder_processed / f"{file.stem}_{processors_name}.json"
            data = taxonomy.model_dump_json(indent=4)
            with open(out_path, 'w') as f:
                f.write(data)


if __name__ == '__main__':
    process_taxonomy()
