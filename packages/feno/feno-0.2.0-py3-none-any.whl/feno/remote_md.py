import os
import re
import configparser

from typing import List, Optional
from .log import Log

class Title:
    @staticmethod
    def extract_title(readme_file):
        title = open(readme_file).read().split("\n")[0]
        parts = title.split(" ")
        if parts[0].count("#") == len(parts[0]):
            del parts[0]
        title = " ".join(parts)
        return title

class RemoteCfg:
    def __init__(self):
        self.user = ""
        self.repo = ""
        self.base = ""
        self.branch = "master"

    def read(self, cfg_path: str):
        if not os.path.isfile(cfg_path):
            print("no remote.cfg found")

        config = configparser.ConfigParser()
        config.read(cfg_path)

        self.user = config["DEFAULT"]["user"]
        self.repo = config["DEFAULT"]["rep"]
        self.base = config["DEFAULT"]["base"]
        self.branch = config["DEFAULT"]["branch"]
        self.tag = config["DEFAULT"]["tag"]

    @staticmethod
    def search_cfg_path(source_dir) -> Optional[str]:
        # look for the remote.cfg file in the current folder
        # if not found, look for it in the parent folder
        # if not found, look for it in the parent's parent folder ...

        path = os.path.abspath(source_dir)
        while path != "/":
            cfg_path = os.path.join(path, "remote.cfg")
            if os.path.isfile(cfg_path):
                return cfg_path
            path = os.path.dirname(path)
        
        return None

class Absolute:

    # processa o conteúdo trocando os links locais para links absolutos utilizando a url remota
    @staticmethod
    def __replace_remote(content: str, remote_raw: str, remote_view: str, remote_folder: str) -> str:
        if not remote_raw.endswith("/"):
            remote_raw += "/"
        if not remote_view.endswith("/"):
            remote_view += "/"
        if not remote_folder.endswith("/"):
            remote_folder += "/"

        #trocando todas as imagens com link local
        regex = r"!\[(.*?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
        subst = "![\\1](" + remote_raw + "\\3)"
        result = re.sub(regex, subst, content, 0)


        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?/)\)"
        subst = "[\\1](" + remote_folder + "\\3)"
        result = re.sub(regex, subst, result, 0)

        #trocando todos os links locais cujo conteudo nao seja vazio
        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
        subst = "[\\1](" + remote_view + "\\3)"
        result = re.sub(regex, subst, result, 0)

        return result

    @staticmethod
    def relative_to_absolute(content: str, cfg: RemoteCfg, hook):
        base_hook = os.path.join(cfg.base, hook)
        user_repo = os.path.join(cfg.user, cfg.repo)
        remote_raw    = os.path.join("https://raw.githubusercontent.com", user_repo, cfg.branch , base_hook)
        remote_view    = os.path.join("https://github.com/", user_repo, "blob", cfg.branch, base_hook)
        remote_folder = os.path.join("https://github.com/", user_repo, "tree", cfg.branch, base_hook)
        return Absolute.__replace_remote(content, remote_raw, remote_view, remote_folder)

    @staticmethod
    def from_file(source_file, output_file, cfg: RemoteCfg, hook):
        content = open(source_file).read()
        content = Absolute.relative_to_absolute(content, cfg, hook)
        open(output_file, "w").write(content)
        

class RemoteMd:

    @staticmethod
    def insert_preamble(lines: List[str], online: str, tkodown: str) -> List[str]:

        text = "\n- Veja a versão online: [aqui.](" + online + ")\n"
        text += "- Para programar na sua máquina (local/virtual) use:\n"
        text += "  - `" + tkodown + "`\n"
        text += "- Se não tem o `tko`, instale pelo [LINK](https://github.com/senapk/tko#tko).\n\n---"

        lines.insert(1, text)

        return lines

    @staticmethod
    def insert_qxcode_preamble(cfg: RemoteCfg, content: str, hook) -> str:
        base_hook = os.path.join(cfg.base, hook)

        lines = content.split("\n")
        online_readme_link = os.path.join("https://github.com", cfg.user, cfg.repo, "blob", cfg.branch, base_hook, "Readme.md")
        tkodown = "tko down " + cfg.tag + " " + hook
        lines = RemoteMd.insert_preamble(lines, online_readme_link, tkodown)
        return "\n".join(lines)

    @staticmethod
    def run(remote_cfg: RemoteCfg, source: str, target: str, hook, insert_preamble: bool) -> bool:    
        content = open(source).read()
        if remote_cfg is not None:
            if insert_preamble:
                content = RemoteMd.insert_qxcode_preamble(remote_cfg, content, hook)
            content = Absolute.relative_to_absolute(content, remote_cfg, hook)
        open(target, "w").write(content)

if __name__ == "__main__":
    remote_cfg = RemoteCfg()
    remote_cfg.read(RemoteCfg.get_default_cfg_path())
    hook = os.path.basename(os.path.abspath("."))
    RemoteMd.run(remote_cfg, "Readme.md", ".cache/Readme.md")
