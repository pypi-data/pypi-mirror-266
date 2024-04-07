cmake_minimum_required(VERSION 3.5...3.27)
project(fast_CAR LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON) 

find_package(pybind11 REQUIRED)
pybind11_add_module(fast_CAR FFATS/pybind11_CAR/fast_CAR.cpp)

find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    target_link_libraries(fast_CAR PUBLIC OpenMP::OpenMP_CXX)
endif()
