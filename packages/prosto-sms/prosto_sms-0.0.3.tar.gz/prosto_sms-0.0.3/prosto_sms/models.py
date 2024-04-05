from typing import Optional

from pydantic import BaseModel


class GetPricesData(BaseModel):
    group_directions: dict


class GetMessageReportData(BaseModel):
    id: int
    sender_name: str
    text: str
    phone: str
    type: int
    n_raw_sms: int
    start_time: str  # TODO: в будущем datetime pls
    last_update: str   # TODO: в будущем datetime pls
    id_tarifs_group: int
    state: int
    state_text: str
    credits: float


class WaitCallData(BaseModel):
    call_to_number: str
    id_call: str
    waiting_call_from: str


class GetProfileData(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    credits: float
    credits_used: float
    credits_name: str
    currency: str
    sender_name: str
    referral_id: Optional[int]


class PushMessageData(BaseModel):
    id: int
    credits: float
    n_raw_sms: int
    sender_name: str
    call_to_number: Optional[str]


class Message(BaseModel):
    err_code: str
    text: str
    type: str


class GetProfileAnswer(BaseModel):
    msg: Optional[Message]
    data: Optional[GetProfileData]


class Answer(BaseModel):
    msg: Optional[Message]
    data: Optional[dict]


class BaseAnswer(BaseModel):
    response: Answer
