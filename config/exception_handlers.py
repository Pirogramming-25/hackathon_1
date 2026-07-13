from rest_framework.views import exception_handler


def common_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
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
