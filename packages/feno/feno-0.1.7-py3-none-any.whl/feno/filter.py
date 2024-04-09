import enum
import os
import argparse
from typing import Tuple
import shutil

from .__init__ import __version__

# modes
# == RAW
# ++ CUT
# -- DEL
# $$ COM

class Mark:
    def __init__(self, marker, indent):
        self.marker: str = marker
        self.indent: int = indent

    def __str__(self):
        return f"{self.marker}{self.indent}"

class Mode(enum.Enum):
    ADD = 1 # inserir cortando por degrau
    RAW = 2 # inserir tudo
    DEL = 3 # apagar tudo

class LegacyFilter:
    def __init__(self, filename):
        self.mode = Mode.RAW
        self.level = 1
        self.com = "//"
        if filename.endswith(".py"):
            self.com = "#"
        elif filename.endswith(".puml"):
            self.com = "'"

    def process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            if line[-(3 + len(self.com)):-1] == self.com + "++":
                self.mode = Mode.ADD
                self.level = int(line[-1])
            elif line == self.com + "==":
                self.mode = Mode.RAW
            elif line == self.com + "--":
                self.mode = Mode.DEL
            elif self.mode == Mode.DEL:
                continue
            elif self.mode == Mode.RAW:
                output.append(line)
            elif self.mode == Mode.ADD:
                margin = (self.level + 1) * "    "
                if not line.startswith(margin):
                    output.append(line)
        return "\n".join(output)

def get_comment(filename: str) -> str:
    com = "//"
    if filename.endswith(".py"):
        com = "#"
    elif filename.endswith(".puml"):
        com = "'"
    return com

class Filter:
    def __init__(self, filename):
        self.filename = filename
        self.stack = [Mark("==", 0)]
        self.com = get_comment(filename)

    def get_marker(self) -> str:
        return self.stack[-1].marker

    def get_indent(self) -> int:
        return self.stack[-1].indent

    def outside_scope(self, line):
        left_spaces = len(line) - len(line.lstrip())
        return left_spaces < self.get_indent()

    def parse_mode(self, line):
        marker_list = ["$$", "++", "==", "--"]
        with_left = line.rstrip()
        word = with_left.lstrip()
        for marker in marker_list:
            if word == self.com + " " + marker:
                len_spaces = len(with_left) - len(self.com + " " + marker)
                while len(self.stack) > 0 and self.stack[-1].indent >= len_spaces:
                    self.stack.pop()
                self.stack.append(Mark(marker, len_spaces))
                return True
        return False


    def __process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            # print(line)
            # print(", ".join([str(st) for st in self.stack]))
            while self.outside_scope(line) and self.get_marker() != "++":
                self.stack.pop()
            if self.parse_mode(line):
                continue
            elif self.get_marker() == "--":
                continue
            elif self.get_marker() == "==":
                output.append(line)
            elif self.get_marker() == "$$":
                line = line.replace(" " * self.get_indent() + self.com + " ", " " * self.get_indent(), 1)
                output.append(line)
            elif self.get_marker() == "++" and not line.startswith((1 + self.get_indent()) * " "):
                output.append(line)
        return "\n".join(output)
    
    def process(self, content: str) -> str:
        content = LegacyFilter(self.filename).process(content)
        return self.__process(content)

def clean_com(target: str, content: str) -> str:
    com = get_comment(target)
    lines = content.split("\n")
    output = [line for line in lines if not line.lstrip().startswith(com)]
    return "\n".join(output)

class DeepFilter:
    extensions = [".md", ".c", ".cpp", ".h", ".hpp", ".py", ".java", ".js", ".ts", ".hs", ".txt"]

    def __init__(self):
        self.cheat_mode = False
        self.quiet_mode = False
        self.indent = ""
    
    def print(self, *args, **kwargs):
        if not self.quiet_mode:
            print(" " * self.indent, end="")
            print(*args, **kwargs)

    def set_indent(self, prefix: str):
        self.indent = prefix
        return self

    def set_quiet(self, value):
        self.quiet_mode = (value == True)
        return self
    
    def set_cheat(self, value):
        self.cheat_mode = (value == True)
        return self

    def copy(self, source, destiny, deep: int):
        # print("debug", source, destiny, deep)
        if deep == 0:
            return
        if os.path.isdir(source):
            chain = source.split(os.sep)
            if len(chain) > 1 and chain[-1].startswith("."):
                return
            if not os.path.isdir(destiny):
                os.makedirs(destiny)
            for file in sorted(os.listdir(source)):
                self.copy(os.path.join(source, file), os.path.join(destiny, file), deep - 1)
        else:
            filename = os.path.basename(source)

            if not any([filename.endswith(ext) for ext in self.extensions]):
                return
            content = open(source, "r").read()

            processed = Filter(filename).process(content)

            if self.cheat_mode:
                if processed != content:
                    cleaned = clean_com(source, content)
                    with open(destiny, "w") as f:
                        f.write(cleaned)
            elif processed != "":
                with open(destiny, "w") as f:
                    f.write(processed)
            

            line = ""
            if self.cheat_mode:
                if processed != content:
                    line += "(cleaned ): "
                else:
                    line += "(disabled): "
            else:
                if processed == "":
                    line += "(disabled): "
                elif processed != content:
                    line += "(filtered): "
                else:
                    line += "(        ): "
            line += destiny

            self.print(line)

def open_file(path): 
        if os.path.isfile(path):
            with open(path) as f:
                file_content = f.read()
                return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=str, help='file or folder to process')
    parser.add_argument('-u', '--update', action="store_true", help='update source file')
    parser.add_argument('-c', '--cheat', action="store_true", help='recursive cheat mode cleaning comments on students files')
    parser.add_argument('-o', '--output', type=str, help='output target')
    parser.add_argument("-v", '--version', action="store_true", help='print version')
    parser.add_argument("-r", "--recursive", action="store_true", help="recursive mode")
    parser.add_argument("-f", "--force", action="store_true", help="force mode")
    parser.add_argument("-q", "--quiet", action="store_true", help="quiet mode")
    parser.add_argument("-i", "--indent", type=int, default=0, help="indent using spaces")

    args = parser.parse_args()

    if args.version:
        print(__version__)
        exit()

    if args.cheat:
        args.recursive = True

    if args.recursive:
        if args.output is None:
            print("Error: output is required in recursive mode")
            exit()
        if not os.path.isdir(args.target):
            print("Error: target must be a folder in recursive mode")
            exit()
        if os.path.exists(args.output):
            if not args.force:
                print("Error: output folder already exists")
                exit()
            else:
                shutil.rmtree(args.output)
                os.makedirs(args.output)

        deep_filter = DeepFilter().set_cheat(args.cheat).set_quiet(args.quiet).set_indent(args.indent)
        deep_filter.copy(args.target, args.output, 10)
        exit()

    file = args.target
    success, content = open_file(file)
    if success:

        if args.cheat:
            content = clean_com(file, content)
        else:
            content = Filter(file).process(content)

        if args.output:
            if os.path.isfile(args.output):
                old = open(args.output).read()
                if old != content:
                    open(args.output, "w").write(content)
            else:                
                open(args.output, "w").write(content)
        elif args.update:
            with open(file, "w") as f:
                f.write(content)
        else:
            print(content)

if __name__ == '__main__':
    main()
