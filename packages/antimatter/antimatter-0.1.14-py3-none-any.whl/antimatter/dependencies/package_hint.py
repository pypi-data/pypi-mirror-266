import os
from typing import Dict, List, Tuple

from packaging.requirements import InvalidRequirement, Requirement


def _parse_requirement(fname: str) -> List[Requirement]:
    """
    Parses requirements from the file with the given name.

    :param fname: The requirement filename to parse.
    :return: A Requirement list parsed from the requirements file
    """
    reqs = []
    with open(fname, "r", encoding="utf-8") as fh:
        for line in fh.readlines():
            try:
                reqs.append(Requirement(line))
            except InvalidRequirement:
                pass

    return reqs


def _parse_requirements(_dir: str) -> Dict[str, List[Tuple[List[str], Requirement]]]:
    """
    Builds a mapping of dependencies to the build options requiring them, and the
    associated versions, using requirement files in the current working directory.

    :param _dir: The working directory to use for building requirements.
    :return: The dependency mapping
    """
    reqs = {}
    _dir = os.path.abspath(_dir)
    for f in os.listdir(_dir):
        req_file, ext = os.path.splitext(f)
        if ext == ".txt":
            for r in _parse_requirement(os.path.join(_dir, f)):
                if r.name not in reqs:
                    reqs[r.name] = []
                existing_reqs = reqs[r.name]
                is_present = False
                for t in existing_reqs:
                    if str(t[1]) == str(r):
                        t[0].append(req_file)
                        is_present = True
                if not is_present:
                    reqs[r.name].append(([req_file], r))

    return reqs


def _build_requirements(working_dir: str) -> Dict[str, List[Tuple[List[str], Requirement]]]:
    """
    Builds a mapping of dependencies to the build options requiring them, and the
    associated versions. If a 'requirements' directory is not found in the working
    directory, this will also check one directory higher.

    :param working_dir: The working directory to use for building requirements.
    :return: The dependency mapping
    """
    if "requirements" not in os.listdir(working_dir):
        working_dir = os.path.abspath(os.path.join(working_dir, "../"))
    if "requirements" not in os.listdir(working_dir):
        return {}
    return _parse_requirements(os.path.join(working_dir, "requirements"))


# Requirements directory should be contained in the same parent directory
# as this file's directory
_pkgs = _build_requirements(os.path.dirname(os.path.dirname(__file__)))


def as_install_hint(module_name: str) -> str:
    """
    Get the installation hint from the given module name.

    :param module_name: The module name to find an installation hint for
    :return: A hint for the user as to an action to take for the module
    """
    req_txt = "Recommended action: "
    pip_txt = "'pip install {}'"
    pip_list_txt = "{} for extras {}"

    imports = _pkgs.get(module_name, [])
    imp_txt = "UNKNOWN"
    if len(imports) == 1:
        _, req = imports[0]
        imp_txt = pip_txt.format(str(req))
    elif len(imports) > 1:
        imp_list = []
        for imp in imports:
            extras, req = imp
            imp_list.append(pip_list_txt.format(pip_txt.format(str(req)), str(extras)))
        imp_txt = "; ".join(imp_list)

    return req_txt + imp_txt
