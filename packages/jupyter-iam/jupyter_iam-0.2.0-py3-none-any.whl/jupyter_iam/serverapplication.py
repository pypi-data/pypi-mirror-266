"""The Jupyter IAM Server application."""

import os

from traitlets import Unicode

from jupyter_server.utils import url_path_join
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin

from ._version import __version__

from .handlers.auth.handler import CallbackOAuth
from .handlers.index.handler import IndexHandler
from .handlers.config.handler import ConfigHandler
from .handlers.echo.handler import WsEchoHandler
from .handlers.relay.handler import WsRelayHandler
from .handlers.proxy.handler import WsProxyHandler
from .handlers.ping.handler import WsPingHandler


DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./static")

DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./templates")


class JupyterIamExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    """The Jupyter IAM Server extension."""

    name = "jupyter_iam"

    extension_url = "/jupyter_iam"

    load_other_extensions = True

    static_paths = [DEFAULT_STATIC_FILES_PATH]
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    config_a = Unicode("", config=True, help="Config A example.")
    config_b = Unicode("", config=True, help="Config B example.")
    config_c = Unicode("", config=True, help="Config C example.")

    def initialize_settings(self):
        self.log.debug("Jupyter IAM Config {}".format(self.config))

    def initialize_templates(self):
        self.serverapp.jinja_template_vars.update({"jupyter_iam_version" : __version__})

    def initialize_handlers(self):
        self.log.debug("Jupyter IAM Config {}".format(self.settings['jupyter_iam_jinja2_env']))
        handlers = [
            ("jupyter_iam", IndexHandler),
            (url_path_join("jupyter_iam", "config"), ConfigHandler),
            (url_path_join("jupyter_iam", "echo"), WsEchoHandler),
            (url_path_join("jupyter_iam", "relay"), WsRelayHandler),
            (url_path_join("jupyter_iam", "proxy"), WsProxyHandler),
            (url_path_join("jupyter_iam", "ping"), WsPingHandler),
            (url_path_join("jupyter_iam", "oauth", "callback"), CallbackOAuth),
        ]
        self.handlers.extend(handlers)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterIamExtensionApp.launch_instance
