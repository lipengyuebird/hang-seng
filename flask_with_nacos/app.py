import threading
import time
from typing import Union
from configparser import ConfigParser

import nacos.exception

from flask import Flask
from flask.helpers import *
from flask.scaffold import *
from flask import cli

from nacos import NacosClient

from .exceptions import *


class FlaskWithNacos(Flask):
    _config_file_attrs = ['.py', '.conf', '.cfg']
    data_id_list = []

    def __init__(
            self,
            import_name: str,
            nacos_server: str,
            nacos_namespace: str,
            config_file: Optional[str] = 'app_config.py',
            static_url_path: Optional[str] = None,
            static_folder: Optional[Union[str, os.PathLike]] = "static",
            static_host: Optional[str] = None,
            host_matching: bool = False,
            subdomain_matching: bool = False,
            template_folder: Optional[str] = "templates",
            instance_path: Optional[str] = None,
            instance_relative_config: bool = False,
            root_path: Optional[str] = None,
    ):
        super().__init__(
            import_name,
            static_url_path,
            static_folder,
            static_host,
            host_matching,
            subdomain_matching,
            template_folder,
            instance_path,
            instance_relative_config,
            root_path,
        )

        self.port = None
        self.host = None
        self.nacos_service_name = self.import_name.replace("_", "-")

        config_file_type = '.py'

        if not config_file:
            for attr in self._config_file_attrs:
                if ('app_config' + attr) in os.listdir(find_package(os.getenv('FLASK_APP'))[1]):
                    config_file = 'app_config' + attr
                    config_file_type = attr
                    break

        if not config_file:
            raise ConfigFileException(
                'Config file name is not specified '
                'and none of '.join([f'"app_config{attr}" ' for attr in self._config_file_attrs]) +
                'is found in the app root.'
            )

        self.nacos_client = NacosClient(nacos_server, namespace=nacos_namespace)

        if '.py' == config_file_type:
            self.config.from_mapping(self._load_config_from_py(config_file))
        else:
            self.config.from_mapping(self._load_config_from_conf(config_file))

    def __del__(self):
        self.nacos_client.remove_naming_instance(self.nacos_service_name, self.host, self.port,
                                                 cluster_name='DEFAULT', ephemeral=True)

    def run(
        self,
        host: t.Optional[str] = None,
        port: t.Optional[int] = None,
        debug: t.Optional[bool] = None,
        load_dotenv: bool = True,
        **options: t.Any,
    ) -> None:

        if os.environ.get("FLASK_RUN_FROM_CLI") == "true":
            from flask.debughelpers import explain_ignored_app_run

            explain_ignored_app_run()
            return

        if get_load_dotenv(load_dotenv):
            cli.load_dotenv()

            # if set, let env vars override previous values
            if "FLASK_ENV" in os.environ:
                self.env = get_env()
                self.debug = get_debug_flag()
            elif "FLASK_DEBUG" in os.environ:
                self.debug = get_debug_flag()

        # debug passed to method overrides all other sources
        if debug is not None:
            self.debug = bool(debug)

        server_name = self.config.get("SERVER_NAME")
        sn_host = sn_port = None

        if server_name:
            sn_host, _, sn_port = server_name.partition(":")

        if not host:
            if sn_host:
                host = sn_host
            else:
                host = "127.0.0.1"

        if port or port == 0:
            port = int(port)
        elif sn_port:
            port = int(sn_port)
        else:
            port = 5000

        options.setdefault("use_reloader", self.debug)
        options.setdefault("use_debugger", self.debug)
        options.setdefault("threaded", True)

        cli.show_server_banner(self.env, self.debug, self.name, False)

        self.host = host
        self.port = port

        self.nacos_client.add_naming_instance(self.nacos_service_name, host, port, cluster_name='DEFAULT', ephemeral=True)
        heartbeat_thread = threading.Thread(
            target=self._heartbeat_routine,
            args=(host, port, True)
        )
        heartbeat_thread.daemon = True
        heartbeat_thread.start()


        from werkzeug.serving import run_simple

        try:
            run_simple(t.cast(str, host), port, self, **options)
        finally:
            # reset the first request information if the development server
            # reset normally.  This makes it possible to restart the server
            # without reloader and that stuff from an interactive shell.
            self._got_first_request = False

    def _load_config_from_py(self, config_file: str):
        import sys
        sys.path.append(find_package(os.getenv('FLASK_APP'))[1])
        conf = __import__(config_file.replace('.py', ''))
        # conf_dict = {}
        attribute = eval(f'conf.{self.env}')
        for key in attribute.keys():
            if not attribute[key]:
                attribute[key] = self.nacos_client.get_config(key, 'DEFAULT_GROUP')
        # for group_name in dir(conf):
        #     attribute = eval(f'conf.{group_name}')
        #     if isinstance(attribute, dict):
        #         for key in attribute.keys():
        #             if not attribute[key]:
        #                 attribute[key] = self.nacos_client.get_config(key, snake_case(group_name))
        #         conf_dict = {**conf_dict, **attribute}
        return attribute

    def _load_config_from_conf(self, config_file: str):
        with open(os.path.join(find_package(os.getenv('FLASK_APP'))[1], config_file), 'r', encoding='utf-8') as fp:
            if not fp:
                raise ConfigFileException(f'Could not find config file: {config_file}')
            conf = ConfigParser()
            conf.read_file(fp)
            return {
                data_id: conf.get(group, data_id) if conf.get(group, data_id)
                else self.nacos_client.get_config(data_id, group)
                for group in conf.sections() for data_id in conf.options(group)
            }

    def _heartbeat_routine(self, host, port, ephemeral):
        while True:
            try:
                self.nacos_client.send_heartbeat(self.nacos_service_name, host, port, cluster_name='DEFAULT', ephemeral=ephemeral)
            except nacos.exception.NacosRequestException:
                pass
            finally:
                time.sleep(1)
