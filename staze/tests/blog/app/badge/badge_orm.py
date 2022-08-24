from typing import TYPE_CHECKING
from staze import Database


if TYPE_CHECKING:
    from blog.app.user.user_orm import AdvancedUserOrm


class BadgeOrm(Database.Orm):
    _name = Database.column(Database.string(150))
    _advanced_user_orms = Database.relationship(
        'AdvancedUserOrm',
        backref='_badge_orm',
        foreign_keys='AdvancedUserOrm._badge_id')

    @classmethod
    def create(cls, name: str) -> 'BadgeOrm':
        return cls(_name=name)

    def add_advanced_user(self, advanced_user_orm: 'AdvancedUserOrm'):
        self._advanced_user_orms.append(advanced_user_orm)
