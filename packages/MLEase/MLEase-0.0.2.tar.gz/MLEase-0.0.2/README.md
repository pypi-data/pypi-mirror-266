# Machine Learning Ease

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MachLearnEase is a Python package that simplifies machine learning tasks by providing easy-to-use tools and utilities.

## Installation

You can install MLEase using pip:

```bash
pip install MLEase
```

## Usage

MLEase provides a variety of tools to streamline your machine learning workflow. Here's an example of how to use the `MissingValueImputer` and `OutlierRemoverScaler` classes:

```python
from mlease import MissingValueImputer, OutlierRemoverScaler
import pandas as pd

# Example usage of MissingValueImputer
imputer = MissingValueImputer(strategy='mean')
data = {'A': [1, 2, None, 4], 'B': [5, None, 7, 8]}
df = pd.DataFrame(data)
imputed_df = imputer.fit_transform(df)

# Example usage of OutlierRemoverScaler
scaler = OutlierRemoverScaler()
transformed_data = scaler.fit_transform(data)

#Example of Bucketizer
bucketizer = Bucketizer(num_classes=3, use_qcut=True, automatic_num_classes=True)
transformed_data = bucketizer.fit_transform(data)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
