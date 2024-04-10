from sys import argv, version_info
from os import mkdir, getcwd, chdir, listdir, remove
from os import path, system
from colorama import Fore, init
init()

from shutil import rmtree

from euph.plusdata import *


prive_text = '(euph)'

if version_info.major * 1000 + version_info.minor > 3008:
    verPython = f'{Fore.GREEN} Version is suitable!'
else:
    verPython = f'{Fore.YELLOW} Version is not suitable!'

HELP_TEXT = f'''
{Fore.MAGENTA}* Version:{Fore.GREEN} Euphoria 1.1.3
{Fore.MAGENTA}* Author:{Fore.GREEN} Markada (markada.py@gmail.com)
{Fore.MAGENTA}* Python:{verPython}
{Fore.MAGENTA}* Commands:
    {Fore.CYAN}py -m euph help {Fore.WHITE} — show this text
    {Fore.CYAN}py -m euph init <mod> {Fore.WHITE} — creates an empty Python project named "Project"
    {Fore.CYAN}py -m euph init <mod> <name> {Fore.WHITE} — creates an empty Python project with the name you specified in <name>
    {Fore.CYAN}py -m euph add <name> {Fore.WHITE} — creates a folder with the specified name and the files "__init__.py" and "__main__.py" in it
    {Fore.CYAN}py -m euph shell {Fore.WHITE} — launching the Euphoria shell
{Fore.MAGENTA}* Shell commands:
    {Fore.CYAN}#help{Fore.WHITE} — show this text
    {Fore.CYAN}#ls{Fore.WHITE} — shows a list of packages in the project
    {Fore.CYAN}#exit{Fore.WHITE} — comes out of the shell
    {Fore.CYAN}#q{Fore.WHITE} — comes out of the shell
    {Fore.CYAN}#add <mod> <name>{Fore.WHITE} — adds a module
    {Fore.CYAN}#del all{Fore.WHITE} — remove all packages
    {Fore.CYAN}#del all <mod>{Fore.WHITE} — 
    {Fore.CYAN}#del <name>{Fore.WHITE} — 
{Fore.MAGENTA}* Explanation of details:{Fore.LIGHTGREEN_EX}
    * <mod> - in <mod> there can be: `i` - imported package, `m` - launched module{Fore.RESET}
'''


def check_naming_error(name):
    if len(name) >= 255:
        print(Fore.RED + 'The length of the project name is more than 255!')
        exit(1)

    if [i for i in name if i in '+=[]:*?;«,./\<>| ']:
        print(Fore.RED + 'The project name contains prohibited characters! (+=[]:*?;«,./\<>| )')
        exit(1)

    if path.exists(path.join('src', name)):
        print(Fore.RED + 'The directory already contains a folder or file with the same name!')
        exit(1)


def init_project(name, mod):
    check_naming_error(name)

    pathToProject = path.join(getcwd(), name)
    pathToPackage = path.join(getcwd(), name, 'src', name)

    mkdir(pathToProject)
    mkdir( path.join(getcwd(), name, 'src') )
    mkdir(pathToPackage)

    # Create LICENSE
    with open(path.join(pathToProject, 'LICENSE'), 'w', encoding='utf-8') as file:
        file.write(MIT)

    # Create README
    with open(path.join(pathToProject, 'README.md'), 'w', encoding='utf-8') as file:
        file.write(f'# {name}\n')

    # Create CHANGELOG
    with open(path.join(pathToProject, 'CHANGELOG'), 'w', encoding='utf-8') as file:
        file.write('')

    # Create .pypirc
    with open(path.join(pathToProject, '.pypirc'), 'w', encoding='utf-8') as file:
        file.write(PYPIRC)

    # Create pyproject.toml
    with open(path.join(pathToProject, 'pyproject.toml'), 'w', encoding='utf-8') as file:
        file.write(PYPROJECT_TEXT)

    if mod == 'm':
        with open(path.join(pathToPackage, '__main__.py'), 'w', encoding='utf-8') as file:
            file.write(MAIN__TEXT)

    elif mod == 'i':
        with open(path.join(pathToPackage, '__init__.py'), 'w', encoding='utf-8') as file:
            file.write('')

    else:
        print(Fore.RED + f'No mod "{mod}"! But there is "i" and "m"')
    
    return 1


def shell_parser(args: str) -> bool:
    match args.split():
        case ['#exit'] | ['#q']:
            exit(0)

        case ['#del', 'all']:
            req = input(f'{Fore.GREEN + prive_text + Fore.RESET} Delete everything? (y) (Y/n) ')
            
            if req in 'Nn' and req != '':
                return 1
            
            chdir('src')

            for pdir in listdir():
                ex_init = path.exists(path.join(getcwd(), pdir, '__init__.py'))
                ex_main = path.exists(path.join(getcwd(), pdir, '__main__.py'))

                if ex_init or ex_main:
                    rmtree(pdir)
                    print(f'    { Fore.RED + "DELETED " + Fore.BLUE + pdir + Fore.RESET} ')

            chdir('..')

        case ['#del', 'all', mod]:
            req = input(f'{Fore.GREEN + prive_text + Fore.RESET} Remove all packages? (y) (Y/n) ')
            
            if req in 'Nn' and req != '':
                return 1
            
            chdir('src')

            for pdir in listdir():
                ex_init = path.exists(path.join(getcwd(), pdir, '__init__.py'))
                ex_main = path.exists(path.join(getcwd(), pdir, '__main__.py'))

                if (mod == 'i') and ex_init:
                    rmtree(pdir)
                    print(f'    { Fore.RED + "DELETED " + Fore.BLUE + pdir + Fore.RESET} ')
                
                if (mod == 'm') and ex_main:
                    rmtree(pdir)
                    print(f'    { Fore.RED + "DELETED " + Fore.BLUE + pdir + Fore.RESET} ')

            chdir('..')

        case ['#del', name]:
            req = input(f'Remove package "{name}"? (y) (Y/n) ')
            
            if req in 'Nn' and req != '':
                return 1
            
            chdir('src')

            if not path.exists(name):
                chdir('..')
                return 1

            ex_init = path.exists(path.join(getcwd(), name, '__init__.py'))
            ex_main = path.exists(path.join(getcwd(), name, '__main__.py'))

            if ex_main:
                rmtree(name)
                print(f'    { Fore.RED + "DELETED " + Fore.BLUE + name + Fore.RESET} ')

            elif ex_init:
                rmtree(name)
                print(f'    { Fore.RED + "DELETED " + Fore.BLUE + name + Fore.RESET} ')

            chdir('..')

        case ['#ls']:
            packs = []

            chdir('src')

            print(f'{Fore.BLUE}src/{Fore.RESET}')

            for pdir in listdir():
                chdir(pdir)
                
                ex_init = path.exists(path.join('__init__.py'))
                ex_main = path.exists(path.join('__main__.py'))

                if ex_init and ex_main:
                    print(f'    { Fore.LIGHTGREEN_EX + "BOTH " + Fore.BLUE + pdir + Fore.RESET} ')
                elif ex_init:
                    print(f'    { Fore.LIGHTCYAN_EX + "INIT " + Fore.BLUE + pdir + Fore.RESET} ')
                elif ex_main:
                    print(f'    { Fore.LIGHTMAGENTA_EX + "MAIN " + Fore.BLUE + pdir + Fore.RESET} ')
                
                chdir('..')
            
            chdir('..')

        case ['#add', mod, name]:
            if not path.exists('pyproject.toml'):
                print(Fore.RED + 'The current directory is not a Python project!')
                exit(1)

            check_naming_error(name)
            pathToPack = path.join(getcwd(), 'src', name)

            if not path.exists('src'):
                print(Fore.RED + 'There is no "src" folder in the project folder!')
                exit(1)

            if mod == 'm':
                mkdir(pathToPack)
                with open(path.join(pathToPack, '__main__.py'), 'w', encoding='utf-8') as file:
                    file.write(MAIN__TEXT)
                
            elif mod == 'i':
                mkdir(pathToPack)
                with open(path.join(pathToPack, '__init__.py'), 'w', encoding='utf-8') as file:
                    file.write('')
                
            else:
                print(Fore.RED + f'No mod "{mod}"! But there is "i" and "m"')

        case ['#help']:
            print(HELP_TEXT)
            
        case _:
            return 0
    
    return 1


def main():
    match argv[1:]:
        case ['init', mod, name]:
            if mod in ('i', 'm'):
                init_project(name, mod)
                print(Fore.GREEN + f'The project "{name}" has been successfully created!')

        case ['init', mod]:
            if mod in ('i', 'm'):
                init_project("Project", mod)
                print(Fore.GREEN + f'The project "Project" has been successfully created!')

        case ['shell']:
            while 1:
                if not path.exists('pyproject.toml'):
                    print(Fore.RED + 'This directory is not a Python project!')
                    exit(1)

                prive = f'{Fore.GREEN + prive_text + Fore.RESET} '
                cmd = input(prive)

                req = shell_parser(cmd)

                if req == 0:
                    system(cmd)
        
        case ['help']:
            print(HELP_TEXT)

        case _:
            print(Fore.RED + 'No command 🤔')


if __name__ == '__main__':
    # chdir('myPack')
    main()
