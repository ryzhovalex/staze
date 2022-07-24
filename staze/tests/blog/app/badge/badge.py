from staze import Database


class Badge(Database.Orm):
    name = Database.column(Database.string(150))
    advanced_users = Database.relationship(
        'AdvancedUser', backref='badge', foreign_keys='AdvancedUser.badge_id')

    @classmethod
    def create(cls, name: str) -> 'Badge':
        return cls(name=name)
