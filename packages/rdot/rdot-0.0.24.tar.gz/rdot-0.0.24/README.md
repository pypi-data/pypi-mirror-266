# Rate Distortion Optimization Tools

[![test](https://github.com/nathimel/rdot/actions/workflows/test.yml/badge.svg)](https://github.com/nathimel/rdot/actions/workflows/test.yml)

## Introduction

RDOT (Rate Distortion Optimization Tools) is a software library that aims to provide efficient, unified tools for computing rate distortion functions.

For low cardinalities, the solutions to rate distortion (Shannon, 1959), information bottleneck (IB) (Tishby et al., 1999) and related objectives are feasible to solve with Blahut-Arimoto (BA) style algorithms. This library unifies several different variants on the rate distortion objective and provides solvers using BA and reverse deterministic annealing. Implementation is heavily inspired by, but slightly different or more general than, the libraries [embo](https://pypi.org/project/embo/) and [dit](https://dit.readthedocs.io/en/latest/). This library was created to overcome two shortcomings of these existing libraries:

- **embo** is a fast implementation of generalized IB, but has no support for getting solution encoders, or using deterministic annealing, which is useful for preserving some structure between nearby optima.

- **dit** is a more general library supporting discrete information theory, but is slow.
In contrast, **rdot** is a fast, general implementation of rate-distortion objectives that yields all relevant components of fixed-point solutions.

## Installing RDOT

First, set up a virtual environment (e.g. via [miniconda](https://docs.conda.io/en/latest/miniconda.html), `conda create -n rdot python=3`, and `conda activate rdot`).

### Method 1. Install via pypi

Install RDOT via pypi (We recommend doing this inside a virtual environment)

`pip install rdot`

### Method 2. Install locally

- Download or clone this repository and navigate to the root folder.

- Install RDOT (inside a virtual environment)

    `pip install -e .`

## Getting started

- Check out the [examples](src/examples), which contains a [notebook](src/examples/test_visualizations.ipynb) walking through rate distortion problems, and a comparison of IB solutions for **rdot** and **embo**.

- To see more real usage examples, visit the codebase for [compression theory for concept learning](https://github.com/nathimel/compression-theory-concept-learning), or for exploring IB-efficient vocabularies in the context of [signaling games](https://github.com/nathimel/ibsg).

## Modules

The main module is [rdot.ba](src/rdot/ba.py), which includes a unified hierarchy of optimizer classes for defining and solving rate distortion objectives.

There are several auxiliary modules, including:

- [rdot.distortions](src/rdot/distortions.py) for defining distortion functions,
- [rdot.information](src/rdot/information.py) helper functions for working with distributions and information-theoretic quantities,
- [rdot.probability](src/rdot/probability.py) helper functions for working with distributions,
- [rdot.postprocessing](src/rdot/postprocessing.py) helper functions for ensuring the quality of solutions computed via `rdot.ba`.

## Testing

Unit tests are written using pytest in the [test_rd.py](src/tests/test_rd.py) file and executed via running `pytest` from the root folder.

<details>

<summary>References:</summary>

> Shannon, C.E. (1959). Coding theorems for a discrete source with a fidelity criterion. Institute of Radio Engineers,
National Convention Record 4:142–163.

> Tishby, N., Pereira F.C., & Bialek, W. (1999). The information bottleneck method. *Proceedings of the 37th Annual Allerton Conference on Communication, Control and Computing*, eds Hajek B, Sreenivas RS (Univ of Illinois, Urbana, IL), pp 368– 377.

</details>
