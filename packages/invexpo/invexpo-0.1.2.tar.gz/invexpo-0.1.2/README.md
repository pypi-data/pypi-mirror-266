# Inverse Exponential Distribution
This is a custom probability density function I created to solve a particular problem I had at work, however it could also be useful to others.

This distribution aims to fit exponentially *ascending* data on a continuous interval [a, b]. That is, it's not bound to zero like the regular exponential distribution and can be defined for any interval.

With this module, I aim to mimic the `scipy` API it has for its distributions (although not *everything* is implemented.)

## Dependencies
This module uses [scipy](https://github.com/scipy/scipy/blob/main/LICENSE.txt) for a lot of the backend which (at the time of writing) is licensed under BSD-3.

## Warnings
* When fitting your data, the lower and upper bounds are determined by the min/max of the data; this will severely impact the results if you have very low/high extremes. It's recommended to treat your data and ensure the sample you're fitting is a "natural"-looking exponentially ascending shape.

## Example Data
This is an example of exponentially ascending data on the interval `[600, 800]`

* NOTE: this distribution can capture various shapes whether it's a slow rise or sharper rise. This example used a fairly linear rise as a demonstration.

<img width="580" alt="image" src="https://github.com/Kiyoshika/inverse-exponential/assets/49159969/e3b89740-747c-4ccb-8b63-b3c21313da18">

## Mathematical Details
If you're interested in the actual derivation, see the [whitepaper](whitepapers/) directory in this repo (will list all revisions of the paper as a separate PDF.)

## Installation
Install with `pip3 install invexpo` or download from the [releases](https://github.com/Kiyoshika/inverse-exponential/releases) and install locally.

## Usage
Initialize an "empty" distribution:
```python
from invexpo.inverse_exponential import InverseExponential

invex = InverseExponential()
```

You can either fit the distribution to data or create a theoretical distribution.

Note that `fit()` only accepts python lists as of now:
```python
# sample data that mimics an "exponentially increasing" function bounded by [600, 800]
data = [600, 625, 650, 675, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800]

invex = InverseExponential()

# fit to data
invex.fit(data)

# there is also a maxiter parameter if the optimizer fails to converge
# for some reason, but usually there might be a more serious problem
# if that's happening...
invex.fit(data, maxiter=12345)

# create theoretical distribution
# NOTE: the 'a' (shape) parameter is usually very small, large numbers can cause overflows.
# Larger values of 'a' will create sharper peaks. Smaller values will more smoothly
# transition over the interval.
invex.create(a = 0.007, lower_bound = 300, upper_bound = 900)
```

### Methods
After fitting/creating a distribution you can use the following methods:

* `get_parameter() -> float`
  * Returns the value of `a`, the shape parameter
* `pdf(x: float) -> float`
  * Evaluates the probability density function at `x` (i.e., `P(x)`)
* `cdf(x: float) -> float`
  * Evaluate the cumulative density function at `x`, (i.e., `P(X <= x)`)
* `icdf(p: float) -> float`
  * Evaluate the inverse CDF to get a percentile `p` for `0 <= p <= 1`
* `ppf(p: float) -> float`
  * Same as `icdf` just a different name (percentile point function)
* `integrate(lower_bound: float, upper_bound: float) -> float`
  * Integrates the pdf over the interval `[lower_bound, upper_bound]`
* `rvs(size: int = 1) -> list[float]`
  * Generate `size` random variables from the distribution
* `moment(n: int) -> float`
  * Obtain the `n`-th moment of the distribution
* `mean() -> float`
  * Obtain the mean of the distribution (equivalent to `moment(1)`)
* `median() -> float`
  * Obtain the median of the distribution
* `var() -> float`
  * Obtain the variance of the distribution (equivalent to `moment(2) - moment(1)**2`)
* `std() -> float`
  * Obtain the standard deviation of the distribution (equivalent to `np.sqrt(var())`)
