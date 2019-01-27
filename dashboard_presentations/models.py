from dataclasses import dataclass, field
from typing import List

from actions.actions import ActionPayload

@dataclass
class PresentationPayload(ActionPayload):
    email_subject: str = None
    email_body: str = None
    email_destinations: List[str] = field(default_factory=list)
