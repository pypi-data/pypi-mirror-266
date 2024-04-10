# Euphoria 1.1.3
* Euphoria is a small CLI library for quick initialization and support of projects in Python project format
* Euphoria shell - a small, additional utility for more detailed editing of projects


## Euphoria Commands
* Creating a project without specifying the project name: `py -m euph init <mod>`
* Create a project by specifying the project name: `py -m euph init <mod> <name>`, where `<name>` is the folder/file name and `<mod>` is to create a package (insert `i`) or Python module (`m`, can be launched with `python -m`)
* Help: `py -m euph help`
* Launch Euphoria shell: `py -m euph shell`

After executing the `init` command, a folder with the following structure appears in the current directory:
```
/<project>
    /src
        /<project>
            /__init__.py or __main__.py
        /.pypirc
        /CHANGELOG
        /LICENSE
        /pyproject.toml
        /README.md
```


## Euphoria shell
* To exit the shell: `#q` or `#exit`
* Shows Euphoria help: `#help`
* Displays a list of created modules to the console: `#ls`
* Adding a package to a directory: `#add <mod> <name>`
* Delete module: `#del <name>`
* Delete all modules: `#del all`
* Delete all modules of a specific type: `#del all <mod>`
