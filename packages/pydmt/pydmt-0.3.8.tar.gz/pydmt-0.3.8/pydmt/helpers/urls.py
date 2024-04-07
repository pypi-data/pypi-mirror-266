import importlib

import pydmt.helpers.project
from pydmt.utils.importlib import module_exists


def get_github_username():
    mod = importlib.import_module("config.personal")
    if hasattr(mod, "github_username"):
        return getattr(mod, "github_username")
    return None


def get_launchpad_username():
    mod = importlib.import_module("config.personal")
    if hasattr(mod, "launchpad_username"):
        return getattr(mod, "launchpad_username")
    return None


def get_website():
    github_username = get_github_username()
    name = pydmt.helpers.project.get_name()
    return f"https://{github_username}.github.io/{name}"


def get_website_source():
    github_username = get_github_username()
    name = pydmt.helpers.project.get_name()
    return f"https://github.com/{github_username}/{name}"


def get_website_git():
    github_username = get_github_username()
    name = pydmt.helpers.project.get_name()
    return f"git://github.com/{github_username}/{name}.git"


def get_website_ppa():
    launchpad_username = get_github_username()
    return f"https://launchpanet/~{launchpad_username}/+archive/ubuntu/ppa"


def get_deps():
    if module_exists("config.deps"):
        mod = importlib.import_module("config.deps")
        if hasattr(mod, "packages"):
            return getattr(mod, "packages")
        return None
    return None
