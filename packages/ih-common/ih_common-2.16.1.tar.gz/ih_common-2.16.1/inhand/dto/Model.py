import json
import datetime




class Metadata:
    created_at: datetime = None
    updated_at: datetime = None
    created_by: str = None
    updated_by: str = None

    def __init__(self, created_by: str = None, updated_by: str = None):
        if created_by is not None:
            self.created_by = created_by;
            self.created_at = datetime.now()
        elif updated_by is not None:
            self.updated_by = updated_by
            self.updated_at = datetime.now()

    def toDict(self):
        kv = {}
        if self.updated_by is not None:
            kv['updated_by'] = self.updated_by
            kv['updated_at'] = self.updated_at
        else:
            kv['created_by'] = self.created_by
            kv['created_at'] = self.created_at
        return kv

    @staticmethod
    def fromDict(kv: dict):
        metadata = Metadata()
        metadata.created_by = None if ['created_by'] not in kv.keys() else kv['created_by']
        metadata.created_at = None if ['created_at'] not in kv.keys() else kv['created_at']
        metadata.updated_by = None if ['updated_by'] not in kv.keys() else kv['updated_by']
        Metadata.updated_at = None if ['updated_at'] not in kv.keys() else kv['updated_at']
        return metadata

    def tostring(self):
        json_string = json.dumps(self.toDict());
        return json_string

class Model:
    metadata: Metadata = None

    def updatedby(self, by: str):
        if self.metadata is None:
            self.metadata = Metadata(created_by=by, updated_by=by)
        else:
            self.metadata.updated_by = by
            self.metadata.updated_at = datetime.now()