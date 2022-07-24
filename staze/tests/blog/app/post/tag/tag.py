from staze import Database, log


class Tag(Database.Orm):
    name = Database.column(Database.string(100), unique=True)

    @classmethod
    @log.catch
    def create(cls, name: str) -> 'Tag':
        return cls(name=name)
