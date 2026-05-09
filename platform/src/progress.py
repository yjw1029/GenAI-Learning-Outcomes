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
    "试前调查问卷 (Python)": "/stage/pretest_py",
    "试前调查问卷 (博弈论)": "/stage/pretest_math",
    "代码基础能力测试": "/stage/captest_py",
    "数学基础能力测试": "/stage/captest_math",
    "试后调查问卷": "/stage/posttest",
    "Python基础教程": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B.pdf",
    "Python教程视频": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E6%95%99%E5%AD%A6%E8%A7%86%E9%A2%91.mp4",
    "Python学习平台使用教程": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E5%AD%A6%E4%B9%A0%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%96%87%E6%A1%A3%201.pdf",
    "Python对话平台使用教程": "https://miaowa.blob.core.windows.net/llm4edu/Python%E5%9F%BA%E7%A1%80%E5%AD%A6%E4%B9%A0%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%96%87%E6%A1%A3%202.pdf",
    "博弈论基础教程": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B.pdf",
    "博弈论基础视频": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80.mp4",
    "博弈论学习平台使用教程": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%96%87%E6%A1%A3%201.pdf",
    "博弈论对话平台使用教程": "https://miaowa.blob.core.windows.net/llm4edu/%E5%8D%9A%E5%BC%88%E8%AE%BA%E5%9F%BA%E7%A1%80%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%96%87%E6%A1%A3%202.pdf",
}

stage_resources_py = {
    S0: [],
    S1: ["试前调查问卷 (Python)", "代码基础能力测试"],
    S2: [
        {
            "default": "Python学习平台使用教程",
            "gpt": "Python对话平台使用教程",
        },
    ],
    S3: [],
    S4: ["Python基础教程", "Python教程视频"],
    S5: ["Python基础教程", "Python教程视频"],
    S6: ["Python基础教程", "Python教程视频"],
    S7: ["试后调查问卷"],
    S8: [],
}

stage_resources_math = {
    S0: [],
    S1: ["试前调查问卷 (博弈论)", "数学基础能力测试"],
    S2: [
        {
            "default": "博弈论学习平台使用教程",
            "gpt": "博弈论对话平台使用教程",
        }
    ],
    S3: [],
    S4: ["博弈论基础教程", "博弈论基础视频"],
    S5: ["博弈论基础教程", "博弈论基础视频"],
    S6: ["博弈论基础教程", "博弈论基础视频"],
    S7: ["试后调查问卷"],
    S8: [],
}

# Add confirmation questions for each stage
stage_confirm_questions = {
    S0: [
        "我已使用电脑参与测试，没有使用手机或平板",
        "我已关闭浏览器插件和扩展",
        "我已确认网络状态良好",
        "我已开启屏幕共享",
        "如参加博弈论课程，我已准备好纸笔",
        "如本阶段介绍中要求测试截图，我已测试过截图功能，可以正常使用",
        "如本阶段介绍中要求测试公式展示，我已确认公式可以正常渲染展示"
    ],
    S1: [
        "我已完成试前问卷调查",
        "我已完成基础能力测试问卷",
    ],
    S2: [
        "我已阅读平台使用教程并了解平台使用方法",
    ],
    S3: [
        "我已观看课程视频或阅读教程文档",
        "我已在规定时间内完成课程学习"
    ],
    S4: [
        "我已在规定时间内完成作业1的所有题目",
        "我已提交所有答案"
    ],
    S5: [
        "我已在规定时间内完成课程复习",
    ],
    S6: [
        "我已在规定时间内完成作业2的所有题目",
        "我已提交所有答案"
    ],
    S7: [
        "我已完成试后问卷调查",
    ],
    S8: [
        "我已检查页面底部个人信息，确认无误"
    ]
}

def _minutes(s):
    t = STAGE_MAX_TIME[s]
    return f"{t//60} 分钟"


mapping = {
    S0: '<b>未开始，完成检查后点击下一步开始计时：</b><br><ul><li>请使用电脑参与测试，请勿使用手机或平板。</li><li>关闭浏览器插件和扩展。</li><li>确认网络状态，如果因为卡顿问题导致实验无法正常进展，请联系管理员另选时间进行测试。网络测试网站：<a href="https://test.ustc.edu.cn/" target="_blank">链接</a>。</li><li>确认已开启屏幕共享。</li><li>参加博弈论课程的同学需要完成计算题，请准备纸笔。</li></ul>',
    S1: f"<b>试前问卷调查（{_minutes(S1)}），请完成附加文件中试前问卷调查的填写，完成试前问卷调查后，在五分钟内完成基础能力测试问卷。</b> <br> <span>基础能力测试问卷链接点击即开始计时，<strong>请勿提前点开</strong>！请务必确认点击<strong>提交</strong>按钮提交问卷！</span>",
    S2: f"<b>学习与试用平台（{_minutes(S2)}），请阅读附加文件中的平台使用教程，了解平台使用方法，完成之后回到本页面点击下一步。</b>",
    S3: f"<b>课程学习（{_minutes(S3)}），请点击 <a href='/stage/learning'>链接</a> 进入课程学习平台，观看课程视频或教程文档在规定时间内完成课程学习，完成之后回到本页面点击下一步。",
    S4: f"<b>完成作业 1（{_minutes(S4)}），请点击 <a href='/stage/a1'>链接</a> 进入作业平台完成作业 1，完成之后回到本页面点击下一步。</b> <p>根据学习表现，排名前10％的参与者将获得额外200元人民币的激励。排名在10％至40％范围内的参与者将获得100元人民币的激励</p> <span>学习表现指标为：20％ * 作业1的得分 *（1+作业1的速度）+ 30％ * 作业2的得分 *（1+作业2的速度）</span>",
    S5: f"<b>课程复习（{_minutes(S5)}），请点击 <a href='/stage/review'>链接</a> 进入复习平台平台进行复习，完成之后回到本页面点击下一步</b> <br> <span>复习题可查看题目答案</span>",
    S6: f"<b>完成作业 2（{_minutes(S6)}），请点击 <a href='/stage/a2'>链接</a> 进入作业平台完成作业 2，完成之后回到本页面点击下一步</b> <p>根据学习表现，排名前10％的参与者将获得额外200元人民币的激励。排名在10％至40％范围内的参与者将获得100元人民币的激励</p> <span>学习表现指标为：20％ * 作业1的得分 *（1+作业1的速度）+ 30％ * 作业2的得分 *（1+作业2的速度）</span>",
    S7: f"<b>试后问卷调查（{_minutes(S7)}），请完成附加文件中试后问卷调查的填写，完成之后回到本页面点击下一步。</b> <br> <span>请务必确认点击<strong>提交</strong>按钮提交问卷！</span>",
    S8: "<b>全部完成，请再次检查页面底部个人信息，确认无误后即可退出。</b>",
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
            self.status = progress_value.value.get("stage", S0)
            # Initialize confirmation state for the current stage
            self.confirm_status = {question: False for question in stage_confirm_questions.get(self.status, [])}

    async def set_next_stage(self):
        if self.status == S8:
            ui.notify("实验已全部完成，感谢您的参与！三秒后将返回登录页。", position="center")
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
            progress_history = [(a.value.get("stage"), a.timestamp) for a in actions]
            china_tz = pytz.timezone("Asia/Shanghai")

            progress_str = f"您的用户名是：**{self.username}**\n\n"
            for event, timestamp in progress_history:
                utc_time = datetime.utcfromtimestamp(timestamp)
                utc_time = utc_time.replace(tzinfo=pytz.utc)
                china_time = utc_time.astimezone(china_tz)
                time_str = china_time.strftime("%Y-%m-%d %H:%M:%S")

                progress_str += f"* **{event}**: {time_str}\n\n"
            return progress_str
        else:
            return "未开始"

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
                "退出登录",
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
本次测试一共分为 7 个阶段，需在规定时间按顺序完成：

1. 试前问卷调查（{_minutes(S1)}）；
2. 学习与试用平台（{_minutes(S2)}）；
3. 课程学习（{_minutes(S3)}）；
4. 完成作业 1（{_minutes(S4)}）；
5. 课程复习（{_minutes(S5)}）；
6. 完成作业 2（{_minutes(S6)}）；
7. 试后问卷调查（{_minutes(S7)}）。

作业1、复习和作业2阶段均为**<span style="color: red;">开卷</span>**，可在附加资料中访问课程教材及视频。作业2阶段**<span style="color: red;">无对话助手</span>**。

当前阶段剩余时间将以**<span style="color: green;">绿色</span>**字体在当前进度下显示。

剩余时间结束后，您仍有20分钟时间停留在当前阶段，剩余停留时间将以**<span style="color: red;">红色</span>**字体在当前进度下展示。

停留时间结束后，若您还未进入下一阶段，我们将视为您选择**退出实验**。

**退出登陆计时仍会继续**。
        """
                )

            # with ui.row().classes("bg-white col-start-1 col-end-11"):
            with ui.expansion(text="当前进度", value=True).classes(
                "bg-white col-start-2 col-end-12"
            ):
                ui.label(text="当前阶段").classes(
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
                        label.set_text(f"当前阶段剩余: {timeformat}")
                        if countdown_time == 0:
                            ui.notify(
                                f"当前阶段已结束，您还可在页面停留{STAY_TIME // 60}分钟。请尽快进入下一阶段，否则视为放弃实验",
                                position="center",
                                close_button="好的",
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
                        label.set_text(f"当前阶段已结束，您还可以在当前页面停留: {timeformat}")

                        if countdown_time == 60:
                            ui.notify(
                                "停留时间还有1分钟结束，请尽快进入下一阶段，否则视为放弃实验",
                                position="center",
                                type="warning",
                                close_button="好的",
                            )
                        if countdown_time < 0:
                            # Check whether the user already entered the next stage before marking FINISHED
                            latest_status = get_latest_action(self.username, "progress")
                            if latest_status and latest_status.value.get("stage") != self.status:
                                # User has entered the next stage; refresh the page
                                self.status = latest_status.value.get("stage")
                                self.start_time = latest_status.timestamp
                                self.build_progress.refresh()
                                return
                            
                            ui.notify(
                                "停留时间还已到，您已放弃实验，感谢您的参与！一秒后将返回登录页。",
                                position="center",
                                type="error",
                                close_button="好的",
                            )
                            await asyncio.sleep(1)
                            
                            # Check again to ensure the user didn't enter the next stage at the last second
                            latest_status = get_latest_action(self.username, "progress")
                            if latest_status and latest_status.value.get("stage") != self.status:
                                # User has entered the next stage; refresh the page
                                self.status = latest_status.value.get("stage")
                                self.start_time = latest_status.timestamp
                                self.build_progress.refresh()
                                return
                                
                            # Only mark as FINISHED after confirming the user did not enter the next stage
                            latest_status = get_latest_action_value(
                                username=app.storage.user.get("username"),
                                action="progress",
                            )
                            if (
                                latest_status
                                and latest_status.get("stage") != "FINISHED"
                            ):
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
                    ui.label(text="请确认以下内容：").classes(
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

                ui.label(text="请填写:\"我确认完成该阶段\"后，点击\"下一步\"进入下一阶段：").classes(
                    "bg-blue-200 p-1.5 text-blue-600 font-bold rounded-md mt-4"
                )
                next_step_reason = ui.input(label="提交说明（请填写:\"我确认完成该阶段\"）").classes("w-full").props("rounded outlined")
                # Disable the input until all confirmation questions are checked
                next_step_reason.set_enabled(all(self.confirm_status.values()))

                next_step_btn = ui.button("下一步", on_click=self.set_next_stage)
                next_step_btn.bind_enabled_from(
                    next_step_reason,
                    "value",
                    backward=lambda a: a == "我确认完成该阶段",
                )

            with ui.expansion(text="进度历史", value=False).classes(
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

        ui.markdown("<b>截图粘贴测试</b><ul><li>对话助手支持粘贴截屏图像进行对话</li><li>Windows用户使用Windows 徽标键+Shift+S截屏，教程链接：<a href='https://support.microsoft.com/zh-cn/office/%E5%A4%8D%E5%88%B6%E7%AA%97%E5%8F%A3%E6%88%96%E5%B1%8F%E5%B9%95%E5%86%85%E5%AE%B9-98c41969-51e5-45e1-be36-fb9381b32bb7' target='_blank'>链接</a></li><li>Mac用户使用Shift+Command+Control+4截屏至剪贴板，教程链接：<a href='https://support.apple.com/zh-cn/102646' target='_blank'>链接</a></li><li>请在如下输入框测试粘贴截图：先截图至剪贴板，然后粘贴到如下输入框；可粘贴多张图片；点击图像右上角的叉号取消对应图像输入。</li></ul>")

        self.show_images()
        text = (
            ui.input(placeholder="截图粘贴测试框")
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
r"""<b>公式展示测试，请确认以下公式可以正常渲染：</b> 
$$
f(x) = \\begin{cases}
    2x - 1    & \\text{当 } -2 \\leq x \\leq 1, \\\\
    -x^2      & \\text{当 } x > 1
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
                additional_info += f"<br><br>本阶段附加资料：<br>{additional_resources}"

        return additional_info
