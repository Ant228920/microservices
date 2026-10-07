import httpx
import pybreaker
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
)

breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=10)


class UserNotFoundException(Exception):
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_not_exception_type(UserNotFoundException)
)
def _get_user(user_id: int, correlation_id: str):
    response = httpx.get(
        f"http://localhost:8001/users/{user_id}",
        headers={"X-Correlation-ID": correlation_id},
        timeout=2
    )

    if response.status_code == 404:
        raise UserNotFoundException(f"User {user_id} not found")

    response.raise_for_status()
    return response.json()


def get_user(user_id: int, correlation_id: str):
    return breaker.call(_get_user, user_id, correlation_id)