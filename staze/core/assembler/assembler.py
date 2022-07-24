from __future__ import annotations
import os
import sys
import importlib.util
from typing import TYPE_CHECKING, Any
from dotenv import load_dotenv

from warepy import (
    format_message, load_yaml, get_enum_values, Singleton
)
from flask_socketio import SocketIO
import pytest
from staze.core.assembler.assembler_error import AssemblerError
from staze.core.app.app_mode_enum import (
    DatabaseAppModeEnum, RunAppModeEnum, AppModeEnumUnion, HelperAppModeEnum)
from staze.core.error_handler import ErrorHandler

from staze.core.socket.socket import Socket
from staze.core.service.service import Service
from staze.core.log import log
from staze.core.error.error import Error
from staze.core.model.config import Config

from staze.core.database.database import Database
from staze.core.app.app import App

if TYPE_CHECKING:
    from .build import Build


class Assembler(Singleton):
    """Assembles all project instances and initializes it.

    Acts automatically and shouldn't be inherited directly by project in any
    form.

    TODO: Write all init args
    Args:
        extra_configs_by_name (optional):
            Configs to be appended to appropriate ones described in Build
            class. Defaults to None.
            Contain config name as key (which is compared to Config
            name field) and configuration mapping as value, e.g.:
    ```python
    extra_configs_by_name = {
        "app": {"TESTING": True},
        "database": {"database_uri": "sqlite3:///:memory:"}
    }
    ```
        root_dir (optional):
            Root dir to execute project from. Defaults to `os.getcwd()`.
            Required in cases of calling this function not from actual
            project root (e.g. from tests) to set root path explicitly.
    """
    def __init__(
            self, 
            mode_enum: AppModeEnumUnion,
            mode_args: list[str] = [],
            source_filename: str = 'build',
            build: Build | None = None,
            host: str = 'localhost',
            port: int = 5000,
            root_dir: str = os.getcwd(),
            extra_configs_by_name: dict[str, Any] | None = None) -> None:
        # Define attributes for getter methods to be used at builder
        # Do not set extra_configs_by_name to None at initialization, because
        # `get()` method called from this dictionary
        self.extra_configs_by_name = {}
        self.root_dir = root_dir
        self.socket_enabled: bool = False

        self.mode_enum: AppModeEnumUnion = mode_enum
        self.mode_args: list[str] = mode_args

        # Load build from module
        if build:
            self.build = build
        else:
            self.build = self._load_target_build(source_filename)

        # Environs should be loaded from app's root directory
        load_dotenv(os.path.join(self.root_dir, self.build.env_path))

        # Use build in further assignment
        self.service_classes = self.build.service_classes
        self.view_classes = self.build.view_classes
        self.shell_processors = self.build.shell_processors
        self.ctx_processor_func = self.build.ctx_processor_func
        self.each_request_func = self.build.each_request_func
        self.first_request_func = self.build.first_request_func
        self.sock_classes = self.build.sock_classes

        self.default_error_handler = self.build.default_error_handler
        self.default_builtin_error_hanlder = \
            self.build.default_builtin_error_handler

        # Load env or use build default
        self.config_dir: str
        env_config_dir = os.getenv('CONFIG_DIR')
        if isinstance(env_config_dir, str) and env_config_dir:
            log.info(
                f'Env CONFIG_DIR specified to {env_config_dir},'
                ' use it by default')
            self.config_dir = env_config_dir
        else:
            self.config_dir = self.build.config_dir

        self._build_configs(self.config_dir)
        
        self._build_builtin_services(mode_enum, host, port)
        self._build_builtin_helpers()

        # Namespace to hold all initialized services. Should be used only for
        # testing purposes, when direct import of services are unavailable
        self._custom_services: dict[str, Any] = {}

        # Add extra configs
        if extra_configs_by_name:
            self.extra_configs_by_name = extra_configs_by_name

        self._register_self_singleton()

        self._build_log()
        self._build_custom_services()
        self._build_custom_views()
        self._build_custom_shell_processors()
        self._build_custom_cli_cmds()
        self._build_custom_socks()

        # Call postponed build from created App.
        try:
            self.app.postbuild()
        except NotImplementedError:
            pass

    @property
    def custom_services(self):
        return self._custom_services

    def _register_self_singleton(self):
        """Register self instance to Singleton instance.
        
        This should be done at initialization to avoid built services Assembler
        initialization problem via `Assembler.instance()` call.
        """
        type(self.__class__).instances[self.__class__] = self

    def _load_target_build(self, source_filename: str) -> Build:
        """Load target module spec from location, where cli were called."""
        # Add root_dir to sys.path to avoid ModuleNotFoundError during lib
        # importing
        sys.path.append(self.root_dir)

        module_location = os.path.join(self.root_dir, source_filename + ".py")
        module_spec = importlib.util.spec_from_file_location(
            source_filename, module_location)
        if module_spec and module_spec.loader:
            main_module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(main_module)
            # TODO: Add validation of result build?
            return main_module.build
        else:
            raise NameError(
                format_message(
                    "Could not resolve module spec for location: {}.",
                    module_location))

    def _build_configs(self, config_dir: str) -> None:
        """Traverse through config files under given config_dir and create 
        Configs from them.

        Name taken from filename of config and should be the same as specified 
        at config's target service_class.name.

        Names can contain additional extension like `name.prod.yaml` according
        to appropriate app modes. These configs launched per each mode. Config
        without this extra extension, considered `prod` moded.
        """
        self.config_classes: list[Config] = []

        config_path: str = os.path.join(self.root_dir, config_dir)
        source_map_by_name: dict[str, dict[RunAppModeEnum, str]] = \
            Config.find_config_files(config_path)

        for name, source_map in source_map_by_name.items():
            self.config_classes.append(Config(
                name=name,
                source_by_app_mode=source_map))

    def _build_builtin_services(
            self, mode_enum: AppModeEnumUnion, host: str, port: int) -> None:
        """Assign builting service cells if configuration file for its service
        exists.
        """
        # First service to be initialized is always the App
        self.app: App = App(
            mode_enum=mode_enum, host=host, port=port, 
            config=self._assemble_service_config('app'),
            ctx_processor_func=self.ctx_processor_func,
            each_request_func=self.each_request_func,
            first_request_func=self.first_request_func)
        layers_to_log: list[str] = []

        # Enable only modules with specified configs.
        # TODO:
        #   Instead of catching ValueError, which could be anything, make
        #   own custom error inside find_by_name()
        if self.config_classes:
            try:
                Config.find_by_name('database', self.config_classes)
            except ValueError:
                pass
            else:
                self.database: Database = Database(
                    config=self._assemble_service_config('database'))

                # Perform Database postponed setup
                self._perform_database_postponed_setup()
                layers_to_log.append('database')
            try:
                Config.find_by_name('socket', self.config_classes)
            except ValueError:
                pass
            else:
                self.socket = Socket(
                    config=self._assemble_service_config('socket'),
                    app=self.app)
                self.socket_enabled = True
                layers_to_log.append('socket')
            
            if layers_to_log:
                log.info(f'Enabled layers: {", ".join(layers_to_log)}')

    def _build_builtin_helpers(self) -> None:
        self._build_error_handler()

    def run(self):
        if isinstance(self.mode_enum, RunAppModeEnum):
            if self.mode_enum is RunAppModeEnum.TEST:
                self._run_test()
            else:
                self._run_app()
        elif isinstance(self.mode_enum, HelperAppModeEnum):
            if self.mode_enum is HelperAppModeEnum.SHELL:
                self._run_shell()
            elif self.mode_enum is HelperAppModeEnum.CMD: 
                # TODO: Custom cmds after assembler build operations.
                raise NotImplementedError
            elif self.mode_enum is HelperAppModeEnum.DEPLOY:
                # TODO: Implement deploy operation.
                raise NotImplementedError
            else:
                raise TypeError
        elif isinstance(self.mode_enum, DatabaseAppModeEnum):
            with self.app.app_context():
                if self.mode_enum is DatabaseAppModeEnum.INIT:
                    self.database.init_migration()
                elif self.mode_enum is DatabaseAppModeEnum.MIGRATE:
                    self.database.migrate_migration()
                elif self.mode_enum is DatabaseAppModeEnum.UPGRADE:
                    self.database.upgrade_migration()
                else:
                    raise TypeError
        else:
            raise TypeError

    def _run_shell(self):
        """Invoke app interactive shell."""
        self.app.run_shell()

    def _run_app(self):
        self.app.run()

    def _run_test(self):
        log.info('Run tests')
        pytest.main(self.mode_args)
        

    def _build_log(self) -> None:
        """Call chain to build log."""
        # Try to find log config cell and build log class from it
        if self.config_classes:
            try:
                log_config_class = Config.find_by_name("log", self.config_classes)
            except ValueError:
                log_config = None
            else:
                # Parse config mapping from cell and append extra configs,
                # if they are given
                app_mode_enum: RunAppModeEnum
                if type(self.mode_enum) is RunAppModeEnum:
                    app_mode_enum = RunAppModeEnum(self.mode_enum.value) 
                else:
                    # Assign dev app mode for all other app modes
                    app_mode_enum = RunAppModeEnum.DEV
                log_config = log_config_class.parse(
                    app_mode_enum=app_mode_enum,
                    root_dir=self.root_dir, 
                    update_with=self.extra_configs_by_name.get("log", None)
                )

            # Init logger
            log_kwargs = log.DEFAULT_LOG_PARAMS

            if log_config:
                for k, v in log_config.items():
                    log_kwargs[k] = v

            log.configure(**log_kwargs)

    def _build_custom_socks(self) -> None:
        if self.sock_classes and self.socket_enabled:
            for sock_class in self.sock_classes:
                socketio: SocketIO = self.socket.get_socketio()

                # Register class for socketio namespace
                # https://flask-socketio.readthedocs.io/en/latest/getting_started.html#class-based-namespaces
                socketio.on_namespace(sock_class(sock_class.NAMESPACE))
                # Also register error handler for the same namespace
                socketio.on_error(sock_class.NAMESPACE)(
                    sock_class.ERROR_HANDLER) 
        elif self.sock_classes and not self.socket_enabled:
            raise AssemblerError(
                'Sock classes are given, but Socket itself is not enabled')
        elif not self.sock_classes and self.socket_enabled:
            log.warning('Socket enabled, but sock classes are not given')

    def _perform_database_postponed_setup(self) -> None:
        """Postponed setup is required, because Database uses Flask app to init
        native SQLAlchemy database inside, so it's possible only after App
        initialization.

        The setup_database requires native flask app to work with.
        """
        self.database.setup(flask_app=self.app.get_native_app())

    def _build_custom_services(self) -> None:
        if self.service_classes:
            for service_class in self.service_classes:
                if self.config_classes:
                    service_config = self._assemble_service_config(
                        name=service_class.get_config_name()) 
                else:
                    service_config = {}

                service: Service = Service(config=service_config)
                self._custom_services[service_class.get_config_name()] = \
                    service

    def _assemble_service_config(
            self,
            name: str, is_errors_enabled: bool = False) -> dict[str, Any]:
        """Check for service's config in config cells by comparing its given
        name and return it as dict.

        If appropriate config hasn't been found, raise ValueError if
        `is_errors_enabled = True` or return empty dict otherwise.
        """
        try:
            config_class_with_target_name: Config = Config.find_by_name(
                name, self.config_classes)
        except ValueError:
            # If config not found and errors enabled, raise error.
            if is_errors_enabled:
                message = format_message(
                    "Appropriate config for given name {} hasn't been found.",
                    name)
                raise ValueError(message)
            else:
                config: dict[str, Any] = {}
        else:
            if type(config_class_with_target_name) is not Config:
                raise TypeError(format_message(
                    "Type of cell should be Config, but {} received",
                    type(config_class_with_target_name)))
            else:
                app_mode_enum: RunAppModeEnum
                if type(self.mode_enum) is RunAppModeEnum:
                    app_mode_enum = RunAppModeEnum(self.mode_enum.value) 
                else:
                    # Assign dev app mode for all other app modes.
                    app_mode_enum = RunAppModeEnum.DEV
                config = config_class_with_target_name.parse(
                    root_dir=self.root_dir, 
                    update_with=self.extra_configs_by_name.get(name, None),
                    app_mode_enum=app_mode_enum)
    
        # Each builtin service should receive essential fields for their
        # configs, such as root_dir, because they cannot import Assembler
        # due to circular import issue and get this fields by themselves
        if 'root_dir' in config:
            raise ValueError(
                'Service config shouldn\'t contain key `root_dir`')
        config["root_dir"] = self.root_dir

        return config

    def _fetch_yaml_project_version(self) -> str:
        """Fetch project version from info.yaml from the root path and return it. 

        TODO:
            Replace this logic with senseful one. Better use configuration's
            version? Or __init__.py or main.py specified.
        """
        info_data = load_yaml(os.path.join(self.root_dir, "./info.yaml"))
        project_version = info_data["version"]
        return project_version

    def _build_custom_views(self) -> None:
        """Build all views by registering them to app."""
        if self.view_classes:
            for view_class in self.view_classes:
                self.app.register_view(view_class)

    def _build_custom_shell_processors(self) -> None:
        if self.shell_processors:
            self.app.register_shell_processor(*self.shell_processors)

    def _build_custom_cli_cmds(self) -> None:
        # TEMP:
        #   In development
        #
        # if self.cli_cmds:
        #     self.app.register_cli_cmd(*self.cli_cmds)
        pass

    def _build_error_handler(self) -> None:
        ErrorHandler(
            app=self.app,
            default_error_handler=self.default_error_handler,
            default_builtin_error_handler=self.default_builtin_error_hanlder)
