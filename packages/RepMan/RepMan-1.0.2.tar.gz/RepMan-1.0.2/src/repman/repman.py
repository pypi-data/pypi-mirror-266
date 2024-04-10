#!/usr/bin/env python3

## OS Support
# Linux -> aarch64
# MacOs -> AppleSilicon(arm64)

__version__ = '1.0.1'

from repman._repmanfunctions import funcdefs
from repman._repmanhelps import helptext
from termcolor import colored
from optioner import options
from sys import argv
from re import match


# list value removing function
def rem(original:list[str], remove:list[str]) -> list[str]:
    removed:list[str] = []
    for x in original:
        if x not in remove:
            removed.append(x)
    
    return removed

# main function
def main():
    try:
        # helptext
        help = helptext(__version__)
        # functions
        funk = funcdefs(__version__)
        # create arguments
        shortargs = ['h', 'v', 'a', 'i', 'o', 'l', 'lp', 'ae', 'al', 'u', 'sr']
        longargs = ['help', 'version', 'add', 'init', 'open', 'list', 'list-w-path', 'add-existing', 'add-local', 'update', 'set-remote']
        
        # All args
        original = shortargs.copy()
        original.extend(longargs)
        
        # mutually exclusive args
        mutex = [
            ['v', 'version'],rem(original, ['v', 'version', 'h', 'help']),
            ['a', 'add'],rem(original, ['a', 'add', 'h', 'help']),
            ['o','open'],rem(original, ['o','open', 'h', 'help']),
            ['i', 'init'],rem(original, ['i', 'init', 'h', 'help']),
            ['l', 'list'],rem(original, ['l', 'list', 'h', 'help']),
            ['lp', 'list-w-path'],rem(original, ['lp', 'list-w-path', 'h', 'help']),
            ['ae', 'add-existing'],rem(original, ['ae', 'add-existing', 'h', 'help']),
            ['al', 'add-local'], rem(original, ['al', 'add-local', 'h', 'help']),
            ['u', 'update'], rem(original, ['u', 'update', 'h', 'help']),
            ['sr', 'set-remote'], rem(original, ['sr', 'set-remote', 'h', 'help'])
        ]
        
        optctrl = options(shortargs, longargs, argv[1:], ifthisthennotthat=mutex)
        
        args, check, error, falseargs = optctrl._argparse()
        
        if not check:
            print(colored('RepMan Err', 'red'), f': {error}')
            exit(1)
        else:
            if len(args)==0:
                if len(falseargs)>0:
                    print(colored('RepMan Err', 'red'), ': you got the wrong guy bruh.')
                    exit(1)
                print(colored('RepMan Err', 'red'), ': Please tell me what to do.')
                exit(1)
            else:
                # help
                if '-h' in args:
                    # check for other args if there, and show help accordingly
                    otherarg = ''
                    if len(args)==2:
                        # if length of all args = 2, i.e some other arg is there
                        # find -h's index, the other one must be the arg, the user is asking help for.
                        index = args.index('-h')
                        if index==0:
                            otherarg = args[1]
                        else:
                            otherarg = args[0]
                        
                        if otherarg=='-h' or otherarg=='--help':
                            help.base()
                        elif otherarg=='-v' or otherarg=='--version':
                            help.version_h(otherarg)
                        elif otherarg=='-i' or otherarg=='--init':
                            help.init_h(otherarg)
                        elif otherarg=='-a' or otherarg=='--add':
                            help.add_h(otherarg)
                        elif otherarg=='-o' or otherarg=='--open':
                            help.open_h(otherarg)
                        elif otherarg == '-l' or otherarg == '--list':
                            help.list_h(otherarg)
                        elif otherarg == '-lp' or otherarg == '--list-w-path':
                            help.listwpath_h(otherarg)
                        elif otherarg == '-ae' or otherarg == '--add-existing':
                            help.addexisting_h(otherarg)
                        elif otherarg == '-al' or otherarg == '--add-local':
                            help.addlocal_h(otherarg)
                        elif otherarg == '-u' or otherarg == '--update':
                            help.update_h(otherarg)
                        elif otherarg == '-sr' or otherarg == '--set-remote':
                            help.setremote_h(otherarg)
                        else:
                            print(colored('RepMan Err', 'red'), f': argument \'{otherarg}\' is not recognised.')
                    elif len(args)<2:
                        help.base()
                    elif len(args)>2:
                        print(colored('RepMan Err', 'red'), ': Please use one argument at a time to show help on that argument.')
                        print(colored('Format', 'blue'), ': \'repman <argument> -h\' or \'repman <argument> --help\'.')
                        exit(1)
                    else:
                        print(colored('RepMan Err', 'red'), ': Could not resolve arguments.')
                        print(colored('RepMan Hint', 'blue'), ': Run \'repman -h\' or \'repman --help\'.')
                        exit(1)
                elif '--help' in args:
                    # check for other args if there, and show help accordingly
                    otherarg = ''
                    if len(args)==2:
                        # if length of all args = 2, i.e some other arg is there
                        # find -h's index, the other one must be the arg, the user is asking help for.
                        index = args.index('--help')
                        if index==0:
                            otherarg = args[1]
                        else:
                            otherarg = args[0]
                        
                        if otherarg=='-h' or otherarg=='--help':
                            help.base()
                        elif otherarg=='-v' or otherarg=='--version':
                            help.version_h(otherarg)
                        elif otherarg=='-i' or otherarg=='--init':
                            help.init_h(otherarg)
                        elif otherarg=='-a' or otherarg=='--add':
                            help.add_h(otherarg)
                        elif otherarg=='-o' or otherarg=='--open':
                            help.open_h(otherarg)
                        elif otherarg == '-l' or otherarg == '--list':
                            help.list_h(otherarg)
                        elif otherarg == '-lp' or otherarg == '--list-w-path':
                            help.listwpath_h(otherarg)
                        elif otherarg == '-ae' or otherarg == '--add-existing':
                            help.addexisting_h(otherarg)
                        elif otherarg == '-al' or otherarg == '--add-local':
                            help.addlocal_h(otherarg)
                        elif otherarg == '-u' or otherarg == '--update':
                            help.update_h(otherarg)
                        elif otherarg == '-sr' or otherarg == '--set-remote':
                            help.setremote_h(otherarg)
                        else:
                            print(colored('RepMan Err', 'red'), f': argument \'{otherarg}\' is not recognised.')
                    elif len(args)<2:
                        help.base()
                    elif len(args)>2:
                        print(colored('RepMan Err', 'red'), ': Please use one argument at a time to show help on that argument.')
                        print(colored('Format', 'blue'), ': \'repman <argument> -h\' or \'repman <argument> --help\'.')
                        exit(1)
                    else:
                        print(colored('RepMan Err', 'red'), ': Could not resolve arguments.')
                        print(colored('RepMan Hint', 'blue'), ': Run \'repman -h\' or \'repman --help\'.')
                        exit(1)
                else:
                    pass
                
                # version
                if '-v' in args or '--version' in args:
                    help.version()
                
                # init
                if '-i' in args:
                    index = argv.index('-i')
                    try:
                        value = argv[index+1]
                    except IndexError:
                        value = None
                    
                    if value==None:
                        funk.init()
                    else:
                        funk.init(value)
                elif '--init' in args:
                    index = argv.index('--init')
                    try:
                        value = argv[index+1]
                    except IndexError:
                        value = None
                    
                    if value==None:
                        funk.init()
                    else:
                        funk.init(value)
                
                # add
                if '-a' in args:
                    index = argv.index('-a')
                    try:
                        value = argv[index+1]
                    except IndexError:
                        value = None
                    
                    if value==None:
                        print(colored('RepMan', 'red'), ': \'-a\' needs a value.')
                        exit(1)
                    else:
                        funk.add(value)
                elif '--add' in args:
                    index = argv.index('--add')
                    
                    try:
                        value = argv[index+1]
                    except IndexError:
                        value = None
                    
                    if value==None:
                        print(colored('RepMan', 'red'), ': \'--add\' needs a value.')
                        exit(1)
                    else:
                        funk.add(value)
                
                # add existing
                if '-ae' in args:
                    index = argv.index('-ae')
                    
                    value:list[str] = []
                    try:
                        for i in range(index+1, len(argv)):
                            value.append(argv[i])
                    except IndexError:
                        print(colored('RepMan', 'red'), ': \'-ae\' needs atleast one value.')
                        exit(1)
                    
                    funk.addexisting(value)
                    
                elif '--add-existing' in args:
                    index = argv.index('--add-existing')
                    
                    value:list[str] = []
                    try:
                        for i in range(index+1, len(argv)):
                            value.append(argv[i])
                    except IndexError:
                        print(colored('RepMan', 'red'), ': \'--add-existing\' needs atleast one value.')
                        exit(1)
                    
                    funk.addexisting(value)
                
                # list
                if '-l' in args or '--list' in args:
                    funk.lister(False)
                
                # list with path
                if '-lp' in args or '--list-w-path' in args:
                    funk.lister(True)
                
                # open
                if '-o' in args:
                    index = argv.index('-o')
                    
                    value:list[str] = []
                    try:
                        for i in range(index+1, len(argv)):
                            value.append(argv[i])
                    except IndexError:
                        print(colored('RepMan', 'red'), ': \'-o\' needs atleast one value.')
                        exit(1)
                    
                    funk.openthis(value)
                elif '--open' in args:
                    index = argv.index('--open')
                    
                    value:list[str] = []
                    try:
                        for i in range(index+1, len(argv)):
                            value.append(argv[i])
                    except IndexError:
                        print(colored('RepMan', 'red'), ': \'--open\' needs atleast one value.')
                        exit(1)
                    
                    funk.openthis(value)
                
                # update
                if '-u' in args:
                    index = argv.index('-u')
                    try:
                        value = argv[index+1]
                        funk.update(value)
                    except IndexError:
                        print(colored('RepMan', 'red'), ': \'-u\' needs a value.')
                        exit(1)
                elif '--update' in args:
                    index = argv.index('--update')
                    try:
                        value = argv[index+1]
                        funk.update(value)
                    except IndexError:
                        print(colored('RepMan', 'red'), ': \'--update\' needs a value.')
                        exit(1)
                
                # add local
                if '-al' in args:
                    index = argv.index('-al')
                    value:list[str] = []
                    try:
                        for i in range(index+1, len(argv)):
                            value.append(argv[i])
                    except IndexError:
                        print(colored('RepMan', 'red'), ': \'-al\' needs atleast one value.')
                        exit(1)
                elif '--add-local' in args:
                    index = argv.index('--add-local')
                    value:list[str] = []
                    try:
                        for i in range(index+1, len(argv)):
                            value.append(argv[i])
                    except IndexError:
                        print(colored('RepMan', 'red'), ': \'--add-local\' needs atleast one value.')
                        exit(1)
                    
                funk.addlocal(value)
                
                # set remote
                if '-sr' in args:
                    index = argv.index('-sr')
                    value:list[str] = []
                    try:
                        for i in range(index+1, len(argv)):
                            value.append(argv[i])
                    except IndexError:
                        print(colored('RepMan', 'red')+': \'-sr\' needs two values. <project> and <remote>')
                        exit(1)
                    
                    project:str = ''
                    remote:str = ''
                    if len(value)==2:
                        for v in value:
                            if match(r'^https://github.com/\w+/\w+', v) or match(r'^\w+/\w+', v):
                                remote = v
                            else:
                                project = v
                        funk.setremote(project, remote)
                    else:
                        print(colored('RepMan', 'red')+': \'-sr\' accepts only two values')
                        exit(1)
                    
    except KeyboardInterrupt:
        print('\n'+colored('RepMan', 'red')+": Decide Karen!")
                

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nRepMan: Keyboard Interrupt')
        exit(1)