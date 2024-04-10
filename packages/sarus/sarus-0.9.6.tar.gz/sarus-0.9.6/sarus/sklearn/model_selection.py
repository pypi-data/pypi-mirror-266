from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init, sarus_property
import numpy as np

try:
    import sklearn.model_selection as sk_model_selection
    from sklearn.model_selection import *  # noqa: F401
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class TimeSeriesSplit(DataSpecWrapper[sk_model_selection.TimeSeriesSplit]):
    @sarus_init("sklearn.SK_TIME_SERIES_SPLIT")
    def __init__(
        self,
        *,
        n_splits=5,
        n_repeats=10,
        random_state=None,
        _dataspec=None,
    ):
        ...


class RepeatedStratifiedKFold(
    DataSpecWrapper[sk_model_selection.RepeatedStratifiedKFold]
):
    @sarus_init("sklearn.SK_REPEATED_STRATIFIED_KFOLD")
    def __init__(
        self,
        *,
        n_splits=5,
        n_repeats=10,
        random_state=None,
        _dataspec=None,
    ):
        ...


class KFold(DataSpecWrapper[sk_model_selection.KFold]):
    @sarus_init("sklearn.SK_KFOLD")
    def __init__(self, n_splits=5, *, shuffle=False, random_state=None):
        ...


class GridSearchCV(DataSpecWrapper[sk_model_selection.GridSearchCV]):
    @sarus_init("sklearn.SK_GRID_SEARCH_CV")
    def __init__(
        self,
        *,
        estimator,
        param_grid,
        scoring=None,
        n_jobs=None,
        refit=True,
        cv=None,
        verbose=0,
        pre_dispatch="2*n_jobs",
        error_score=np.nan,
        return_train_score=False,
    ):
        ...

    @sarus_property("sklearn.SK_BEST_PARAMS_")
    def best_params_(self):
        ...

    @sarus_property("sklearn.SK_BEST_SCORE_")
    def best_score_(self):
        ...


register_ops()
