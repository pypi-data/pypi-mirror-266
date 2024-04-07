"""Code to easily call the post hoc ensembling methods."""
from __future__ import annotations

from phem.application_utils import methods_factories


def get_ensemble_switch_case_config(method, rng_seed=None, metric=None, n_jobs=None,
                                    is_binary=None, labels=None):


    if method == "SingleBest":
        return methods_factories._factory_SingleBest(metric=metric)
    # -- Best Configs on Val data from Purucker et al. QDO-ES Paper
    elif method == "GES":
        return methods_factories._factory_es(rng_seed, metric, n_jobs, True)
    elif method == "QDO-ES":
        return methods_factories._factory_qdo(
            rng_seed, metric, is_binary, labels, n_jobs, "sliding",
            "bs_configspace_similarity_and_loss_correlation", 49, "RandomL2Combinations",
            1, "combined_dynamic", "two_point_crossover", 0.5,
            True, 0.5, True, None,None, None, 1., None, 40,
        )
    elif method == "QO-ES":
        return methods_factories._factory_qdo(
            rng_seed, metric, is_binary, labels, n_jobs, "quality",
            None, 49, "RandomL2Combinations",
            1, "combined_dynamic", "average", 0.5,
            True, 0.5, True, None,None, None, 1., None, 40,
        )
    else:
        raise ValueError(f"Unknown method! Got: {method}")
