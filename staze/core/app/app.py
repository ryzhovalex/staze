import os
import sys
import code
import secrets
from typing import Callable, Type

from flask_cors import CORS
from turbo_flask import Turbo
from flask_session import Session
from flask.testing import FlaskClient
from staze.core import validation
from staze.core.app.app_error import AppError
from staze.core.app.app_mode_enum import (
    RunAppModeEnum, HelperAppModeEnum, DatabaseAppModeEnum, AppModeEnumUnion)
from staze.core.log.log import log
from flask import Flask, request
from flask.wrappers import Response
from flask import cli as flask_cli
from flask.ctx import AppContext, RequestContext
from warepy import get_enum_values
from staze.core.log.log import log

from staze.core.service.service import Service
from staze.core.view.view import View
from .turbo_action_enum import TurboActionEnum


class App(Service):
    """Core app's class.
    """
    def __init__(
                self, 
                config: dict,
                mode_enum: AppModeEnumUnion,
                host: str,
                port: int,
                ctx_processor_func: Callable | None = None,
                before_request_func: Callable | None = None,
                before_first_request_func: Callable | None = None,
                after_request_func: Callable | None = None
            ) -> None:
        self._host = host
        self._port = port

        # Templates by default searched within src/app, which allows to
        # integrate them directly to their logical component's folders
        self.DEFAULT_TEMPLATE_DIR = os.path.join(
            config['root_dir'], 'src/app')
        self.DEFAULT_STATIC_DIR = os.path.join(
            config['root_dir'], 'src/assets')
        self.DEFAULT_INSTANCE_DIR = os.path.join(config['root_dir'], 'var')

        # Convert all keys from given config to upper case
        self.config = self._make_upper_keys(config)
        self._assign_defaults_to_config(self.config)
        self._validate_config(self.config)

        self.INSTANCE_DIR: str = self.config.get(
            "INSTANCE_DIR", self.DEFAULT_INSTANCE_DIR
        )
        self.TEMPLATE_DIR: str = self.config.get(
            "TEMPLATE_DIR", self.DEFAULT_TEMPLATE_DIR
        ) 
        self.STATIC_DIR: str = self.config.get(
            "STATIC_DIR", self.DEFAULT_STATIC_DIR
        )

        super().__init__(self.config)
        self._mode_enum: AppModeEnumUnion = mode_enum
        self._root_dir: str = self.config['ROOT_DIR']

        self.native_app = self._spawn_native_app(self.config)
        self.native_app.config.from_mapping(self.config)
        self._enable_cors(self.config)
        self._enable_testing_config(self.config)
        self._add_random_hex_token_to_config()
        # Initialize turbo.js
        # https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask
        self.turbo = Turbo(self.native_app)

        # Initialize flask-session after all settings are applied
        # FIXME:
        #   flask-session is commented out due to error on flask-admin with
        #   missing secret_key of the application
        # self.flask_session = Session(self.native_app)
        self._flush_redis_session_database()

        self._before_request_func = before_request_func
        self._before_first_request_func = before_first_request_func
        self._ctx_processor_func = ctx_processor_func
        if after_request_func:
            self._after_request_func = after_request_func
        else:
            self._after_request_func = self._handle_after_request_default

        self._init_app_daemons()

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def mode(self) -> str:
        return self._mode_enum.value

    @property
    def root_dir(self) -> str:
        return self._root_dir

    @property
    def test_client(self) -> FlaskClient:
        return self.native_app.test_client()

    def _handle_after_request_default(self, response: Response) -> Response:
        """Log all responses
        """
        # This line should be exactly here, at the top of the after_request
        # function in order to work properly on flask-admin, but i don't know
        # why it works this way
        # https://github.com/closeio/Flask-gzip/issues/7
        response.direct_passthrough = False

        # https://gist.github.com/alexaleluia12/e40f1dfa4ce598c2e958611f67d28966
        log_func: Callable

        # All request-related data will be populated in log layer, so here work
        # only with response
        _log = log.logger.bind(
            http_response_headers=dict(response.headers),
            http_response_status_code=response.status_code,
            http_response_mime_type=response.mimetype,
            http_response_body_content=response.get_data(as_text=True)
        )

        if response.status_code < 400:
            log_func = _log.info
        else:
            log_func = _log.exception

        log_func(f'{request.method} {request.path} - {response}')
        
        return response

    def _assign_defaults_to_config(self, config: dict) -> None:
        if 'TEMPLATE_DIR' not in config:
            config['TEMPLATE_DIR'] = self.DEFAULT_TEMPLATE_DIR
        if 'STATIC_DIR' not in config:
            config['STATIC_DIR'] = self.DEFAULT_STATIC_DIR
        if 'INSTANCE_DIR' not in config:
            config['INSTANCE_DIR'] = self.DEFAULT_INSTANCE_DIR

    def _validate_config(self, config: dict) -> None:
        """Check if all keys in the config are correct."""
        # TODO
        pass

    def _make_upper_keys(self, mapping: dict) -> dict:
        rmap = {}
        for k, v in mapping.items():
            rmap[k.upper()] = v
        return rmap
    
    def _enable_cors(self, config: dict) -> None:
        # Enable CORS for the app's resources.
        is_cors_enabled = config.get("IS_CORS_ENABLED", None)
        if is_cors_enabled:
            CORS(self.native_app)

    def _flush_redis_session_database(self) -> None:
        # Flush redis session database if mode is not `prod`. 
        if self._mode_enum is not RunAppModeEnum.PROD: 
            if self.native_app.config.get("SESSION_TYPE", None):
                if self.native_app.config["SESSION_TYPE"] == "redis":
                    log.info(
                        "Flush session redis Database because"
                        " of non-production run.")
                    session_interface = self.native_app.session_interface
                    redis = session_interface.redis  # type: ignore
                    redis.flushdatabase()
            else:
                # Apply default null interface, basically do nothing.
                pass
    
    def _add_random_hex_token_to_config(self) -> None:
        # Generate random hex token for App's secret key, if not given in
        # config.
        if self.native_app.config["SECRET_KEY"] is None:
            secret_key: str = secrets.token_hex(16)
            self.native_app.config["SECRET_KEY"] = secret_key
            
    def _enable_testing_config(self, config: dict) -> None:
        # Enable testing if appropriate mode has been set. Do not rely on enum
        # if given config explicitly sets TESTING.
        if config.get("TESTING", None) is None:
            if self._mode_enum is RunAppModeEnum.TEST:
                self.native_app.config["TESTING"] = True
            else:
                self.native_app.config["TESTING"] = False
        else:
            self.native_app.config["TESTING"] = config["TESTING"]

    def _spawn_native_app(self, config: dict) -> Flask:
        # Set Flask environs according to given mode.
        # Setting exactly through environs instead of config recommended by
        # Flask creators.
        # https://flask.palletsprojects.com/en/2.0.x/config/#:~:text=Using%20the%20environment,a%20previous%20value.
        #
        if self._mode_enum not in [RunAppModeEnum.DEV, RunAppModeEnum.TEST]:
            os.environ["FLASK_DEBUG"] = '0'
        else:
            os.environ["FLASK_DEBUG"] = '1'

        return Flask(
            __name__, 
            instance_path=self.INSTANCE_DIR, 
            template_folder=self.TEMPLATE_DIR, 
            static_folder=self.STATIC_DIR
        )

    def get_secret_key(self) -> str:
        """Return secret key defined in App's config."""
        return self.native_app.config["SECRET_KEY"]

    def get_url(self) -> str:
        """Return app's url.

        Hostname may be e.g. `http://127.0.0.1:5000/`.

        Warning:
            Has url resolving issues described in issue #6.
        """
        return "http://" + self.host + ":" + str(self.port) + "/"

    def get_native_app(self) -> Flask:
        """Return native app."""
        return self.native_app

    def get_instance_path(self) -> str:
        """Return app's instance path."""
        return self.native_app.instance_path

    def run(self) -> None:
        """Run Flask app."""
        self.native_app.run(
            host=self.host, port=self.port)

    def app_context(self) -> AppContext:
        return self.native_app.app_context()

    def test_request_context(self) -> RequestContext:
        return self.native_app.test_request_context()

    def register_view(
            self, view_class: type[View],
            _is_self_test: bool = False
            ) -> None:
        """Register given view class for the app."""
        endpoint: str
        methods: list[str]

        if view_class.ENDPOINT:
            endpoint = view_class.ENDPOINT
        else:
            endpoint = view_class.get_transformed_route()

        methods = view_class.METHODS

        validation.validate(endpoint, str)

        view_func = view_class.as_view(endpoint)

        try:
            self.native_app.add_url_rule(
                view_class.ROUTE, view_func=view_func,
                methods=methods)
        except AssertionError as error:
            if not _is_self_test:
                raise AppError(*error.args)

    def register_error(
            self,
            error_class: type[Exception],
            handler_function: Callable) -> None:
        self.native_app.register_error_handler(error_class, handler_function)

    def push_turbo(
            self,
            action: TurboActionEnum,
            target: str,
            template_path: str,
            ctx_data: dict = {}
        ) -> None:
        """Push turbo action to target with rendered from path template
        contextualized with given data.
        
        Args:
            action:
                Turbo-Flask action to perform.
            target:
                Id of HTML element to push action to.
            template_path:
                Path to template to render.
            ctx_data (optional):
                Context data to push to rendered template.
                Defaults to empty dict.
        """
        with self.native_app.app_context():
            action = action.value
            target = target
            template_path = template_path
            ctx_data = ctx_data
            exec(
                f"self.turbo.push(self.turbo.{action}"
                "(render_template("
                f"'{template_path}', **{ctx_data}), '{target}'))")

    def postbuild(self) -> None:
        """Abstract method to perform post-injection operation related to app. 
        
        Called by Assembler.

        WARNING:
            This method not working as intended now (runs not actually after
            app starting), so better to not use it temporary.
        
        Raise:
            NotImplementedError:
                If not re-implemented in children.
        """
        raise NotImplementedError(
            "Method `postbuild` hasn't been reimplemented.")

    def register_cli_cmd(self, *cmds: Callable) -> None:
        """Register cli cmds for the app."""
        # TODO: Implement.
        raise NotImplementedError("CLI cmds support in development.")
        # for cmd in cmds:
        #     self.native_app.cli.add_command(cmd)

    def register_shell_processor(self, *shell_processors: Callable) -> None:
        """Register shell processors for the app."""
        for processor in shell_processors:
            self.native_app.shell_context_processor(processor)

    def run_shell(self) -> None:
        """Adapted version of ``Flask.cli.shell_command`` by Pallets.

        Run an interactive Python shell in the context of a given
        Flask application.  The application will populate the default
        namespace of this shell according to its configuration.

        This is useful for executing small snippets of management code
        without having to manually setup the application.
        """
        banner = (
            f"Python {sys.version} on {sys.platform}\n"
            f"App: {self.native_app.import_name} [{self.native_app.env}]\n"
            f"Instance: {self.native_app.instance_path}"
        )
        ctx: dict = {}

        # Support the regular Python interpreter startup script if someone
        # is using it.
        startup = os.environ.get("PYTHONSTARTUP")
        if startup and os.path.isfile(startup):
            with open(startup) as f:
                eval(compile(f.read(), startup, "exec"), ctx)

        ctx.update(self.native_app.make_shell_context())

        # Site, customize, or startup script can set a hook to call when
        # entering interactive mode. The default one sets up readline with
        # tab and history completion.
        interactive_hook = getattr(sys, "__interactivehook__", None)

        if interactive_hook is not None:
            try:
                import readline
                from rlcompleter import Completer
            except ImportError:
                pass
            else:
                # rlcompleter uses __main__.__dict__ by default, which is
                # flask.__main__. Use the shell context instead.
                readline.set_completer(Completer(ctx).complete)

            interactive_hook()

        code.interact(banner=banner, local=ctx)

    def _init_app_daemons(self) -> None:
        if self._ctx_processor_func:
            self._ctx_processor_func = self.native_app.context_processor(
                self._ctx_processor_func)

        if self._before_request_func:
            self._before_request_func = self.native_app.before_request(
                self._before_request_func
            )

        if self._before_first_request_func:
            self._before_first_request_func = \
                self.native_app.before_first_request(
                    self._before_first_request_func
                )

        if self._after_request_func:
            self._after_request_func = self.native_app.after_request(
                self._after_request_func
            )
