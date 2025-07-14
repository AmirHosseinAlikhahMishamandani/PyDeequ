# PyDeequPlus

[![PyPI version](https://img.shields.io/pypi/v/pydeequplus)](https://pypi.org/project/pydeequplus/) [![License](https://img.shields.io/badge/License-Apache_2.0%20OR%20MIT-blue.svg)](#license)

A **100% Python** implementation of [Amazon Deequ](https://github.com/awslabs/deequ) for data validation, built on **pandas**.

## 🚀 Features

- **Constraint checks**: Uniqueness, completeness, min/max, pattern matching, etc.  
- **Profiles & suggestions**: Automatic constraint recommendation based on data profiling.  
- **Row-level schema enforcement**: Define and validate per-row column constraints.  
- **Pandas-native**: No JVM or Spark dependency—pure Python.  

## 🔧 Installation

```bash
# From PyPI
pip install pydeequplus

# From source
git clone https://github.com/yourorg/pydeequplus.git
cd pydeequplus
pip install .
````

## 📖 Quick Start

```python
import pandas as pd
from pydeequplus import (
    RowLevelSchema, 
    RowLevelSchemaValidator
)

# Sample data
df = pd.DataFrame({
    "id": ["1", "2", None, "4"],
    "age": ["10", "twenty", "30", "40"]
})

# Define schema
schema = (RowLevelSchema()
    .with_string_column("id", is_nullable=False)
    .with_int_column("age", min_value=0, max_value=120)
)

# Validate
result = RowLevelSchemaValidator.validate(df, schema)

print("Valid rows:")
print(result.valid_rows)
print(f"Number of invalid rows: {result.num_invalid_rows}")
```

## 📂 Project Structure

```
pydeequplus/
├── src/
│   └── pydeequplus/
│       ├── ...
│       ├── ...
│       └── ...
├── tests/
│   └── ...
├── LICENSE
├── README.md
└── setup.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/foo`)
3. Commit your changes (`git commit -am 'Add foo feature'`)
4. Push to the branch (`git push origin feature/foo`)
5. Open a Pull Request

Please follow our code style (PEP8) and write tests for new features.

## 🛡️ License

This project is **dual-licensed** under:

* **Apache License 2.0** for code derived from [Amazon Deequ](https://github.com/awslabs/deequ)
* **MIT License** for all original code written by **Neuroligence**

See [LICENSE](./LICENSE) for full terms.

---

*Originally inspired by Amazon Deequ — thank you to the AWS open-source team!*

```
::contentReference[oaicite:0]{index=0}
```
