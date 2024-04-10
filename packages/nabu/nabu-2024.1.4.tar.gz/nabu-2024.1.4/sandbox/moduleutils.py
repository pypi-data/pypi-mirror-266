from os import path
import pkgutil
import sys
import nabu

# module_path = path.dirname(mymodule.__file__)
def get_module_files(module_path, print_files=False):
    module_name = path.basename(module_path)
    res = {}
    for _, submodule_name, is_folder in pkgutil.iter_modules([module_path]):
        submodule_path = path.join(module_path, submodule_name)
        if is_folder:
            res[submodule_name] = get_module_files(submodule_path, print_files=print_files)
        fname = submodule_path + ".py"
        if path.isfile(fname):
            res[submodule_name] = fname
            if print_files:
                print(fname)
    return res



def get_module_output_name(module_path, fname, target_dir):
    fname2 = fname.replace(module_path, "")
    module_name = path.basename(module_path)
    return path.join(target_dir, module_name + fname2.replace("/", ".").replace(".py", ""))


if __name__ == "__main__":
    def print_usage():
        print("Usage: %s <get_files|get_path|get_module_output_name>" % sys.argv[0])

    nargs = len(sys.argv[1:])
    if nargs == 0:
        print_usage()
        exit(0)
    nabu_path = path.dirname(nabu.__file__)
    if sys.argv[1] == "get_files":
        get_module_files(nabu_path, print_files=True)
    elif sys.argv[1] == "get_path":
        print(nabu_path)
    elif sys.argv[1] == "get_module_output_name":
        if nargs != 3:
            print("Usage: %s get_module_outfile <file name> <target dir>" % sys.argv[0])
            exit(0)
        print(get_module_output_name(nabu_path, sys.argv[2], sys.argv[3]))
        exit(0)
    else:
        print_usage()
        exit(0)
