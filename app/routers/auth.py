from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from app.security import COOKIE_NAME, auth_enabled, create_session_cookie, valid_login
from app.config import settings

router = APIRouter(tags=["Auth"])


def _login_page(error: str = "") -> str:
    error_html = f'<div class="error">{error}</div>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calorie Tracker Login</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f7f4ef;
            color: #1f2933;
        }}
        form {{
            width: min(92vw, 360px);
            display: grid;
            gap: 12px;
            padding: 22px;
            background: #fffdf9;
            border: 1px solid #e5ded2;
            border-radius: 8px;
        }}
        h1 {{ margin: 0 0 4px; font-size: 1.25rem; }}
        label {{ display: grid; gap: 6px; font-size: 0.9rem; font-weight: 600; }}
        input {{
            height: 42px;
            border: 1px solid #cfc7bb;
            border-radius: 6px;
            padding: 0 10px;
            font: inherit;
        }}
        button {{
            height: 42px;
            border: 1px solid #2563eb;
            border-radius: 6px;
            background: #2563eb;
            color: white;
            font: inherit;
            font-weight: 700;
            cursor: pointer;
        }}
        .error {{ color: #b42318; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <form method="post" action="/auth/login">
        <h1>Calorie Tracker</h1>
        {error_html}
        <label>Username<input name="username" autocomplete="username" required></label>
        <label>Password<input name="password" type="password" autocomplete="current-password" required></label>
        <button type="submit">Log in</button>
    </form>
</body>
</html>"""


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page():
    if not auth_enabled():
        return RedirectResponse(url="/chat/")
    return HTMLResponse(_login_page())


@router.post("/auth/login", include_in_schema=False)
def login(username: str = Form(...), password: str = Form(...)):
    if not valid_login(username, password):
        return HTMLResponse(_login_page("That login did not work."), status_code=401)

    response = RedirectResponse(url="/chat/", status_code=303)
    response.set_cookie(
        COOKIE_NAME,
        create_session_cookie(username),
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.post("/auth/logout", include_in_schema=False)
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response
