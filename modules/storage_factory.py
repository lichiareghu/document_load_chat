import shelve

class Data:
    def __init__(self,name):
        self.name = name
    #
    def save_object(self,object):
        with shelve.open("Data") as db:
            if self.name in list(db.keys()):
                tmp = db[self.name]
                tmp.update(object)
                db[self.name] = tmp
            else:
                db[self.name] = object
            return db[self.name]

    def get_objects(self):
        with shelve.open("Data") as db:
            object = db[self.name] if self.name in list(db.keys()) else None
        return object

    def remove_object(self,keyname):
        tmp = self.get_objects()
        if keyname in list(tmp.keys()):
            tmp.pop(keyname)
        if tmp:
            with shelve.open("Data") as db:
                db[self.name] = tmp
        return tmp

