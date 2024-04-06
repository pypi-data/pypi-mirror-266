from datetime import datetime
from typing import Any, List, Optional, Callable

import requests
from pytz import UTC
from .errors import ResponseError
from .types import ParticipantType, Conversation, Attachment

API_BASE_URL = "https://api.gradient-labs.ai"
USER_AGENT = "Gradient Labs Python"


class Client:
    def __init__(self, *, api_key: str, base_url: str = API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    def assign_conversation(
        self,
        *,
        conversation_id: str,
        participant_type: ParticipantType,
        assignee_id: Optional[str] = None,
        timeout: int = None,
    ) -> None:
        """Assigns a conversation to the given participant."""
        _ = self._put(
            f"conversations/{conversation_id}/assignee",
            {
                "assignee_id": assignee_id,
                "assignee_type": participant_type,
            },
            timeout=timeout,
        )

    def end_conversation(self, *, conversation_id: str, timeout: int = None) -> None:
        """Ends the conversation"""
        _ = self._put(
            f"conversations/{conversation_id}/end",
            {},
            timeout=timeout,
        )

    def read_conversation(
        self, *, conversation_id: str, timeout: int = None
    ) -> Conversation:
        """Retrieves the conversation"""
        body = self._get(
            f"conversations/{conversation_id}",
            {},
            timeout=timeout,
        )
        return Conversation.from_dict(body)

    def start_conversation(
        self,
        *,
        conversation_id: str,
        customer_id: str,
        channel: str,
        metadata: Any = None,
        timeout: int = None,
    ) -> Conversation:
        """Starts a conversation."""
        body = self._post(
            "conversations",
            {
                "id": conversation_id,
                "customer_id": customer_id,
                "channel": channel,
                "metadata": metadata,
            },
            timeout=timeout,
        )
        return Conversation.from_dict(body)

    def add_message(
        self,
        *,
        message_id: str,
        conversation_id: str,
        body: str,
        participant_id: str,
        participant_type: ParticipantType,
        created: datetime = None,
        timeout: int = None,
        attachments: List[Attachment] = None,
    ) -> None:
        """Adds a message to a conversation."""
        if created is None:
            created = datetime.now()

        body = self._post(
            f"conversations/{conversation_id}/messages",
            {
                "id": message_id,
                "body": body,
                "participant_id": participant_id,
                "participant_type": participant_type,
                "created": UTC.localize(created).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "attachments": [a.to_dict() for a in attachments]
                if attachments is not None
                else [],
            },
            timeout=timeout,
        )

    def _post(self, path: str, body: Any, timeout: int = None):
        return self._api_call(requests.post, path, body, timeout)

    def _put(self, path: str, body: Any, timeout: int = None):
        return self._api_call(requests.put, path, body, timeout)

    def _get(self, path: str, body: Any, timeout: int = None):
        return self._api_call(requests.get, path, body, timeout)

    def _api_call(
        self, request_func: Callable, path: str, body: Any, timeout: int = None
    ):
        url = f"{self.base_url}/{path}"
        rsp = request_func(
            url,
            json=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": USER_AGENT,
            },
            timeout=timeout,
        )
        if rsp.status_code < 200 or rsp.status_code > 299:
            raise ResponseError(rsp)
        if len(rsp.content) != 0:
            return rsp.json()
