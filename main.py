
import argparse

from interpretator import main

parser = argparse.ArgumentParser(description='Execute .c file')
parser.add_argument('-f', '--file', help='File with C code')
parser.add_argument('-c', '--code', help='Code of C code')


args = parser.parse_args()
if not args.file and not args.code:
    argparse.ArgumentParser().error('You must choose one argument [-f or -c]')

elif args.file and args.code:
    argparse.ArgumentParser().error('You can choose only one argument [-f or -c]')

code = ''
if args.file:
    with open(args.file, 'r') as file:
        code = file.read()
else:
    code = args.code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute .c file')
    parser.add_argument('-f', '--file', help='File with C code')
    parser.add_argument('-c', '--code', help='Code of C code')

    args = parser.parse_args()
    if not args.file and not args.code:
        argparse.ArgumentParser().error('You must choose one argument [-f or -c]')

    elif args.file and args.code:
        argparse.ArgumentParser().error('You can choose only one argument [-f or -c]')

    code = ''
    if args.file:
        f = open(args.file, "r")
        code = f.read()
    else:
        code = args.code

    main(code)


