# Install-Preserve

Install-Preserve is a Python library that helps detect already installed packages and removes them from the `install_requires` list within the `setup.py` file. This prevents accidentally overwriting hand-compiled libraries such as OpenCV, PyTorch, or TensorFlow.

## Usage

```python
from setuptools import setup

try:
    from install_preserve import preserve
except ImportError:
    import pip
    pip.main(['install', 'install-preserve'])
    from install_preserve import preserve
    

requirements = [
    'pyyaml',
    'tqdm',
    'numpy',
    'easydict==1.9.0',
    'scikit-image==0.17.2',
    'scikit-learn==0.24.2',
    'joblib',
    'matplotlib',
    'pandas',
    'albumentations==0.5.2',
    'hydra-core==1.1.0',
    'tabulate',
    'webdataset',
    'packaging',
    'wldhx.yadisk-direct',
    'opencv-python',
    'torch==2.0.0'
]

excludes = [
    'tqdm',
    'opencv-python:cv2',  # Note the colon delimited statement to illustrate <package-name>:<import alias>
    'torch'
]
requirements = preserve(requirements, excludes, verbose=True)

setup(
    name='your_package',
    version='1.0',
    install_requires=requirements,
    # Other setup options...
)
```

### Example Output

```
excluding package tqdm as it is already installed
excluding package opencv-python as it is already installed
excluding package pytorch as it is already installed
```

## Installation

To install, you can use pip:

```bash
pip install install-preserve
```

## License

This library is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues on the [GitHub repository](https://github.com/manbehindthemadness/install-preserve).