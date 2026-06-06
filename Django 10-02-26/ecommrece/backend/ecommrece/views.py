import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .chat_agent import get_or_create_chat_user, run_chat_agent


@dataclass(frozen=True)
class ChatEntry:
    id: str
    sender: str
    text: str
    created_at: str


_CHAT_STORE: Dict[str, List[ChatEntry]] = {}


def _serialize_chat_entries(entries):
    return [asdict(entry) for entry in entries]


@csrf_exempt
def chat_history(request):
    email = request.GET.get("email", "guest@ecommrece.local")
    user = get_or_create_chat_user(email)
    chat_entries = _CHAT_STORE.get(user.email, [])

    return JsonResponse(
        {
            "email": user.email,
            "messages": _serialize_chat_entries(chat_entries),
        }
    )


@csrf_exempt
def chat_message(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    data = json.loads(request.body or b"{}")
    message = (data.get("message") or "").strip()
    email = data.get("email", "guest@ecommrece.local")

    if not message:
        return JsonResponse({"detail": "Message is required"}, status=400)

    user = get_or_create_chat_user(email)
    response_text = run_chat_agent(user, message)

    created_at = datetime.now(timezone.utc).isoformat()
    entries = _CHAT_STORE.setdefault(user.email, [])
    entry_id = f"{len(entries) + 1}"
    entries.extend(
        [
            ChatEntry(
                id=f"user-{entry_id}",
                sender="user",
                text=message,
                created_at=created_at,
            ),
            ChatEntry(
                id=f"agent-{entry_id}",
                sender="agent",
                text=response_text,
                created_at=created_at,
            ),
        ]
    )

    return JsonResponse(
        {
            "id": entry_id,
            "email": user.email,
            "message": message,
            "response": response_text,
            "created_at": created_at,
        }
    )
