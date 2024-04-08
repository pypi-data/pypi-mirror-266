import os
import jpype as jp
import jpype.imports
from jpype import *

from ncache.util.Environment import *


def initialize_jpype():
    """
    This function initializes the JPype and prepare it to call code from .jar files
    """
    jars = []

    import ncache.lib
    directory = ncache.lib.__path__[0]

    for filename in os.listdir(directory):
        if filename.endswith(".jar") or filename.endswith(".dll"):
            jars.append(os.path.join(directory, filename))
        else:
            continue

    jarspath = "-Djava.class.path=%s" % os.pathsep.join(jars)

    # noinspection PyUnresolvedReferences
    jvmpath = jp.getDefaultJVMPath()

    # noinspection PyUnresolvedReferences
    if not jp.isJVMStarted():
        # noinspection PyUnresolvedReferences
        jp.startJVM(jvmpath, "-ea", jarspath, convertStrings=True)


initialize_jpype()
