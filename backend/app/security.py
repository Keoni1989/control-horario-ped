from fastapi import Request


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"


def is_ip_allowed(client_ip: str, allowed_ip_prefix: str | None) -> bool:
    if not allowed_ip_prefix:
        return False

    allowed_prefixes = [
        prefix.strip()
        for prefix in allowed_ip_prefix.split(",")
        if prefix.strip()
    ]

    return any(client_ip.startswith(prefix) for prefix in allowed_prefixes)