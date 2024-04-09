from typing import Any, Dict, List, Optional

from seaplane.gen.carrier import ApiException, KeyValueApi, KeyValueConfig

from seaplane.errors import SeaplaneError
from seaplane.sdk_internal_utils.retry import retry
from seaplane.sdk_internal_utils.token_auth import get_pdk_client, method_with_token

SP_STORES = ["_SEAPLANE_INTERNAL"]


class KeyValueStorageAPI:
    """
    Class for handling Key-Value Store API calls.
    """

    _allow_internal: bool
    """
    If set, allows the wrapper to manipulate Seaplane-internal buckets.

    Should not be set in customer code!
    """

    def __init__(self) -> None:
        self._allow_internal = False

    def get_kv_api(self, access_token: str) -> KeyValueApi:
        return KeyValueApi(get_pdk_client(access_token))  # type: ignore

    @method_with_token
    def list_stores(self, token: str) -> List[str]:
        """
        List stores

        Returns a List of KV store names
        """
        api = self.get_kv_api(token)
        list = []
        resp = api.list_stores()
        for name in sorted(resp):
            if self._allow_internal or name not in SP_STORES:
                list.append(name)

        return list

    @method_with_token
    def create_store(self, token: str, name: str, body: Optional[Dict[str, Any]] = None) -> None:
        """
        Create a KV store

        The optional body can be used to configure the store. Example:
        {
            "max_value_size": 8388608,
            "history": 2,
            "ttl": 500,
            "replicas": 3,
            "allow_locations": [
                "region/xn"
            ],
            "deny_locations": [
                "country/nl"
            ]
        }
        """
        if not self._allow_internal and name in SP_STORES:
            raise SeaplaneError(f"Cannot create KV store with Seaplane-internal name `{name}`")

        api = self.get_kv_api(token)
        if not body:
            body = {}
        kv_config = KeyValueConfig.from_dict(body)

        def op() -> None:
            return api.create_store(
                kv_store=name,
                key_value_config=kv_config,
            )

        def verify() -> Any:
            return api.get_store(
                kv_store=name,
            )

        try:
            retry(op, verify)
        except Exception:
            raise SeaplaneError(f"Failed creating store: {name}")

    @method_with_token
    def delete_store(self, token: str, name: str) -> None:
        """
        Delete a KV store
        """
        if not self._allow_internal and name in SP_STORES:
            raise SeaplaneError(f"Cannot delete KV store with Seaplane-internal name `{name}`")
        api = self.get_kv_api(token)

        def op() -> None:
            try:
                api.delete_store_with_http_info(kv_store=name)
            except ApiException as e:
                if e.status == 404:
                    return None

        def verify() -> Any:
            try:
                api.get_store_with_http_info(kv_store=name)
                return False
            except ApiException as e:
                return e.status == 404

        try:
            retry(op, verify)
        except Exception:
            raise SeaplaneError(f"Failed deleting store: {name}")

    def exists(self, store: str, key: str) -> bool:
        """
        Check if a key exists in a KV store
        """
        try:
            self.get_key(store, key)
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            raise e

    def get(self, store: str, key: str, default: Any = None) -> Any:
        """
        Get a key value or return the default if key does not exist
        """
        try:
            value = self.get_key(store, key)
            return value
        except ApiException as e:
            if e.status == 404:
                return default
            raise e

    @method_with_token
    def list_keys(self, token: str, store_name: str) -> List[str]:
        """
        List keys in a store

        Returns a List of names of keys in the specified store
        """
        if not self._allow_internal and store_name in SP_STORES:
            raise SeaplaneError(
                f"Cannot list keys in store with Seaplane-internal name `{store_name}`"
            )
        api = self.get_kv_api(token)

        resp = api.list_keys(
            kv_store=store_name,
        )
        list = []
        for name in sorted(resp):
            list.append(name)
        return list

    @method_with_token
    def get_key(
        self, token: str, store_name: str, key: str, version_id: Optional[str] = None
    ) -> Any:
        """
        Get a key value

        Optional version_id to get a specific revision
        """
        api = self.get_kv_api(token)
        resp = api.get_key(key=key, kv_store=store_name, if_match=version_id)
        return resp

    @method_with_token
    def set_key(self, token: str, store_name: str, key: str, value: bytes) -> None:
        """
        Set a key value

        The expected value must be bytes, so if using a string you must encode()
        """
        # TODO: version_id???
        api = self.get_kv_api(token)
        api.put_key(
            key=key,
            kv_store=store_name,
            body=value,
        )

    @method_with_token
    def delete_key(
        self, token: str, store_name: str, key: str, purge: Optional[bool] = False
    ) -> None:
        """
        Delete a key

        Optional purge bool determines whether older revisions are also purged
        """
        # TODO: version_id???
        api = self.get_kv_api(token)
        api.delete_key(
            key=key,
            kv_store=store_name,
            purge="true" if purge else "false",
        )


kv_store = KeyValueStorageAPI()
