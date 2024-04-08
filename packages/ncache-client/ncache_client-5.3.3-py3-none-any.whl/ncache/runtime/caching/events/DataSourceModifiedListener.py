from ncache.runtime.WriteBehindOpResult import WriteBehindOpResult
from ncache.util.JavaInstancesFactory import *


@JImplements(environment.get("DataSourceModifiedListener"), deferred=True)
class DataSourceModifiedListener:
    def __init__(self, callablefunction):
        self.callablefunction = callablefunction

    @JOverride
    def onDataSourceModified(self, key, writebehindopresult):
        writebehindopresult = WriteBehindOpResult(writebehindopresult)
        self.callablefunction(str(key), writebehindopresult)
