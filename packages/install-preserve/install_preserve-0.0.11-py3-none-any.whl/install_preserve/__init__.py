"""
Lets init some stuff!
"""
import re
import importlib.util


def preserve(requirements: list[str], criteria: list[str], verbose: bool = False) -> list:
    """
    Preserve packages listed in the criteria argument if they are already installed.
    """
    package_names = list()
    for requirement in requirements:
        package_names.append(re.sub(r'[^a-zA-Z0-9]+$', '', requirement.split('=')[0]))
    for item in criteria:
        alias = name = item
        if ':' in item:
            name, alias = item.split(':')
        if importlib.util.find_spec(alias) is not None:
            if verbose:
                print(f'excluding package {name} as it is already installed')
            index = package_names.index(name)
            package_names.pop(index)
            requirements.pop(index)
    return requirements


def test():
    """
    Simple test of the above logic.
    """
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
        'opencv-python>=3.4.2.17',
        'pytorch>=2.0.0'
    ]

    excludes = [
        'tqdm',
        'opencv-python:cv2',
        'pytorch:torch'
    ]
    requirements = preserve(requirements, excludes, verbose=True)
    for requirement in requirements:
        print(requirement)
