
# pycredits 

[![codecov](https://codecov.io/gh/DSCI-310-2024/pycredits/graph/badge.svg?token=L68Uui9hpr)](https://codecov.io/gh/DSCI-310-2024/pycredits)


pycredits is DSCI310 Group 12's package for conducting data analyses related to credit risk. This package offers functions designed to facilitate common tasks in credit risk analysis, including data preprocessing, exploratory data analysis, data cleaning, and hyper-parameter tuning. Building off of packages [matplotplib](https://github.com/matplotlib/matplotlib) and [scikit-learn](https://github.com/scikit-learn/scikit-learn), pycredits streamlines the use of scikit-learn's functions as well as simplifys the creation of specific matplotlib plots relevant to credit analysis.

## Installation

```bash
$ pip install pycredits
```

## Usage

`pycredits` provides several useful functions for data preprocessing and analysis in understanding credit risk, such as, preprocess data, create histograms, transform labels, and create parameter grids for grid search.

```python
from pycredits import preprocess_data, column_histogram, map_labels_to_binary, param_grid_for_grid_search
import matplotlib.pyplot as plt

# Preprocess data
X_transformed, y, preprocessor = preprocess_data(df, numeric_features, categorical_features)

# Create histogram for a column
column_plot = column_histogram(fig_width, fig_height, data_frame, column_name)
plt.show()

# Transform label values
y_transformed = map_labels_to_binary(y)

# Create parameter grid for grid search
param_grid = param_grid_for_grid_search(n_estimators_range, max_depth_range)
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`pycredits` was created by Jade Bouchard, Shahrukh Islam Prithibi, Sophie Yang, and Yovindu Don. It is licensed under the terms of the MIT license.

## Credits

`pycredits` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
