import sys
import os
import argparse
from xsh.host import *
from xsh.key import key



def init(args):
    if not os.path.exists(os.path.expanduser('~/.ssh/')):
        os.makedirs(os.path.expanduser('~/.ssh/'))  

    if not os.path.exists(os.path.expanduser('~/.xsh')):
        os.makedirs(os.path.expanduser('~/.xsh'))

    if not os.path.exists(os.path.expanduser('~/.ssh/keys')):
        os.makedirs(os.path.expanduser('~/.ssh/keys'))
    
    if not os.path.exists(os.path.expanduser('~/.ssh/config')):
        with open(os.path.expanduser('~/.ssh/config'), 'w') as f:
            f.write('')

    with open(os.path.expanduser('~/.xsh/config'), 'w') as f:
        f.write('')
    print('Initialized xsh')


def help(args):
    print('Usage: xsh <command> [args]')
    print('Commands:')
    print('  init')
    print('  key <command> [args]')
    print('  host <command> [args]')



def main_cli():
    parser = argparse.ArgumentParser(
        prog='xsh',
        description='xsh - a config manager for ssh',
        epilog="Run 'xsh help' for more information."
        )
    parser.add_argument('command', help='command to run')
    parser.add_argument('args', nargs='*', help='arguments for the command')
    args = parser.parse_args()

    commendMap = {
        'init': init,
        'host': host,
        'key': key,
        'help': help,
        'add': hostAdd,
        'ls': hostList,
        'connect': hostConnect,
        'rm': hostRemove,
    }

    if not os.path.exists(os.path.expanduser('~/.xsh')):
        print('Initializing xsh')
        init([])
        print('Generating your first ssh key')
        key(['add', 'default'])

    if args.command in commendMap:
        commendMap[args.command](args.args)
    else:
        os.system(f'ssh {args.command}')
        sys.exit(1)
    

    
