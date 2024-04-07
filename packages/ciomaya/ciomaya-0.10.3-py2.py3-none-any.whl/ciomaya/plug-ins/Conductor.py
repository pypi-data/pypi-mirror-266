import sys
import os

CIODIR = os.environ.get("MAYA_CIODIR")
sys.path.append(CIODIR)


import maya.api.OpenMaya as om

from ciocore import data as coredata
import maya.cmds as mc
from ciomaya.lib import conductor_menu


def maya_useNewAPI():
    pass


def initializePlugin(obj):
    # Use "0.10.3 to cause the version to be replaced at build time."

    plugin = om.MFnPlugin(obj, "Conductor", "0.10.3", "Any")
    # ciomaya imports must come after check_pymel.
    from ciomaya.lib.nodes.conductorRender import conductorRender
    try:
        plugin.registerNode(
            "conductorRender",
            conductorRender.id,
            conductorRender.creator,
            conductorRender.initialize,
            om.MPxNode.kDependNode,
        )
    except:
        sys.stderr.write("Failed to register conductorRender\n")
        raise

    
    conductor_menu.load()

    coredata.init("maya-io")


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)

    # ciomaya imports must come after check_pymel.
    from ciomaya.lib.nodes.conductorRender import conductorRender
    try:
        plugin.deregisterNode(conductorRender.id)
    except:
        sys.stderr.write("Failed to deregister conductorRender\n")
        raise

    # ciomaya imports must come after check_pymel.
    from ciomaya.lib import conductor_menu
    conductor_menu.unload()
