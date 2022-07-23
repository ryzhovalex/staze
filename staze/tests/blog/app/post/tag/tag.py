from staze import orm, log


class Tag(orm.Mapper):
    name = orm.column(orm.string(100), unique=True)

    @classmethod
    @log.catch
    def create(cls, name: str) -> 'Tag':
        return cls(name=name)
