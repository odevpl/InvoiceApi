import time
from fastapi import Request
from http import HTTPStatus
from api.utils.logger import logger


async def logging_middleware(request: Request, call_next):
    start = time.perf_counter()

    # Exclude favicon
    if request.url.path == "/favicon.ico":
        return await call_next(request)

    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        status = HTTPStatus(response.status_code)

        log_extra = {
            "req": {
                "method": request.method,
                "path": request.url.path,
            },
            "res": {
                "status_code": status.value,
                "status_text": status.phrase,
                "duration_ms": duration_ms,
            },
        }

        message = f"{status.value} {status.phrase}"

        if status.value >= 500:
            logger.error(message, extra=log_extra)
        elif status.value >= 400:
            logger.warning(message, extra=log_extra)
        else:
            logger.info(message, extra=log_extra)

        return response

    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log_extra = {
            "req": {
                "method": request.method,
                "path": request.url.path,
            },
            "res": {
                "status_code": 500,
                "status_text": "Internal Server Error",
                "duration_ms": duration_ms,
            },
        }
        logger.error("Unhandled exception", extra=log_extra, exc_info=True)
        raise
