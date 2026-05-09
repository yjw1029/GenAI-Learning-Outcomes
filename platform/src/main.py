import argparse
import asyncio
from typing import Optional
import os
from PIL import Image
import base64
import io

from admin import AdminPageBuilder
from configs import AppConfig
from consent import ConsentPageBuilder
from database import (
    async_create_database,
    async_get_latest_action_value,
    create_database,
    get_latest_action_value,
)
from fastapi import Request
from fastapi.responses import RedirectResponse
from learning import LearningPageBuilder
from nicegui import Client, app, ui
from problem import ProbelmPageBuilder
from progress import ProgressBuilder
from survey import SurveyPageBuilder

from starlette.middleware.base import BaseHTTPMiddleware

S0 = "未开始"
S1 = "试前问卷调查"
S2 = "学习与试用平台"
S3 = "课程学习"
S4 = "完成作业 1"
S5 = "课程复习"
S6 = "完成作业 2"
S7 = "试后问卷调查"
S8 = "全部完成"
S9 = "FINISHED"


def parse_args():
    parser = argparse.ArgumentParser(description="Run the NiceGUI app.")
    parser.add_argument(
        "--port", type=int, default=8080, help="Port to run the app on."
    )
    parser.add_argument("--config-path", type=str, default="config.toml")
    parser.add_argument("--config", dest="config_path", type=str)
    args = parser.parse_args()
    return args


args = parse_args()
cfg = AppConfig(args.config_path)


def add_footer():
    with ui.footer(fixed=False).classes("bg-gray-100 text-black") as footer:
        ui.markdown(
            """
    <footer id="ms" classes="w-full">
        <div classes="w-full">
            <div classes="items-center content-center">
                <a href="https://privacy.microsoft.com/privacystatement">Privacy & Cookies</a>
                <span>|</span>
                <a href="https://www.microsoft.com/trademarks">Trademarks</a>
                <span>|</span>
                <a href="https://go.microsoft.com/fwlink/?LinkID=206977">Terms of Use</a>
                <span>|</span>
                <span>© 2019 Microsoft</span>
            </div>
        </div>
    </footer>
    """
        ).classes("w-full")


unrestricted_page_routes = {"/login"}
restricted_routes = {
    "/progress",
    "/stage/learning",
    "/stage/a1",
    "/stage/a2",
    "/stage/review",
    "/stage/test",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get("authenticated", False):
            if (
                request.url.path in Client.page_routes.values()
                and request.url.path not in unrestricted_page_routes
            ):
                app.storage.user[
                    "referrer_path"
                ] = request.url.path  # remember where the user wanted to go
                return RedirectResponse("/login")

        return await call_next(request)


class ConsentMiddleware(BaseHTTPMiddleware):
    """
    This middleware checks if the user has agreed to the consent form.
    If not, it redirects them to the consent page.
    """

    async def dispatch(self, request: Request, call_next):
        if (
            request.url.path not in restricted_routes
            and not request.url.path.startswith("/assets/edu")
        ):
            return await call_next(request)

        user = app.storage.user
        latest_consent = await async_get_latest_action_value(
            username=user.get("username"), action="consent"
        )
        if latest_consent is None or not latest_consent.get("agree", False):
            return RedirectResponse(url="/consent")

        return await call_next(request)


app.add_middleware(AuthMiddleware)
app.add_middleware(ConsentMiddleware)


@ui.page("/")
def main_page() -> None:
    return RedirectResponse("/login")


@ui.page("/login")
def login() -> Optional[RedirectResponse]:
    async def try_login() -> (
        None
    ):  # local function to avoid passing username and password as arguments
        if not cookie_check.value:
            ui.notify("同意Cookie使用后方能进行测试", color="negative")
            return

        if username.value == "11m3edu_4dmin" and password.value == "admin12312691237":
            # go to admin setting page
            app.storage.user.update({"username": username.value, "authenticated": True})
            ui.navigate.to(app.storage.user.get("referrer_path", "/admin"))
        else:
            if cfg.valid_user_pass(username.value, password.value):
                latest_status = await async_get_latest_action_value(
                    username=username.value, action="progress"
                )
                if latest_status and latest_status.get("stage") == "FINISHED":
                    ui.notify("您已完成本次实验！谢谢参与", color="positive")
                else:
                    app.storage.user.update(
                        {"username": username.value, "authenticated": True}
                    )
                    ui.navigate.to(
                        app.storage.user.get("referrer_path", "/consent")
                    )  # go back to where the user wanted to go
            else:
                ui.notify("用户名或密码错误", color="negative")

    if app.storage.user.get("authenticated", False):
        if app.storage.user.get("username") == "11m3edu_4dmin":
            return RedirectResponse("/admin")
        else:
            # whether the user has finished the course
            latest_status = get_latest_action_value(
                username=app.storage.user.get("username"), action="progress"
            )

            if latest_status and latest_status.get("stage") == "FINISHED":
                ui.notify("您已完成本次实验！谢谢参与", color="positive")
            else:
                return RedirectResponse("/consent")

    with ui.row().classes("w-full h-screen grid grid-cols-11") as row:
        with ui.card().classes("my-auto col-start-5 col-end-8 align-middle"):
            ui.label("欢迎登录").classes("w-full text-2xl justify-center flex")
            username = ui.input("用户名").classes("w-full").on("keydown.enter", try_login)
            password = (
                ui.input("密码", password=True, password_toggle_button=True)
                .classes("w-full")
                .on("keydown.enter", try_login)
            )
            with ui.row().classes("w-full flex items-center"):
                cookie_check = ui.checkbox("我同意cookie使用")
                ui.link("了解更多").style("color: #326ed1").on(
                    "click", lambda: more_info.open()
                )

                # Create dialog
                with ui.dialog(value="关于Cookie的使用") as more_info, ui.card().classes(
                    "w-full"
                ):
                    ui.label("本网站使用Cookie来进行数据分析、提供个性化内容和广告。继续浏览本网站，即表示您同意此用途。")
                    ui.button("关闭").on("click", lambda: more_info.close()).classes(
                        "ml-auto"
                    )

            ui.button("登录", on_click=try_login, color="#467aab").style("color: #ffffff")
    add_footer()


@ui.page("/stage/learning")
def learning() -> Optional[RedirectResponse]:
    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S3:
        return RedirectResponse("/progress")

    builder = LearningPageBuilder(cfg, stage="learning", user=user)

    builder.build()
    add_footer()


# @ui.page("/stage/test")
# def review() -> Optional[RedirectResponse]:
#     user = app.storage.user

#     builder = ProbelmPageBuilder(cfg, stage="test", user=user)
#     builder.build()

#     add_footer()

@ui.page("/stage/pretest_py")
def pretest() -> Optional[RedirectResponse]:
    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S1:
        return RedirectResponse("/progress")

    vgroup = cfg.uservgroup(user.get("username", None))
    if not vgroup.startswith("py"):
        return RedirectResponse("/progress")
    
    builder = SurveyPageBuilder(cfg, stage="pretest", survey_name="pretest_py", user=user)
    builder.build()


@ui.page("/stage/pretest_math")
def pretest() -> Optional[RedirectResponse]:
    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S1:
        return RedirectResponse("/progress")

    vgroup = cfg.uservgroup(user.get("username", None))
    if not vgroup.startswith("math"):
        return RedirectResponse("/progress")
    
    builder = SurveyPageBuilder(cfg, stage="pretest", survey_name="pretest_math", user=user)
    builder.build()


@ui.page("/stage/captest_py")
def pretest() -> Optional[RedirectResponse]:
    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S1:
        return RedirectResponse("/progress")
    
    vgroup = cfg.uservgroup(user.get("username", None))
    if not vgroup.startswith("py"):
        return RedirectResponse("/progress")
    

    builder = SurveyPageBuilder(cfg, stage="pretest", survey_name="captest_py", user=user, time_limit=True)
    builder.build()

@ui.page("/stage/captest_math")
def pretest() -> Optional[RedirectResponse]:
    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S1:
        return RedirectResponse("/progress")
    
    vgroup = cfg.uservgroup(user.get("username", None))
    if not vgroup.startswith("math"):
        return RedirectResponse("/progress")

    builder = SurveyPageBuilder(cfg, stage="pretest", survey_name="captest_math", user=user, time_limit=True)
    builder.build()


@ui.page("/stage/posttest")
def pretest() -> Optional[RedirectResponse]:
    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S7:
        return RedirectResponse("/progress")

    builder = SurveyPageBuilder(cfg, stage="posttest", survey_name="post", user=user)
    builder.build()


@ui.page("/stage/a1")
def a1() -> Optional[RedirectResponse]:
    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S4:
        return RedirectResponse("/progress")

    builder = ProbelmPageBuilder(cfg, stage="a1", user=user)
    builder.build()

    add_footer()


@ui.page("/stage/a2")
def a2() -> Optional[RedirectResponse]:
    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S6:
        return RedirectResponse("/progress")

    builder = ProbelmPageBuilder(cfg, stage="a2", user=user)
    builder.build()

    add_footer()


@ui.page("/stage/review")
def review() -> Optional[RedirectResponse]:
    from problem import ProbelmPageBuilder

    user = app.storage.user

    latest_status = get_latest_action_value(
        username=app.storage.user.get("username"), action="progress"
    )

    if latest_status is None or latest_status.get("stage") != S5:
        return RedirectResponse("/progress")

    builder = ProbelmPageBuilder(cfg, stage="review", user=user, show_answer=True)
    builder.build()

    add_footer()


@ui.page("/progress")
def progress() -> Optional[RedirectResponse]:
    user = app.storage.user

    builder = ProgressBuilder(cfg, user=user)
    builder.build()

    add_footer()


@ui.page("/consent")
def consent() -> Optional[RedirectResponse]:
    user = app.storage.user

    app.storage.user.get("usr", False)
    latest_consent = get_latest_action_value(
        username=user.get("username"), action="consent"
    )
    if latest_consent and latest_consent.get("agree", False):
        return RedirectResponse(url="/progress")

    builder = ConsentPageBuilder(cfg, user=user)
    builder.build()
    add_footer()


@ui.page("/admin")
def admin() -> Optional[RedirectResponse]:
    user = app.storage.user

    if user.get("username", None) != "11m3edu_4dmin":
        app.storage.user.clear()
        print(user.get("username", None))
        return RedirectResponse("/login")

    builder = AdminPageBuilder(cfg, user=user)
    builder.build()
    add_footer()

if __name__ in {"__main__", "__mp_main__"}:
    create_database()
    app.add_static_files("/assets", "src/assets")

    asyncio.run(async_create_database())
    ui.run(
        port=args.port,
        title="LLM4Edu",
        favicon="src/assets/icon.png",
        storage_secret="THIS_NEEDS_TO_BE_CHANGED",
    )
