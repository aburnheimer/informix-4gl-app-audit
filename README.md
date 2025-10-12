# informix-4gl-app-audit
Derive statistics about Informix-4GL applications installed under a parent
directory (i.e. module)

## Description
Utilities to derive statistics about the source code files for Informix 4GL
applications under a parent directory - typically a *.4gm* module.

## Installation

Clone the repo:

```bash
git clone https://github.com/aburnheimer/informix-4gl-app-audit
```

...and if desired, create a virtual environment to be isolated from the
installation of Python provided by the operating system:
```bash
cd informix-4gl-app-audit
virtualenv ./
# ... or ...
virtualenv -p /usr/local/bin/python3.6 ./
```

Create a test source code module to run the audit on:

```bash
make testmod
# ... and make cleantestmod, as desired ...
```

### Requirements:
```bash
pip install -r requirements.txt
```

## Usage

Audit a 4GL Module by providing the path to it:

```bash
make audittest.pq
```

Examine the results using any of the included Jupyter notebook files,
e.g. [newness_compares.ipynb](newness_compares.ipynb)


### app-audit.py CLI Usage

```
usage: app-audit.py [-h] [-o OUT] [-v] [roots ...]

Create a DataFrame of filesystem stats for one or more module directories.

positional arguments:
  roots          module directories to scan (default: audittest.4gm)

options:
  -h, --help     show this help message and exit
  -o, --out OUT  optional output filename; use .parquet or .pq to write Parquet (falls back to CSV on error)
  -v, --verbose  enable verbose logging
```

### app-audit.py Example
```bash
pythonn ./app-audit.py -o audittest.pq audittest.4gm
```

## Contributing
Contributions are welcome. Please open issues and pull requests including:
- Respect to code style / linting
- Testing for new features
- Instructions to exercise the issue or feature with examples

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for more details.

## Contact
* Email:
  * aburnheimer@gmail.com
* Github:
  * https://github.com/aburnheimer/