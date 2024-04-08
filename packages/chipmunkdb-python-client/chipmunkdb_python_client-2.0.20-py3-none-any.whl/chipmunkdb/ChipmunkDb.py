from typing import List

import requests
import io
import pyarrow as pa
import pyarrow.parquet as pq
import json
import pandas as pd



class StorageEntry:
    key: str
    value: str
    datetime: str
    tags: [str]

class FilterEntry:
    key: str
    tags: [str]


class ChipmunkDb():
    def __init__(self, host, port=8091, autoConnect=True):
        self.host = host
        self.port = port
        self.autoConnect = autoConnect
        self.initialize()

    def connect(self):

        return True

    def initialize(self):
        if (self.autoConnect):
            self.connect()
        return True

    def getHostAndPort(self):
        return 'http://'+str(self.host)+":"+str(self.port)

    def create_from_pandas(self, collection, df):
        return self.savePandas(collection, df, mode="create")

    def dropCollection(self, collection):
        res = requests.delete(url=self.getHostAndPort()+"/collection/"+collection+"/drop", data={"collection": collection, "drop": True})
        return res.json()

    def collections(self):
        res = requests.get(url=self.getHostAndPort()+"/collections")
        return res.json()["collections"]

    def collection_info(self, collection):
        res = requests.get(url=self.getHostAndPort()+"/collection/"+collection)
        data = res.json()
        if "error" in data:
            return None
        return data["collection"]

    def get_document(self, directory, document):
        res = requests.get(url=self.getHostAndPort()+"/directory/"+directory+"/"+document)
        retdata = res.json()
        return retdata["data"]

    def save_document(self, directory, document, data, type="single"):
        res = requests.post(url=self.getHostAndPort()+"/directory/"+directory+"/"+document, data=json.dumps({"data": data, "type": type}))
        retdata = res.json()
        if "error" in retdata:
            return None
        return retdata["data"]

    def generate_random_id(self):
        import random
        import string
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(10))

    def save_collection(self, collection):

        res = requests.post(url=self.getHostAndPort()+'/collection/'+collection+'/save')
        return res.json()

    def save_as_pandas(self, df, collection, mode="append", domain=None, session_id=None, end=False):

        if session_id is None:
            # lets iterate over the dataframe and send chunks with a session_id
            session_id = self.generate_random_id()

            while True:
                chunk = df.head(40000)
                if chunk.empty:
                    break
                df = df.tail(-40000)
                self.save_as_pandas(chunk, collection, mode=mode, domain=domain, session_id=session_id, end=df.shape[0] == 0)

        else:

            f = io.BytesIO()
            table = pa.Table.from_pandas(df)
            pq.write_table(table, f)

            headerData = {"mode": mode,  "domain": domain}
            if session_id is not None:
                headerData["session_id"] = session_id
                headerData["end"] = end

            f.seek(0, 0)
            res = requests.post(url=self.getHostAndPort()+'/collection/' + str(collection) + '/insertRaw',
                                files={"data": f.getvalue()},
                                headers={"Content-Type": 'application/octet-stream', "x-data": json.dumps(headerData)})
            f.close()

        return True

    def query(self, query, domain=None):
        domainQ = ""
        if domain is not None:
            domainQ = "&domain="+domain
        res = requests.get(url=self.getHostAndPort()+"/query?q="+query+domainQ, headers={"x-data": json.dumps({"streamed-response": "true"})})
        data = res.json()

        return data["result"]

    def dropColumn(self, collection, columns, domain=None):
        res = requests.delete(url=self.getHostAndPort() + "/collection/" + collection + "/dropColumns",
                           headers={"Content-Type": 'application/octet-stream',
                                    "x-data": json.dumps({"columns": columns, "domain": domain})})
        data = res.content

        return data

    def collection_as_pandas(self, collection, columns=[], domain=None):
        res = requests.get(url=self.getHostAndPort()+"/collection/"+collection+"/rawStream",
                           headers={"Content-Type": 'application/octet-stream', "x-data": json.dumps({"columns": columns, "domain": domain})})
        data = res.content

        pq_file = io.BytesIO(data)
        df = pd.read_parquet(pq_file)

        return df

    def collection_as_pandas_additional(self, collection, additionalCollections: [], columns=[], domain=None):
        res = requests.get(url=self.getHostAndPort()+"/collection/"+collection+"/rawStream",
                           headers={"Content-Type": 'application/octet-stream', "x-data": json.dumps({"columns": columns,
                                                                                                      "additionalCollections": additionalCollections,
                                                                                                      "domain": domain})})
        data = res.content

        pq_file = io.BytesIO(data)
        df = pd.read_parquet(pq_file)

        return df

    def storages(self):
        res = requests.get(url=self.getHostAndPort()+"/storages")
        return res.json()["storages"]

    def drop_storage(self, storage):
        res = requests.delete(url=self.getHostAndPort()+"/storage/"+storage)
        return res.json()["success"]

    def get_storage(self, storage):
        res = requests.get(url=self.getHostAndPort()+"/storage/"+storage)
        return res.json()["data"]

    def filter_storage(self, storage, filters: List[FilterEntry]):
        res = requests.post(url=self.getHostAndPort()+"/storage/"+storage+"/filter", data=json.dumps(filters))
        if res.status_code != 200:
            raise(res.json()["message"])
        return res.json()["data"]


    def save_keys_to_storage(self, storage, keys: List[StorageEntry]):
        res = requests.post(url=self.getHostAndPort()+"/storage/"+storage, data=json.dumps(keys))
        return res.json()["count"]

    def get_key_for_storage(self, storage, key):
        res = requests.get(url=self.getHostAndPort()+"/storage/"+storage+"/"+key)
        return res.json()["data"]

def main():
    pass