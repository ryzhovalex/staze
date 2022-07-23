from staze import orm


class Badge(orm.Model):
    name = orm.column(orm.string(150))
    advanced_users = orm.relationship(
        'AdvancedUser', backref='badge', foreign_keys='AdvancedUser.badge_id')

    @classmethod
    def create(cls, name: str) -> 'Badge':
        return cls(name=name)
