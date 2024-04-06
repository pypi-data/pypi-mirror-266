import json

from paloma_sdk.core.broadcast import SyncTxBroadcastResult
from paloma_sdk.core.scheduler import MsgCreateJob, MsgExecuteJob

from ..wallet import Wallet
from ._base import BaseAsyncAPI, sync_bind
from .tx import CreateTxOptions

__all__ = ["AsyncJobSchedulerAPI", "JobSchedulerAPI"]


class AsyncJobSchedulerAPI(BaseAsyncAPI):
    async def create_job(
        self,
        wallet: Wallet,
        job_id: str,
        contract_address: str,
        abi: dict,
        payload: str,
        chain_type: str,
        chain_reference_id: str,
        creator: str,
        signers: list[str],
    ) -> SyncTxBroadcastResult:
        """Create a job with data
        Args:
            wallet (Wallet): Job creator paloma wallet
            job_id (str): Job ID
            contract_address (str): Contract address to run the message on the purpose chain
            abi (dict): ABI data of the smart contract
            payload (str): default payload data of the job
            chain_type (str): purpose chain type
            chain_reference_id (str): chain reference id in paloma
            creator (str): job creator
            signers (list[str]): signers list
        Returns:
            SyncTxBroadcastResult: transaction result
        """
        definition = {
            "abi": json.dumps(abi, separators=[",", ":"]),
            "address": contract_address,
        }
        definition_json = json.dumps(definition, separators=[",", ":"])
        payload_json = json.dumps({"hexPayload": payload}, separators=[",", ":"])
        create_tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgCreateJob(
                        {
                            "id": job_id,
                            "owner": "",
                            "routing": {
                                "chain_type": chain_type,
                                "chain_reference_id": chain_reference_id,
                            },
                            "definition": definition_json,
                            "payload": payload_json,
                            "is_payload_modifiable": True,
                            "permissions": {"whitelist": [], "blacklist": []},
                            "triggers": [],
                            "address": "",
                        },
                        {
                            "creator": creator,
                            "signers": signers,
                        },
                    )
                ]
            )
        )
        create_tx_result = await self._c.tx.broadcast_sync(create_tx)
        return create_tx_result

    async def execute_job(
        self,
        wallet: Wallet,
        job_id: str,
        payload: str,
        creator: str,
        signers: list[str],
    ) -> SyncTxBroadcastResult:
        """Execute a job with data
        Args:
            wallet (Wallet): Job creator paloma wallet
            job_id (str): Job ID
            payload (str): payload data of the job on execution
            creator (str): job creator
            signers (list[str]): signers list
        Returns:
            SyncTxBroadcastResult: transaction result
        """
        execute_tx = await wallet.create_and_sign_tx(
            CreateTxOptions(
                msgs=[
                    MsgExecuteJob(
                        job_id,
                        json.dumps({"hexPayload": payload}, separators=[",", ":"]),
                        {
                            "creator": creator,
                            "signers": signers,
                        },
                    )
                ]
            )
        )
        create_tx_result = await self._c.tx.broadcast_sync(execute_tx)
        return create_tx_result


class JobSchedulerAPI(AsyncJobSchedulerAPI):
    @sync_bind(AsyncJobSchedulerAPI.create_job)
    def create_job(
        self,
        wallet: Wallet,
        job_id: str,
        contract_address: str,
        abi: dict,
        payload: str,
        chain_type: str,
        chain_reference_id: str,
        creator: str,
        signers: list[str],
    ) -> SyncTxBroadcastResult:
        pass

    @sync_bind(AsyncJobSchedulerAPI.execute_job)
    def execute_job(
        self,
        wallet: Wallet,
        job_id: str,
        payload: str,
        creator: str,
        signers: list[str],
    ) -> SyncTxBroadcastResult:
        pass

    create_job.__doc__ = AsyncJobSchedulerAPI.create_job.__doc__
    execute_job.__doc__ = AsyncJobSchedulerAPI.execute_job.__doc__
