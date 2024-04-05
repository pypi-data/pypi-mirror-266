import argparse
import sys
import os

from .actions import Actions
from .__init__ import __version__
from .log import Log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('targets', metavar='T', type=str, nargs='*', help='folders')
    parser.add_argument("--check", "-c", action="store_true", help="Check if the file needs to be rebuilt")
    parser.add_argument("--version", "-v", action="store_true", help="Prints the version")

    parser.add_argument("--brief", "-b", action="store_true", help="Brief mode")
    parser.add_argument("--erase", "-e", action="store_true", help="Erase .html and .tio temp files")
    parser.add_argument("--remote", "-r", action="store_true", help="Search for remote.cfg file and create absolute links")
    parser.add_argument("--tko", "-t", action="store_true", help="Insert tko preamble")
    

    args = parser.parse_args()
    Log.set_verbose(not args.brief)
    
    if args.version:
        print(__version__)
        sys.exit(0)

    if len(args.targets) == 0:
        print("fail: No targets specified")
        exit(1)

    for target in args.targets:
        hook = os.path.basename(os.path.abspath(target))

        actions = Actions(target, args.remote, args.tko)
        Log.resume(hook, end=": [ ")
        Log.verbose(hook, end=" ")

        if not actions.validate():
            continue

        actions.load_title()
        actions.create_cache()
        actions.update_markdown()

        if not args.check or actions.need_rebuild():
            actions.recreate_cache() # erase .cache
            actions.copy_drafts()
            actions.update_markdown() # se os drafts tiverem mudado o markdown precisa ser atualizado
            actions.remote_md()
            actions.html()
            actions.build_cases()
            actions.run_local_sh()
            actions.init_vpl()
            actions.create_mapi()
            actions.clean(args.erase)

        Log.resume("]")


if __name__ == "__main__":
    main()
