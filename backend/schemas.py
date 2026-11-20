import ipaddress, re
from pydantic import BaseModel, Field, field_validator

class DeviceIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    ip_address: str
    mac_address: str = ""
    status: str = "online"
    connected_website: str = ""
    x: float | None = None
    y: float | None = None
    @field_validator('name')
    @classmethod
    def clean_name(cls, v):
        v=v.strip()
        if not v: raise ValueError('Name cannot be blank')
        return v
    @field_validator('ip_address')
    @classmethod
    def valid_ip(cls,v):
        try: return str(ipaddress.IPv4Address(v))
        except Exception as e: raise ValueError('A valid IPv4 address is required') from e
    @field_validator('mac_address')
    @classmethod
    def valid_mac(cls,v):
        v=v.strip()
        if v and not re.fullmatch(r'(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}',v): raise ValueError('Invalid MAC address')
        return v
    @field_validator('status')
    @classmethod
    def valid_status(cls,v):
        if v not in ('online','offline'): raise ValueError('Status must be online or offline')
        return v
    @field_validator('connected_website')
    @classmethod
    def clean_site(cls,v): return v.strip().lower().removeprefix('https://').removeprefix('http://').split('/')[0]

class ConnectionIn(BaseModel):
    source_device_id: int
    target_device_id: int

class DFSIn(BaseModel): start_device_id: int
class ReachabilityIn(BaseModel): source_device_id: int; target_device_id: int
