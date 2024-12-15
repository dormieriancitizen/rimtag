import dbm

with dbm.open("cache/persistent.dbm","c") as db:
    for key in db.keys():
        print(db[key])