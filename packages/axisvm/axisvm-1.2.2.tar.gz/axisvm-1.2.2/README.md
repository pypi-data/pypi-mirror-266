# **PyAxisVM** - The official python package for **AxisVM**

![alt text](https://github.com/AxisVM/DynamoToAxisVM/blob/master/Documentation/images/AxisVM%20logo.bmp)

<table>
    <tr>
        <td>Latest Release</td>
        <td>
            <a href="https://pypi.org/project/axisvm/"/>
            <img src="https://badge.fury.io/py/axisvm.svg"/>
        </td>
    </tr>
    <tr>
        <td>License</td>
        <td>
            <a href="https://opensource.org/licenses/MIT"/>
            <img src="https://img.shields.io/badge/License-MIT-yellow.svg"/>
        </td>
    </tr>
</table>

## Overview

The **PyAxisVM** project offers a high-level interface to **AxisVM**, making its operations available directly from Python. It builds on top of Microsoft's COM technology and supports all the features of the original **AxisVM** COM type library, making you able to
  
* build, manipulate and analyse **AxisVM** models

* find better solutions with iterative methods

* combine the power of **AxisVM** with third-party Python libraries

* build extension modules

On top of that, **PyAxisVM** enhances the type library with Python's slicing mechanism, context management and more, that enables writing clean, concise, and readable code.

## Installation

This is optional, but we suggest you to create a dedicated virtual enviroment at all times to avoid conflicts with your other projects. Create a folder, open a command shell in that folder and use the following command

```console
>>> python -m venv venv_name
```

Once the enviroment is created, activate it via typing

```console
>>> .\venv_name\Scripts\activate
```

The **AxisVM** python package can be installed (either in a virtual enviroment or globally) from PyPI using `pip` on Python >= 3.7 <= 3.10:

```console
>>> pip install axisvm
```

or chechkout with the following command over HTTPS via <https://github.com/AxisVM/pyaxisvm.git> or by using the GitHub CLI

```console
gh repo clone AxisVM/pyaxisvm
```

and install from source by typing

```console
>>> pip install .
```

If you want to run the tests, you can install the package along with the necessary optional dependencies like this

```console
>>> pip install ".[test]"
```

### Development mode

If you are a developer and want to install the library in development mode, the suggested way is by using this command:

```console
>>> pip install "-e .[test, dev]"
```

If you plan to touch the docs, you can install the requirements for that as well:

```console
>>> pip install "-e .[test, dev, docs]"
```

## **Documentation and Issues**

The ***AxisVM API Reference Guide*** is available in pdf format,  you can download it [***here***](https://axisvm.eu/axisvm-downloads/#application).

The documentation of this library is available [***here***](https://axisvm.github.io/pyaxisvm-docs/).

Please feel free to post issues and other questions at **PyAxisVM** Issues. This is the best place to post questions and code related to issues with this project. If you are not familiar with GitHub, you can also reach out to us through the usual channels, but if you are, GitHub is preferred.

## Dependencies

You will need a local licenced copy of **AxisVM** version >= 13r2. To get a copy of **AxisVM**, please visit our [***homepage***](https://axisvm.eu/).

## License

**PyAxisVM** is licensed under the [MIT license](https://opensource.org/license/mit/).

This module, **PyAxisVM** makes no commercial claim over AxisVM whatsoever. This tool extends the functionality of **AxisVM** by adding a Python interface to the **AxisVM** COM service without changing the core behavior or license of the original software. The use of **PyAxisVM** requires a legally licensed local copy of **AxisVM**.
