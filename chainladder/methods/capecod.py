# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from chainladder.methods import Benktander
import pandas as pd
import warnings


class CapeCod(Benktander):
    """Applies the CapeCod technique to triangle **X**

    Parameters
    ----------
    trend : float (default=0.0)
        The cape cod trend assumption.  Any Trend transformer on X will override
        this argument.
    decay : float (defaut=1.0)
        The cape cod decay assumption
    n_iters : int, optional (default=1)
        Number of iterations to use in the Benktander model.
    apriori_sigma : float, optional (default=0.0)
        Standard deviation of the apriori.  When used in conjunction with the
        bootstrap model, the model samples aprioris from a lognormal distribution
        using this argument as a standard deviation.
    random_state : int, RandomState instance or None, optional (default=None)
        Seed for sampling from the apriori distribution.  This is ignored when
        using as a deterministic method.
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    groupby :
        An option to group levels of the triangle index together for the purposes
        of deriving the apriori measures.  If omitted, each level of the triangle
        index will receive its own apriori computation.


    Attributes
    ----------
    triangle :
        returns **X**
    ultimate_ :
        The ultimate losses per the method
    ibnr_ :
        The IBNR per the method
    apriori_ :
        The trended apriori vector developed by the Cape Cod Method
    detrended_apriori_ :
        The detrended apriori vector developed by the Cape Cod Method
    """

    def __init__(self, trend=0, decay=1, n_iters=1, apriori_sigma=0.0,
                 random_state=None, groupby=None):
        self.trend = trend
        self.decay = decay
        self.n_iters = n_iters
        self.apriori_sigma = apriori_sigma
        self.random_state = random_state
        self.groupby = groupby

    def fit(self, X, y=None, sample_weight=None):
        """Fit the model with X.

        Parameters
        ----------
        X : Triangle-like
            Loss data to which the model will be applied.
        y : None
            Ignored
        sample_weight : Triangle-like
            The exposure to be used in the method.
        Returns
        -------
        self : object
            Returns the instance itself.
        """

        if sample_weight is None:
            raise ValueError("sample_weight is required.")
        self.apriori = 1.0
        self.X_ = self.validate_X(X)
        self.validate_weight(X, sample_weight)
        sample_weight = sample_weight.set_backend(self.X_.array_backend)
        self.apriori_, self.detrended_apriori_ = self._handle_aprioris(X, sample_weight)
        self.expectation_ = self.detrended_apriori_ * sample_weight.values
        super().fit(X, y, self.expectation_)
        return self

    def _handle_aprioris(self, X, sample_weight):
        if self.groupby is not None:
            if callable(self.groupby):
                X_gb = X.groupby(self.groupby(X))
                sw_gb = sample_weight.groupby(self.groupby(sample_weight))
            else:
                X_gb = X.groupby(self.groupby)
                sw_gb = sample_weight.groupby(self.groupby)
            grouped = CapeCod(
                decay=self.decay, trend=self.trend, n_iters=self.n_iters,
                apriori_sigma=self.apriori_sigma, random_state=self.random_state).fit(
                X_gb.sum(), sample_weight=sw_gb.sum())
            gb_apriori_ = grouped.apriori_
            gb_detrended_apriori_ = grouped.detrended_apriori_
            indices = sw_gb.groups.indices
            index_map = {vi: k for k,v in indices.items() for vi in v}
            gb_map = {i[1][0]: i[0] for i in gb_apriori_.index.iterrows()}
            triangle_map = pd.Series({
                k: gb_map[v] for k, v in index_map.items()}).sort_index().values
            apriori_ = sample_weight.copy()
            apriori_.values = gb_apriori_.values[triangle_map]
            detrended_apriori_ = sample_weight.copy()
            detrended_apriori_.values = gb_detrended_apriori_.values[triangle_map]
            return apriori_, detrended_apriori_
        else:
            return self._get_capecod_aprioris(X, sample_weight)

    def _get_capecod_aprioris(self, X, sample_weight):
        """ Private method to establish CapeCod Apriori """
        xp = X.get_array_module()
        ult = X.copy()
        latest = X.latest_diagonal.values
        len_orig = sample_weight.shape[-2]
        reported_exposure = sample_weight.values / self._align_cdf(ult, sample_weight)
        if hasattr(X, "trend_"):
            if self.trend != 0:
                warnings.warn(
                    "CapeCod Trend assumption is ignored when X has a trend_ property."
                )
            trend_array = X.trend_.latest_diagonal.values
        else:
            trend_array = (X.trend(self.trend) / X).latest_diagonal.values
        if hasattr(sample_weight, "olf_"):
            sw_olf_array = sample_weight.olf_.values
        else:
            sw_olf_array = 1
        if hasattr(X, "olf_"):
            X_olf_array = X.olf_.values
        else:
            X_olf_array = 1
        decay_matrix = self.decay ** xp.abs(
            xp.arange(len_orig)[None].T - xp.arange(len_orig)[None]
        )
        weighted_exposure = xp.swapaxes(reported_exposure, -1, -2) * decay_matrix
        trended_ultimate = (latest * trend_array * X_olf_array) / (
            reported_exposure * sw_olf_array
        )
        trended_ultimate = xp.swapaxes(trended_ultimate, -1, -2)
        apriori = xp.nansum(weighted_exposure * trended_ultimate, -1) / xp.nansum(
            weighted_exposure, -1
        )
        ult.values = apriori[..., None]

        apriori_ = ult.copy()
        detrended_ultimate = apriori_.values / trend_array / X_olf_array * sw_olf_array
        detrended_apriori_ = ult.copy()
        detrended_apriori_.values = detrended_ultimate
        return self._set_ult_attr(apriori_), self._set_ult_attr(detrended_apriori_)


    def predict(self, X, sample_weight=None):
        """Predicts the CapeCod ultimate on a new triangle **X**

        Parameters
        ----------
        X : Triangle
            Loss data to which the model will be applied.
        sample_weight : Triangle
            For exposure-based methods, the exposure to be used for predictions

        Returns
        -------
        X_new: Triangle
            Loss data with CapeCod ultimate applied
        """
        if sample_weight is None:
            raise ValueError("sample_weight is required.")
        apriori_, detrended_apriori_ = self._get_capecod_aprioris(
            X, sample_weight
        )
        expectation_ = detrended_apriori_ * sample_weight.values
        X_new = super().predict(X,  expectation_)
        X_new.apriori_ = apriori_
        X_new.detrended_apriori_ = detrended_apriori_
        X_new.expectation_ = expectation_
        return X_new
