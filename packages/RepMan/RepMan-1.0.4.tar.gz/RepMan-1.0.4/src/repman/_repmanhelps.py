#
# RepMan Helper file.
#

from termcolor import colored

class helptext:
    def __init__(self, version:str):
        self.version = version
    
    # function to show credits
    def credits(self):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored('credits\n', 'red'))
        print('  |  Author: Soumyo Deep Gupta (@d33pster)  |')
        print('  |  Email: deep.main.ac@gmail.com          |')
        print('  |  copyright @d33pster                    |')
        print('\nEND')
        exit(0)
    
    # function to display version and exit
    def version_s(self):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print('         version', colored(f'v{self.version}', 'red'))
        print('         author:', colored('d33pster', 'light_blue'))
        print('         GitHub:', colored('https://github.com/d33pster', 'light_blue'))
        exit(0)
    
    # function to print general help
    def base(self):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help\n')
        print('  |  -h or --help          : show this help text and exit.')
        print('  |  -v or --version       : show version and exit.')
        print('  |  -i or --init          : initialize settings, configurations and exit.')
        print('  |  -a or --add           : add a git repository under RepMan\'s care.')
        print('  |  -o or --open          : open a project/repository.')
        print('  |  -l or --list          : list all the projects under RepMan\'s care. and exit.')
        print('  |  -lp or --list-w-path  : list all the projects under RepMan\'s care with their paths and exit.')
        print('  |  -ae or --add-existing : Add an already cloned repository under RepMan\'s care.')
        print('  |  -al or --add-local    : Add a local git repository under RepMan\'s care.')
        print('  |  -u or --update        : update a repository.',colored('[requires internet]', 'red'))
        print('  |  -sr or --set-remote   : set remote for a project.\n')
        print(colored('NOTE', 'blue'), ': For further help, run', colored('\'repman <argument> -h\'', 'red'), 'or', colored('\'repman <argument> --help\'.', 'red'))
        print('\nEND')
        exit(0)
    
     # function to print specialized help on '-v' or '--version'
    def version_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This Argument shows the version information  |')
        print('  | of RepMan.                                   |')
        print('\nEND')
        exit(0)
    
    # function to print specialized help on '-i' or '--init'
    def init_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is used to initialize RepMan.  |')
        print('  |                                              |')
        print('  | It will automatically detect and try to Ini- |')
        print('  | tialize RepMan and all its Configurations.   |')
        print('  |                                              |')
        print('  | This Argument may ask input from the user a- |')
        print('  | bout few Configurations.                     |')
        print('  |                                              |')
        print('  |', colored('Format', 'red')+': \'repman -i\' or \'repman --init\'       |')
        print('  |                                              |')
        print('  | Note: you can also specify the init path af- |')
        print('  | ter the -i or --init arg.                    |')
        print('  |                                              |')
        print('\nEND')
        exit(0)
    
    # function to print specialized help on '-a' or '--add'
    def add_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is used to add git repositori- |')
        print('  | es under RepMan\'s care. This basically means |')
        print('  | RepMan will manage that repository for you.  |')
        print('  |                                              |')
        print('  |', colored('Format', 'red')+': \'repman -a <link>\'                   |')
        print('  |                 or                           |')
        print('  |          \'repman -a <username>/<repo>\'       |')
        print('  |                                              |')
        print('\nEND')
        exit(0)
    
    # function to print specialized help on '-o' or '--open'
    def open_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is used to open projects and   |')
        print('  | work on them as you please.                  |')
        print('  |                                              |')
        print('  | RepMan will automatically add .gitignore fi- |')
        print('  | le if it is not present in the opened proje- |')
        print('  | ct.                                          |')
        print('  |                                              |')
        print('  | Since this is a python project itself, RepMan|')
        print('  | will add the necessary files in the .gitign- |')
        print('  | ore file. such as \'dist\' if the destination  |')
        print('  | is found to be a python project.             |')
        print('  |                                              |')
        print('  |',colored('Format', 'red')+': \'repman -o <project-name>\'           |')
        print('  |                                              |')
        print('\nEND')
        exit(0)
    
    # function to print specialized help on '-l' or '--list'
    def list_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is used to list all the proje- |')
        print('  | cts under RepMan\'s care.                     |')
        print('  |                                              |')
        print('  |', colored('Format', 'red')+': \'repman -l\' or \'repman --list\'       |')
        print('  |                                              |')
        print('\nEND')
        exit(0)
    
    # function to print specialized help on '-lp' or '--list-w-path'
    def listwpath_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is used to list all the proje- |')
        print('  | cts  and their paths under RepMan\'s care.    |')
        print('  |                                              |')
        print('  |', colored(' Format', 'red')+': \'repman -lp\'                        |')
        print('  |                                              |')
        print('\nEND')
        exit(0)
    
    # function to print specialized help on '-ae' or '--add-existing'
    def addexisting_h(self ,arg: str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is used to add pre-cloned dir- |')
        print('  | ectory under RepMan\'s care.                  |')
        print('  |                                              |')
        print('  |', colored('Format', 'red')+': \'repman -ae <path>\'                  |')
        print('  |                                              |')
        print('\nEND')
        exit(0)
    
    # function to print specialized help on '-al' or '--add-local'
    def addlocal_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is for adding local git repos- |')
        print('  | itory under RepMan\'s care.                   |')
        print('  |                                              |')
        print('  | You might be prompted to set the default     |')
        print('  | branch and remote repository link(if not yet |')
        print('  | created, then create one.)                   |')
        print('  |                                              |')
        print('  |', colored('Format', 'red')+': \'repman -al <path>\'                  |')
        print('  |                                              |')
        print('\nEND')
        exit(0)
    
        # function to print specialized help on '-u' or '--update'
    def update_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is used to update a project    |')
        print('  | with github remote repository.               |')
        print('  |                                              |')
        print('  | Each file\'s commit msg will be asked.        |')
        print('  |                                              |')
        print('  |', colored('Format', 'red')+': \'repman -u <project-name>\'           |')
        print('  |                                              |')
        print(colored('\nNote', 'red'), ': Requires Internet Connectivity.')
        print('\nEND')
        exit(0)
    
    def setremote_h(self, arg:str):
        print(colored('RepMan', 'blue'), ': Repository Manager (alias: Project Manager)')
        print(colored(f'v{self.version}\n', 'red'))
        print('help', colored('EXTENDED', 'blue'), f': help for \'{arg}\'\n')
        print('  | This argument is used to set the remote or-  |')
        print('  | igin of a project. If remote is already set, |')
        print('  | It will be overwritten.                      |')
        print('  |                                              |')
        print('  |', colored('Format', 'red')+': \'repman -sr <project> <remote>\'      |')
        print('  |                                              |')
        print('  | <remote> can be either in the form of a link |')
        print('  | or <username>/<repo>                         |')
        print('  |                                              |')
        print('\nEND')
        exit(0)