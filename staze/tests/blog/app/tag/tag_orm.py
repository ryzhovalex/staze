from staze import Database, log


class TagOrm(Database.Orm):
    _name = Database.column(Database.string(100), unique=True)

    @classmethod
    def create(cls, name: str) -> 'TagOrm':
        return cls(_name=name)
