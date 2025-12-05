import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.wind_resource import WindResourceModel
import numpy as np


def test_power_law_profile_basic():

    # Create model object with empty file list (we don't load any data here)
    model = WindResourceModel(nc_files=[])

    # Simple fake wind speed at 10 m
    speed_10m = np.array([5.0])  # 5 m/s at 10 m

    # Use power law to get wind speed at 100 m
    speed_100m = model.power_law_profile(
        speed_ref=speed_10m,
        z_ref=10,
        z_target=100,
        alpha=0.14,
    )

    # We expect that speed at 100 m is bigger than at 10 m
    assert speed_100m[0] > speed_10m[0]


def test_weibull_fit_not_nan():
 
    model = WindResourceModel(nc_files=[])

    # Create fake wind speed data (100 values of 8 m/s)
    speeds = np.full(100, 8.0)

    # Fit Weibull distribution
    A, k = model.fit_weibull(speeds)

    # Check that we got numbers, not NaN
    assert not np.isnan(A)
    assert not np.isnan(k)


def test_weibull_mean_roughly_correct():
   
    model = WindResourceModel(nc_files=[])

    speeds = np.full(100, 8.0)  # again 8 m/s
    A, k = model.fit_weibull(speeds)

    # If A or k is NaN (should not happen), fail the test
    assert not np.isnan(A)
    assert not np.isnan(k)

    # Compute theoretical mean of Weibull: mean = A * Gamma(1 + 1/k)
    from scipy.special import gamma

    mean_weibull = A * gamma(1.0 + 1.0 / k)

    # Check that the mean is close to 8.0 (within +/- 1 m/s)
    assert abs(mean_weibull - 8.0) < 1.0
