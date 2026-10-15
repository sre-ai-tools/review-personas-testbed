"""The caller's identity. API Gateway's JWT authorizer has already verified the token."""

from fastapi import HTTPException, Request


def current_email(request: Request) -> str:
    event = request.scope.get("aws.event", {})
    claims = event.get("requestContext", {}).get("authorizer", {}).get("jwt", {}).get("claims", {})
    email = claims.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Missing identity")
    return email.lower()
