import os

from .log import Log
from .filter import Filter

class Tree:
    @staticmethod
    def deep_filter_copy(source, destiny, deep: int):
        if deep == 0:
            return
        if os.path.isdir(source):
            chain = source.split(os.sep)
            if len(chain) > 1 and chain[-1].startswith("."):
                return
            if not os.path.isdir(destiny):
                os.makedirs(destiny)
            for file in sorted(os.listdir(source)):
                Tree.deep_filter_copy(os.path.join(source, file), os.path.join(destiny, file), deep - 1)
        else:
            filename = os.path.basename(source)
            text_extensions = [".md", ".c", ".cpp", ".h", ".hpp", ".py", ".java", ".js", ".ts", ".hs", ".txt"]
            if not any([filename.endswith(ext) for ext in text_extensions]):
                return
            content = open(source, "r").read()
            processed = Filter(filename).process(content)
            if processed == content:
                Log.verbose("         =====: ", end="")
                open(destiny, "w").write(processed)
            elif processed == "" or processed == "\n":
                Log.verbose("         empty: ", end="")
            else:
                Log.verbose("         draft: ", end="")
                open(destiny, "w").write(processed)
            Log.verbose(destiny)

