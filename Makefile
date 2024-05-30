PYTHON=/home/sasce/.cache/pypoetry/virtualenvs/softwaretopics-k-hmEQ_C-py3.11/bin/python
export PYTHONPATH := ${PYTHONPATH}:src/
export HYDRA_FULL_ERROR=1

complete_wiki:
	${PYTHON} src/pipeline/complete_taxonomy.py -m completion=wikidata completion.take_all=False completion.type_threshold=0,3,5,10 completion.max_depth=2,3,4 hydra.launcher.n_jobs=1
	${PYTHON} src/pipeline/complete_taxonomy.py -m completion=wikidata completion.take_all=True completion.type_threshold=10 completion.max_depth=10 hydra.launcher.n_jobs=1

complete_cso:
	${PYTHON} src/pipeline/complete_taxonomy.py -m completion=cso completion.threshold=0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,2 completion.sentence_transformer=all-mpnet-base-v2,all-MiniLM-L6-v2

complete_llm:
	${PYTHON} src/pipeline/complete_taxonomy.py -m completion=llm completion.model=gpt-3.5-turbo,gpt-4-1106-preview completion.prompt_type=w_taxo,simple hydra.launcher.n_jobs=1

complete_llm_iter:
	${PYTHON} src/pipeline/complete_taxonomy.py -m completion=llm-iter completion.model=gpt-3.5-turbo,gpt-4-1106-preview completion.prompt_type=w_taxo,simple hydra.launcher.n_jobs=1

postprocess:
	${PYTHON} src/pipeline/postprocess_taxonomy.py -m 'processing/processors=[],[cycle],[abstract],[bridge],[minimization]'
	${PYTHON} src/pipeline/postprocess_taxonomy.py -m 'processing/processors=[cycle,abstract],[cycle,bridge],[cycle,minimization],[abstract,bridge],[abstract,minimization],[bridge,minimization]'
	${PYTHON} src/pipeline/postprocess_taxonomy.py -m 'processing/processors=[cycle,abstract,bridge],[cycle,abstract,minimization],[cycle,bridge,minimization],[abstract,bridge,minimization]'
	${PYTHON} src/pipeline/postprocess_taxonomy.py -m 'processing/processors=[cycle,abstract,bridge,minimization]'

complete_all: complete_wiki complete_cso complete_llm complete_llm_iter

complete: complete_all postprocess

ensemble:
	${PYTHON} src/pipeline/ensemble_taxonomies.py -m 'ensemble=cascade,simple,disambiguate'

# Evaluation
evaluate_taxonomies:
	${PYTHON} src/pipeline/evaluation_metrics.py hydra.launcher.n_jobs=1
	${PYTHON} scripts/python/hyperparameter_correlation.py

inter_model:
	${PYTHON} src/pipeline/inter_models_eval.py

evaluate: evaluate_taxonomies inter_model

hyper_optimization:
	${PYTHON} src/pipeline/hyperparameter_optimization.py -m optimizer=pareto,scoring,WASPAS,ARAS,COCOSO,CODAS,COPRAS,EDAS,VIKOR metrics=default,few


# R scripts for plots in the paper
#
#metrics:
#	Rscript scripts/R/metrics.R
#
#grouped_metrics:
#	Rscript scripts/R/grouped_metrics.R
#
#correctness:
#	Rscript scripts/R/wikiid_correctness.R
#
#corr_heatmap:
#	Rscript scripts/R/corr_heatmap.R
#
#intersections:
#	Rscript scripts/R/.R
#

plots: metrics