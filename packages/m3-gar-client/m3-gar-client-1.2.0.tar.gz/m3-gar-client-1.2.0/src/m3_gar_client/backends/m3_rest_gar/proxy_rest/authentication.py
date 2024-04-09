from rest_framework.authentication import (
    SessionAuthentication,
)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    """Авторизация без проверки CSRF токена.

    Пользователь должен быть авторизован, но проверка CSRF токена не
    выполняется, т.к. токен не передается с формы.
    """

    def enforce_csrf(self, request):
        return
