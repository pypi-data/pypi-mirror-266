
import os
import sys


def keyAdd(args):
    if len(args) != 1:
        print('Usage: xsh keygen <name>')
        sys.exit(1)
    name = args[0]

    # check if key already exists
    if os.path.exists(os.path.expanduser(f'~/.ssh/keys/{name}')):
        print(f'Key {name} already exists')
        sys.exit(1)

    savePath = os.path.expanduser(f'~/.ssh/keys/')

    os.system(f'ssh-keygen -t rsa -b 4096 -f {savePath + name} -N ""')


    print(f'Generated key {name}')
    print(f'Public key saved to {savePath}')
          



def keyList(args):
    keys = os.listdir(os.path.expanduser('~/.ssh/keys'))
    for key in keys:
        if not key.endswith('.pub'):
            print(key)


def keyRemove(args):
    if len(args) != 1:
        print('Usage: xsh key rm <name>')
        sys.exit(1)

    name = args[0]
    os.remove(os.path.expanduser(f'~/.ssh/keys/{name}'))
    os.remove(os.path.expanduser(f'~/.ssh/keys/{name}.pub'))


def keyHelp(args):
    print('Usage: xsh key <command> [args]')
    print('Commands:')
    print('  add <name>')
    print('  ls')
    print('  rm <name>')


def key(args):
    if len(args) < 1:
        print('Usage: xsh key <command> [args]')
        sys.exit(1)

    commend = args[0]
    args = args[1:]
    commendMap = {
        'add': keyAdd,
        'ls': keyList,
        'rm': keyRemove,
        'help': keyHelp,
    }

    if commend not in commendMap:
        print('Invalid command')
        sys.exit(1)
    
    commendMap[commend](args)