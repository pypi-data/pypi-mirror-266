 &mu;hw

&mu;hw, MicroHardware, is a lightweight asynchronous
command parsing and serving framework.

## Install

### PyPI

Installing the latest release from [PyPI](https://pypi.org).

```console
pip install -U uhw
```

### Repository

When using [git](https://git-scm.com), clone the repository and 
change your present working directory.

```console
git clone http://github.com/mcpcpc/uhw
cd uhw/
```

Create and activate a virtual environment.

```console
python3 -m venv venv
source venv/bin/activate
```

Install &mu;hw to the virtual environment.

```console
pip install -e .
```

## Usage

See the `examples/` for more complete solutions.

### Quickstart

The following is a basic example of how to spin up a new server instance.

```python 
from uhw import UHW

app = UHW(__name__)

if __name__ == "__main__":
    app.run("127.0.0.1", 5000)
```

### Callbacks

Custom user functions are implemented using the built-in
callback handlers. 

```python
@app.push("FOO")
def set_foo(value: str | None = None) -> None:
    pass  # your callback implementation here

@app.pull("FOO")
def get_foo(value: str | None = None) -> str:
    return "BAR\n"
```

### Debugging

We can use the same example as above and configure logging with the built-in `logging` library.

```python
from logging import basicConfig

from uhw import UHW

basicConfig(level="DEBUG")
app = UHW(__name__)

if __name__ == "__main__":
    app.run("127.0.0.1", 5000)

```

## Todo

* Verify MicroPython compatibility.
* Auto-reload flag for development at runtime.
* Full IEC/IEEE 60488-1-2004 compliance.
