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
- Python >=3.6, no external packages

## Usage

### ...py CLI Usage

```
usage: . . .
```

### ...py Example

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