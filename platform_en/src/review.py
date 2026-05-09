from typing import List, Tuple

from chat_util import get_gpt_prompt
from database import (
    async_add_user_action,
    async_get_latest_action_value,
    get_latest_action_value,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import AzureChatOpenAI, ChatOpenAI
from nicegui import app, run, ui
from problemset import load_problemset
from pyexec import sandbox_run_python
from pyjudge import judge_code, judge_code_async
from utils import io_he, io_rhe, log_event

TIMEOUT = 5


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

    def _init_chat(self, api_type, cfg):
        output_parser = StrOutputParser()

        if api_type == "azure":
            self.chat = AzureChatOpenAI(
                azure_endpoint=cfg.get("chat_tab", "azure_endpoint"),
                api_key=cfg.get("chat_tab", "openai_api_key"),
                azure_deployment=cfg.get("chat_tab", "openai_model"),
                api_version="2023-09-01-preview",
                streaming=True,
                max_tokens=512,
            )
        elif api_type == "openai":
            self.chat = ChatOpenAI(
                base_url=cfg.get("chat_tab", "openai_base_url"),
                api_key=cfg.get("chat_tab", "openai_api_key"),
                model=cfg.get("chat_tab", "openai_model"),
                streaming=True,
                max_tokens=512,
            )
        else:
            raise ValueError(f"Unknown api_type: {api_type}")
        self.chain = self.chat | output_parser

    @property
    def pname(self):
        return self.title2pname[self.select1.value]

    def build(self):
        ui.add_head_html(
            """<style>
            .q-drawer--right { width: 30% !important }
            .large-textarea .q-field__control { height: 100%; }
            </style>
            """
        )
        with ui.header().classes("p-0") as header:
            with ui.button(icon="person").props("flat color=white width=200px"):
                with ui.menu() as menu:
                    ui.menu_item(f"{self.username}")
                    ui.separator()
                    ui.menu_item("Back to home", lambda: ui.navigate.to("/progress"))
                    ui.menu_item(
                        "Log out",
                        lambda: (app.storage.user.clear(), ui.navigate.to("/login")),
                    )
                    ui.separator()
                    ui.menu_item("Close", on_click=menu.close)

            with ui.button("Problem List", icon="list").props("flat color=white width=200px"):
                ui.tooltip("Show all problems").classes("text-sm")

            with ui.button(icon="chevron_left").props("flat color=white width=200px"):
                ui.tooltip("Previous").classes("text-sm")

            with ui.button(icon="chevron_right").props("flat color=white width=200px"):
                ui.tooltip("Next").classes("text-sm")

            if self.course == "py" or self.gpt_enabled:
                with ui.button(
                    on_click=lambda: right_drawer.toggle(), icon="menu"
                ).props("flat color=white").classes("ml-auto"):
                    ui.tooltip("Toggle right sidebar").classes("text-sm")

        with ui.row().style("width: 100%").classes("flex item-center w-full h-full"):
            self.build_answer_page()

        if self.course == "py" or self.gpt_enabled:
            with ui.right_drawer(elevated=True).classes(
                "chat-drawer bg-white-100"
            ) as right_drawer:
                self.build_chat_page()

    def build_answer_page(self):
        last_textarea_content = None

        with ui.column().classes("flex item-center w-full h-full"):

            def clear_judge():
                self.judge_detailed_rslt.set_content("")
                self.judge_overall_rslt.set_content("")

            with ui.row().classes("w-full grid grid-cols-5 items-end"):
                # ui.label("Currently working on:")
                self.select1 = ui.select(
                    self.problem_titles,
                    value=self.problem_titles[0],
                    on_change=clear_judge,
                ).classes("col-start-2 col-end-3 text-base")

                def update_timer():
                    countdown_time = int(sec_label.text)
                    if countdown_time >= 0:
                        # Convert remaining time to hours:minutes:seconds
                        mins, secs = divmod(countdown_time, 60)
                        hours, mins = divmod(mins, 60)
                        timeformat = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
                        label.set_text(f"Time left in current stage: {timeformat}")
                        countdown_time -= 1
                        sec_label.set_text(str(countdown_time))

                        if countdown_time == 60:
                            ui.notify("1 minute left in this stage", position="center", level="info")
                    else:
                        label.set_text("Countdown finished")
                        ui.navigate.to(
                            app.storage.user.get("referrer_path", "/progress")
                        )

                with ui.column().classes("w-full my-auto"):
                    sec_label = ui.label(text=20 * 60)
                    sec_label.set_visibility(False)
                    label = ui.label().classes("text-red-500 text-base")
                    # Set a timer to update every second
                    ui.timer(1.0, update_timer)

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
                    return description
                else:
                    return question["description"]

            with ui.row().classes("w-full").style("padding-right: 150px"):
                ui.markdown().bind_content_from(
                    self.select1,
                    "value",
                    backward=lambda a: build_desc(self.questions[self.title2pname[a]]),
                )

            def get_pcode(ptitle):
                nonlocal last_textarea_content
                pname = self.title2pname[ptitle]
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

            with ui.row().classes("w-full"):
                self.textarea = (
                    ui.textarea(value="")
                    .classes("w-2/3 h-52 text-base large-textarea")
                    .props("rounded outlined input-class=mx-3")
                    .bind_value_from(
                        self.select1,
                        "value",
                        backward=get_pcode,
                    )
                )
            with ui.row():
                submit_button = ui.button("Submit")

            if self.show_answer:
                with ui.expansion("Solutions").classes("text-base bg-zinc-100 w-4/6"):
                    ui.markdown().bind_content_from(
                        self.select1,
                        "value",
                        backward=lambda a: self.questions[self.title2pname[a]][
                            "answer"
                        ],
                    ).classes("w-full")

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
                        f"{self.pname}::judge",
                        {"value": self.textarea.value, "judge_ret": judge_ret},
                    )
                else:
                    await async_add_user_action(
                        self.username,
                        f"{self.pname}::answer",
                        {"value": self.textarea.value},
                    )
                    ui.notify("Submitted", type="positive")

            async def record_change():
                nonlocal last_textarea_content
                current_content = self.textarea.value

                if current_content != last_textarea_content:
                    await async_add_user_action(
                        self.username,
                        f"{self.pname}::answer",
                        {"value": current_content},
                    )
                    last_textarea_content = current_content

            submit_button.on("click", submit_answer)
            ui.timer(5, record_change)

    def get_chat_hist(self, ptitle):
        pname = self.title2pname[ptitle]
        pname_msg = get_latest_action_value(self.username, f"{pname}::chat")
        if pname_msg:
            return pname_msg["messages"]
        return []

    def recall_messages(self):
        self.messages = self.get_chat_hist(self.select1.value)
        self.chat_messages.refresh()

    @ui.refreshable
    def chat_messages(self) -> None:
        for name, text in self.messages:
            if name == "Bot":
                with ui.chat_message(
                    [], name="", sent=name == "You", text_html=True
                ).classes("w-full"):
                    ui.markdown(text)
            elif name == "You":
                ui.chat_message(
                    text.replace("\n", "<br>"),
                    name="",
                    sent=name == "You",
                    text_html=True,
                ).classes("w-full")

    def build_chat_page(self):
        with ui.column().classes("w-full h-full"):
            self.messages: List[Tuple[str, str]] = self.get_chat_hist(
                self.select1.value
            )

            self.select1.on("update:model-value", self.recall_messages)

            async def send() -> None:
                message = text.value

                self.messages.append(
                    (
                        "system",
                        (
                            f"Current answer: {self.textarea.value}\n"
                            f"Current evaluation: {self.judge_overall_rslt.content}\n"
                            f"Detailed evaluation: {self.judge_detailed_rslt.content}"
                        ),
                    )
                )
                self.messages.append(("You", text.value))
                text.value = ""
                self.chat_messages.refresh()

                response = ""
                self.messages.append(("Bot", response))

                role_map = {"You": "human", "Bot": "ai", "system": "system"}
                chat_history = [(role_map[i[0]], i[1]) for i in self.messages[:-1]]

                async_response = self.respond(
                    chat_history,
                    self.pname,
                    {
                        "pname": self.pname,
                        "cur_code": self.textarea.value,
                        "cur_result": self.judge_overall_rslt.content,
                        "cur_detailed_result": self.judge_detailed_rslt.content,
                    },
                )

                async for chunk in async_response:
                    if chunk is None:
                        break
                    response += chunk
                    self.messages[-1] = ("Bot", response)
                    self.chat_messages.refresh()
                    scroll_area.scroll_to(percent=1.0)

                await async_add_user_action(
                    self.username,
                    f"{self.pname}::chat",
                    {"pname": self.select1.value, "messages": self.messages},
                )

            async def clear_message() -> None:
                self.messages.clear()
                self.chat_messages.refresh()

                await async_add_user_action(
                    self.username,
                    f"{self.pname}::chat",
                    {"pname": self.select1.value, "messages": self.messages},
                )

            # the queries below are used to expand the contend down to the footer (content can then use flex-grow to expand)
            ui.query(".q-page").classes("flex")
            ui.query(".nicegui-content").classes("w-full")

            with ui.tabs().classes("w-full") as tabs:
                if self.gpt_enabled:
                    chat_tab = ui.tab("Chat")
                python_tab = ui.tab("Python")

            with ui.tab_panels(
                tabs, value=chat_tab if self.gpt_enabled else python_tab
            ).classes("w-full max-w-2xl mx-auto h-full items-stretch"):
                if self.gpt_enabled:
                    with ui.tab_panel(chat_tab).classes("items-stretch h-full"):
                        with ui.scroll_area().classes(
                            "w-full h-4/6 border"
                        ) as scroll_area:
                            self.chat_messages()
                        placeholder = "message"
                        with ui.row().classes("w-full"):
                            text = (
                                ui.textarea(placeholder=placeholder)
                                .props("rounded outlined input-class=mx-3")
                                .classes("w-full self-center")
                            )
                            send_button = (
                                ui.button("Send").on("click", send).classes("self-center")
                            )
                            clear_button = (
                                ui.button("Clear")
                                .on("click", clear_message)
                                .classes("self-center")
                            )


                def recall_python(ptitle):
                    pname = self.title2pname[ptitle]
                    python_value = get_latest_action_value(
                        self.username, f"{pname}::python"
                    )
                    if python_value:
                        return python_value["value"]
                    return ""

                with ui.tab_panel(python_tab).classes("items-stretch h-full"):
                    with ui.row().classes("w-full"):
                        python_text = (
                            ui.textarea(placeholder="Enter Python code")
                            .props("rounded outlined input-class=mx-3")
                            .classes("w-full self-center")
                            .bind_value_from(
                                self.select1,
                                "value",
                                backward=recall_python,
                            )
                        )
                        exec_button = ui.button("Run").classes("self-center")

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
                "**Execution Status:**\n\n" f"{exec_status}\n\n" "**Execution Result:**\n\n" f"{exec_result}"
            )
            self.exec_spin.set_visibility(False)
            self.exec_rslt.set_content(exce_rslt)

            ptitle = self.select1.value
            pname = self.title2pname[ptitle]
            await async_add_user_action(
                self.username,
                f"{pname}::python",
                {"value": taskcode, "judge_ret": ret},
            )

        exec_button.on("click", submit_code)

    async def respond(self, chat_history, pname, context_dict):
        if not self.gpt_enabled:
            yield "Not available."
        lc_history = []
        system_prompt = get_gpt_prompt(pname, context_dict)
        lc_history.append(SystemMessage(content=system_prompt))

        for role, message in chat_history:
            if role == "You":
                lc_history.append(HumanMessage(content=message))
            if role == "Bot":
                lc_history.append(AIMessage(content=message))

        async for chunk in self.chat.astream(lc_history):
            yield chunk.content

    async def generate_judge_message(self):
        pname = self.title2pname[self.select1.value]
        problem = self.questions[pname]
        answer = self.textarea.value
        testcases = [(case["input"], case["output"]) for case in problem["testcases"]]
        ret = await run.cpu_bound(
            judge_code, answer, problem["code_entrypoint"], testcases
        )

        finished = ret["exec_result"] == "finished"
        passed = finished and all([x["passed"] for x in ret["output"]])

        result, detailed_result = "", ""
        if ret["exec_result"] == "finished":
            # if passed:
            #     mark_solved(pname, taskcode, request)
            result += "All runs completed. " + ("Tests passed. ✅" if passed else "Tests failed. ❌")
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
            result += f"Execution error: {ret['exec_result']}。\n"
        return ret, result, detailed_result


if __name__ in {"__main__", "__mp_main__"}:
    page_builder = ProbelmPageBuilder()
    page_builder.build()
    ui.run()
