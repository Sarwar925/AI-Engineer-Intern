import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services.adk_agent import generate_reply
from .services.woocommerce import is_product_query, lookup_store_facts

# ---------------------------------------------------------- #
# ---------Health endpoint for quick service checks--------- #
# ---------------------------------------------------------- #
def health_check(request):
    return JsonResponse({"status": "ok"})

# ---------------------------------------------------------- #
# -------Chat message endpoint for frontend requests-------- #
# ---------------------------------------------------------- #
@csrf_exempt
@require_http_methods(["POST"])
def chat_message(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    message = str(payload.get("message", "")).strip()
    email = str(payload.get("email", "")).strip()

    if not email and getattr(request, "user", None) and request.user.is_authenticated:
        email = getattr(request.user, "email", "")

    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    try:
        store_context = lookup_store_facts(message) if is_product_query(message) else {}
        reply = generate_reply(message, email=email)
    except Exception as exc:  # pragma: no cover
        return JsonResponse(
            {
                "error": "The chat service could not process your message.",
                "details": str(exc),
            },
            status=500,
        )

    return JsonResponse(
        {
            "reply": reply,
            "context": store_context,
        }
    )
