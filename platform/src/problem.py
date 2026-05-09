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

# from codemirror import CodeMirror
from database import (
    async_add_user_action,
    async_get_latest_action_value,
    get_actions,
    get_latest_action_value,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import AzureChatOpenAI, ChatOpenAI
from markdown import Markdown
from nicegui import app, run, ui
from problemset import load_problemset
from pyexec import sandbox_run_python
from pyjudge import judge_code, judge_code_async
from utils import io_he, io_rhe, log_event

TIMEOUT = 5

STAGE_MAX_TIME = {
    "learning": 40 * 60,
    "a1": 20 * 60,
    "a2": 20 * 60,
    "review": 20 * 60,
    "test": 20 * 60,
}

STAGE_NAME_MAP = {
    "learning": "课程学习",
    "a1": "完成作业 1",
    "a2": "完成作业 2",
    "review": "课程复习",
    "test": "测试",
}


class ProbelmPageBuilder:
    def __init__(self, cfg, stage, user=None, show_answer=False):
        self.cfg = cfg
        self.user = user
        self.username = user.get("username", None)

        self.show_answer = show_answer
        self.stage = stage

        self.vgroup = cfg.uservgroup(self.username)
        self.working_group = cfg.getvgroup(self.vgroup, f"{stage}_group")
        self.course = "py" if self.vgroup.startswith("py") else "math"

        if self.course == "py":
            pnames = cfg.getgroup(self.working_group, "code_tab", "available_problem")
        else:
            pnames = cfg.getgroup(self.working_group, "math_tab", "available_problem")

        if stage == "review":
            a1_working_group = cfg.getvgroup(self.vgroup, "a1_group")
            if self.course == "py":
                a1_pnames = cfg.getgroup(
                    a1_working_group, "code_tab", "available_problem"
                )
            else:
                a1_pnames = cfg.getgroup(
                    a1_working_group, "math_tab", "available_problem"
                )
            pnames = a1_pnames + pnames

        (
            self.problem_titles,
            self.pname2title,
            self.title2pname,
            self.questions,
        ) = load_problemset(pnames, self.course)

        api_type = cfg.get("chat_tab", "openai_api_type") or "openai"

        self.gpt_enabled = self.cfg.getgroup(self.working_group, "chat_tab", "enabled")
        if self.gpt_enabled:
            self._init_chat(api_type, cfg)

        self.current_problem = self.title2pname[self.problem_titles[0]]
        self.get_question_status()

        progress_values = get_actions(self.username, "progress")
        for i in progress_values:
            if i.value["stage"] == STAGE_NAME_MAP[stage]:
                self.start_time = i.timestamp
                break

    def get_question_status(self):
        self.question_status = {}

        if self.course == "py":
            for p in self.questions:
                p_judge = get_latest_action_value(
                    self.username,
                    f"{p}::judge",
                )
                if p_judge is None:
                    self.question_status[p] = {"tried": False, "solved": False}
                elif p_judge["judge_ret"]["solved"]:
                    self.question_status[p] = {"tried": True, "solved": True}
                else:
                    self.question_status[p] = {"tried": True, "solved": False}
        else:
            for p in self.questions:
                p_judge = get_latest_action_value(
                    self.username,
                    f"{p}::submit",
                )
                if p_judge is None:
                    self.question_status[p] = {"tried": False}
                else:
                    self.question_status[p] = {"tried": True}

    def _init_chat(self, api_type, cfg):
        output_parser = StrOutputParser()

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
        self.chain = self.chat | output_parser

    def build(self):
        ui.add_head_html(
            """<style>
            .q-drawer--right { width: 30% !important }
            .large-textarea .q-field__control { height: 100%; }
            .q-scrollarea__content {max-width: 100%;}
            .q-message-container div {max-width: 100%;}
            .codehilite {
                overflow-x: scroll;
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
                    inlineMath: [ ['$','$'], ["\\(","\\)"], ["\\[","\\]"]],
                    displayMath: [ ['$$','$$'], ["\\[","\\]"], ["\\(","\\)"]],
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
                    ui.notify("时间已到,即将返回主页", position="center", level="warning")

                    # Force redirect via JavaScript to ensure it succeeds
                    referrer_path = app.storage.user.get("referrer_path", "/progress")
                    ui.run_javascript(
                        f"""
                        setTimeout(function() {{
                            window.location.href = '{referrer_path}';
                        }}, 500);
                    """
                    )

                    # As a fallback, still run the original redirect logic
                    ui.navigate.to(referrer_path)

            label = ui.label().classes("text-white px-10")
            ui.timer(1.0, update_timer)

        with ui.row().classes("w-full h-full grid grid-cols-12"):
            with ui.card().classes("grow h-screen grid-cols-subgrid col-span-2"):
                with ui.scroll_area().classes("w-full h-screen"):
                    self.build_question_page()

            with ui.row().classes(
                "grow w-full h-d v h grid-cols-subgrid col-span-10 grid grid-cols-12"
            ):
                if self.course == "py" or self.gpt_enabled:
                    with ui.card().classes(
                        "grow h-screen grid-cols-subgrid col-span-8"
                    ):
                        with ui.scroll_area().classes("w-full h-screen"):
                            self.build_answer_page()

                    with ui.card().classes(
                        "grow h-screen grid-cols-subgrid col-span-4"
                    ):
                        # with ui.scroll_area().classes("w-full h-full"):
                        self.chat_upload_images()
                        self.build_chat_page()
                else:
                    with ui.card().classes("grow h-full grid-cols-subgrid col-span-12"):
                        with ui.scroll_area().classes("w-full h-screen"):
                            self.build_answer_page()

        ui.run_javascript(
            """
            const header = getElement(4).$el;
            window.scrollTo(0, header.scrollHeight);
            """
        )

    @ui.refreshable
    def build_question_page(self):
        def change_problem_fn(q):
            async def fn():
                self.current_problem = q
                self.build_answer_page.refresh()
                self.build_chat_page.refresh()

                await async_add_user_action(
                    self.username,
                    f"{self.current_problem}::click",
                    {"stage": self.stage, "pname": self.current_problem},
                )

            return fn

        ui.html("<h3>题目列表</h3>").classes("markdown-body")

        add_seperator = False
        for q in self.questions:
            status = self.question_status[q]

            if self.stage == "review" and "review" in q and not add_seperator:
                ui.separator()
                add_seperator = True

            button = (
                ui.button(self.pname2title[q])
                .on("click", change_problem_fn(q))
                .classes("w-full")
            )

            if self.course == "py":
                if status["tried"] and status["solved"]:
                    button.props("color=primary")
                elif status["tried"] and not status["solved"]:
                    button.props("color=orange")
                else:
                    button.props("outline")
            else:
                if status["tried"]:
                    button.props("color=primary")
                else:
                    button.props("outline")

    @ui.refreshable
    def build_status_tag(self):
        status = self.question_status[self.current_problem]
        tried = status["tried"]
        if self.course == "py":
            solved = status["solved"]
            if not tried and not solved:
                html = f"<small>未尝试</small>"
            elif tried and not solved:
                html = f"<small>正在尝试 💡</small>"
            else:
                html = f"<small>已通过 ✅</small>"
        else:
            if not tried:
                html = f"<small>未提交</small>"
            else:
                html = f"<small>已提交 ✅</small>"
        ui.html(html)

    @ui.refreshable
    def build_answer_page(self):
        last_textarea_content = None

        with ui.column().classes("flex item-center w-full h-full"):

            def clear_judge():
                self.judge_detailed_rslt.set_content("")
                self.judge_overall_rslt.set_content("")

            def build_desc(question):
                if self.course == "py":
                    valid_cases = question["validcases"]
                    examples_text = ""
                    for idx, case in enumerate(valid_cases):
                        examples_text += f"**Example {idx+1}**\n\n"
                        examples_text += f"Input: `{io_rhe(case['input'])}`, Output: `{io_rhe(case['output'])}`\n\n"
                        examples_text += f"Comment: `{case['comment']}`\n\n"
                        examples_text += "\n"
                    description = question["description"]
                    description += "\n\n"
                    description += examples_text
                    markdown_text = description
                else:
                    markdown_text = question["description"]

                html_output = markdown.markdown(markdown_text, extensions=["tables"])
                return html_output

            with ui.row().classes("w-full"):
                self.build_status_tag()

            with ui.row().classes("w-full"):
                ui.html(build_desc(self.questions[self.current_problem])).classes(
                    "markdown-body"
                )

            def get_pcode(pname):
                nonlocal last_textarea_content
                latest_answer = get_latest_action_value(
                    self.username, f"{pname}::answer"
                )
                if latest_answer:
                    pcode = latest_answer["value"]
                else:
                    if self.course == "py":
                        pcode = self.questions[pname]["code_template"]
                    else:
                        pcode = self.questions[pname]["math_template"]
                last_textarea_content = pcode
                return pcode

            if self.show_answer:

                async def log_show_answer():
                    await async_add_user_action(
                        self.username,
                        f"{self.current_problem}::show_answer",
                        {
                            "stage": self.stage,
                            "pname": self.current_problem,
                            "status": self.answer_expand.value,
                        },
                    )

                with ui.expansion("点击查看题目答案", on_value_change=log_show_answer).classes(
                    "text-base bg-zinc-100 w-full"
                ) as self.answer_expand:
                    ui.markdown(
                        markdown.markdown(
                            self.questions[self.current_problem]["answer"],
                            extensions=["tables"],
                        )
                        if self.course == "math"
                        else self.questions[self.current_problem]["answer"]
                    ).classes("w-full")

            with ui.row().classes("w-full").classes("outline-double"):
                self.textarea = (
                    ui.codemirror(
                        value=get_pcode(self.current_problem), language="Python"
                    )
                    # .classes("w-2/3 h-52 text-base large-textarea")
                    # .props("rounded outlined input-class=mx-3")
                )
            with ui.row():
                submit_button = ui.button("提交")

            with ui.row():
                self.judge_overall_rslt = ui.markdown()

            with ui.row():
                self.judge_spin = ui.spinner(size="lg")
                # spin.set_visibility(False)
                self.judge_detailed_rslt = ui.markdown()
                self.judge_spin.set_visibility(False)

            self.judge_overall_rslt.set_content("")
            self.judge_detailed_rslt.set_content("")

            async def submit_answer():
                if self.course == "py":
                    self.judge_overall_rslt.set_content("")
                    self.judge_detailed_rslt.set_content("")
                    self.judge_spin.set_visibility(True)
                    (
                        judge_ret,
                        result,
                        detailed_result,
                    ) = await self.generate_judge_message()
                    self.judge_spin.set_visibility(False)
                    self.judge_overall_rslt.set_content(result)
                    self.judge_detailed_rslt.set_content(detailed_result)

                    await async_add_user_action(
                        self.username,
                        f"{self.current_problem}::judge",
                        {
                            "stage": self.stage,
                            "value": self.textarea.value,
                            "judge_ret": judge_ret,
                        },
                    )

                    self.question_status[self.current_problem]["tried"] = True

                    if judge_ret["solved"]:
                        self.question_status[self.current_problem]["solved"] = True
                    else:
                        self.question_status[self.current_problem]["solved"] = False
                else:
                    await async_add_user_action(
                        self.username,
                        f"{self.current_problem}::submit",
                        {"stage": self.stage, "value": self.textarea.value},
                    )
                    ui.notify("已提交", type="positive")
                    self.question_status[self.current_problem]["tried"] = True

                self.build_status_tag.refresh()
                self.build_question_page.refresh()

            async def record_change():
                nonlocal last_textarea_content
                current_content = self.textarea.value

                if current_content != last_textarea_content:
                    await async_add_user_action(
                        self.username,
                        f"{self.current_problem}::answer",
                        {"stage": self.stage, "value": current_content},
                    )
                    last_textarea_content = current_content

            submit_button.on("click", submit_answer)
            ui.timer(5, record_change)

            ui.run_javascript(
                'MathJax.typesetPromise().catch(err => console.error("Typeset failed: " + err.message));'
            )

    def get_chat_hist(self, pname):
        pname_msg = get_latest_action_value(self.username, f"{pname}::chat")
        if pname_msg:
            return pname_msg["messages"]
        return []

    @ui.refreshable
    def build_chat_page(self):
        with ui.column().classes("w-full h-full"):
            messages: List[Tuple[str, str]] = self.get_chat_hist(self.current_problem)
            latest_ai_message = ""

            def recall_messages():
                nonlocal messages
                messages = self.get_chat_hist(self.current_problem)
                chat_messages.refresh()

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
                answer = self.textarea.value
                for name, content in messages:
                    if name != "You":
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
                            sent=name == "You",
                            text_html=True,
                        ).classes("w-full markdown-body").props("bg-color=grey-3")
                    else:
                        with ui.chat_message(
                            name="", sent=name == "You", text_html=True
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
                messages.append(("You", curr_messages))
                text.value = ""
                chat_messages.refresh()

                self.images = []
                self.show_images.refresh()

                messages.append(("Bot", latest_ai_message))
                async for chunk in self.respond(
                    messages,
                    self.current_problem,
                    {
                        "pname": self.current_problem,
                        "cur_code": self.textarea.value,
                        "cur_result": self.judge_overall_rslt.content,
                        "cur_detailed_result": self.judge_detailed_rslt.content,
                    },
                ):
                    latest_ai_message += chunk
                    messages[-1] = ("Bot", latest_ai_message)
                    latest_message.refresh()
                    # scroll_area.scroll_to(percent=1.0)
                latest_ai_message = ""
                latest_message.refresh()
                chat_messages.refresh()

                await async_add_user_action(
                    self.username,
                    f"{self.current_problem}::chat",
                    {
                        "stage": self.stage,
                        "pname": self.current_problem,
                        "messages": messages,
                    },
                )

            async def clear_message() -> None:
                messages.clear()
                chat_messages.refresh()

                await async_add_user_action(
                    self.username,
                    f"{self.current_problem}::chat",
                    {
                        "stage": self.stage,
                        "pname": self.current_problem,
                        "messages": messages,
                    },
                )

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

                pname = self.current_problem
                await async_add_user_action(
                    self.username,
                    f"{pname}::python",
                    {"stage": self.stage, "value": taskcode, "judge_ret": ret},
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
            ).classes("w-full max-w-2xl mx-auto h-full items-stretch"):
                if self.gpt_enabled:
                    with ui.tab_panel(chat_tab).classes("items-stretch h-full p-0 m-0"):
                        with ui.scroll_area().classes(
                            "w-full h-4/6 border"
                        ) as scroll_area:
                            chat_messages()
                            latest_message()
                        placeholder = "输入消息"
                        with ui.row().classes("w-full"):
                            self.show_images()

                            text = (
                                ui.textarea(placeholder=placeholder)
                                .props("rounded outlined input-class=mx-3")
                                .classes("mychatbox w-full self-center")
                                .style("white-space: pre-wrap;")
                            )
                            send_button = (
                                ui.button("发送").on("click", send).classes("self-center")
                            )
                            clear_button = (
                                ui.button("清空")
                                .on("click", clear_message)
                                .classes("self-center")
                            )


                def recall_python(pname):
                    python_value = get_latest_action_value(
                        self.username, f"{pname}::python"
                    )
                    if python_value:
                        return python_value["value"]
                    return ""

                if self.course == "py":
                    with ui.tab_panel(python_tab).classes("items-stretch h-full"):
                        with ui.row().classes("w-full"):
                            with ui.row().classes("w-full outline-double"):
                                python_text = (
                                    ui.codemirror(
                                        recall_python(self.current_problem),
                                        language="Python",
                                    )
                                    .props("rounded outlined input-class=mx-3")
                                    .classes("w-full self-center")
                                )
                            exec_button = ui.button("执行").classes("self-center")

                        with ui.row():
                            self.exec_spin = ui.spinner(size="lg")
                            self.exec_rslt = ui.markdown()

                        self.exec_spin.set_visibility(False)
                        self.exec_rslt.set_content("")

                        exec_button.on("click", submit_code)

        ui.run_javascript("paste_clipboard_listener();")

    async def respond(self, chat_history, pname, context_dict):
        if not self.gpt_enabled:
            yield "Not available."

        lc_history = []
        # context_dict = dict(zip(["pname", "cur_answer"], context_infos))

        system_prompt = get_gpt_prompt(pname, context_dict)

        lc_history.append(SystemMessage(content=system_prompt))

        for role, message in chat_history:
            if role == "You":
                lc_history.append(HumanMessage(content=message))
            if role == "Bot":
                lc_history.append(AIMessage(content=message))

        async for chunk in self.chat.astream(lc_history):
            yield (chunk.content)

    async def generate_judge_message(self):
        pname = self.current_problem
        problem = self.questions[pname]
        answer = self.textarea.value
        testcases = [(case["input"], case["output"]) for case in problem["testcases"]]
        ret = await run.cpu_bound(
            judge_code, answer, problem["code_entrypoint"], testcases
        )

        finished = ret["exec_result"] == "finished"
        passed = finished and all([x["passed"] for x in ret["output"]])
        ret["solved"] = passed

        result, detailed_result = "", ""
        if ret["exec_result"] == "finished":
            # if passed:
            #     mark_solved(pname, taskcode, request)
            result += "全部运行完成。" + ("测试通过。✅" if passed else "测试未通过。❌")
            flag_first_error = True
            for idx, ((case_input, case_expected), case) in enumerate(
                zip(testcases, ret["output"])
            ):
                flag = "✅" if case["passed"] else "❌"
                detailed_result += f"**Case {idx+1} {flag}**\n\n"
                if not case["passed"] and flag_first_error:
                    flag_first_error = False
                    detailed_result += f"Input: `{io_rhe(case_input)}`, Output: `{io_he(case['output'])}`\n\n"
                    detailed_result += f"Expected: `{io_rhe(case_expected)}`\n\n"
                    detailed_result += f"Messages: `{case['message']}`\n\n"
                    detailed_result += "\n\n"
        else:
            result += f"运行出错，错误原因：{ret['exec_result']}。\n"
        return ret, result, detailed_result

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


if __name__ in {"__main__", "__mp_main__"}:
    page_builder = ProbelmPageBuilder()
    page_builder.build()
    ui.run()
