import time
from dataclasses import dataclass
from dataclasses import field as data_field
from typing import Optional

from dataclasses_json import config as json_config
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class AccessToken:
    access_token: Optional[str] = data_field(default=None, metadata=json_config(field_name="access_token"))
    token_type: Optional[str] = data_field(default=None, metadata=json_config(field_name="token_type"))
    expires_in: Optional[int] = data_field(default=None, metadata=json_config(field_name="expires_in"))
    refresh_token: Optional[str] = data_field(default=None, metadata=json_config(field_name="refresh_token"))
    scope: Optional[str] = data_field(default=None, metadata=json_config(field_name="scope"))

    def get_expires_in_timestamp(self):
        now = time.time()

        expires_in = self.expires_in
        if self.expires_in < 529196400:
            expires_in = now + expires_in

        return expires_in
