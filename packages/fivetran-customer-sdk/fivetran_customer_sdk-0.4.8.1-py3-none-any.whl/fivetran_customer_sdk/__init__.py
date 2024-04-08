import argparse
import docker
import grpc
import importlib.util
import inspect
import json
import os
import requests as rq
import sys

from concurrent import futures
from datetime import datetime
from docker.types import Mount
from google.protobuf import timestamp_pb2

from fivetran_customer_sdk.protos import common_pb2
from fivetran_customer_sdk.protos import connector_sdk_pb2
from fivetran_customer_sdk.protos import connector_sdk_pb2_grpc

TESTER_IMAGE_NAME = "fivetrandocker/sdk-connector-tester"
TESTER_IMAGE_VERSION = "024.0408.001"
TESTER_CONTAINER_NAME = "fivetran_connector_tester"

BUILDER_IMAGE_NAME = "fivetrandocker/customer-sdk-binary-builder"
BUILDER_IMAGE_VERSION = "024.0304.002"
BUILDER_CONTAINER_NAME = "fivetran_binary_builder"

DEBUGGING = False
TABLES = {}


class Operations:
    @staticmethod
    def upsert(table: str, data: dict) -> list[connector_sdk_pb2.UpdateResponse]:
        _yield_check(inspect.stack())

        responses = []

        columns = _get_columns(table)
        if not columns:
            global TABLES
            for field in data.keys():
                columns[field] = common_pb2.Column(
                    name=field, type=common_pb2.DataType.UNSPECIFIED, primary_key=True)
            new_table = common_pb2.Table(name=table, columns=columns.values())
            TABLES[table] = new_table

            responses.append(connector_sdk_pb2.UpdateResponse(
                operation=connector_sdk_pb2.Operation(
                    schema_change=connector_sdk_pb2.SchemaChange(
                        without_schema=common_pb2.TableList(tables=[new_table])))))

        mapped_data = _map_data_to_columns(data, columns)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.OpType.UPSERT,
            data=mapped_data
        )

        responses.append(
            connector_sdk_pb2.UpdateResponse(
                operation=connector_sdk_pb2.Operation(record=record)))

        return responses

    @staticmethod
    def update(table: str, modified: dict) -> connector_sdk_pb2.UpdateResponse:
        _yield_check(inspect.stack())

        columns = _get_columns(table)
        mapped_data = _map_data_to_columns(modified, columns)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.OpType.UPDATE,
            data=mapped_data
        )

        return connector_sdk_pb2.UpdateResponse(
            operation=connector_sdk_pb2.Operation(record=record))

    @staticmethod
    def delete(table: str, keys: dict) -> connector_sdk_pb2.UpdateResponse:
        _yield_check(inspect.stack())

        columns = _get_columns(table)
        mapped_data = _map_data_to_columns(keys, columns)
        record = connector_sdk_pb2.Record(
            schema_name=None,
            table_name=table,
            type=common_pb2.OpType.DELETE,
            data=mapped_data
        )

        return connector_sdk_pb2.UpdateResponse(
            operation=connector_sdk_pb2.Operation(record=record))


    @staticmethod
    def checkpoint(state: dict) -> connector_sdk_pb2.UpdateResponse:
        _yield_check(inspect.stack())
        return connector_sdk_pb2.UpdateResponse(
                 operation=connector_sdk_pb2.Operation(checkpoint=connector_sdk_pb2.Checkpoint(
                     state_json=json.dumps(state))))


def _get_columns(table: str) -> dict:
    columns = {}
    if table in TABLES:
        for column in TABLES[table].columns:
            columns[column.name] = column

    return columns


def _map_data_to_columns(data: dict, columns: dict) -> dict:
    mapped_data = {}
    for k, v in data.items():
        if v is None:
            mapped_data[k] = common_pb2.ValueType(null=True)
        elif isinstance(v, list):
            raise ValueError("Value type cannot be list")
        elif (k in columns) and columns[k].type != common_pb2.DataType.UNSPECIFIED:
            if columns[k].type == common_pb2.DataType.BOOLEAN:
                mapped_data[k] = common_pb2.ValueType(bool=v)
            elif columns[k].type == common_pb2.DataType.SHORT:
                mapped_data[k] = common_pb2.ValueType(short=v)
            elif columns[k].type ==  common_pb2.DataType.INT:
                mapped_data[k] = common_pb2.ValueType(int=v)
            elif columns[k].type ==  common_pb2.DataType.LONG:
                mapped_data[k] = common_pb2.ValueType(long=v)
            elif columns[k].type ==  common_pb2.DataType.DECIMAL:
                mapped_data[k] = common_pb2.ValueType(decimal=v)
            elif columns[k].type ==  common_pb2.DataType.FLOAT:
                mapped_data[k] = common_pb2.ValueType(float=v)
            elif columns[k].type ==  common_pb2.DataType.DOUBLE:
                mapped_data[k] = common_pb2.ValueType(double=v)
            elif columns[k].type ==  common_pb2.DataType.NAIVE_DATE:
                timestamp = timestamp_pb2.Timestamp()
                dt = datetime.strptime(v, "%Y-%m-%d")
                timestamp.FromDatetime(dt)
                mapped_data[k] = common_pb2.ValueType(naive_date=timestamp)
            elif columns[k].type ==  common_pb2.DataType.NAIVE_DATETIME:
                if '.' not in v: v = v + ".0"
                timestamp = timestamp_pb2.Timestamp()
                dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
                timestamp.FromDatetime(dt)
                mapped_data[k] = common_pb2.ValueType(naive_datetime=timestamp)
            elif columns[k].type ==  common_pb2.DataType.UTC_DATETIME:
                timestamp = timestamp_pb2.Timestamp()
                if '.' in v:
                    dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f%z")
                else:
                    dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S%z")
                timestamp.FromDatetime(dt)
                mapped_data[k] = common_pb2.ValueType(utc_datetime=timestamp)
            elif columns[k].type ==  common_pb2.DataType.BINARY:
                mapped_data[k] = common_pb2.ValueType(binary=v)
            elif columns[k].type ==  common_pb2.DataType.XML:
                mapped_data[k] = common_pb2.ValueType(xml=v)
            elif columns[k].type ==  common_pb2.DataType.STRING:
                incoming = v if isinstance(v, str) else str(v)
                mapped_data[k] = common_pb2.ValueType(string=incoming)
            elif columns[k].type ==  common_pb2.DataType.JSON:
                mapped_data[k] = common_pb2.ValueType(json=json.dumps(v))
            else:
                raise ValueError(f"Unknown data type: {columns[k].type}")
        else:
            # We can infer type from the value
            if isinstance(v, int):
                if abs(v) > 2147483647:
                    mapped_data[k] = common_pb2.ValueType(long=v)
                else:
                    mapped_data[k] = common_pb2.ValueType(int=v)
            elif isinstance(v, float):
                mapped_data[k] = common_pb2.ValueType(float=v)
            elif isinstance(v, bool):
                mapped_data[k] = common_pb2.ValueType(bool=v)
            elif isinstance(v, bytes):
                mapped_data[k] = common_pb2.ValueType(binary=v)
            elif isinstance(v, list):
                raise ValueError("Value type cannot be list")
            elif isinstance(v, dict):
                mapped_data[k] = common_pb2.ValueType(json=json.dumps(v))
            elif isinstance(v, str):
                mapped_data[k] = common_pb2.ValueType(string=v)
            else:
                # Convert arbitrary objects to string
                mapped_data[k] = common_pb2.ValueType(string=str(v))

    return mapped_data


def _yield_check(stack):
    # Known issue with inspect.getmodule() and yield behavior in a frozen application.
    # When using inspect.getmodule() on stack frames obtained by inspect.stack(), it fails
    # to resolve the modules in a frozen application due to incompatible assumptions about
    # the file paths. This can lead to unexpected behavior, such as yield returning None or
    # the failure to retrieve the module inside a frozen app
    # (Reference: https://github.com/pyinstaller/pyinstaller/issues/5963)
    if not DEBUGGING:
        return

    called_method = stack[0].function
    calling_code = stack[1].code_context[0]
    if f"{called_method}(" in calling_code:
        if 'yield' not in calling_code:
            print(f"ERROR: Please add 'yield' to '{called_method}' operation on line {stack[1].lineno} in file '{stack[1].filename}'")
            os._exit(1)
    else:
        # This should never happen
        raise RuntimeError(f"Unable to find '{called_method}' function in stack")


def _check_dict(incoming: dict, string_only: bool = False):
    if not incoming:
        return {}

    if not isinstance(incoming, dict):
        raise ValueError("Configuration should be a dictionary")

    if string_only:
        for k, v in incoming.items():
            if not isinstance(v, str):
                print("ERROR: Use only string values in configuration")
                os._exit(1)

    return incoming


class Connector(connector_sdk_pb2_grpc.ConnectorServicer):
    def __init__(self, update, schema=None):
        self.schema_method = schema
        self.update_method = update

        self.configuration = None
        self.state = None

    # Call this method to deploy the connector to Fivetran platform
    def deploy(self, project_path: str, deploy_key: str, group: str, connection: str, configuration: dict = None):
        if not deploy_key: print("ERROR: Missing deploy key"); os._exit(1)
        if not connection: print("ERROR: Missing connection name"); os._exit(1)
        _check_dict(configuration)

        secrets_list = []
        for k, v in configuration.items():
            secrets_list.append({"key": k, "value": v})

        connection_config = {
            "schema": connection,
            "secrets_list": secrets_list,
            "sync_method": "DIRECT",
            "custom_payloads": [],
        }
        group_id, group_name = self.__get_group_info(group, deploy_key)
        print(f"Deploying '{project_path}' to '{group_name}/{connection}'")
        self.__write_run_py(project_path)
        # TODO: we need to do this step on the server (upload code instead)
        self.__create_standalone_binary(project_path)
        upload_file_path = os.path.join(project_path, "dist", "__run")
        if not self.__upload(upload_file_path, deploy_key,group_id,connection):
            os._exit(1)
        connection_id = self.__get_connection_id(connection, group, group_id, deploy_key)
        if connection_id:
            print(f"Connection '{connection}' already exists in group '{group}', updating configuration .. ", end="", flush=True)
            self.__update_connection(connection_id, connection, group_name, connection_config, deploy_key)
            self.__force_sync(connection_id, connection, deploy_key)
            print("✓")
        else:
            response = self.__create_connection(deploy_key, group_id, connection_config)
            if response.ok:
                print(f"New connection with name '{connection}' created")
            else:
                print(f"ERROR: Failed to create new connection: {response.json()['message']}")
                os._exit(1)

    @staticmethod
    def __force_sync(id: str, name: str, deploy_key: str):
        resp = rq.post(f"https://api.fivetran.com/v1/connectors/{id}/sync",
                       headers={"Authorization": f"Basic {deploy_key}"},
                       json={"force": True})

        if not resp.ok:
            print(f"WARNING: Unable to start sync on connection '{name}'")

    @staticmethod
    def __update_connection(id: str, name: str, group: str, config: dict, deploy_key: str):
        resp = rq.patch(f"https://api.fivetran.com/v1/connectors/{id}",
                        headers={"Authorization": f"Basic {deploy_key}"},
                        json={
                                "config": config,
                                "run_setup_tests": True
                        })

        if not resp.ok:
            print(f"ERROR: Unable to update connection '{name}' in group '{group}'")
            os._exit(1)

    @staticmethod
    def __get_connection_id(name: str, group: str, group_id: str, deploy_key: str):
        resp = rq.get(f"https://api.fivetran.com/v1/groups/{group_id}/connectors",
                      headers={"Authorization": f"Basic {deploy_key}"},
                      params={"schema": name})
        if not resp.ok:
            print(f"ERROR: Unable to fetch connection list in group '{group}'")
            os._exit(1)

        if resp.json()['data']['items']:
            return resp.json()['data']['items'][0]['id']

        return None

    @staticmethod
    def __create_connection(deploy_key: str, group_id: str, config: dict):
        response = rq.post(f"https://api.fivetran.com/v1/connectors",
                           headers={"Authorization": f"Basic {deploy_key}"},
                           json={
                                 "group_id": group_id,
                                 "service": "my_built",
                                 "config": config,
                                 "paused": False,
                                 "run_setup_tests": True,
                                 "sync_frequency": "360",
                           })
        return response

    @staticmethod
    def __create_standalone_binary(project_path: str):
        print("Preparing artifacts ..")
        print("1 of 4 .. ", end="", flush=True)
        docker_client = docker.from_env()
        image = f"{BUILDER_IMAGE_NAME}:{BUILDER_IMAGE_VERSION}"
        result = docker_client.images.list(image)
        if not result:
            # Pull the builder image if missing
            docker_client.images.pull(BUILDER_IMAGE_NAME, BUILDER_IMAGE_VERSION, platform="linux/amd64")

        for container in docker_client.containers.list(all=True):
            if container.name == BUILDER_CONTAINER_NAME:
                if container.status == "running":
                    print("ERROR: Another deploy process is running")
                    os._exit(1)

        container = None
        try:
            # TODO: Check responses in each step and look for "success" phrases
            container = docker_client.containers.run(
                image=image,
                name=BUILDER_CONTAINER_NAME,
                command="/bin/sh",
                mounts=[Mount("/myapp", project_path, read_only=False, type="bind")],
                tty=True,
                detach=True,
                working_dir="/myapp",
                remove=True)
            print("✓")

            print("2 of 4 .. ", end="", flush=True)
            resp = container.exec_run("pip install fivetran_customer_sdk")
            print("✓")

            print("3 of 4 .. ", end="", flush=True)
            if os.path.isfile(os.path.join(project_path, "requirements.txt")):
                resp = container.exec_run("pip install -r requirements.txt")
            print("✓")

            print("4 of 4 .. ", end="", flush=True)
            resp = container.exec_run("rm __run")
            resp = container.exec_run("pyinstaller --onefile --clean __run.py")
            print("✓")

            if not os.path.isfile(os.path.join(project_path, "dist", "__run")):
                print("Failed to create deployment file")
                os._exit(1)

        finally:
            if container:
                container.stop()

    @staticmethod
    def __upload(local_path: str, deploy_key: str, group_id: str, connection: str) -> bool:
        print("Uploading .. ", end="", flush=True)
        response = rq.post(f"https://api.fivetran.com/v2/deploy/{group_id}/{connection}",
                           files={'file': open(local_path, 'rb')},
                           headers={"Authorization": f"Basic {deploy_key}"})
        if response.ok:
            print("✓")
            return True

        print("fail\nERROR: ", response.reason)
        return False

    @staticmethod
    def __write_run_py(project_path: str):
        with open(os.path.join(project_path, "__run.py"), "w") as fo:
            fo.writelines([
                "import sys\n",
                "from connector import connector\n",
                "if len(sys.argv) == 3 and sys.argv[1] == '--port':\n",
                "   server = connector.run(port=int(sys.argv[2]))\n",
                "else:\n",
                "   server = connector.run()\n"
            ])

    @staticmethod
    def __get_group_info(group: str, deploy_key: str) -> tuple[str, str]:
        resp = rq.get("https://api.fivetran.com/v1/groups",
                      headers={"Authorization": f"Basic {deploy_key}"})

        if not resp.ok:
            print(f"ERROR: Unable to fetch list of groups, status code = {resp.status_code}")
            os._exit(1)

        # TODO: Do we need to implement pagination?
        groups = resp.json()['data']['items']
        if not groups:
            print("ERROR: No destinations defined in the account")
            os._exit(1)

        if len(groups) == 1:
            return groups[0]['id'], groups[0]['name']
        else:
            if not group:
                print("ERROR: Group name is required when there are multiple destinations in the account")
                os._exit(1)

            for grp in groups:
                if grp['name'] == group:
                    return grp['id'], grp['name']

        print(f"ERROR: Specified group was not found in the account: {group}")
        os._exit(1)

    # Call this method to run the connector in production
    def run(self, port: int = 50051, configuration: dict = None, state: dict = None) -> grpc.Server:
        global DEBUGGING

        self.configuration = _check_dict(configuration, True)
        self.state = _check_dict(state)

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        connector_sdk_pb2_grpc.add_ConnectorServicer_to_server(self, server)
        server.add_insecure_port("[::]:" + str(port))
        server.start()
        print("Connector started, listening on " + str(port))
        if DEBUGGING:
            return server
        server.wait_for_termination()

    # This method starts both the server and the local testing environment
    def debug(self, project_path: str = None, port: int = 50051, configuration: dict = None, state: dict = None) -> bool:
        global DEBUGGING
        DEBUGGING = True

        project_path = os.getcwd() if project_path is None else project_path
        print(f"Debugging connector: {project_path}")
        server = self.run(port, configuration, state)

        # Uncomment this to run the tester manually
        #server.wait_for_termination()

        docker_client = docker.from_env()
        image = f"{TESTER_IMAGE_NAME}:{TESTER_IMAGE_VERSION}"
        result = docker_client.images.list(image)
        # Pull the tester image if missing
        if not result:
            print(f"Downloading connector tester {TESTER_IMAGE_VERSION} .. ", end="", flush=True)
            docker_client.images.pull(TESTER_IMAGE_NAME, TESTER_IMAGE_VERSION, platform="linux/amd64")
            print("✓")

        error = False
        try:
            for container in docker_client.containers.list(all=True):
                if container.name == TESTER_CONTAINER_NAME:
                    if container.status == "running":
                        container.stop()
                    else:
                        container.remove()
                    break

            working_dir = os.path.join(project_path, "files")
            try:
                os.mkdir(working_dir)
            except FileExistsError:
                pass

            container = docker_client.containers.run(
                image=image,
                name=TESTER_CONTAINER_NAME,
                command="--connector-sdk=true",
                mounts=[Mount("/data", working_dir, read_only=False, type="bind")],
                network="host",
                remove=True,
                detach=True,
                environment=["GRPC_HOSTNAME=host.docker.internal"])

            for line in container.attach(stdout=True, stderr=True, stream=True):
                msg = line.decode("utf-8")
                print(msg, end="")
                if ("Exception in thread" in msg) or ("SEVERE:" in msg):
                    error = True

        finally:
            server.stop(grace=2.0)
            return not error

    # -- Methods below override ConnectorServicer methods
    def ConfigurationForm(self, request, context):
        if not self.configuration:
            self.configuration = {}

        # Not going to use the tester's configuration file
        return common_pb2.ConfigurationFormResponse()

    def Test(self, request, context):
        return None

    def Schema(self, request, context):
        global TABLES

        if not self.schema_method:
            return connector_sdk_pb2.SchemaResponse(schema_response_not_supported=True)
        else:
            configuration = self.configuration if self.configuration else request.configuration
            response = self.schema_method(configuration)

            for entry in response:
                if 'table' not in entry:
                    raise ValueError("Entry missing table name: " + entry)

                table_name = entry['table']

                if table_name in TABLES:
                    raise ValueError("Table already defined: " + table_name)

                table = common_pb2.Table(name=table_name)
                columns = {}

                if "primary_key" not in entry:
                    ValueError("Table requires at least one primary key: " + table_name)

                for pkey_name in entry["primary_key"]:
                    column = columns[pkey_name] if pkey_name in columns else common_pb2.Column(name=pkey_name)
                    column.primary_key = True
                    columns[pkey_name] = column

                if "columns" in entry:
                    for name, type in entry["columns"].items():
                        column = columns[name] if name in columns else common_pb2.Column(name=name)

                        if isinstance(type, str):
                            if type.upper() == "BOOLEAN":
                                column.type = common_pb2.DataType.BOOLEAN
                            elif type.upper() == "SHORT":
                                column.type = common_pb2.DataType.SHORT
                            elif type.upper() == "LONG":
                                column.type = common_pb2.DataType.LONG
                            elif type.upper() == "FLOAT":
                                column.type = common_pb2.DataType.FLOAT
                            elif type.upper() == "DOUBLE":
                                column.type = common_pb2.DataType.DOUBLE
                            elif type.upper() == "NAIVE_DATE":
                                column.type = common_pb2.DataType.NAIVE_DATE
                            elif type.upper() == "NAIVE_DATETIME":
                                column.type = common_pb2.DataType.NAIVE_DATETIME
                            elif type.upper() == "UTC_DATETIME":
                                column.type = common_pb2.DataType.UTC_DATETIME
                            elif type.upper() == "BINARY":
                                column.type = common_pb2.DataType.BINARY
                            elif type.upper() == "XML":
                                column.type = common_pb2.DataType.XML
                            elif type.upper() == "STRING":
                                column.type = common_pb2.DataType.STRING
                            elif type.upper() == "JSON":
                                column.type = common_pb2.DataType.JSON
                            else:
                                raise ValueError("Unrecognized column type: ", str(type))

                        elif isinstance(type, dict):
                            if type['type'].upper() != "DECIMAL":
                                raise ValueError("Expecting DECIMAL data type")
                            column.type = common_pb2.DataType.DECIMAL
                            column.decimal.precision = type['precision']
                            column.decimal.scale = type['scale']

                        else:
                            raise ValueError("Unrecognized column type: ", str(type))

                        if name in entry["primary_key"]:
                            column.primary_key = True

                        columns[name] = column

                table.columns.extend(columns.values())
                TABLES[table_name] = table

            return connector_sdk_pb2.SchemaResponse(without_schema=common_pb2.TableList(tables=TABLES.values()))

    def Update(self, request, context):
        configuration = self.configuration if self.configuration else request.configuration
        state = self.state if self.state else json.loads(request.state_json)

        try:
            for resp in self.update_method(configuration=configuration, state=state):
                if isinstance(resp, list):
                    for r in resp:
                        yield r
                else:
                    yield resp

        except TypeError as e:
            if str(e) != "'NoneType' object is not iterable":
                raise e


def find_connector_object(project_path):
    module_name = "customer_connector_code"
    connector_py = os.path.join(project_path, "connector.py")
    spec = importlib.util.spec_from_file_location(module_name, connector_py)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    for obj in dir(module):
        if not obj.startswith('__'):  # Exclude built-in attributes
            obj_attr = getattr(module, obj)
            if '<fivetran_customer_sdk.Connector object at' in str(obj_attr):
                return obj_attr

    print("Unable to find connector object")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(allow_abbrev=False)

    # Positional
    parser.add_argument("command", help="debug|run|deploy")
    parser.add_argument("project_path", nargs='?', default=os.getcwd(), help="Path to connector project directory")

    # Optional (Not all of these are valid with every mutually exclusive option below)
    parser.add_argument("--port", type=int, default=None, help="Provide port number to run gRPC server")
    parser.add_argument("--state", type=str, default=None, help="Provide state as JSON string or file")
    parser.add_argument("--configuration", type=str, default=None, help="Provide secrets as JSON string or file")
    parser.add_argument("--deploy-key", type=str, default=None, help="Provide deploy key")
    parser.add_argument("--group", type=str, default=None, help="Group name of the destination")
    parser.add_argument("--connection", type=str, default=None, help="Connection name (aka 'destination schema')")

    args = parser.parse_args()

    connector_object = find_connector_object(args.project_path)

    # Process optional args
    ft_group = args.group if args.group else os.getenv('GROUP', None)
    ft_connection = args.connection if args.connection else os.getenv('CONNECTION', None)
    deploy_key = args.deploy_key if args.deploy_key else os.getenv('DEPLOY_KEY', None)
    configuration = args.configuration if args.configuration else os.getenv('CONFIGURATION', None)
    state = args.state if args.state else os.getenv('STATE', None)

    if configuration:
        json_filepath = os.path.join(args.project_path, args.configuration)
        if os.path.isfile(json_filepath):
            with open(json_filepath, 'r') as fi:
                configuration = json.load(fi)
        else:
            if configuration.lstrip().startswith("{"):
                configuration = json.loads(configuration)
            else:
                raise ValueError("Unrecognized format for configuration")
    else:
        configuration = {}

    if state:
        json_filepath = os.path.join(args.project_path, args.state)
        if os.path.isfile(json_filepath):
            with open(json_filepath, 'r') as fi:
                state = json.load(fi)
        elif state.lstrip().startswith("{"):
            state = json.loads(state)
    else:
        state = {}

    if args.command.lower() == "deploy":
        if args.port:
            print("WARNING: 'port' parameter is not used for 'deploy' command")
        if args.state:
            print("WARNING: 'state' parameter is not used for 'deploy' command")
        connector_object.deploy(args.project_path, deploy_key, ft_group, ft_connection, configuration)

    elif args.command.lower() == "debug":
        port = 50051 if not args.port else args.port
        connector_object.debug(args.project_path, port, configuration, state)

    elif args.command.lower() == "run":
        port = 50051 if not args.port else args.port
        connector_object.run(port, configuration, state)

    else:
        raise NotImplementedError("Invalid command: ", args.command)


if __name__ == "__main__":
    main()
