from ._base import BaseAsyncAPI, sync_bind
from ..wallet import Wallet
from .tx import CreateTxOptions
from paloma_sdk.core.wasm import MsgExecuteContract
from paloma_sdk.core.coins import Coins
from paloma_sdk.core.broadcast import SyncTxBroadcastResult

__all__ = ["AsyncPalomaswapAPI", "PalomaswapAPI"]

class AsyncPalomaswapAPI(BaseAsyncAPI):
    async def create_xyk_pair(
        self,
        wallet: Wallet,
        factory: str,
        token0: str,
        token1: str,
    ) -> SyncTxBroadcastResult:
        execute_msg = {"create_pair": {
            "pair_type": {"xyk":{}},
            "asset_infos": [{"token":{"contract_addr":token0}},{"token":{"contract_addr":token1}}],
        }}
        funds = Coins()
        tx = await wallet.create_and_sign_tx(CreateTxOptions(
            msgs=[MsgExecuteContract(
                wallet.key.acc_address,
                factory,
                execute_msg,
                funds
            )]
        ))
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def create_xyk_native_pair(
        self,
        wallet: Wallet,
        factory: str,
        denom: str,
        token: str,
    ) -> SyncTxBroadcastResult:
        execute_msg = {"create_pair": {
            "pair_type": {"xyk":{}},
            "asset_infos": [{"native_token":{"denom":denom}},{"token":{"contract_addr":token}}],
        }}
        funds = Coins()
        tx = await wallet.create_and_sign_tx(CreateTxOptions(
            msgs=[MsgExecuteContract(
                wallet.key.acc_address,
                factory,
                execute_msg,
                funds
            )]
        ))
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def create_stable_pair(
        self,
        wallet: Wallet,
        factory: str,
        tokens: list,
    ) -> SyncTxBroadcastResult:
        asset_infos = []
        for token in tokens:
            asset_infos.append({"token":{"contract_addr":token}})
        execute_msg = {"create_pair": {
            "pair_type": {"stable":{}},
            "asset_infos": asset_infos,
        }}
        funds = Coins()
        tx = await wallet.create_and_sign_tx(CreateTxOptions(
            msgs=[MsgExecuteContract(
                wallet.key.acc_address,
                factory,
                execute_msg,
                funds
            )]
        ))
        result = await self._c.tx.broadcast_sync(tx)
        return result

    async def create_stable_native_pair(
        self,
        wallet: Wallet,
        factory: str,
        denoms: list,
        tokens: list,
    ) -> SyncTxBroadcastResult:
        asset_infos = []
        for denom in denoms:
            asset_infos.append({"native_token":{"denom":denom}})
        for token in tokens:
            asset_infos.append({"token":{"contract_addr":token}})
        execute_msg = {"create_pair": {
            "pair_type": {"stable":{}},
            "asset_infos": asset_infos,
        }}
        funds = Coins()
        tx = await wallet.create_and_sign_tx(CreateTxOptions(
            msgs=[MsgExecuteContract(
                wallet.key.acc_address,
                factory,
                execute_msg,
                funds
            )]
        ))
        result = await self._c.tx.broadcast_sync(tx)
        return result

class PalomaswapAPI(AsyncPalomaswapAPI):
    @sync_bind(AsyncPalomaswapAPI.create_xyk_pair)
    def create_xyk_pair(
        self,
        wallet: Wallet,
        factory: str,
        token0: str,
        token1: str,
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncPalomaswapAPI.create_xyk_native_pair)
    def create_xyk_native_pair(
        self,
        wallet: Wallet,
        factory: str,
        denom: str,
        token: str,
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncPalomaswapAPI.create_stable_pair)
    def create_stable_pair(
        self,
        wallet: Wallet,
        factory: str,
        tokens: list,
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncPalomaswapAPI.create_stable_native_pair)
    def create_stable_native_pair(
        self,
        wallet: Wallet,
        factory: str,
        denoms: list,
        tokens: list,
    ) -> SyncTxBroadcastResult:
        pass

    create_xyk_pair.__doc__ = AsyncPalomaswapAPI.create_xyk_pair.__doc__
    create_xyk_native_pair.__doc__ = AsyncPalomaswapAPI.create_xyk_native_pair.__doc__
    create_stable_pair.__doc__ = AsyncPalomaswapAPI.create_stable_pair.__doc__
    create_stable_native_pair.__doc__ = AsyncPalomaswapAPI.create_stable_native_pair.__doc__
