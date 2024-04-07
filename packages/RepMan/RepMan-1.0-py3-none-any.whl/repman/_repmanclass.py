#
# RepMan Class File
#

from termcolor import colored
from os import getcwd as pwd, popen as getoutputof, system as run, chdir, listdir, environ, makedirs
from os.path import expanduser, join, basename, exists as there, dirname, abspath
from pathlib import Path
from tkinter import filedialog
from re import search, match
import pandas as pd
from tabulate import tabulate
from shutil import copytree
import subprocess
import platform

####################### CLASS REPMAN ############################

class repman:
    def __init__(self, projectpath:str = None):
        # version
        self.version = ''
        # fetch project path if defined.
        if projectpath==None:
            self.path = ''
        else:
            self.path = projectpath
        # working path -> where it is called.
        self.workingpath = pwd()
        # get current os
        self.operatingsystem = platform.system()
        # projectlist
        self.projects: list[dict] = []
    
    ################### SET PATH FROM OUTSIDE ###############################
    def setvariables(self):
        try:
            self.path = environ['REPMAN_PROJECT_PATH']
        except KeyError:
            raise RuntimeError('bad call of setvariables function before running init.')
        # dot folder
        self.dotfolder = join(self.path, '.repman')
        if not there(self.dotfolder):
            makedirs(self.dotfolder)
        # -> get project list.
        try: 
            with open(join(self.dotfolder, '.projects'), 'r') as proj:
                content = proj.readlines()
            for c in content:
                c = c.replace('\n','')
                data = {
                    'project':c.split(':')[0],
                    'path':c.split(':')[1]
                }
                self.projects.append(data)
        except FileNotFoundError:
            pass

    ############## OPEN FUNCTION INSIDE REPMAN CLASS #############################
    def open(self, name:str):
        print(' ')
    
    ############## LISTER FUNCTION INSIDE REPMAN CLASS #############################
    def lister(self, path:bool=False):
        if len(self.projects)>0:
            lister = pd.DataFrame(self.projects)
            if not path:
                lister = pd.DataFrame(lister['project'].to_list(), columns=['project'])
            print(colored('Following repos are currently under RepMan\'s care:', 'light_blue'))
            print(tabulate(lister, headers='keys', tablefmt='rounded_grid', missingval='?', showindex=False))
        else:
            print(colored('RepMan', 'red'),': No project found under RepMan\'s care.')

    ############## ADD-EXISTING FUNCTION INSIDE REPMAN CLASS #############################
    def add_existing(self, paths:list[str]):
        for path in paths:
            path = abspath(path)
            # if already inside the project directory
            if dirname(path) == self.path:
                # add entry in the .projects file
                with open(join(self.dotfolder, '.projects'), 'a') as projfile:
                    projfile.write(basename(path)+':'+path+'\n')
                print('RepMan:', colored(f'Added {basename(path)} -> {path}', 'green'))
            else:
                ## copy
                try:
                    newpath = copytree(path, join(self.path, basename(path)))
                except FileNotFoundError:
                    print(colored('RepMan', 'red'), f': No such file in this directory. <- {path}')
                    exit(1)
                print('RepMan:', colored(f'Added {basename(path)} -> {newpath}', 'green'))
    
    ############## ADD FUNCTION INSIDE REPMAN CLASS #############################
    def add(self, url:str):
        # set project path
        self.path = environ['REPMAN_PROJECT_PATH']
        chdir(self.path)
        # check format -> must be github link or <username>/<repo>
        if match(r'^https://github.com/\w+/\w+$', url):
            if match(r'^https://github.com/\w+/\w+.git$', url):
                # remove extension and save
                urlbasename = Path(url).stem
            else:
                urlbasename = basename(url)

            # -> try cloning
            # output = getoutputof(f'git clone {url}').readlines()
            with open(join(self.dotfolder, '.log'), 'w') as logfile:
                subprocess.Popen(['git', 'clone', f'{url}'], stderr=logfile, stdout=logfile).wait()
        elif match(r'^\w+/\w+$', url):
            urlbasename = url.split('/')[1]
            # -> try cloning
            with open(join(self.dotfolder, '.log'), 'w') as logfile:
               subprocess.Popen(['git', 'clone', f'https://github.com/{url}.git'], stderr=logfile, stdout=logfile).wait()
        
        # -> check log for output
        with open(join(self.dotfolder, '.log'), 'r') as log:
            logfile = log.readlines()
        # -> check output
        index = len(logfile)-1
        # -> if error
        if match(r'^fatal:\s+\w+$', logfile[index]):
            print('RepMan:', colored(f'Cannot add \'{urlbasename}\'. Check for Spelling Errors.', 'red'))
            exit(1)
        
        # if no error
        # -> save project data to .projects
        with open(join(self.dotfolder, '.projects'), 'a') as projfile:
            projfile.write(f"{urlbasename}:{join(self.path, urlbasename)}\n")
        # -> print added
        print('RepMan:', colored(f'Added {urlbasename} -> {join(self.path, urlbasename)}', 'green'))
    
    ############## INITIALIZE FUNCTION INSIDE REPMAN CLASS #############################
    def initialize(self):
        # Requisites:
        #   1. installation of code
        #   2. installation of git
        #   3. project folder creation - ask for location.
        try:
            ## PRINT INIT ##
            print(colored('RepMan', 'blue'), colored(f'v{self.version}', 'red'))
            print('RepMan:', colored('Jumpstart', 'yellow'))
            
            ## INSTALLATION OF CODE ##
            # -> check existing installation
            checkcodeinstall = True
            if self.operatingsystem=='Linux' or self.operatingsystem=='Darwin':
                try:
                    line = getoutputof('code -v').readline().replace('\n', '').replace('v','').split('.')[0] # should be version
                    
                    try:
                        line = int(line)
                    except ValueError:
                        checkcodeinstall = False
                except IndexError:
                    checkcodeinstall = False
                
                if not checkcodeinstall:
                    installvscode()
                else:
                    print('RepMan:', colored(f"vscode found -> v{getoutputof('code -v').readline().replace('\n','')}", 'green'))
            ## CODE INSTALLATION END ##

            ## installation of git ##
            checkgitinstall = True
            if self.operatingsystem == 'Linux':
                # for linux
                try:
                    line = getoutputof('git -v').readline().replace('\n','').split(' ')[2].split('.')[0]

                    try:
                        line = int(line)
                    except ValueError:
                        checkgitinstall = False
                except IndexError:
                    checkgitinstall = False
            elif self.operatingsystem == 'Darwin':
                # for macos
                gitversion = None
                line = getoutputof('git -v').readline().replace('\n','').split(' ')
                
                length = len(line)
                for i in range(length):
                    if len(line[i].split('.'))==3:
                        gitversion = line[i]
                        break
                
                if gitversion==None:
                    checkgitinstall = False
            
            if not checkgitinstall:
                installgit()
            else:
                print('RepMan:', colored(f"git found -> v{getoutputof('git -v').readline().replace('\n','').split(' ')[2]}", 'green'))
            ## GIT INSTALL END ##
            
            ## Project Folder check ##
            if self.path == '':
                print(colored(' Choose a Project folder...', 'blue'), end='\r')
                # -> get filepath
                self.path = filedialog.askdirectory(initialdir=self.workingpath, title='select project path')
            else:
                pass
                
            # -> resolve where to save the project path
            if platform.system()=='Linux' or platform.system()=='Darwin':
                # -> go to home dir
                chdir(expanduser('~'))
                # -> resolve shell
                shells = []
                filenames = listdir()
                # count shells
                for filename in filenames:
                    if search('^.\w+shrc$', filename):
                        shells.append(filename)
                # update every shell
                for shell in shells:
                    # -> remove pre-existing entry of path if any
                    with open(join(expanduser('~'), f'{shell}'), 'r') as shfile:
                        entries = shfile.read().split('\n')
                    
                    for i in range(len(entries)):
                        if search(r'^export\s+REPMAN_PROJECT_PATH=/\w+', entries[i]):
                            # index = entries.index(entry)
                            entries[i] = '\n'
                    
                    with open(join(expanduser('~'), f'{shell}'), 'w') as shfile:
                        for entry in entries:
                            if entry=='\n':
                                entry = ''
                                shfile.write(entry)
                            else:
                                shfile.write(entry+'\n')
                    
                    run(f"echo \"export REPMAN_PROJECT_PATH={self.path}\" >> ~/{shell}")
            print('RepMan:', colored(f'Project Folder set to {self.path}', 'green'))
            print('RepMan:', colored('Jumpstart END', 'green'))
            print('RepMan:', colored('Terminal restart requested!', 'red'))
            chdir(self.workingpath)
            exit(0)
        except KeyboardInterrupt:
            exit(1)

## installgit funtion outside repman class ##
def installgit():
    print('RepMan:', colored('git not found.', 'red'))
    print('RepMan:', colored('Installing git.', 'yellow'), end='\r')
    
    os = platform.system()
    
    if os == 'Linux':
        subprocess.Popen(['sudo', 'apt-get', 'install', 'git'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()
        print('RepMan:', colored(f"git installed -> v{getoutputof('git -v').readline().replace('\n','').split(' ')[2]}", 'green'))
    elif os == 'Darwin':
        subprocess.Popen(['brew', 'install', 'git'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()
        line = getoutputof('git -v').readline().replace('\n','').split(' ')
                
        length = len(line)
        for i in range(length):
            if len(line[i].split('.'))==3:
                gitversion = line[i]
                break
        
        print('RepMan:', colored(f'git installed -> {gitversion}', 'green'))

## installvscode funtion outside repman class ##
def installvscode():
    print('RepMan:', colored('vscode not found.', 'red'))
    
    os = platform.system()
    
    if os == 'Linux':
        if getoutputof('arch').read().replace('\n','')=='aarch64':
            print('RepMan:', colored('Downloading vscode.', 'yellow'), end='\r')
            subprocess.Popen(['gdown', 'https://drive.google.com/uc?id=1-PlorBHwmve5-rYx4LGgEsVdcVcsxigE'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()
            print('RepMan:', colored('Downloaded vscode', 'green'))
            print('RepMan:', colored('Installing vscode', 'yellow'), end='\r')
            subprocess.Popen(['sudo', 'dpkg', '-i', './code-arm64.deb'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()
            print('RepMan:', colored(f"vscode installed -> v{getoutputof('code -v').readline().replace('\n','')}", 'green'))
    elif os == 'Darwin':
        if getoutputof('arch').read().replace('\n','')=='arm64':
            print('RepMan:', colored('Using Brew to install vscode.', 'yellow'), end='\r')
            subprocess.Popen(['brew', 'install', '--cask', 'visual-studio-code'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()
            print('RepMan:', colored(f"vscode installed -> v{getoutputof('code -v').readline().replace('\n','')}", 'green'))