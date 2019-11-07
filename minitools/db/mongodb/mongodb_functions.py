import json
import pandas as pd

__all__ = ('mongodb2csv', 'mongodb2json')


def mongodb2csv(mongodb):
    df = pd.DataFrame(mongodb.findAll().documents)
    df.to_csv(f"mongodb2csv-{mongodb.dbName}-{mongodb.collName}.csv")
    print('Mongodb transform to CSV SUCCESS!')


def mongodb2json(mongodb, dropColumn='_id'):
    documents = mongodb.findAll().documents
    if dropColumn:
        for doc in documents:
            doc.pop(dropColumn)
    with open(f"{mongodb.dbName}-{mongodb.collName}.json", 'w', encoding='utf-8') as f_w:
        f_w.write(json.dumps(documents, ensure_ascii=False))
    print('Mongodb transform to JSON SUCCESS!')
