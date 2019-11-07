from minitools.db.mongodb import MongodbBase, mongodb2csv, mongodb2json

if __name__ == '__main__':
    test = MongodbBase('github', 'statistics_by_month')
    print(test.find(commit_count=5).documents)
    print(test.find(size={'commit_count': 4}).documents)
    mongodb2json(test)
    mongodb2csv(test)
