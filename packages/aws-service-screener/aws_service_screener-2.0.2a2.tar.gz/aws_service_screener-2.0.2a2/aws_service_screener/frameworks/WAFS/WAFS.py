import json

import aws_service_screener.constants as _C
from aws_service_screener.frameworks.Framework import Framework

class WAFS(Framework):
    def __init__(self, data):
        super().__init__(data)
        pass
    
if __name__ == "__main__":
    data = json.loads(open(_C.FRAMEWORK_DIR + '/api.json').read())
    # print(data)
    o = WARS(data)
    o.readFile()
    # o.obj()
    o.generateMappingInformation()