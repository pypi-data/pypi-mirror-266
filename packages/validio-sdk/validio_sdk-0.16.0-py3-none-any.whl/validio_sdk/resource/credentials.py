"""Credentials configuration."""

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._resource_graph import RESOURCE_GRAPH
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    NODE_TYPE_FIELD_NAME,
    ImportValue,
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
    _import_resource_params,
    get_children_node,
    with_resource_graph_info,
)

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class Credential(Resource):
    """
    Base class for a credential resource.

    https://docs.validio.io/docs/credentials
    """

    def __init__(self, name: str, __internal__: ResourceGraph | None = None) -> None:
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        # Credentials are at the root sub-graphs.
        g: ResourceGraph = __internal__ or RESOURCE_GRAPH
        super().__init__(name, g)

        self._resource_graph: ResourceGraph = g
        self._resource_graph._add_root(self)

    @abstractmethod
    def _immutable_fields(self) -> set[str]:
        pass

    @abstractmethod
    def _mutable_fields(self) -> set[str]:
        pass

    @abstractmethod
    def _secret_fields(self) -> set[str] | None:
        pass

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Credential"

    def _encode(self) -> dict[str, object]:
        return _encode_resource(self)

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        g: ResourceGraph,
    ) -> "Credential":
        from validio_sdk.resource.sources import Source

        args: dict[str, Any] = obj[CONFIG_FIELD_NAME]

        # Some credentials wrap other credentials and if so they have a field
        # set with the name of the other credential. For those we need to pop
        # the name from the config field names and instead ensure we have
        # `warehouse_credential` set to the full object.
        warehouse_credential_name = args.pop("warehouse_credential_name", None)
        if warehouse_credential_name:
            args["warehouse_credential"] = ctx.credentials[warehouse_credential_name]

        credential = cls(**with_resource_graph_info(args, g))
        children_obj = cast(
            dict[str, dict[str, dict[str, Any]]], get_children_node(obj)
        )

        Credential._decode_children(ctx, children_obj, credential, Source, "sources")

        return credential

    @staticmethod
    def _decode_children(
        ctx: "DiffContext",
        children_obj: dict[str, dict[str, dict[str, object]]],
        credential: "Credential",
        resource_cls: type,
        resource_module: str,
    ) -> None:
        # We need to import the validio_sdk module due to the `eval`
        # ruff: noqa: F401
        import validio_sdk

        resources_obj = (
            children_obj[resource_cls.__name__]
            if resource_cls.__name__ in children_obj
            else {}
        )
        resources = {}
        for resource_name, value in resources_obj.items():
            cls = eval(
                f"validio_sdk.resource.{resource_module}.{value[NODE_TYPE_FIELD_NAME]}"
            )
            r = cast(Any, resource_cls)._decode(ctx, cls, value, credential)
            resources[resource_name] = r
            ctx.__getattribute__(resource_module)[resource_name] = r

        if len(resources) > 0:
            credential._children[resource_cls.__name__] = resources

    def _import_params(self) -> dict[str, ImportValue]:
        secret_fields = {
            field: ImportValue(value="UNSET", comment="FIXME: Add secret value")
            for field in (self._secret_fields() or set({}))
        }

        skip_fields = self._secret_fields() or set()

        # We always skip all fields suffixe with `_name` if they're a part of
        # our `DiffContext`. Since `warehouse_credential_name` is not a child
        # resource this is also not a part of the context. Instead we'll
        # manually have to skip this field.
        skip_fields.add("warehouse_credential_name")

        return {
            **_import_resource_params(resource=self, skip_fields=skip_fields),
            **secret_fields,
        }


class DemoCredential(Credential):
    """A demo credential resource."""

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return set({})

    def _secret_fields(self) -> set[str] | None:
        return None


class DbtCredential(Credential):
    """A dbt base class credential."""

    def __init__(
        self,
        name: str,
        warehouse_credential: "Credential",
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param warehouse_credential: A credential that has access to the
        resources
        """
        super().__init__(name, __internal__)
        self.warehouse_credential_name = warehouse_credential.name

    def _immutable_fields(self) -> set[str]:
        return set()

    def _secret_fields(self) -> set[str] | None:
        return set()

    def _api_create_input(self, namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            namespace=namespace,
            overrides={
                "warehouse_credential_id": ctx.credentials[
                    self.warehouse_credential_name
                ]._must_id(),
            },
        )

    def _api_update_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_update_input_params(
            self,
            overrides={
                "warehouse_credential_id": ctx.credentials[
                    self.warehouse_credential_name
                ]._must_id(),
            },
        )


class DbtCoreCredential(DbtCredential):
    """A dbt core credential."""

    def __init__(
        self,
        name: str,
        warehouse_credential: "Credential",
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param warehouse_credential: A credential that has access to the
        resources
        """
        super().__init__(name, warehouse_credential, __internal__)

    def _mutable_fields(self) -> set[str]:
        return {"warehouse_credential_name"}


class DbtCloudCredential(DbtCredential):
    """A dbt cloud credential."""

    def __init__(
        self,
        name: str,
        warehouse_credential: "Credential",
        account_id: str,
        token: str,
        api_base_url: str | None = None,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param warehouse_credential: A credential that has access to the
        resources
        :param accound_id: dbt cloud account id
        :param api_base_url: Base URL to access the dbt cloud instance
        """
        super().__init__(name, warehouse_credential, __internal__)
        self.account_id = account_id
        self.api_base_url = api_base_url
        self.token = token

    def _secret_fields(self) -> set[str] | None:
        return {"token"}

    def _mutable_fields(self) -> set[str]:
        return {"account_id", "api_base_url", "token", "warehouse_credential_name"}


class GcpCredential(Credential):
    """
    A credential resource that can be used to authenticate against
    Google Cloud Platform services.
    """

    def __init__(
        self,
        name: str,
        credential: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param credential: Service account JSON credential
        """
        super().__init__(name, __internal__)
        self.credential = credential

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return set({})

    def _secret_fields(self) -> set[str] | None:
        return {"credential"}


class AwsCredential(Credential):
    """A credential resource that can be used to authenticate against AWS services."""

    def __init__(
        self,
        name: str,
        access_key: str,
        secret_key: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param access_key: Access key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param secret_key: Secret key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        """
        super().__init__(name, __internal__)
        self.access_key = access_key
        self.secret_key = secret_key

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"access_key"}

    def _secret_fields(self) -> set[str] | None:
        return {"secret_key"}


class SnowflakeCredential(Credential):
    """A credential resource that can be used to connect to a Snowflake table."""

    def __init__(
        self,
        name: str,
        account: str,
        user: str,
        password: str,
        warehouse: str | None = None,
        role: str | None = None,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param account: Snowflake account identifier
        :param user: Username having read access to the desired table.
        :param password: Password of the specified user.
        :param warehouse: Snowflake virtual warehouse to use to run queries.
        :param role: Snowflake role to assume when running queries.
        """
        super().__init__(name, __internal__)
        self.account = account
        self.user = user
        self.password = password
        self.warehouse = warehouse
        self.role = role

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"account", "user", "warehouse", "role"}

    def _secret_fields(self) -> set[str] | None:
        return {"password"}


class PostgresLikeCredential(Credential):
    """
    A credential resource that can be used to connect to
    a Postgres-compatible table.
    """

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        user: str,
        password: str,
        default_database: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param host: DNS hostname or IP address at which to reach the database server.
        :param port: Port number of the database server.
        :param user: Username having read access to the desired table.
        :param password: Password of the specified user.
        :param default_database: Name of the default database to use this
            credential with. This can be overridden e.g. in a Source configuration.
        """
        super().__init__(name, __internal__)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.default_database = default_database

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"host", "port", "user", "default_database"}

    def _secret_fields(self) -> set[str] | None:
        return {"password"}


class PostgreSqlCredential(PostgresLikeCredential):
    """
    A credential resource that can be used to connect to a Postgres table.

    https://docs.validio.io/docs/postgresql
    """


class AwsRedshiftCredential(PostgresLikeCredential):
    """
    A credential resource that can be used to connect to a Redshift table.

    https://docs.validio.io/docs/redshift
    """


class AwsAthenaCredential(Credential):
    """Athena credential resource."""

    def __init__(
        self,
        name: str,
        access_key: str,
        secret_key: str,
        region: str,
        query_result_location: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param access_key: Access key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param secret_key: Secret key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param region: Region where the Athena service resides. e.g. eu-central-1
        :param query_result_location: S3 bucket to store query results
            e.g s3://myathenabucket/results
        """
        super().__init__(name, __internal__)
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.query_result_location = query_result_location

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"access_key", "region", "query_result_location"}

    def _secret_fields(self) -> set[str] | None:
        return {"secret_key"}


class KafkaSslCredential(Credential):
    """
    A Kafka TLS credential.

    Security protocol: SSL

    https://docs.validio.io/docs/kafka#authentication-methods-for-source-config
    """

    def __init__(
        self,
        name: str,
        bootstrap_servers: list[str],
        ca_certificate: str,
        client_certificate: str,
        client_private_key: str,
        client_private_key_password: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param bootstrap_servers: List of Kafka server addresses to connect to.
            example: ['localhost:9092']
        :param ca_certificate: Certificate of the Certificate authority (CA)
            in CRT format.
        :param client_certificate: Client SSL certificate in PEM format.
        :param client_private_key: Client private key certificate in PEM format.
        :param client_private_key_password: Password or passphrase of
            client_private_key.
        """
        super().__init__(name, __internal__)
        self.bootstrap_servers = bootstrap_servers
        self.ca_certificate = ca_certificate
        self.client_certificate = client_certificate
        self.client_private_key = client_private_key
        self.client_private_key_password = client_private_key_password

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"bootstrap_servers"}

    def _secret_fields(self) -> set[str] | None:
        return {
            "ca_certificate",
            "client_certificate",
            "client_private_key",
            "client_private_key_password",
        }


class KafkaSaslSslPlainCredential(Credential):
    """
    A Kafka SASL SSL credential.

    Security protocol: SASL_SSL
    Sasl mechanism: PLAIN

    https://docs.validio.io/docs/kafka#authentication-methods-for-source-config
    """

    def __init__(
        self,
        name: str,
        bootstrap_servers: list[str],
        username: str,
        password: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param bootstrap_servers: List of Kafka server addresses to connect to.
            example: ['localhost:9092']
        :param username: Username for the credential
        :param password: Password for the credential
        """
        super().__init__(name, __internal__)
        self.bootstrap_servers = bootstrap_servers
        self.username = username
        self.password = password

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"bootstrap_servers"}

    def _secret_fields(self) -> set[str] | None:
        return {"username", "password"}


KafkaCredential = Union[KafkaSslCredential, KafkaSaslSslPlainCredential]


class DatabricksCredential(Credential):
    """A credential resource that can be used to connect to a Databricks table."""

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        access_token: str,
        http_path: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param host: A host of Databricks deployment
        :param port: A port of Databricks deployment
        :param access_token: An access token of system principal or a user
        :param http_path: Username having read access to the desired table.
        """
        super().__init__(name, __internal__)
        self.host = host
        self.port = port
        self.access_token = access_token
        self.http_path = http_path

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"host", "port", "http_path"}

    def _secret_fields(self) -> set[str] | None:
        return {"access_token"}


class AzureSynapseCredential(Credential):
    """A base class of Azure Credential resource."""

    def __init__(self, name: str, __internal__: ResourceGraph | None = None) -> None:
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        super().__init__(name, __internal__)


class AzureSynapseEntraIdCredential(AzureSynapseCredential):
    """An Entra ID credential resource that can be used
    to connect to an Azure Synapse table.
    """

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        client_id: str,
        client_secret: str,
        database: str | None = None,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param host: A host of Azure Synapse deployment
        :param port: A port of Azure Synapse deployment
        :param client_id: Application (client) ID of Azure system account.
        :param client_secret: Client secret value of Azure system account.
        :param database: Name of the database to connect to
        """
        super().__init__(name, __internal__)
        self.host = host
        self.port = port
        self.client_id = client_id
        self.client_secret = client_secret
        self.database = database

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"host", "port", "client_id", "database"}

    def _secret_fields(self) -> set[str] | None:
        return {"client_secret"}


class AzureSynapseSqlCredential(AzureSynapseCredential):
    """A Sql credential resource that can be used
    to connect to an Azure Synapse table.
    """

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str | None = None,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param host: A host of Azure Synapse SQL pool server
        :param port: A port of Azure Synapse SQL pool server
        :param username: SQL Server username.
        :param password: SQL Server password.
        :param database: Name of the database to connect to
        """
        super().__init__(name, __internal__)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"host", "port", "username", "database"}

    def _secret_fields(self) -> set[str] | None:
        return {"password"}


class TableauConnectedAppCredential(Credential):
    """
    A credential resource that can be used to connect
    to Tableau using connected app.
    """

    def __init__(
        self,
        name: str,
        host: str,
        site: str,
        user: str,
        client_id: str,
        secret_id: str,
        secret_value: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param host: Host address to the Tableau instance
        :param site: Name of Tableau site
        :param user: Tableau username
        :param client_id: The connected app's unique id
        :param secret_id: The connected app's secret key identifier.
        :param secret_value: The connected app's secret key.
        """
        super().__init__(name, __internal__)
        self.host = host
        self.site = site
        self.user = user
        self.client_id = client_id
        self.secret_id = secret_id
        self.secret_value = secret_value

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"host", "site", "user", "client_id", "secret_id"}

    def _secret_fields(self) -> set[str] | None:
        return {"secret_value"}


class TableauPersonalAccessTokenCredential(Credential):
    """
    A credential resource that can be used to connect
    to Tableau using a personal access token.
    """

    def __init__(
        self,
        name: str,
        host: str,
        site: str,
        token_name: str,
        token_value: str,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param host: Host address to the Tableau instance
        :param site: Name of Tableau site
        :param user: Tableau username
        :param token_name: Personal access token name
        :param token_value: Personal access token secret
        """
        super().__init__(name, __internal__)
        self.host = host
        self.site = site
        self.token_name = token_name
        self.token_value = token_value

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"host", "site", "token_name"}

    def _secret_fields(self) -> set[str] | None:
        return {"token_value"}
