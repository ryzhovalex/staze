from __future__ import annotations
import re
from functools import wraps
from typing import TYPE_CHECKING, Callable, Any, TypeVar

from warepy import format_message, snakefy
from staze.core.database.orm_not_found_error import OrmNotFoundError
from staze.core.model.model import Model
from staze.core.log import log
from flask import Flask
import flask_migrate
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import Model as BaseOrm
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr

from staze.core.service.service import Service
from .database_type_enum import DatabaseTypeEnum

if TYPE_CHECKING:
    hybrid_property = property


AnyOrm = TypeVar('AnyOrm', bound='Database.Orm')


# TODO: Fix type hinting for decorated functions under this decorator.
def migration_implemented(func: Callable):
    @wraps(func)
    def inner(self_instance, *args, **kwargs):
        if type(self_instance) is not Database:
            raise TypeError(
                "Decorator migration_implemented cannot be"
                f" applied to type {type(self_instance)}")
        elif not self_instance.migration:
            error_message = "Migrate object hasn't been implemented yet"
            raise AttributeError(error_message)
        else:
            return func(self_instance, *args, **kwargs)
    return inner


class Orm(BaseOrm):
    """Base orm model responsible of holding database model's data and at least
    it's basic CRUD operations.

    Contains create(), get_first(), get_all() and del_first() methods as
    Create, Retrieve and Delete representatives.
    Update representatives are defined individually at each subclass
    (e.g. `set_something()`), and by default accessed via basic model
    alteration, e.g. `MyModel.name = 'Another name'`.
    """
    # As superclass sqlalchemy used instead of `orm` class to avoid reference
    # errors
    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/customizing/

    # Name to exclude on tablename forming
    _BASE_NAME: str = 'Orm'

    _id = sa.Column(sa.Integer, primary_key=True)
    _type = sa.Column(sa.String(250))

    @hybrid_property
    def id(self):
        return self._id

    @hybrid_property
    def type(self):
        return self._type

    @declared_attr
    def __tablename__(cls) -> str:
        cls_name: str = cls.__name__  # type: ignore
        return snakefy(cls_name)

    @declared_attr
    def __identity__(cls) -> str:
        return snakefy(cls.__name__.replace(cls._BASE_NAME, ''))  # type: ignore

    @declared_attr
    def __mapper_args__(cls) -> dict[str, Any]:
        args: dict[str, Any] = {}
        args.update({
            'polymorphic_on': '_type',
            'polymorphic_identity': cls.__identity__
        })
        return args

    @classmethod
    def create(cls: AnyOrm, **kwargs) -> AnyOrm:
        """Create model and return it.
        
        Accepts all given kwargs and thus is recommended to be redefined at
        subclasses.

        Model creation intended to be done only through this method.
        """
        model = cls(**kwargs)
        return model

    @classmethod
    def get_first(
            cls,
            order_by: object | list[object] | None = None,
            **kwargs) -> Database.Orm:
        """Filter first ORM orm model by given kwargs and return it.
        
        Raise:
            ValueError:
                No such ORM model in database matched given kwargs
        """
        query: Any = cls.query.filter_by(**kwargs)  # type: ignore

        if order_by is not None:
            query = cls._order_query(query, order_by)

        model: Database.Orm = query.first()

        if not model:
            raise OrmNotFoundError(orm_name=cls.__name__, **kwargs)
        else:
            return model

    @classmethod
    def get_all(
            cls,
            order_by: object | list[object] | None = None,
            limit: int | None = None,
            **kwargs) -> list[Database.Orm]:
        """Filter all ORM orm models by given kwargs and return them.

        Return:
            List of found models.
            If no models found, empty list is returned.
        """
        query: Any = cls.query.filter_by(**kwargs)  # type: ignore

        if order_by is not None:
            query = cls._order_query(query, order_by)

            if limit:
                query = query.limit(limit)
        elif limit:
            query = query.limit(limit)

        models: list[Database.Orm] = query.all()

        if type(models) is not list:
            raise OrmNotFoundError(model_name=cls.__name__, **kwargs)
        else:
            # Return models even if it's empty list
            return models

    @classmethod
    def delete_first(
            cls,
            order_by: object | list[object] | None = None,
            **kwargs) -> None:
        """Delete first accessed by `get_first()` method model."""
        database: Database = Database.instance()
        model: Database.Orm = cls.get_first(order_by=order_by, **kwargs)
        database.delete(model)

    @staticmethod
    def _order_query(query: Any, order_by: object | list[object]) -> object:
        if type(order_by) is list:
            return query.order_by(*order_by)
        else:
            return query.order_by(order_by)

    @property
    def model(cls) -> Model:
        """Transform self to a Model instance.
        
        Model here should be defined explicitly at subclass of superclass
        Model.

        Example:
            UserOrm has to define User(Model) subclass and redefine this
            method to construct User(Model) class with values from the Orm
            it requires.
            It's often useful for API calls to Orms.

        Returns:
            Model:
                Model subclass contained required to expose Orm's
                properties.
        """
        raise NotImplementedError(
            'Should be re-implemented for Orm-specific Model subclass')


class Database(Service):
    """Operates over database processes."""
    # Helper references for shorter writing at ORMs.
    # Ignore lines added for a workaround to fix issue:
    # https://github.com/microsoft/pylance-release/issues/187
    native_database = SQLAlchemy(model_class=Orm)
    Orm: Any = native_database.Model 
    column = native_database.Column
    integer = native_database.Integer
    string = native_database.String
    text = native_database.Text
    float = native_database.Float
    boolean = native_database.Boolean
    foreign_key = native_database.ForeignKey
    table = native_database.Table
    check_constraint = native_database.CheckConstraint
    relationship = native_database.relationship
    backref = native_database.backref
    pickle = native_database.PickleType
    binary = native_database.LargeBinary
    datetime = native_database.DateTime

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.DEFAULT_URI = f"sqlite:///{self.config['root_dir']}/sqlite3.database"

        self.native_database = Database.native_database
        # For now service config propagated to Database domain
        self._assign_uri_from_config(config)

    def _assign_uri_from_config(self, config: dict) -> None:
        raw_uri = config.get("uri", None)  # type: str

        if not raw_uri:
            log.info(f"URI for database is not specified, using default")
            raw_uri = self.DEFAULT_URI
        else:
            # Case 1: SQLite Database
            # Developer can give relative path to the Database
            # (it will be absolutized at Config.parse()),
            # by setting sqlite Database extension to `.database`, e.g.:
            #   `./instance/sqlite3.database`
            # or by setting full absolute path with protocol, e.g.:
            #   `sqlite:////home/user/project/instance/sqlite3.database`
            if raw_uri.rfind(".database") != -1 or "sqlite:///" in raw_uri:
                if "sqlite:///" not in raw_uri: 
                    # Set absolute path to database
                    # Ref: https://stackoverflow.com/a/44687471/14748231
                    self.uri = "sqlite:///" + raw_uri
                else:
                    self.uri = raw_uri
                self.type_enum = DatabaseTypeEnum.SQLITE
            # Case 2: PostgreSQL Database
            elif re.match(r"postgresql(\+\w+)?://", raw_uri):
                # No need to calculate path since psql uri should be given in
                # full form
                self.uri = raw_uri
                self.type_enum = DatabaseTypeEnum.PSQL
            else:
                raise ValueError(
                    "Unrecognized or yet unsupported type of Database uri:"
                    f" {raw_uri}")
            
            # WARNING:
            #   Never print full Database uri to config, since it may
            #   contain user's password (as in case of psql)
            log.info(f"Set database type: {self.type_enum.value}")

    @migration_implemented
    def init_migration(
            self,
            directory: str = "migrations",
            multidatabase: bool = False) -> None:
        """Initializes migration support for the application."""
        flask_migrate.init(directory=directory, multidb=multidatabase)

    @migration_implemented
    def migrate_migration(
        self,
        directory: str = "migrations", 
        message = None, 
        sql = False, 
        head: str = "head", 
        splice = False, 
        branch_label = None, 
        version_path = None, 
        rev_id = None
    ) -> None:
        flask_migrate.migrate(
            directory=directory,
            message=message,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id
        )

    @migration_implemented
    def upgrade_migration(
        self,
        directory: str = "migrations",
        revision: str = "head",
        sql = False,
        tag = None
    ) -> None:
        flask_migrate.upgrade(
            directory=directory,
            revision=revision,
            sql=sql,
            tag=tag
        )

    def setup(self, flask_app: Flask) -> None:
        """Setup Database and migration object with given Flask app."""
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = self.uri
        flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.native_database.init_app(flask_app)

        # render_as_batch kwarg required only for sqlite3 databases to avoid
        # ALTER TABLE issue on migrations
        # https://blog.miguelgrinberg.com/post/fixing-alter-table-errors-with-flask-migrate-and-sqlite
        if self.type_enum is DatabaseTypeEnum.SQLITE:
            is_sqlite_database = True
        else:
            is_sqlite_database = False
        self.migration = flask_migrate.Migrate(flask_app, self.native_database, render_as_batch=is_sqlite_database)

    def get_native_database(self) -> SQLAlchemy:
        return self.native_database

    @migration_implemented
    def get_migration(self) -> flask_migrate.Migrate:
        """Return migration object.
        
        Raise:
            AttributeError: If Migrate object hasn't implemented yet.
        """
        return self.migration

    @migration_implemented
    def create_all(self) -> None:
        self.native_database.create_all()

    @migration_implemented
    def drop_all(self):
        "Drop all tables."
        self.native_database.drop_all()

    @migration_implemented
    def add(self, *entities):
        """Place an object in the session."""
        for entity in entities:
            self.native_database.session.add(entity)

    @migration_implemented
    def delete(self, *entities):
        for entity in entities:
            self.native_database.session.delete(entity)

    @migration_implemented
    def push(self, *entities):
        """Add entity to session and immediately commit the session."""
        for entity in entities:
            self.add(entity)
        self.commit()

    @migration_implemented
    def refresh(self, *entities):
        for entity in entities:
            self.native_database.session.refresh(entity)

    @migration_implemented
    def expire(self, *entities):
        for entity in entities:
            self.native_database.session.expire(entity)

    @migration_implemented
    def refpush(self, *entities):
        self.push(*entities)
        self.refresh(*entities)

    @migration_implemented
    def commit(self):
        """Commit current transaction."""
        self.native_database.session.commit()

    @migration_implemented
    def rollback(self):
        self.native_database.session.rollback()

    @migration_implemented
    def remove(self):
        self.native_database.session.remove()
