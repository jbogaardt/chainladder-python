.. _tails:

.. currentmodule:: chainladder

===============
Tail Estimators
===============

Basics and Commonalities
=========================

The Tails module provides a variety of tail transformers that allow for the
extrapolation of development patterns beyond the end of the triangle.  Tail
factors are used extensively in commercial lines of business.

Every tail estimator produced a ``tail_`` attribute which represents the point
estimate of the tail of the Triangle.

Run Off
-------
In addition to point estimates, tail estimators support run-off analysis.  The
``ldf_`` and ``cdf_`` attribute splits the tail point estimate into enough
development patterns to allow for tail run-off to be examined for at least another
valuation year. For an annual ``development_grain`` grain, the development pattterns
include two additional patterns.

  >>> development.cdf_
           12-Ult    24-Ult    36-Ult    48-Ult    60-Ult    72-Ult    84-Ult    96-Ult   108-Ult
  (All)  8.920234  2.974047  1.831848  1.441392  1.230198  1.104917  1.060448  1.026309  1.009217
  >>> tail.cdf_
           12-Ult    24-Ult    36-Ult    48-Ult    60-Ult    72-Ult    84-Ult    96-Ult   108-Ult   120-Ult   132-Ult
  (All)  9.004403  3.002109  1.849133  1.454993  1.241806  1.115343  1.070454  1.035993  1.018739  1.009436  1.005006

For quarterly grain, there are five additional development patterns and for monthly
there are thirteen.

**Example:**
  >>> triangle = cl.load_sample('quarterly')['paid']
  >>> tail = cl.TailCurve().fit(triangle)
  >>> # Slice just the tail entries
  >>> tail.cdf_[~tail.ldf_.development.isin(triangle.link_ratio.development)]
         135-Ult   138-Ult   141-Ult   144-Ult  147-Ult
  (All)  1.00065  1.000531  1.000434  1.000355  1.00029

  .. note::
     The point estimate ``tail_`` of the tail is the CDF for 135-Ult. The remaining
     CDFs simply represent the run-off of this tail.


Attachment Age
--------------
By default, tail estimators attach to the oldest ``development`` age of the ``Triangle``.
In practice, the last several known development factors of a ``Triangle`` can be
unreliable and attaching the tail earlier and using it as a smoothing mechanism
is preferred.  All tail estimators have an ``attachment_age`` parameter that
allows you to select the development age to which the tail will attach.

  >>> import chainladder as cl
  >>> import pandas as pd
  >>> raa = cl.load_sample('raa')
  >>> pd.concat((
  ...     cl.TailCurve().fit(raa).ldf_.T.iloc[:, 0].rename('Unsmoothed'),
  ...     cl.TailCurve(attachment_age=12).fit(raa).ldf_.T.iloc[:, 0].rename('Curve Fit')
  ... ), 1).plot(grid=True, title='Exponential Smoothing of LDF');

.. figure:: /auto_examples/images/sphx_glr_plot_exponential_smoothing_001.png
   :target: ../auto_examples/plot_exponential_smoothing.html
   :align: center
   :scale: 70%

Regardless of where you attach a tail, there will be incremental patterns to at
least one year past the end of the `Triangle` to support run-off analysis.

.. _constant:

TailConstant
=============
:class:`TailConstant` allows you to input a tail factor as a constant.  This is
useful when relying on tail selections from an external source like industry data.

The tail factor supplied applies to all individual triangles contained within
the Triangle object.  If this is not the desired outcome, slicing individual
triangles and applying :class:`TailConstant` separately to each can be done.

Decay
-----
For run-off analysis, you can control the decay of your tail.  An exponential
``decay`` parameter is also available to facilitate the run off analysis described
above.

  >>> import chainladder as cl
  >>> abc = cl.Development().fit_transform(cl.load_sample('abc'))
  >>> abc = cl.TailConstant(tail=1.05, decay=0.95).fit_transform(abc)
  >>> abc.ldf_
            12-24     24-36     36-48     48-60     60-72     72-84     84-96    96-108   108-120   120-132   132-144   144-Ult
  (All)  2.308599  1.421098  1.199934  1.113445  1.072736  1.047559  1.034211  1.026047  1.020188  1.016259  1.002436  1.047448

As we can see in the example, the 5% tail in the example is split between the
amount to run-off over the subsequent calendar period **132-144**, and the
remainder, **144-Ult**.  The split is controlled by the ``decay`` parameter. We
can always reference our ``tail_`` point estimate.

  >>> abc.tail_
         132-Ult
  (All)     1.05



.. _curve:

TailCurve
==========
:class:`TailCurve` allows for extrapolating a tail factor using curve fitting.
Currently, exponential decay of LDFs and inverse power curve (for slower decay)
are supported.


  >>> import chainladder as cl
  >>> import pandas as pd
  >>> clrd = cl.load_sample('clrd').groupby('LOB').sum()['CumPaidLoss']
  >>> cdf_ip = cl.TailCurve(curve='inverse_power').fit(clrd)
  >>> cdf_xp = cl.TailCurve(curve='exponential').fit(clrd)
  >>> pd.concat((cdf_ip.tail_.rename("Inverse Power"),
  ...            cdf_xp.tail_.rename("Exponential")), axis=1).plot(
  ...         kind='bar', grid=True, title='Curve Fit Comparison').set(
  ...         xlabel='Industry', ylabel='Tail Factor');

.. figure:: /auto_examples/images/sphx_glr_plot_tailcurve_compare_001.png
   :target: ../auto_examples/plot_tailcurve_compare.html
   :align: center
   :scale: 50%

In general, ``inverse_power`` fit produce more conservative tail estimates than
the ``exponential`` fit.  Both are fit using basic OLS regression on your selected
development patterns.



Extrapolation Period
---------------------
The ``extrap_periods`` parameter allows for limiting how far beyond the edge of
the triangle the tail should be extrapolated.  Results for the ``inverse_power``
curve are sensitive to this parameter as it tends to converge slowly to its
asymptotic value.

.. figure:: /auto_examples/images/sphx_glr_plot_extrap_period_001.png
   :target: ../auto_examples/plot_extrap_period.html
   :align: center
   :scale: 50%

Regression parameters
----------------------
Underlying the curve fit is an OLS regression which generates both a ``slope_``
and ``intercept_`` term.

For the ``exponential`` curve fit with slope, b and intercept a, the tail factor
is:

.. math::
   \prod_{i}^{N}1+exp(\beta X+\alpha )

For the ``inverse_power`` curve, the tail factor is:

.. math::
   \prod_{i}^{N}1+exp(\alpha) X^{\beta}


Deriving the ``tail_`` factor manually:

  >>> import chainladder as cl
  >>> import numpy as np
  >>> raa = cl.load_sample('raa')
  >>> tail = cl.TailCurve('exponential').fit(raa)
  >>> tail.tail_
          120-Ult
  (All)  1.009436
  >>> # Manual calculation
  >>> np.prod((1+np.exp(np.arange(10, 10+tail.extrap_periods)*tail.slope_.values+tail.intercept_.values)))
  1.0094357515812302
  >>> tail = cl.TailCurve('inverse_power').fit(raa)
  >>> tail.tail_
          120-Ult
  (All)  1.101482
  >>> # Manual calculation
  >>> np.prod(1+np.exp(tail.intercept_.values)*(np.arange(10, 10+tail.extrap_periods)**tail.slope_.values))
  1.1014821181181595

.. topic:: References

  .. [CAS2013] `CAS Tail Factor Working Party, "The Estimation of Loss Development Tail
      Factors: A Summary Report", Casualty Actuarial Society E-Forum <https://www.casact.org/sites/default/files/database/forum_13fforum_02-tail-factors-working-party.pdf>`__


.. _bondy:

TailBondy
==========
:class:`TailBondy` allows for setting the tail factor using the Generalized Bondy
method.  The main estimate of the method is the Bondy exponent.  The tail factor
is can be described as a function of using an ``ldf_`` factor representative of the
last age in the Triangle and the Bondy exponent ``b_``.

More formally, the tail factor is defined as:

.. math::
   F(n)=f(n-1)^{B}f(n-1)^{B^{2}}...=f(n-1)^{\frac{B}{1-B}}

Rather than using the last known development factor explicitly, we estimate the
fitted LDF using the formula above along with the ``earliest_age`` parameter.
The following example shows how the :class:`TailBondy` estimator develops a
tail factor from ``b_``, the Bondy exponent.

  >>> import chainladder as cl
  >>> # Data and initial development patterns
  >>> triangle = cl.load_sample('tail_sample')
  >>> dev = cl.Development(average='simple').fit_transform(triangle)
  >>> # Estimate the Bondy Tail
  >>> tail = cl.TailBondy(earliest_age=12).fit(dev)
  >>> # Get last fitted LDF of the model
  >>> last_fitted_ldf = (tail.earliest_ldf_**(tail.b_**8))
  >>> # Calculate the tail using the Bondy formula above
  >>> last_fitted_ldf**(tail.b_/(1-tail.b_))
         incurred     paid
  Total
  Total  1.003982  1.02773
  >>> # Compare to actual tail
  >>> tail.tail_
         incurred     paid
  Total
  Total  1.003982  1.02773

.. topic:: References

  .. [CAS2013] `CAS Tail Factor Working Party, "The Estimation of Loss Development Tail
      Factors: A Summary Report", Casualty Actuarial Society E-Forum <https://www.casact.org/sites/default/files/database/forum_13fforum_02-tail-factors-working-party.pdf>`__


.. _tailclark:

TailClark
==========
:class:`TailClark` is a continuation of the :class:`ClarkLDF` model.  Familiarity
with :ref:`Growth Curve Fitting<clarkldf>` will aid in understanding this Estimator.
The growth curve approach used by Clark produces development patterns for any
age including ages beyond the edge of the Triangle.

An example completing Clark's model:

  >>> import chainladder as cl
  >>> genins = cl.load_sample('genins')
  >>> dev = cl.ClarkLDF()
  >>> tail = cl.TailClark()
  >>> tail.fit(dev.fit_transform(genins)).cdf_
            12-Ult    24-Ult    36-Ult    48-Ult    60-Ult    72-Ult    84-Ult    96-Ult   108-Ult   120-Ult   132-Ult
  (All)  21.086776  5.149415  2.993038  2.229544  1.857163  1.642623  1.505601  1.411711  1.344001  1.293236  1.253992

Truncated pattterns
--------------------

Clark warns of the dangers of extrapolating too far beyond the edge of a Triangle,
particularly with a heavy tailed distribution.  In these cases, it is suggested that
a suitable cut-off age or ``truncation_age`` be established where losses are considered
fully developed.

  >>> tail = cl.TailClark(truncation_age=245)
  >>> tail.fit(dev.fit_transform(genins)).cdf_
            12-Ult   24-Ult    36-Ult    48-Ult    60-Ult    72-Ult    84-Ult    96-Ult   108-Ult   120-Ult   132-Ult
  (All)  19.209306  4.69099  2.726575  2.031041  1.691804  1.496359  1.371531  1.285997  1.224313  1.178065  1.142313



.. topic:: References

  .. [CD2003] `Clark, David R., "LDF Curve-Fitting and Stochastic Reserving: A Maximum Likelihood Approach",
               Casualty Actuarial Society Forum, Fall, 2003 <https://www.casact.org/sites/default/files/database/forum_03fforum_03ff041.pdf>`__
