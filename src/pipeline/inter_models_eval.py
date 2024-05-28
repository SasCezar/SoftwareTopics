from pathlib import Path

import hydra
import pandas as pd
from more_itertools import flatten
from omegaconf import DictConfig

from entity import Taxonomy


def get_pair_intersections(taxonomies):
    """Get the pairwise intersections between all taxonomies.
    And the intersection between all taxonomies """
    intersections = []
    pairs = []
    for name1, taxo1 in taxonomies.items():
        pairs_1 = {(x[0].lower(), x[1].lower()) for x in taxo1.pairs}
        pairs.append(pairs_1)
        for name2, taxo2 in taxonomies.items():
            if name1 == name2:
                continue

            pairs_2 = {(x[0].lower(), x[1].lower()) for x in taxo2.pairs}

            pairs.append(pairs_2)
            intersection = pairs_1.intersection(pairs_2)
            intersections.append([name1, name2, len(intersection)])

    res = set.intersection(*map(set, pairs))
    tot = len(set.union(*map(set, pairs)))
    intersections.append(['All', 'All', len(res)])

    return intersections


def get_terms_intersections(taxonomies):
    """Get the pairwise intersections between all taxonomies.
And the intersection between all taxonomies """

    intersections = []
    terms = []
    for name1, taxo1 in taxonomies.items():
        terms_1 = set([x.lower() for x in flatten([tuple(x[:2]) for x in taxo1.pairs])])
        terms.append(terms_1)
        for name2, taxo2 in taxonomies.items():
            if name1 == name2:
                continue

            terms_2 = set([x.lower() for x in flatten([tuple(x[:2]) for x in taxo2.pairs])])
            terms.append(terms_2)
            intersection = terms_1.intersection(terms_2).intersection(
                set([x.lower() for x in taxo1.gitranking_qid.keys()]))
            intersections.append([name1, name2, len(intersection)])

    res = set.intersection(*map(set, terms))
    intersections.append(['All', 'All', len(res)])

    return intersections


def get_unmatched_intersections(taxonomies):
    """Get the pairwise intersections between all taxonomies.
    And the intersection between all taxonomies """

    intersections = []
    terms = []
    for name1, taxo1 in taxonomies.items():
        terms_1 = set([x.lower() for x in flatten([tuple(x[:2]) for x in taxo1.pairs])])
        terms_1 = set([x.lower() for x in taxo1.gitranking_qid.keys()]).difference(terms_1)
        print(len(terms_1), taxo1.num_unique_missing)
        for name2, taxo2 in taxonomies.items():
            if name1 == name2:
                continue

            terms_2 = set([x.lower() for x in flatten([tuple(x[:2]) for x in taxo2.pairs])])
            terms_2 = set([x.lower() for x in taxo2.gitranking_qid.keys()]).difference(terms_2)
            terms.append(terms_2)
            intersection = terms_1.intersection(terms_2)
            intersections.append([name1, name2, len(intersection)])

    res = set.intersection(*map(set, terms))
    intersections.append(['All', 'All', len(res)])
    return intersections


def get_new_terms_intersections(taxonomies):
    intersections = []
    terms = []
    for name1, taxo1 in taxonomies.items():
        terms_1 = set([x.lower() for x in flatten([tuple(x[:2]) for x in taxo1.pairs])])
        terms.append(terms_1)
        for name2, taxo2 in taxonomies.items():
            if name1 == name2:
                continue

            terms_2 = set([x.lower() for x in flatten([tuple(x[:2]) for x in taxo2.pairs])])
            terms.append(terms_2)
            intersection = terms_1.intersection(terms_2)
            intersection = intersection.difference(set([x.lower() for x in taxo1.gitranking_qid.keys()]))
            intersections.append([name1, name2, len(intersection)])

    res = set.intersection(*map(set, terms))
    res = res.difference(set([x.lower() for x in taxo1.gitranking_qid.keys()]))
    intersections.append(['All', 'All', len(res)])

    return intersections


@hydra.main(version_base='1.3', config_path="../conf", config_name="inter_eval")
def inter_model_eval(cfg: DictConfig):
    models = cfg.best.best_models
    name = cfg.best.name

    taxonomies = {}
    for src, path in models.items():
        taxonomies[src] = Taxonomy.load(path)

    res = []
    intersections = get_pair_intersections(taxonomies)
    intersections = [(x[0], x[1], 'Pairs', x[2]) for x in intersections]
    df = pd.DataFrame(intersections, columns=['Model1', 'Model2', 'Metric', 'Intersection'])
    out_path = f'{Path(cfg.taxonomy_folder) / f"pairs_intersections_{name}.csv"}'
    df.to_csv(out_path, index=False)
    res.append(df)

    intersections = get_terms_intersections(taxonomies)
    intersections = [(x[0], x[1], 'Gitranking', x[2]) for x in intersections]
    df = pd.DataFrame(intersections, columns=['Model1', 'Model2', 'Metric', 'Intersection'])
    out_path = f'{Path(cfg.taxonomy_folder) / f"terms_intersections_{name}.csv"}'
    df.to_csv(out_path, index=False)
    res.append(df)

    intersections = get_new_terms_intersections(taxonomies)
    intersections = [(x[0], x[1], 'New Terms', x[2]) for x in intersections]
    df = pd.DataFrame(intersections, columns=['Model1', 'Model2', 'Metric', 'Intersection'])
    out_path = f'{Path(cfg.taxonomy_folder) / f"new_terms_intersections_{name}.csv"}'
    df.to_csv(out_path, index=False)
    res.append(df)

    intersections = get_unmatched_intersections(taxonomies)
    intersections = [(x[0], x[1], 'Unmatched', x[2]) for x in intersections]
    df = pd.DataFrame(intersections, columns=['Model1', 'Model2', 'Metric', 'Intersection'])
    out_path = f'{Path(cfg.taxonomy_folder) / f"unmatched_intersections_{name}.csv"}'
    df.to_csv(out_path, index=False)
    res.append(df)

    df = pd.concat(res)
    df.to_csv(f'{Path(cfg.taxonomy_folder) / f"intersections_{name}.csv"}', index=False)


if __name__ == '__main__':
    inter_model_eval()
