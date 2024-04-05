from .jsontools import JsonVPL
from .check import Check
from .remote_md import RemoteMd, Title, RemoteCfg
from .html import HTML
from .cases import Cases
from .log import Log
from .tree import Tree
from .mdpp import Mdpp

from typing import Optional
import subprocess
import os
import shutil

def norm_join(*args):
    return os.path.normpath(os.path.join(*args))

class Actions:
    def __init__(self, source_dir, make_remote: bool, insert_tko_preamble: bool):
        self.cache = norm_join(source_dir, ".cache")
        self.target = norm_join(self.cache, "mapi.json")
        self.source_dir = source_dir
        self.hook = os.path.basename(os.path.abspath(source_dir))
        self.source_readme = norm_join(self.source_dir, "Readme.md")
        self.remote_readme = norm_join(self.cache, "Readme.md")
        self.target_html = norm_join(self.cache, "q.html")
        self.title = ""
        self.cases = norm_join(self.cache, "q.tio")
        self.config_json = norm_join(self.source_dir, "config.json")
        self.mapi_json = norm_join(self.cache, "mapi.json")
        self.cache_src = norm_join(self.cache, "lang")
        self.vpl = None
        self.make_remote: bool = make_remote
        self.insert_tko_preamble: bool = insert_tko_preamble

    def validate(self):
        if not os.path.isdir(self.source_dir):
            print(f"\n    fail: {self.source_dir} is not a directory")
            return False
        if not os.path.isfile(self.source_readme):
            print(f"\n    fail: {self.source_readme} not found")
            return False
        return True

    def load_title(self):
        self.title = Title.extract_title(self.source_readme)

    def create_cache(self):
        if not os.path.exists(self.cache):
            os.makedirs(self.cache)
        return self
    
    def recreate_cache(self):
        shutil.rmtree(self.cache)
        os.makedirs(self.cache)
        return self
    
    def need_rebuild(self):
        if Check.need_rebuild(self.source_dir, self.target):
            Log.resume("Changes ", end="")
            Log.verbose(f"changes in {self.source_dir}")
            return True
            
        Log.verbose("")
        return False
    
    def remote_md(self):
        cfg = RemoteCfg()
        found = False
        if self.make_remote:
            cfg_path = RemoteCfg.search_cfg_path(self.source_dir)
            if cfg_path is None:
                print("\n    fail: no remote.cfg found in the parent folders")
                print("\n    fail: proceeding without make absolute links")
            else:
                found = True
                Log.verbose(f"    remote.cfg: {cfg_path}")
                cfg.read(cfg_path)
        RemoteMd.run(cfg, self.source_readme, self.remote_readme, self.hook, self.insert_tko_preamble)
        if self.make_remote and found:
            Log.resume("AbsoluteMd ", end="")
        Log.verbose(f"    RemoteFile: {self.remote_readme}")
    
    # uses pandoc to generate html from markdown
    def html(self):
        title = Title.extract_title(self.source_readme)
        HTML.generate_html_with_pandoc(title, self.remote_readme, self.target_html, True)
        Log.resume("HTML ", end="")
        Log.verbose(f"    HTML  file: {self.target_html}")

    # uses tko to generate cases file
    def build_cases(self):
        Cases.run(self.cases, self.source_readme, self.source_dir)
        Log.resume("Cases ", end="")
        Log.verbose(f"    Cases file: {self.cases}")

    def copy_drafts(self):
        source_src = norm_join(self.source_dir, "src")
        if os.path.isdir(source_src):
            Log.resume("Drafts ", end="")
            Log.verbose(f"    Drafts dir: {source_src}")
            Tree.deep_filter_copy(source_src, self.cache_src, 5)

    def run_local_sh(self):
        local_sh = norm_join(self.source_dir, "local.sh")
        actual_chdir = os.getcwd()
        if os.path.isfile(local_sh):
            os.chdir(self.source_dir)
            subprocess.run("bash local.sh", shell=True)
            os.chdir(actual_chdir)
            Log.resume("Local.sh ", end="")
            Log.verbose(f"    local.sh executed")

    def init_vpl(self):
        self.vpl = JsonVPL(self.title, open(self.target_html).read())
        self.vpl.set_cases(self.cases)
        if self.vpl.load_config_json(self.config_json, self.source_dir):
            Log.resume("Required ", end="")
            Log.verbose(f"    CfgVplJson: {self.config_json}")
        if self.vpl.load_drafts(self.cache_src):
            Log.resume("Drafts ", end="")

    def create_mapi(self):
        open(self.mapi_json, "w").write(str(self.vpl) + "\n")
        Log.resume("Mapi ", end="")
        Log.verbose(f"    Mapi  file: {self.mapi_json}")

    def clean(self, erase: bool):
        if erase:
            Log.resume("Cleaning ", end="")
            Log.verbose("    Cleaning  : html and cases files")
            os.remove(self.cases)
            os.remove(self.target_html)

    # run mdpp script on source readme
    def update_markdown(self):
        if Mdpp.update_file(self.source_readme):
            Log.resume("Mdpp ", end="")
            Log.verbose(f"    Mdpp updading")
