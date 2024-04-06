from __future__ import annotations

import json
from typing import Union

import attr

from paloma_sdk.core import AccAddress
from paloma_sdk.core.msg import Msg
from paloma_sdk.util.json import JSONSerializable
from paloma_sdk.util.remove_none import remove_none

from .data import Job as Job_pb
from .data import MsgCreateJob as MsgCreateJob_pb
from .data import MsgExecuteJob as MsgExecuteJob_pb
from .data import Permissions as Permissions_pb
from .data import Routing as Routing_pb
from .data import Metadata as Metadata_pb
from .data import ScheduleTrigger as ScheduleTrigger_pb
from .data import Trigger as Trigger_pb

__all__ = [
    "MsgCreateJob",
]


@attr.s
class Job(JSONSerializable):
    """Paloma job details attribute
    Args:
        id: Job ID
        owner:
        routing: chain type and referrence id
        definition: This is the job definition. It is somthing arbitrary as it's different for every chain.
        payload: The payload for the job
        is_payload_modifiable: true if payload needs to be modified on execute. commonly true.
        permissions: whitelist / blacklist
        triggers: schedule triggers / event triggers
        address:
    """

    type_amino = "scheduler/Job"
    type_url = "/palomachain.paloma.scheduler.Job"
    prototype = Job_pb

    id: str = attr.ib()
    owner: str = attr.ib()
    routing: dict = attr.ib()
    definition: str = attr.ib()
    payload: str = attr.ib()
    is_payload_modifiable: bool = attr.ib()
    permissions: dict = attr.ib()
    triggers: list = attr.ib()
    address: str = attr.ib()


@attr.s
class MsgCreateJob(Msg):
    """Create a paloma job
    Args:
        creator: Job creator paloma address
        job: Paloma job details
    """

    type_amino = "scheduler/MsgCreateJob"
    type_url = "/palomachain.paloma.scheduler.MsgCreateJob"
    prototype = MsgCreateJob_pb

    job: Job = attr.ib()
    metadata: dict = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "job": remove_none(self.job),
                "metadata": remove_none(self.metadata),
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgCreateJob:
        return cls(
            job=parse_msg(data["job"]),
            metadata=parse_msg(data["metadata"]),
        )

    def to_proto(self) -> MsgCreateJob_pb:
        return MsgCreateJob_pb(
            job=Job_pb(
                id=self.job["id"],
                owner=bytes(self.job["owner"], "ascii"),
                routing=Routing_pb(
                    chain_type=self.job["routing"]["chain_type"],
                    chain_reference_id=self.job["routing"]["chain_reference_id"],
                ),
                definition=bytes(self.job["definition"], "ascii"),
                payload=bytes(self.job["payload"], "ascii"),
                is_payload_modifiable=self.job["is_payload_modifiable"],
                permissions=Permissions_pb(
                    whitelist=self.job["permissions"]["whitelist"],
                    blacklist=self.job["permissions"]["blacklist"],
                ),
                triggers=[Trigger_pb(schedule=ScheduleTrigger_pb())],
                address=bytes(self.job["address"], "ascii"),
            ),
            metadata=Metadata_pb(
                creator=bytes(self.metadata["creator"], "ascii"),
                signers=[bytes(signer, "ascii") for signer in self.metadata["signers"]],
            ),
        )

    @classmethod
    def from_proto(cls, proto: MsgCreateJob_pb) -> MsgCreateJob:
        return cls(
            job=parse_msg(proto.job),
            metadata=parse_msg(proto.metadata)
        )


@attr.s
class MsgExecuteJob(Msg):
    """Paloma job details attribute
    Args:
        creator: Job runner paloma address
        job_id: Job ID to execute
        payload: The payload for the job execute.
    """

    type_amino = "scheduler/MsgExecuteJob"
    type_url = "/palomachain.paloma.scheduler.MsgExecuteJob"
    prototype = MsgExecuteJob_pb

    job_id: str = attr.ib()
    payload: str = attr.ib()
    metadata: dict = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "job_id": self.job_id,
                "payload": self.payload,
                "metadata": self.metadata,
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgExecuteJob:
        return cls(
            job_id=data["job_id"],
            payload=data["payload"],
            metadata=parse_msg(data["metadata"]),
        )

    def to_proto(self) -> MsgExecuteJob_pb:
        return MsgExecuteJob_pb(
            job_id=self.job_id,
            payload=bytes(self.payload, "ascii"),
            metadata=Metadata_pb(
                creator=bytes(self.metadata["creator"], "ascii"),
                signers=[bytes(signer, "ascii") for signer in self.metadata["signers"]],
            ),
        )

    @classmethod
    def from_proto(cls, proto: MsgExecuteJob_pb) -> MsgExecuteJob:
        return cls(
            job_id=proto.job_id,
            metadata=proto.metadata
        )


def parse_msg(msg: Union[dict, str, bytes]) -> dict:
    if type(msg) is dict:
        return msg
    return json.loads(msg)
