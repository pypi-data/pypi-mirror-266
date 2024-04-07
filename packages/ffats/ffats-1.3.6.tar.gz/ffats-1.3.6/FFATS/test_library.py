from .Feature import FeatureSpace
import numpy as np
from .import_lc_cluster import ReadLC_MACHO
from .PreprocessLC import Preprocess_LC
from .alignLC import Align_LC
import os.path
import tarfile
import sys
import pandas as pd
import pytest


@pytest.fixture
def white_noise():
    data = np.random.normal(size=10000)
    mjd = np.arange(10000)
    error = np.random.normal(loc=0.01, scale=0.8, size=10000)
    second_data = np.random.normal(size=10000)
    mjd2 = np.arange(10000)
    error2 = np.random.normal(loc=0.01, scale=0.8, size=10000)
    aligned_data = data
    aligned_second_data = second_data
    aligned_mjd = mjd
    aligned_error = error
    aligned_error2 = error2
    lc = np.array([data, mjd, error, second_data, aligned_data,
                  aligned_second_data, aligned_mjd, aligned_error, aligned_error2])
    return lc


@pytest.fixture
def periodic_lc():
    N = 100
    mjd_periodic = np.arange(N)
    Period = 20
    cov = np.zeros([N, N])
    mean = np.zeros(N)
    for i in np.arange(N):
        for j in np.arange(N):
            cov[i, j] = np.exp(-(np.sin((np.pi/Period) * (i-j))**2))
    data_periodic = np.random.multivariate_normal(mean, cov)
    lc = np.array([data_periodic, mjd_periodic])
    return lc


@pytest.fixture
def sine_lc():
    N = 100
    mjd_periodic = np.arange(N)
    period = 20
    data_periodic = np.sin((np.pi/period) * mjd_periodic)
    lc = np.array([data_periodic, mjd_periodic])
    return lc


@pytest.fixture
def uniform_lc():
    mjd_uniform = np.arange(1000000)
    data_uniform = np.random.uniform(size=1000000)
    lc = np.array([data_uniform, mjd_uniform])
    return lc


@pytest.fixture
def random_walk():
    N = 10000
    alpha = 1.
    sigma = 0.5
    data_rw = np.zeros([N, 1])
    data_rw[0] = 1
    time_rw = range(1, N)
    for t in time_rw:
        data_rw[t] = alpha * data_rw[t-1] + \
            np.random.normal(loc=0.0, scale=sigma)
    time_rw = np.array(range(0, N)) + 1 * np.random.uniform(size=N)
    data_rw = data_rw.squeeze()
    lc = np.array([data_rw, time_rw])
    return lc

@pytest.fixture
def sequence():
    return range(1000)


def test_Amplitude(benchmark, sequence):
    a = FeatureSpace(featureList=['Amplitude'])
    a = benchmark(a.calculateFeature, sequence)

    # Exact value is 475 but I add some space for an error
    assert(a.result(method='array') >= 474.9 and a.result(method='array') <= 475.1)


def test_Autocor(benchmark, periodic_lc):
    a = FeatureSpace(featureList=['Autocor_length'])
    a = benchmark(a.calculateFeature, periodic_lc[:, 0])

    assert(a.result(method='array') == 1)


def test_bench_Autocor(benchmark, white_noise):
    a = FeatureSpace(featureList=['Autocor_length'])
    a = benchmark(a.calculateFeature, white_noise[:, 0])

    assert(a.result(method='array') == 1)


@pytest.mark.skip('Automean was removed from the library')
def test_Automean(benchmark, white_noise):
    a = FeatureSpace(featureList=['Automean'] , Automean=[0,0])
    a = benchmark(a.calculateFeature, white_noise[0])

    assert(a.result(method='array') >= 0.043 and a.result(method='array') <= 0.046)


@pytest.mark.skip('Invalid assertions')
def test_B_R(benchmark, white_noise):
    a = FeatureSpace(featureList=['Q31_color'])
    a = benchmark(a.calculateFeature, white_noise)

    assert(a.result(method='array') >= 0.043 and a.result(method='array') <= 0.046)


def test_Beyond1Std(benchmark, white_noise):
    a = FeatureSpace(featureList=['Beyond1Std'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >=
            0.30 and a.result(method='array') <= 0.40)


def test_Mean(benchmark, white_noise):
    a = FeatureSpace(featureList=['Mean'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >= -
            0.1 and a.result(method='array') <= 0.1)

@pytest.mark.skip('Invalid assertions')
def test_CAR(benchmark, white_noise):
    a = FeatureSpace(featureList=['CAR_sigma', 'CAR_tau', 'CAR_mean'])
    a = a.calculateFeature(white_noise)

    assert(a.result(method='array') >= 0.043 and a.result(method='array') <= 0.046)


def test_bench_CAR(benchmark, white_noise):
    a = FeatureSpace(featureList=['CAR_sigma', 'CAR_tau', 'CAR_mean'])
    a = benchmark(a.calculateFeature, white_noise)


def test_Con(benchmark, white_noise):
    a = FeatureSpace(featureList=['Con'], Con=1)
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >=
            0.04 and a.result(method='array') <= 0.05)


def test_Eta_color(benchmark, white_noise):
    a = FeatureSpace(featureList=['Eta_color'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >=
            1.9 and a.result(method='array') <= 2.1)


def test_Eta_e(benchmark, white_noise):
    a = FeatureSpace(featureList=['Eta_e'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >=
            1.9 and a.result(method='array') <= 2.1)


def test_FluxPercentile(benchmark, white_noise):
    a = FeatureSpace(featureList=['FluxPercentileRatioMid20', 'FluxPercentileRatioMid35',
                     'FluxPercentileRatioMid50', 'FluxPercentileRatioMid65', 'FluxPercentileRatioMid80'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array')[0] >= 0.145 and a.result(
        method='array')[0] <= 0.160)
    assert (a.result(method='array')[1] >= 0.260 and a.result(
        method='array')[1] <= 0.290)
    assert (a.result(method='array')[2] >= 0.350 and a.result(
        method='array')[2] <= 0.450)
    assert (a.result(method='array')[3] >= 0.540 and a.result(
        method='array')[3] <= 0.580)
    assert (a.result(method='array')[4] >= 0.760 and a.result(
        method='array')[4] <= 0.800)


def test_LinearTrend(benchmark, white_noise):
    a = FeatureSpace(featureList=['LinearTrend'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >= -
            0.1 and a.result(method='array') <= 0.1)

def test_MaxSlope(benchmark, sine_lc):
    a = FeatureSpace(featureList=['MaxSlope'])
    a = benchmark(a.calculateFeature, sine_lc)

    assert(a.result(method='array') >= 0.156 and a.result(method='array') <= 0.157)


def test_Meanvariance(benchmark, uniform_lc):
    a = FeatureSpace(featureList=['Meanvariance'])
    a = benchmark(a.calculateFeature, uniform_lc)

    assert (a.result(method='array') >=
            0.575 and a.result(method='array') <= 0.580)


def test_MedianAbsDev(benchmark, white_noise):
    a = FeatureSpace(featureList=['MedianAbsDev'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >=
            0.630 and a.result(method='array') <= 0.700)

def test_MedianBRP(benchmark, sequence):
    a = FeatureSpace(featureList=['MedianBRP'])
    a = benchmark(a.calculateFeature, sequence)

    assert(a.result(method='array') >= 0.19 and a.result(method='array') <= 0.21)


def test_PairSlopeTrend(benchmark, white_noise):
    a = FeatureSpace(featureList=['PairSlopeTrend'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >= -
            0.25 and a.result(method='array') <= 0.25)

def test_PercentAmplitude(benchmark, sequence):
    a = FeatureSpace(featureList=['PercentAmplitude'])
    a = benchmark(a.calculateFeature, sequence)

    assert(a.result(method='array') >= 0.99 and a.result(method='array') <= 1.01)

def test_PercentDifferenceFluxPercentile(benchmark, sequence):
    a = FeatureSpace(featureList=['PercentDifferenceFluxPercentile'])
    a = benchmark(a.calculateFeature, sequence)

    assert(a.result(method='array') >= 1.801 and a.result(method='array') <= 1.802)


def test_Period_Psi(benchmark, periodic_lc):
    a = FeatureSpace(
        featureList=['PeriodLS', 'Period_fit', 'Psi_CS', 'Psi_eta'])
    a = benchmark(a.calculateFeature, periodic_lc)
    assert (a.result(method='array')[0] >=
            19 and a.result(method='array')[0] <= 21)


def test_Q31(benchmark, white_noise):
    a = FeatureSpace(featureList=['Q31'])
    a = benchmark(a.calculateFeature, white_noise)
    assert (a.result(method='array') >=
            1.30 and a.result(method='array') <= 1.38)

@pytest.mark.skip('No assertions')
def test_Q31B_R(benchmark, white_noise):
    a = FeatureSpace(featureList=['Q31B_R'], Q31B_R = [aligned_second_data, aligned_data])
    a = benchmark(a.calculateFeature, white_noise[0])


def test_Rcs(benchmark, white_noise):
    a = FeatureSpace(featureList=['Rcs'])
    a = benchmark(a.calculateFeature, white_noise)
    assert (a.result(method='array') >= 0 and a.result(method='array') <= 0.1)


def test_Skew(benchmark, white_noise):
    a = FeatureSpace(featureList=['Skew'])
    a = benchmark(a.calculateFeature, white_noise)
    assert (a.result(method='array') >= -
            0.1 and a.result(method='array') <= 0.1)


@pytest.mark.skip('No assertions')
def test_SlottedA(benchmark, white_noise):
    a = FeatureSpace(featureList=['SlottedA'], SlottedA = [mjd, 1])
    a = benchmark(a.calculateFeature, white_noise[0])

def test_SmallKurtosis(benchmark, white_noise):
    a = FeatureSpace(featureList=['SmallKurtosis'])
    a = benchmark(a.calculateFeature, white_noise)
    assert (a.result(method='array') >= -
            0.2 and a.result(method='array') <= 0.2)


def test_Std(benchmark, white_noise):
    a = FeatureSpace(featureList=['Std'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >=
            0.9 and a.result(method='array') <= 1.1)


@pytest.mark.skip('Invalid assertions')
def test_Stetson(benchmark, white_noise):
    a = FeatureSpace(featureList=[
                     'SlottedA_length', 'StetsonK', 'StetsonK_AC', 'StetsonJ', 'StetsonL'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array')[
            1] >= 0.790 and a.result(method='array')[1] <= 0.85)
    assert (a.result(method='array')[
            2] >= 0.20 and a.result(method='array')[2] <= 0.45)
    assert (a.result(method='array')[3] >= -
            0.1 and a.result(method='array')[3] <= 0.1)
    assert (a.result(method='array')[4] >= -
            0.1 and a.result(method='array')[4] <= 0.1)


def test_Gskew(benchmark, white_noise):
    a = FeatureSpace(featureList=['Gskew'])
    a = benchmark(a.calculateFeature, white_noise)

    assert (a.result(method='array') >= -
            0.2 and a.result(method='array') <= 0.2)


def test_StructureFunction(benchmark, random_walk):
    a = FeatureSpace(featureList=['StructureFunction_index_21', 'StructureFunction_index_31',
                                  'StructureFunction_index_32'])
    a = benchmark(a.calculateFeature, random_walk)

    assert (a.result(method='array')[0] >= 1.520 and a.result(
        method='array')[0] <= 2.067)
    assert (a.result(method='array')[1] >= 1.821 and a.result(
        method='array')[1] <= 3.162)
    assert (a.result(method='array')[2] >= 1.243 and a.result(
        method='array')[2] <= 1.562)
