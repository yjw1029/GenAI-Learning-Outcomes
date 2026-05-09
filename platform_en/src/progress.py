import asyncio
import os
import time
from datetime import datetime
from pathlib import Path
import markdown

import pytz
from database import (
    add_user_action,
    async_add_user_action,
    get_actions,
    get_latest_action,
    get_latest_action_value,
)
from nicegui import app, run, ui
from problemset import load_problem
from utils import log_event

os.environ["TZ"] = "Asia/Shanghai"
TIMEOUT = 5
THIS_DIR = Path(__file__).parent
ASSETS_PATH = THIS_DIR / "assets"
CUSTOM_JS = THIS_DIR / "custom.js"

S0 = "Not Started"
S1 = "Pre-test Survey"
S2 = "Learn & Try Platform"
S3 = "Course Learning"
S4 = "Complete Homework 1"
S5 = "Course Review"
S6 = "Complete Homework 2"
S7 = "Post-test Survey"
S8 = "All Done"
S9 = "FINISHED"

# Legacy stage names stored in DB (Chinese) -> English labels
STAGE_ALIASES = {
    "未开始": S0,
    "试前问卷调查": S1,
    "学习与试用平台": S2,
    "课程学习": S3,
    "完成作业 1": S4,
    "课程复习": S5,
    "完成作业 2": S6,
    "试后问卷调查": S7,
    "全部完成": S8,
    "FINISHED": S9,
}


def normalize_stage(stage):
    if stage is None:
        return stage
    return STAGE_ALIASES.get(stage, stage)


STAGE_MAX_TIME = {
    S0: -1,
    S1: 10 * 60,
    S2: 10 * 60,
    S3: 40 * 60,
    S4: 20 * 60,
    S5: 20 * 60,
    S6: 20 * 60,
    S7: 5 * 60,
    S8: -1,
    S9: -20 * 60,
}
STAY_TIME = 20 * 60

_next_S = {S0: S1, S1: S2, S2: S3, S3: S4, S4: S5, S5: S6, S6: S7, S7: S8}



resources = {
    "Pre-test Survey (Python)": "/stage/pretest_py",
    "Pre-test Survey (Game Theory)": "/stage/pretest_math",
    "Coding Basics Test": "/stage/captest_py",
    "Math Basics Test": "/stage/captest_math",
    "Post-test Survey": "/stage/posttest",
    "Python Basics Tutorial": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B.pdf",
    "Python Tutorial Video": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E6%95%99%E5%AD%A6%E8%A7%86%E9%A2%91.mp4",
    "Python Learning Platform Guide": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E5%AD%A6%E4%B9%A0%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%96%87%E6%A1%A3%201.pdf",
    "Python Chat Platform Guide": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E5%AD%A6%E4%B9%A0%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%96%87%E6%A1%A3%202.pdf",
    "Game Theory Basics Tutorial": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B.pdf",
    "Game Theory Basics Video": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80.mp4",
    "Game Theory Learning Platform Guide": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%96%87%E6%A1%A3%201.pdf",
    "Game Theory Chat Platform Guide": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%96%87%E6%A1%A3%202.pdf",
}

stage_resources_py = {
    S0: [],
    S1: ["Pre-test Survey (Python)", "Coding Basics Test"],
    S2: [
        {
            "default": "Python Learning Platform Guide",
            "gpt": "Python Chat Platform Guide",
        },
    ],
    S3: [],
    S4: ["Python Basics Tutorial", "Python Tutorial Video"],
    S5: ["Python Basics Tutorial", "Python Tutorial Video"],
    S6: ["Python Basics Tutorial", "Python Tutorial Video"],
    S7: ["Post-test Survey"],
    S8: [],
}

stage_resources_math = {
    S0: [],
    S1: ["Pre-test Survey (Game Theory)", "Math Basics Test"],
    S2: [
        {
            "default": "Game Theory Learning Platform Guide",
            "gpt": "Game Theory Chat Platform Guide",
        }
    ],
    S3: [],
    S4: ["Game Theory Basics Tutorial", "Game Theory Basics Video"],
    S5: ["Game Theory Basics Tutorial", "Game Theory Basics Video"],
    S6: ["Game Theory Basics Tutorial", "Game Theory Basics Video"],
    S7: ["Post-test Survey"],
    S8: [],
}

# Add confirmation questions for each stage
stage_confirm_questions = {
    S0: [
        "I am using a computer, not a phone or tablet",
        "I have disabled browser plugins/extensions",
        "I have confirmed the network is stable",
        "I have enabled screen sharing",
        "If taking the game theory course, I have paper and pen ready",
        "If this stage requires screenshot testing, I have verified it works",
        "If this stage requires formula rendering, I have confirmed it works"
    ],
    S1: [
        "I have completed the pre-test survey",
        "I have completed the basics test survey",
    ],
    S2: [
        "I have read the platform guide and understand how to use it",
    ],
    S3: [
        "I have watched the course video or read the tutorial",
        "I have completed the learning within the allotted time"
    ],
    S4: [
        "I have completed all Homework 1 questions on time",
        "I have submitted all answers"
    ],
    S5: [
        "I have completed the review on time",
    ],
    S6: [
        "I have completed all Homework 2 questions on time",
        "I have submitted all answers"
    ],
    S7: [
        "I have completed the post-test survey",
    ],
    S8: [
        "I have checked the personal info at the bottom and confirmed it is correct"
    ]
}

def _minutes(s):
    t = STAGE_MAX_TIME[s]
    return f"{t//60} min"


mapping = {
    S0: '<b>Not started. After checks, click Next to start timing:</b><br><ul><li>Use a computer; do not use a phone or tablet.</li><li>Disable browser plugins/extensions.</li><li>Confirm network stability. If lag prevents progress, contact the admin to reschedule. Network test site:<a href="https://www.speedtest.net/" target="_blank">link</a>。</li><li>Confirm screen sharing is enabled.</li><li>Game theory participants need to solve calculations; prepare paper and pen.</li></ul>',
    S1: f"<b>Pre-test survey ({_minutes(S1)}): complete the pre-test survey in the attachments. After that, finish the basics test within five minutes.</b> <br> <span>The basics test link starts the timer on click; <strong>do not open early</strong>. Be sure to click <strong>Submit</strong>.</span>",
    S2: f"<b>Learn & try platform（{_minutes(S2)}），Read the platform guide in the attachments. Return here and click Next when done.</b>",
    S3: f"<b>Course learning ({_minutes(S3)}): click the <a href='/stage/learning'>link</a> to enter the learning platform. Watch the video or read the tutorial and finish within time, then return and click Next.",
    S4: f"<b>Complete Homework 1 ({_minutes(S4)}): click the <a href='/stage/a1'>link</a> to enter the homework platform and finish HW1, then return and click Next.</b> <p>Based on performance, the top 10% receive an extra 200 RMB; ranks 10%-40% receive 100 RMB.</p> <span>Performance metric: 20% * HW1 score * (1 + HW1 speed) + 30% * HW2 score * (1 + HW2 speed).</span>",
    S5: f"<b>Course review ({_minutes(S5)}): click the <a href='/stage/review'>link</a> to review on the platform, then return and click Next.</b> <br> <span>Review questions include viewable solutions.</span>",
    S6: f"<b>Complete Homework 2 ({_minutes(S6)}): click the <a href='/stage/a2'>link</a> to enter the homework platform and finish HW2, then return and click Next.</b> <p>Based on performance, the top 10% receive an extra 200 RMB; ranks 10%-40% receive 100 RMB.</p> <span>Performance metric: 20% * HW1 score * (1 + HW1 speed) + 30% * HW2 score * (1 + HW2 speed).</span>",
    S7: f"<b>Post-test survey ({_minutes(S7)}): complete the post-test survey in the attachments, then return and click Next.</b> <br> <span>Be sure to click <strong>Submit</strong>.</span>",
    S8: "<b>All done. Please re-check the personal info at the bottom and then exit.</b>",
}


def get_resource_desc(res, group):
    if isinstance(res, str):
        url = resources[res]
        return f"<a href='{url}' target='_blank'>{res}</a>"
    elif isinstance(res, dict):
        return get_resource_desc(res[group], group)


class ProgressBuilder:
    def __init__(self, cfg, user=None):
        self.cfg = cfg
        self.user = user
        self.username = user.get("username")

        self.vgroup = cfg.uservgroup(self.username)
        self.review_group = cfg.getvgroup(self.vgroup, f"review_group")
        self.course = "py" if self.vgroup.startswith("py") else "math"
        
        # Add confirmation state dictionary
        self.confirm_status = {question: False for question in stage_confirm_questions.get(S0, [])}

        progress_value = get_latest_action(self.username, "progress")
        if progress_value is None:
            self.status = S0
        else:
            self.start_time = progress_value.timestamp
            self.status = normalize_stage(progress_value.value.get("stage", S0))
            # Initialize confirmation state for the current stage
            self.confirm_status = {question: False for question in stage_confirm_questions.get(self.status, [])}

    async def set_next_stage(self):
        if self.status == S8:
            ui.notify("All stages completed. Thank you for participating! Returning to login in 3 seconds.", position="center")
            await async_add_user_action(
                username=self.username,
                action="progress",
                value={"stage": "FINISHED"},
            )
            await asyncio.sleep(3)
            app.storage.user.clear()
            ui.navigate.to("/login")
        else:
            self.status = _next_S[self.status]
            await async_add_user_action(
                username=self.username, action="progress", value={"stage": self.status}
            )
            self.start_time = time.time()
            # Update confirmation state for the new stage's questions
            self.confirm_status = {question: False for question in stage_confirm_questions.get(self.status, [])}
            self.build_progress.refresh()

    def get_progress_history(self):
        if actions := get_actions(self.username, "progress"):
            progress_history = [(normalize_stage(a.value.get("stage")), a.timestamp) for a in actions]
            china_tz = pytz.timezone("Asia/Shanghai")

            progress_str = f"Your username is: **{self.username}**\n\n"
            for event, timestamp in progress_history:
                utc_time = datetime.utcfromtimestamp(timestamp)
                utc_time = utc_time.replace(tzinfo=pytz.utc)
                china_time = utc_time.astimezone(china_tz)
                time_str = china_time.strftime("%Y-%m-%d %H:%M:%S")

                progress_str += f"* **{event}**: {time_str}\n\n"
            return progress_str
        else:
            return "Not started"

    def build(self):


        ui.add_head_html(
            """<style>
#app {
    --tw-bg-opacity: 1;
    background-color: rgb(229 231 235 / var(--tw-bg-opacity));
}
            </style>
            """
        )

        with ui.header().classes(replace="grid grid-cols-12") as header:
            if self.user:
                ui.button(f"{self.user['username']}", icon="person").props(
                    "flat color=white flat"
                ).classes("grid-cols-subgrid col-span-1")

            ui.button(
                "Log out",
                icon="logout",
                on_click=lambda: (app.storage.user.clear(), ui.navigate.to("/login")),
            ).props("flat color=white flat").classes("grid-cols-subgrid col-span-1")

        self.build_progress()

    @ui.refreshable
    def build_progress(self):
        with ui.column().classes(" w-screen grid grid-cols-12"):
            with ui.row().classes("col-start-2 col-end-12 bg-white p-4"):
                description = ui.markdown(
                    content=f"""#### LLM for Education
This study has 7 stages to be completed in order within the time limits:

1. Pre-test survey（{_minutes(S1)}）；
2. Learn & try platform（{_minutes(S2)}）；
3. Course learning（{_minutes(S3)}）；
4. Complete Homework 1（{_minutes(S4)}）；
5. Course review（{_minutes(S5)}）；
6. Complete Homework 2（{_minutes(S6)}）；
7. Post-test survey（{_minutes(S7)}）。

Homework 1, Review, and Homework 2 are **<span style="color: red;">open-book</span>** with access to materials and videos. Homework 2 has **<span style="color: red;">no chat assistant</span>**.

Remaining time is shown in **<span style="color: green;">green</span>** under the current progress.

After time runs out, you may stay up to 20 minutes; remaining stay time is shown in **<span style="color: red;">red</span>**.

If stay time ends and you have not entered the next stage, we treat it as **withdrawing**.

**The logout timer will continue**.
        """
                )

            # with ui.row().classes("bg-white col-start-1 col-end-11"):
            with ui.expansion(text="Current Progress", value=True).classes(
                "bg-white col-start-2 col-end-12"
            ):
                ui.label(text="Current Stage").classes(
                    "bg-blue-200 p-1.5 text-blue-600 font-bold rounded-md"
                )
                ui.label(text=self.status).classes("w-full p-2 shadow rounded-md")

                async def update_timer():
                    countdown_time = int(
                        self.start_time + STAGE_MAX_TIME[self.status] - time.time()
                    )
                    if countdown_time >= 0:
                        mins, secs = divmod(countdown_time, 60)
                        hours, mins = divmod(mins, 60)
                        timeformat = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
                        label.set_text(f"Time left in current stage: {timeformat}")
                        if countdown_time == 0:
                            ui.notify(
                                f"This stage has ended. You may stay for {STAY_TIME // 60} minutes. Please enter the next stage soon, or it will be treated as withdrawal",
                                position="center",
                                close_button="OK",
                            )
                    else:
                        label.classes("text-red-500 text-base")
                        countdown_time = int(
                            self.start_time
                            + STAGE_MAX_TIME[self.status]
                            + STAY_TIME
                            - time.time()
                        )
                        mins, secs = divmod(countdown_time, 60)
                        hours, mins = divmod(mins, 60)
                        timeformat = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
                        label.set_text(f"This stage has ended. You can stay on this page for: {timeformat}")

                        if countdown_time == 60:
                            ui.notify(
                                "Stay time ends in 1 minute. Please enter the next stage soon, or it will be treated as withdrawal",
                                position="center",
                                type="warning",
                                close_button="OK",
                            )
                        if countdown_time < 0:
                            # Check whether the user already entered the next stage before marking FINISHED
                            latest_status = get_latest_action(self.username, "progress")
                            latest_stage = normalize_stage(latest_status.value.get("stage")) if latest_status else None
                            if latest_stage and latest_stage != self.status:
                                # User has entered the next stage; refresh the page
                                self.status = latest_stage
                                self.start_time = latest_status.timestamp
                                self.build_progress.refresh()
                                return
                            
                            ui.notify(
                                "Stay time is over. You have withdrawn. Thank you for participating! Returning to login in 1 second.",
                                position="center",
                                type="error",
                                close_button="OK",
                            )
                            await asyncio.sleep(1)
                            
                            # Check again to ensure the user didn't enter the next stage at the last second
                            latest_status = get_latest_action(self.username, "progress")
                            latest_stage = normalize_stage(latest_status.value.get("stage")) if latest_status else None
                            if latest_stage and latest_stage != self.status:
                                # User has entered the next stage; refresh the page
                                self.status = latest_stage
                                self.start_time = latest_status.timestamp
                                self.build_progress.refresh()
                                return
                                
                            # Only mark as FINISHED after confirming the user did not enter the next stage
                            latest_status = get_latest_action_value(
                                username=app.storage.user.get("username"),
                                action="progress",
                            )
                            latest_stage = normalize_stage(latest_status.get("stage")) if latest_status else None
                            if latest_stage and latest_stage != "FINISHED":
                                await async_add_user_action(
                                    username=self.username,
                                    action="progress",
                                    value={"stage": "FINISHED"},
                                )
                            app.storage.user.clear()
                            ui.navigate.to("/login")

                if self.status not in [S0, S8]:
                    with ui.column().classes("w-full my-auto"):
                        label = ui.label().classes("text-green-500 text-base")
                        ui.timer(1.0, update_timer)

                additional_info = ui.markdown(
                    content=self.build_additional_info(self.status)
                )

                # additional_info = ui.html(
                #     markdown.markdown(
                #         self.build_additional_info(self.status),
                #         extensions=["tables", "codehilite", "fenced_code"]
                #     )
                # ).classes("markdown-body")

                res_group = "default"
                if self.vgroup.startswith("pygpt") or self.vgroup.startswith("mathgpt"):
                    res_group = "gpt"

                if self.status == S0 and self.course == "math": 
                    self.test_formula()

                if self.status == S0 and res_group == "gpt":
                    self.test_paste()
                
                # Add confirmation question list
                if stage_confirm_questions.get(self.status):
                    ui.label(text="Please confirm the following:").classes(
                        "bg-blue-200 p-1.5 text-blue-600 font-bold rounded-md mt-4"
                    )
                    
                    with ui.column().classes("w-full p-2 shadow rounded-md"):
                        for question in stage_confirm_questions.get(self.status, []):
                            with ui.row().classes("items-center"):
                                def on_change(e):
                                    self.confirm_status[e.sender.text] = e.value
                                    all_confirmed = all(self.confirm_status.values())
                                    next_step_reason.set_enabled(all_confirmed)

                                checkbox = ui.checkbox(question, on_change=on_change).classes("my-1")

                ui.label(text="Type \"I confirm this stage is complete\", then click \"Next\" to proceed:").classes(
                    "bg-blue-200 p-1.5 text-blue-600 font-bold rounded-md mt-4"
                )
                next_step_reason = ui.input(label="Submission note (type: \"I confirm this stage is complete\")").classes("w-full").props("rounded outlined")
                # Disable the input until all confirmation questions are checked
                next_step_reason.set_enabled(all(self.confirm_status.values()))

                next_step_btn = ui.button("Next", on_click=self.set_next_stage)
                next_step_btn.bind_enabled_from(
                    next_step_reason,
                    "value",
                    backward=lambda a: a == "I confirm this stage is complete",
                )

            with ui.expansion(text="Progress History", value=False).classes(
                "bg-white col-start-2 col-end-12"
            ):
                progress_history_str = self.get_progress_history()
                progress_history = ui.markdown(content=progress_history_str)


    def test_paste(self):
        self.images = []
        ui.add_head_html('''
        <script>
            function paste_clipboard_listener() {
                document.querySelector('.mychatbox input').addEventListener('paste', function(event) {
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
        ''')

        ui.markdown("<b>Screenshot Paste Test</b><ul><li>The chat assistant supports pasting screenshots</li><li>Windows: use Win+Shift+S. Tutorial:<a href='https://support.microsoft.com/en-us/office/%E5%A4%8D%E5%88%B6%E7%AA%97%E5%8F%A3%E6%88%96%E5%B1%8F%E5%B9%95%E5%86%85%E5%AE%B9-98c41969-51e5-45e1-be36-fb9381b32bb7' target='_blank'>link</a></li><li>Mac: use Shift+Command+Control+4 to copy to clipboard. Tutorial:<a href='https://support.apple.com/en-us/102646' target='_blank'>link</a></li><li>Test screenshot pasting below: copy to clipboard, then paste. Multiple images allowed. Click the X to remove an image.</li></ul>")

        self.show_images()
        text = (
            ui.input(placeholder="Screenshot paste test box")
            .props("rounded outlined input-class=mx-3")
            .classes("mychatbox w-full self-center")
            .style("white-space: pre-wrap;")
        )

        ui.run_javascript("paste_clipboard_listener()")

        async def display(x) -> None:
            file_path = x.args["file"].strip("\"")
            self.images.append(file_path)
            self.show_images.refresh()

        ui.on("paste_image", display)

    def test_formula(self):
        ui.add_head_html('''
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

            <script type="text/x-mathjax-config">
            MathJax.Hub.Config({{
                tex2jax: {{
                    inlineMath: [ ['$','$'], ["\\(","\\)"], ["\\[","\\]"]],
                    displayMath: [ ['$$','$$'], ["\\[","\\]"], ["\\(","\\)"]],
                    processEscapes: true,
                }}
            }})
        </script>
        ''')

        ui.html(
            markdown.markdown(
r"""<b>Formula render test. Please confirm the formula renders correctly:</b> 
$$
f(x) = \\begin{cases}
    2x - 1    & \\text{when } -2 \\leq x \\leq 1, \\\\
    -x^2      & \\text{when } x > 1
\\end{cases}
$$
""", 
                extensions=["tables", "codehilite", "fenced_code"]
            )
        ).classes("markdown-body")


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
                        ui.badge('X', color='white', text_color="black")
                        .props("outline rounded")
                        .style("border: 1px solid gray; position: absolute; top: -8px; right: -8px; cursor: pointer")
                        .tooltip("Delete image")
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


    def build_additional_info(self, current_stage):
        userinfo = self.cfg.userinfo(self.user["username"])
        vgroup = userinfo["vgroup"]

        if current_stage in mapping:
            additional_info = mapping[current_stage]
        else:
            additional_info = ""

        if vgroup.startswith("py"):
            stage_resources = stage_resources_py
        elif vgroup.startswith("math"):
            stage_resources = stage_resources_math
        else:
            stage_resources = {}

        res_group = "default"
        if vgroup.startswith("pygpt") or vgroup.startswith("mathgpt"):
            res_group = "gpt"

        if current_stage in stage_resources:
            additional_resources = ""
            for res in stage_resources[current_stage]:
                additional_resources += f"{get_resource_desc(res, res_group)}<br>"

            if additional_resources:
                additional_info += f"<br><br>Additional resources for this stage:<br>{additional_resources}"

        return additional_info
