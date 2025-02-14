from invoke import Collection
import os
import sys

sys.path.append(os.path.normpath(os.path.join(__file__, "../..")))  #  noqa

from . import boot, cv, sign


ns = Collection()
for module in [
    boot, cv, sign
]:
    ns.add_collection(Collection.from_module(module))
