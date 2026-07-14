import logging

from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


def common_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        view = context.get("view")
        request = context.get("request")
        logger.exception(
            "Unhandled API exception: method=%s path=%s view=%s",
            getattr(request, "method", "unknown"),
            getattr(request, "path", "unknown"),
            view.__class__.__name__ if view else "unknown",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return response

    detail = response.data
    message = "요청 처리에 실패했습니다."

    if isinstance(detail, dict) and "detail" in detail:
        message = str(detail["detail"])
        detail = None

    body = {
        "success": False,
        "data": detail,
        "message": message,
    }

    response.data = body
    return response
