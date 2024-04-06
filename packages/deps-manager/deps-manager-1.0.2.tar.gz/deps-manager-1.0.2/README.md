
# deps\_manager

This package runs as CLI for dependency management across Python and C++ projects, abstracting language-specific package manager calls.
Simplified dependency management tasks by enabling dependency operations like installation, uninstallation, listing, updating, and locking.


* [deps\_manager](#deps\_manager)
* [Description](#package-description)
* [PyPI Package Link](#pypi-package-link)
* [Usage](#usage)
* [Installation](#installation)
* [History](#history)
* [Credits](#credits)
* [Licence](#licence)
* [Todo and Possible Future Improvements](#todopossible-future-improvements)
* [FAQ](#faq)

## Package Description
* [deps\_manager](#deps\_manager)

This package runs as CLI for dependency management across Python and C++ projects, abstracting language-specific package manager calls.
Simplified dependency management tasks by enabling dependency operations like installation, uninstallation, listing, updating, and locking.

## PyPI Package Link
https://pypi.org/project/deps-manager/

### Usage
* [deps\_manager](#deps\_manager)

#### From the Command Line

command to get package usage help: ```$ deps_manager --help```

command to install packages: ```$ deps-manager install -l python -r /path/to/requirements.txt --venv_path /path/to/virtual/environment```

Alternatively, users can also provide input for options in interactive prompt without the need for additional command-line arguments. 
For example,
```
$ python main.py install
Enter the path to the virtual environment: /path/to/virtual/environment
Enter the requirements.txt file name: /path/to/requirements.txt
Enter the language (python/cpp): python
```

### Installation
* [deps\_manager](#deps\_manager)

Install the package with:
```pip3 install deps_manager```

To install from source and develop:
```
$ git clone git@gitlab.com:harshadatupe8/dependency_manager_cli.git
$ cd dependency_manager_cli
$ python3 setup.py sdist bdist_wheel
$ python3 setup.py develop
```

## History
* [deps\_manager](#deps\_manager)

## Credits
* [deps\_manager](#deps\_manager)

## License
* [deps\_manager](#deps\_manager)

MIT License

## TODO/Possible Future Improvements
* [deps\_manager](#deps\_manager)
    * Check for dependency security vulnerability.
    * Add integration with a GUI.
    * Solve dependency conflicts.

## FAQ
* [deps\_manager](#deps\_manager)
