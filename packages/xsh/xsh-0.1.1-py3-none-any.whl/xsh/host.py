import os
import sys


def hostAdd(args):
    if len(args) != 2:
        print('Usage: xsh add <name> <user@host>')
        sys.exit(1)

    name = args[0]
    host = args[1]
    keys = os.listdir(os.path.expanduser('~/.ssh/keys'))
    keys = [key for key in keys if not key.endswith('.pub')]

    # check if there are any keys
    if len(keys) == 0:
        print("No keys found. Run 'xsh key add <name>'   to add a key")
        sys.exit(1)
    
    # check if name already exists
    with open(os.path.expanduser('~/.ssh/config'), 'r') as f:
        for line in f:
            if line.startswith(f'Host {name}'):
                print(f'Host {name} already exists')
                sys.exit(1)

    # choose key
    for i, key in enumerate(keys):
        print(f'{i+1}. {key}')
    
    try:
        keyIndex = int(input('Choose key: ')) - 1
        key = keys[keyIndex]
    except ValueError:
        print('Invalid input')
        sys.exit(1)
    except IndexError:
        print('Invalid index')
        sys.exit(1)

    user = host.split('@')[0]
    host = host.split('@')[1]

    # add host
    with open(os.path.expanduser('~/.ssh/config'), 'a') as f:
        f.write(f'\nHost {name}\n')
        f.write(f'  HostName {host}\n')
        f.write(f'  User {user}\n')
        f.write(f'  IdentityFile {os.path.expanduser(f"~/.ssh/keys/{key}")}\n')

    print(f'Added {name} {host} {key}\n')
    print("What's next?")
    print("Upload the public key file through your cloud provider's dashboard")
    print(f"    {os.path.expanduser(f'~/.ssh/keys/{key}.pub')}\n")
    print("Or append the following public key to the host's ~/.ssh/authorized_keys file\n")

    with open(os.path.expanduser(f'~/.ssh/keys/{key}.pub'), 'r') as f:
        print(f.read())

    print('Then run the following command to connect to the host')
    print(f'    xsh {name}')


def hostList(args):
    with open(os.path.expanduser('~/.ssh/config'), 'r') as f:
        for line in f:
            if line.startswith('Host '):
                print(line.split()[1])


def hostConnect(args):
    if len(args) != 1:
        print('Usage: xsh connect <name>')
        sys.exit(1)

    name = args[0]

    os.system(f'ssh {name}')
    sys.exit(1)

def hostRemove(args):
    if len(args) != 1:
        print('Usage: xsh rm <name>')
        sys.exit(1)

    name = args[0]
    with open(os.path.expanduser('~/.ssh/config'), 'r') as f:
        lines = f.readlines()

    with open(os.path.expanduser('~/.ssh/config'), 'w') as f:
        i = 0
        removed = False
        while i < len(lines):
            if lines[i].startswith(f'Host {name}'):
                i += 1
                removed = True
                while i < len(lines) and not lines[i].startswith('Host '):
                    i += 1
            else:
                f.write(lines[i])
                i += 1

    if not removed:
        print(f'Host {name} not found')
        
    sys.exit(1)
    


def hostHelp(args):
    print('Usage: xsh host <command> [args]')
    print('Commands:')
    print('  add <name> <user@host>')
    print('  ls')
    print('  connect <name>')
    print('  rm <name>')



def host(args):
    if len(args) < 1:
        print('Usage: xsh host <command> [args]')
        sys.exit(1)

    commend = args[0]
    args = args[1:]
    commendMap = {
        'add': hostAdd,
        'ls': hostList,
        'connect': hostConnect,
        'rm': hostRemove,
        'help': hostHelp,
    }
    
    if commend not in commendMap:
        print('Invalid command')
        sys.exit(1)

    commendMap[commend](args)


if __name__ == '__main__':
    hostRemove(['aws'])