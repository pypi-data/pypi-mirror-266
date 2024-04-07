#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <limits>
#include <numbers>
#include <vector>
#include <omp.h>

namespace py = pybind11;

double fast_CAR(py::array_t<double> parameters, py::array_t<double> t, py::array_t<double> x, py::array_t<double> errors) {
    double *parameters_ptr = (double *)parameters.request().ptr;
    double sigma = parameters_ptr[0];
    double tau = parameters_ptr[1];

    py::buffer_info t_buf = t.request();
    py::buffer_info x_buf = x.request();
    py::buffer_info e_buf = errors.request();

    double *t_ptr = (double *) t_buf.ptr;
    double *x_ptr = (double *) x_buf.ptr;
    double *e_ptr = (double *) e_buf.ptr;

    int N = t_buf.shape[0];
    double x_mean = 0;

    #pragma omp parallel for reduction(+:x_mean)
    for (int i = 0; i < N; ++i) {
        x_mean += x_ptr[i];
    }

    x_mean /= N;
    double b = x_mean / tau;
    const double epsilon = 1e-300;
    
    double omega, omega_prev, omega_zero, a, x_hat, x_hat_prev, x_star, loglik;
    x_hat_prev = 0;
    omega_prev = tau * sigma * sigma / 2;
    omega_zero = omega_prev;
    loglik = 0;
    for (int i = 1; i < N; ++i) {
        a = std::exp(-(t_ptr[i] - t_ptr[i-1]) / tau);
        x_star = x_ptr[i - 1] - b * tau;
        x_hat = a * x_hat_prev + a * omega_prev * (x_star + x_hat_prev) / (omega_prev + std::pow(e_ptr[i-1], 2));
        omega = omega_zero * (1 - a * a) + a * a * omega_prev * (1 - omega_prev / (omega_prev + std::pow(e_ptr[i-1], 2)));
        
        x_star = x_ptr[i] - b * tau;
        loglik += -0.5 * std::pow(x_hat - x_star, 2) / (omega + std::pow(e_ptr[i], 2)) - std::log(std::sqrt(2 * std::numbers::pi * (omega + std::pow(e_ptr[i], 2))));

        if (std::isinf(loglik) && loglik < 0) {
            return std::numeric_limits<double>::quiet_NaN();
        }
    }
    
    return -loglik;
}

PYBIND11_MODULE(fast_CAR, m) {
    m.def("fast_CAR", &fast_CAR, "Fast computation of CAR likelihood");
}
