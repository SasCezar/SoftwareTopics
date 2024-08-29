from entity.taxonomy import Taxonomy
from processing import CycleRemovalProcessing

def clean():
    in_path = '/home/sasce/PycharmProjects/SoftwareTopics/src/pipeline/patched_gitranking_ensemble_patched_cascade_topsis_llm_gpt-4-1106-preview_prompt_type_patch.json'
    out_path = '/home/sasce/PycharmProjects/SoftwareTopics/src/pipeline/patched_gitranking_ensemble_patched_cascade_topsis_llm_gpt-4-1106-preview_prompt_type_patch_final.json'

    taxonomy = Taxonomy().load(in_path)
    cycle = CycleRemovalProcessing()
    taxonomy = cycle.process(taxonomy)
    taxonomy = taxonomy.update()
    data = taxonomy.model_dump_json(indent=4)
    with open(out_path, 'w') as f:
        f.write(data)


if __name__ == '__main__':
    clean()
