"""

"""
import os
import sys
import errno
from shutil import copy2

# /users/me/Conductor/maya/ciomaya
PKG_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = PKG_DIR
CIODIR = os.path.dirname(PKG_DIR)  # /users/me/Conductor/maya
PKGNAME = os.path.basename(PKG_DIR)  # ciomaya
MODULE_FILENAME = "conductor.mod"
PLATFORM = sys.platform
with open(os.path.join(PKG_DIR, "VERSION")) as version_file:
    VERSION = version_file.read().strip()
WIN_MY_DOCUMENTS = 5
WIN_TYPE_CURRENT = 0
SUPPORTED_MAYA_VERSIONS = range(2019, 2026)

def main():
    if not PLATFORM.startswith(("darwin", "win", "linux")):
        sys.stderr.write("Unsupported platform: {}".format(PLATFORM))
        sys.exit(1)

    # Write the Maya module file to the user's module directory under their Maya prefs
    destination = get_maya_module_dir()
    write_maya_mod_file(destination, MODULE_DIR, CIODIR)
    
    # Write another copy of the Maya module file to the ciomaya directory
    # This facilitates setting up the module in a shared environment.
    write_maya_mod_file(MODULE_DIR, ".", "..")
    sys.stdout.write("Completed Maya Module setup!\n")
    
    shared_msg = "If you are an IT administrator setting up Conductor for Maya in a shared environment, please set or append the following environment variable for your artists."
    shared_msg += "\n\nMAYA_MODULE_PATH='{}'\n".format(MODULE_DIR)
    sys.stdout.write(shared_msg)
    

def get_maya_module_dir():

    app_dir = os.environ.get("MAYA_APP_DIR")
    if not app_dir:
        if PLATFORM.startswith("darwin"):
            app_dir = "~/Library/Preferences/Autodesk/maya"
        elif PLATFORM.startswith("linux"):
            app_dir = "~/maya"
        else:  # windows
            try:
                import ctypes.wintypes

                buff = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                ctypes.windll.shell32.SHGetFolderPathW(
                    None, WIN_MY_DOCUMENTS, None, WIN_TYPE_CURRENT, buff
                )
                documents = buff.value
            except BaseException:
                sys.stderr.write(
                    "Couldn't determine MyDocuments folder for the conductor.mod file.\n"
                )
                sys.stderr.write(
                    "You may have to move it manually from the path below if that is not your where your Maya prefs and modules live.\n"
                )
                documents = "~/Documents"
            app_dir = "{}/maya".format(documents)

    return os.path.join(os.path.expanduser(app_dir), "modules")


def write_maya_mod_file(destination, module_dir, ciodir):

    ensure_directory(destination)
    fn = os.path.join(destination, MODULE_FILENAME)
    with open(fn, "w") as f:
        for maya_version in SUPPORTED_MAYA_VERSIONS:
            f.write("+ MAYAVERSION:{} conductor {} {}\n".format(maya_version, VERSION, module_dir))
            join = "="
            if ciodir == "..":
                join=":="
            f.write("MAYA_CIODIR{}{}\n\n".format(join, ciodir))

    sys.stdout.write("Wrote Maya module file: {}\n".format(fn))


def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise


if __name__ == "__main__":
    main()
