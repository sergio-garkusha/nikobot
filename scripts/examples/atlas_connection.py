from pymongo import MongoClient
from pymongo.server_api import ServerApi
uri = "<url is in configparser .ini of this project>"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='<path to your cert, see .ini>',
                     server_api=ServerApi('1'))
db = client['nikovolunteers']
collection = db['orders']
doc_count = collection.count_documents({})
print(doc_count)
