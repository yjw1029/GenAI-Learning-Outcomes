import re
import time
from typing import List, Tuple

import markdown
from azure.identity import (
    AzureCliCredential,
    DefaultAzureCredential,
    get_bearer_token_provider,
)
from chat_util import get_gpt_prompt
from database import (
    async_add_user_action,
    async_get_latest_action_value,
    get_actions,
    get_latest_action_value,
)
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import AzureChatOpenAI, ChatOpenAI
from nicegui import app, run, ui
from problemset import load_problemset
from pyexec import sandbox_run_python
from pyjudge import judge_code, judge_code_async

TIMEOUT = 5

resources = {
    "Python基础教程": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B.pdf",
    "Python教程视频": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E6%95%99%E5%AD%A6%E8%A7%86%E9%A2%91.mp4",
    "博弈论基础教程": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B.pdf",
    "博弈论基础视频": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80.mp4",
}

STAGE_MAX_TIME = {"learning": 40 * 60, "a1": 20 * 60, "a2": 20 * 60, "review": 20 * 60}

STAGE_NAME_MAP = {
    "learning": "课程学习",
    "a1": "完成作业 1",
    "a2": "完成作业 2",
    "review": "课程复习",
}


class LearningPageBuilder:
    def __init__(self, cfg, stage, user=None):
        self.cfg = cfg
        self.user = user
        self.username = user.get("username", None)
        self.stage = stage

        self.vgroup = cfg.uservgroup(self.username)
        self.working_group = cfg.getvgroup(self.vgroup, f"{stage}_group")
        self.course = "py" if self.vgroup.startswith("py") else "math"

        if self.course == "py":
            self.video_url = resources["Python教程视频"]
            self.pdf_url = resources["Python基础教程"]
        else:
            self.video_url = resources["博弈论基础视频"]
            self.pdf_url = resources["博弈论基础教程"]

        api_type = cfg.get("chat_tab", "openai_api_type") or "openai"

        self.gpt_enabled = self.cfg.getgroup(self.working_group, "chat_tab", "enabled")
        if self.gpt_enabled:
            self._init_chat(api_type, cfg)

        progress_values = get_actions(self.username, "progress")
        for i in progress_values:
            if i.value["stage"] == STAGE_NAME_MAP[stage]:
                self.start_time = i.timestamp
                break

    def _init_chat(self, api_type, cfg):
        output_parser = StrOutputParser()

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        if api_type == "azure":
            self.credential = AzureCliCredential()

            token_provider = get_bearer_token_provider(
                self.credential, "https://cognitiveservices.azure.com/.default"
            )

            self.chat = AzureChatOpenAI(
                azure_endpoint=cfg.get("chat_tab", "azure_endpoint"),
                # api_key=cfg.get("chat_tab", "openai_api_key"),
                azure_ad_token_provider=token_provider,
                azure_deployment=cfg.get("chat_tab", "openai_model"),
                api_version="2024-02-15-preview",
                streaming=True,
                max_tokens=4096,
            )
        elif api_type == "openai":
            self.chat = ChatOpenAI(
                base_url=cfg.get("chat_tab", "openai_base_url"),
                api_key=cfg.get("chat_tab", "openai_api_key"),
                model=cfg.get("chat_tab", "openai_model"),
                streaming=True,
                max_tokens=4096,
            )
        else:
            raise ValueError(f"Unknown api_type: {api_type}")
        self.chain = prompt | self.chat | output_parser

    def build(self):
        ui.add_head_html(
            """<style>
            .q-drawer--right { width: 30% !important }
            .large-textarea .q-field__control { height: 100%; }
            .q-scrollarea__content {max-width: 100%;}
            .q-message-container div {max-width: 100%;}
            .codehilite {
                overflow-x: auto;
                display: block;
                white-space: nowrap;
                max-width: 100%;
            }
            </style>

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.css">

            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

            <script type="text/x-mathjax-config">
            MathJax.Hub.Config({
                tex2jax: {
                    inlineMath: [ ['$','$'], ["\\(","\\)"] ],
                    displayMath: [ ['$$','$$'], ["\\[","\\]"] ],
                    processEscapes: true,
                }
            })
            </script>
            """
        )

        with ui.header().classes("p-0 h-fit flex items-center") as header:
            ui.button(f"{self.user['username']}", icon="person").props(
                "flat color=white width=200px"
            )
            ui.button(
                "退出登录",
                icon="logout",
                on_click=lambda: (app.storage.user.clear(), ui.navigate.to("/login")),
            ).props("flat color=white width=200px")
            ui.button(
                "返回主页",
                icon="chevron_left",
                on_click=lambda: ui.navigate.to("/progress"),
            ).props("flat color=white width=200px")

            def update_timer():
                countdown_time = int(
                    self.start_time + STAGE_MAX_TIME[self.stage] - time.time()
                )
                if countdown_time >= 0:
                    mins, secs = divmod(countdown_time, 60)
                    hours, mins = divmod(mins, 60)
                    timeformat = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
                    label.set_text(f"当前阶段剩余: {timeformat}")

                    if countdown_time == 60:
                        ui.notify("本阶段还有1分钟结束", position="center", level="info")
                else:
                    label.set_text("倒计时结束")
                    ui.navigate.to(app.storage.user.get("referrer_path", "/progress"))

            label = ui.label().classes("text-white px-10")
            ui.timer(1.0, update_timer)

        with ui.row().classes("grow w-full grid grid-cols-12"):
            if self.course == "py" or self.gpt_enabled:
                span = "col-span-8"
            else:
                span = "col-start-3 col-span-8"

            with ui.card().classes(f"h-screen grid-cols-subgrid {span}"):
                with ui.tabs().classes("w-full") as tabs:
                    app.storage.user["learning_tab_activated"] = "video"

                    async def on_tab_video_click():
                        app.storage.user["learning_tab_activated"] = "video"

                    async def on_tab_pdf_click():
                        app.storage.user["learning_tab_activated"] = "pdf"

                    ui.tab("视频").on("click", on_tab_video_click)
                    ui.tab("PDF").on("click", on_tab_pdf_click)

                ui.video(self.video_url).classes("w-full h-full").bind_visibility_from(
                    app.storage.user, "learning_tab_activated", value="video"
                )
                ui.html(
                    f'<embed src="{self.pdf_url}" type="application/pdf" width="90%" height="100%"></embed>'
                ).classes(
                    "w-full h-full grow flex justify-center"
                ).bind_visibility_from(
                    app.storage.user, "learning_tab_activated", value="pdf"
                )

            if self.course == "py" or self.gpt_enabled:
                with ui.card().classes("h-screen grid-cols-subgrid col-span-4"):
                    self.chat_upload_images()
                    self.build_chat_page()

        ui.run_javascript(
            """
            const header = getElement(4).$el;
            window.scrollTo(0, header.scrollHeight);
            """
        )

    def get_chat_hist(self):
        pname_msg = get_latest_action_value(self.username, f"learning::chat")
        if pname_msg:
            return pname_msg["messages"]
        return []

    def build_chat_page(self):
        with ui.column().classes("w-full h-full"):
            messages: List[Tuple[str, str]] = self.get_chat_hist()
            latest_ai_message = ""

            def replace_asterisk_in_math(content):
                def replace_asterisk(match):
                    return match.group(0).replace("*", r"\*")

                content = re.sub(
                    r"(\\\\\[.*?\\\\\])|(\\\\\(.*?\\\\\))",
                    replace_asterisk,
                    content,
                    flags=re.DOTALL,
                )

                return content

            @ui.refreshable
            def chat_messages() -> None:
                for name, content in messages:
                    if name != "human":
                        content = (
                            content.replace("\\\\", "\\\\\\\\")
                            .replace("\\[", "\\\\[")
                            .replace("\\]", "\\\\]")
                            .replace("\\(", "\\\\(")
                            .replace("\\)", "\\\\)")
                        )
                        content = replace_asterisk_in_math(content)
                        ui.chat_message(
                            markdown.markdown(
                                content,
                                extensions=["tables", "codehilite", "fenced_code"],
                            ),
                            name="",
                            sent=name == "human",
                            text_html=True,
                        ).classes("w-full markdown-body").props("bg-color=grey-2")
                    else:
                        with ui.chat_message(
                            name="", sent=name == "human", text_html=True
                        ).classes("w-full markdown-body").props(
                            "bg-color=primary text-color=white"
                        ):
                            if isinstance(content, list):
                                for c in content:
                                    if c["type"] == "text":
                                        ui.html(
                                            markdown.markdown(
                                                c["text"],
                                                extensions=[
                                                    "tables",
                                                    "codehilite",
                                                    "fenced_code",
                                                ],
                                            )
                                        )
                                    elif c["type"] == "image_url":
                                        ui.image(source=c["image_url"]["url"])
                            else:
                                ui.html(
                                    markdown.markdown(
                                        content,
                                        extensions=[
                                            "tables",
                                            "codehilite",
                                            "fenced_code",
                                        ],
                                    )
                                )

                ui.run_javascript(
                    'MathJax.typesetPromise().catch(err => console.error("Typeset failed: " + err.message));'
                )

            @ui.refreshable
            def latest_message() -> None:
                if latest_ai_message != "":
                    content = latest_ai_message
                    content = (
                        content.replace("\\\\", "\\\\\\\\")
                        .replace("\\[", "\\\\[")
                        .replace("\\]", "\\\\]")
                        .replace("\\(", "\\\\(")
                        .replace("\\)", "\\\\)")
                    )
                    content = replace_asterisk_in_math(content)
                    ui.chat_message(
                        markdown.markdown(
                            content,
                            extensions=["tables", "codehilite", "fenced_code"],
                        ),
                        name="",
                        sent=False,
                        text_html=True,
                    ).classes("w-full markdown-body").props("bg-color=grey-2")

                ui.run_javascript(
                    'MathJax.typesetPromise().catch(err => console.error("Typeset failed: " + err.message));'
                )

            async def send() -> None:
                nonlocal latest_ai_message
                curr_messages = [{"type": "text", "text": text.value}] + [
                    {"type": "image_url", "image_url": {"url": base64_image}}
                    for base64_image in self.images
                ]

                messages.append(("human", curr_messages))
                text.value = ""
                chat_messages.refresh()
                self.images = []
                self.show_images.refresh()

                messages.append(("ai", latest_ai_message))
                async for chunk in self.chain.astream({"messages": messages[:-1]}):
                    latest_ai_message += chunk
                    messages[-1] = ("ai", latest_ai_message)
                    latest_message.refresh()
                    # scroll_area.scroll_to(percent=1.0)
                latest_ai_message = ""
                latest_message.refresh()
                chat_messages.refresh()

                await async_add_user_action(
                    self.username,
                    f"learning::chat",
                    {"messages": messages},
                )

            async def clear_message() -> None:
                messages.clear()
                chat_messages.refresh()

                await async_add_user_action(
                    self.username,
                    f"learning::chat",
                    {"messages": messages},
                )

            # the queries below are used to expand the contend down to the footer (content can then use flex-grow to expand)
            ui.query(".q-page").classes("flex")
            ui.query(".nicegui-content").classes("w-full")

            with ui.tabs().classes("w-full") as tabs:
                if self.gpt_enabled:
                    chat_tab = ui.tab("对话")
                if self.course == "py":
                    python_tab = ui.tab("Python")

            with ui.tab_panels(
                tabs, value=chat_tab if self.gpt_enabled else python_tab
            ).classes("w-full h-screen items-stretch").props():
                if self.gpt_enabled:
                    with ui.tab_panel(chat_tab).classes("items-stretch h-full w-full"):
                        with ui.scroll_area().classes(
                            "w-full h-4/6 border"
                        ) as scroll_area:
                            chat_messages()
                            latest_message()
                            scroll_area.scroll_to(percent=1.0)
                        placeholder = "输入消息"
                        with ui.row().classes("w-full"):
                            self.show_images()

                            text = (
                                ui.textarea(placeholder=placeholder)
                                .props("rounded outlined input-class=mx-3")
                                .classes("mychatbox w-full self-center")
                            )
                            send_button = (
                                ui.button("发送").on("click", send).classes("self-center")
                            )
                            clear_button = (
                                ui.button("清空")
                                .on("click", clear_message)
                                .classes("self-center")
                            )

                def recall_python():
                    python_value = get_latest_action_value(
                        self.username, f"learning::python"
                    )
                    if python_value:
                        return python_value["value"]
                    return ""

                if self.course == "py":
                    with ui.tab_panel(python_tab).classes("items-stretch h-full"):
                        with ui.row().classes("w-full"):
                            with ui.row().classes("w-full outline-double"):
                                python_text = (
                                    ui.codemirror(recall_python(), language="Python")
                                    .props("rounded input-class=mx-3")
                                    .classes("w-full self-center")
                                )
                            exec_button = ui.button("执行").classes("self-center")

                        with ui.row():
                            self.exec_spin = ui.spinner(size="lg")
                            self.exec_rslt = ui.markdown()

                        self.exec_spin.set_visibility(False)
                        self.exec_rslt.set_content("")

        async def submit_code():
            self.exec_rslt.set_content("")
            self.exec_spin.set_visibility(True)

            taskcode = python_text.value
            timeout = TIMEOUT

            ret = await run.cpu_bound(sandbox_run_python, taskcode, timeout)
            exec_result = ret["exec_result"] if ret["exec_result"] else ""
            exec_status = ret["status"]
            exce_rslt = (
                "**执行状态:**\n\n"
                f"{exec_status}\n\n"
                "**执行结果:**\n\n"
                f"```\n{exec_result}\n```"
            )
            self.exec_spin.set_visibility(False)
            self.exec_rslt.set_content(exce_rslt)

            await async_add_user_action(
                self.username,
                f"learning::python",
                {"value": taskcode, "judge_ret": ret},
            )

        if self.course == "py":
            exec_button.on("click", submit_code)

        ui.run_javascript("paste_clipboard_listener();")

    def chat_upload_images(self):
        self.images = []
        ui.add_head_html(
            """
        <script>
            function paste_clipboard_listener() {
                document.querySelector('.mychatbox textarea').addEventListener('paste', function(event) {
                    var items = (event.clipboardData || event.originalEvent.clipboardData).items;
                    for (index in items) {
                        var item = items[index];
                        if (item.kind === 'file' && item.type.indexOf('image/') !== -1) {
                            const file = item.getAsFile();
                            const reader = new FileReader();
                            reader.onload = async (event) => {
                                const base64 = event.target.result;
                                emitEvent('paste_image', {file: base64});
                            };
                            reader.readAsDataURL(file);
                        }
                    }
                });
            };
        </script>
        """
        )

        async def display(x) -> None:
            file_path = x.args["file"].strip('"')
            self.images.append(file_path)
            self.show_images.refresh()

        ui.on("paste_image", display)

    @ui.refreshable
    def show_images(self):
        with ui.row():
            for i, image in enumerate(self.images):
                with ui.column().style("position: relative;") as img_div:
                    image_display = (
                        ui.image(source=image)
                        .props("width=50px height=50px")
                        .style("border: 1px solid gray; border-radius: 10px;")
                    )

                    delete_button = (
                        ui.badge("X", color="white", text_color="black")
                        .props("outline rounded")
                        .style(
                            "border: 1px solid gray; position: absolute; top: -8px; right: -8px; cursor: pointer"
                        )
                        .tooltip("删除图片")
                    )
                    delete_button.set_visibility(False)

                    def on_mouse_enter_wrap(delete_button):
                        def on_mouse_enter():
                            delete_button.set_visibility(True)

                        return on_mouse_enter

                    def on_mouse_leave_wrap(delete_button):
                        def on_mouse_leave():
                            delete_button.set_visibility(False)

                        return on_mouse_leave

                    def delete_image_wrap(image):
                        def delete_image():
                            self.images.remove(image)
                            self.show_images.refresh()

                        return delete_image

                    img_div.on("mouseenter", on_mouse_enter_wrap(delete_button))
                    img_div.on("mouseleave", on_mouse_leave_wrap(delete_button))

                    delete_button.on("click", delete_image_wrap(image))
