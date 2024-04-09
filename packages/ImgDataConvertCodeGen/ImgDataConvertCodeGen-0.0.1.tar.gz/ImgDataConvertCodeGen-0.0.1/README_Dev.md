# imgdataconvertcodegen Development
## Setup Dev Environment
**Clone the Repository**

```bash
git clone git@github.com:c3di/ImgDataConvertCodeGen.git
```

**Installing Dependencies**

Before installing dependencies, please ensure:
- For TensorFlow with CUDA support, verify system compatibility at [TensorFlow's installation guide](https://www.tensorflow.org/install/pip>).
- Use the correct path for `path/to/requirements.txt` in your project when executing the installation command.

With the Python virtual environment activated, install the required dependencies:
```bash
pip install -r path/to/requirements.txt
```

## Run Tests

Navigate to the root directory and run the tests in the tests folder using the following command:
```bash
pytest tests
```
or run the tests through test runner interface of IDE like PyCharm or Visual Studio Code.

## Build

The version number of this project is automatically determined based on the latest git tag through `setuptools_scm`.
To create a new version, create a new tag and push it to the repository:
```bash
git tag -a v0.1.0 -m "Version 0.1.0"
git push origin v0.1.0
```
Please change the version number accordingly.

To build the package, use the following command:
```bash
tox -e build
```

Also, you can remove old distribution files and temporary build artifacts (`./build` and `./dist`) using the following command:
```bash
tox -e clean
```

## Publish

To publish the package to a package index server, use the following command:
```bash
tox -e publish
```
By default, it uses `testpypi`. If you want to publish the package to be publicly accessible in PyPI, use the `-- --repository pypi` option.