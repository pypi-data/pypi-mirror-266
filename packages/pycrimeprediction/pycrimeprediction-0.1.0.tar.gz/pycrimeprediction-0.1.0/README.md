# pycrimeprediction

```pycrimeprediction``` is DSCI 301 Group 10's Python package for loading, analyzing, and saving data related to crime rates

group 10 description

## Installation

```bash
$ pip install pycrimeprediction
```

## Usage

`pycrimeprediction` can be used to analyze data related to crime rates.

Below is a usage example of two of our functions:

```python
from pycrimeprediction.read_save_data import read_save_data
from pycrimeprediction.add_if_crime import add_if_crime_feature

input_path = "url-for-data.csv"
output_path = "saved-data-to-file.csv"

#Read data and split into examples and labels
df = read_save_data(input_path, output_path)
X = df.iloc[:, 0:-1]
y = df.iloc[:, -1]

#Print Cross-validation results for the Logistic Regression classifier
print(perform_analysis(X,y))
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`pycrimeprediction` was created by Cassandra Zhang, Pragya Singhal, James He, and Ethan Kenny. It is licensed under the terms of the MIT license.

## Credits

`pycrimeprediction` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
