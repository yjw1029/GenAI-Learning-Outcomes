import time
import json
import os
from pathlib import Path
from nicegui import ui, app
import markdown
from database import async_add_user_action, get_latest_action_value, get_latest_action, add_user_action

SURVEY_MAX_TIME = {
    "pretest_py": None,
    "pretest_math": None,
    "posttest": None,
    "captest_py": 5 * 60,
    "captest_math": 5 * 60,
}

class SurveyPageBuilder:
    def __init__(self, cfg, stage, survey_name, user=None, time_limit=False):
        self.cfg = cfg
        self.user = user
        self.username = user.get("username", None)
        
        self.stage = stage
        self.survey_name = survey_name
        self.time_limit = time_limit

        self.vgroup = cfg.uservgroup(self.username)
        self.course = "py" if self.vgroup.startswith("py") else "math"
        
        (
            self.survey_titles,
            self.sname2title,
            self.title2sname,
            self.surveys,
        ) = self.load_surveys(survey_name)

        # Record the start time
        if self.time_limit and SURVEY_MAX_TIME[self.survey_name] is not None:
            # Get the previously recorded start time
            start_time_record = get_latest_action(
                self.username,
                f"{survey_name}::start_time"
            )
            self.submitted_before_return = False
            
            if start_time_record:
                self.start_time = start_time_record.timestamp
            else:
                # If no record exists, store the current time
                add_user_action(
                    self.username,
                    f"{survey_name}::start_time"
                )
                start_time_record = get_latest_action(
                    self.username,
                    f"{survey_name}::start_time"
                )
                self.start_time = start_time_record.timestamp
                
        
        # Set the current survey
        self.current_survey = self.title2sname[self.survey_titles[0]]
        self.get_survey_status()
        
        # Store user responses
        self.user_answers = {}
        self.load_user_answers()

    def load_surveys(self, survey_name):
        """加载问卷数据"""
        survey_titles = []
        sname2title = {}
        surveys = {}
        
        
        survey = self.load_survey(survey_name)
        survey_titles.append(survey["title"])
        sname2title[survey_name] = survey["title"]
        surveys[survey_name] = survey
        
        title2sname = {v: k for k, v in sname2title.items()}
        
        return survey_titles, sname2title, title2sname, surveys
    
    def load_survey(self, sname):
        """加载单个问卷数据"""
        # Survey file path
        survey_path = Path(__file__).parent / "surveyset" / f"{sname}.py"
        
        if not survey_path.exists():
            raise FileNotFoundError(f"Survey {survey_path} not found.")
        
        # Execute survey file
        exec_globals = {}
        exec_locals = {}
        
        exec(open(survey_path).read(), exec_globals, exec_locals)
        
        # Check whether the survey is valid
        required = [
            "title",
            "description",
            "questions"
        ]
        
        for r in required:
            if r not in exec_locals:
                raise ValueError(f"Survey {survey_path} does not have required attribute {r}.")
        
        # Return survey data
        return {k: exec_locals[k] for k in required}
    
    def get_survey_status(self):
        """获取问卷完成状态"""
        self.survey_status = {}
        
        for sname in self.surveys:
            latest_submit = get_latest_action_value(
                self.username, f"{sname}::submit"
            )
            
            self.survey_status[sname] = {
                "submitted": latest_submit is not None
            }
        
        # Add current page index
        self.current_page_index = 0
        self.current_survey_pages = list(self.surveys[self.current_survey]["questions"].keys())
    
    def load_user_answers(self):
        """加载用户之前的回答"""
        for sname in self.surveys:
            latest_answers = get_latest_action_value(
                self.username, f"{sname}::answers"
            )
            
            if latest_answers:
                self.user_answers[sname] = latest_answers
            else:
                self.user_answers[sname] = {}
    
    def build(self):
        """构建问卷页面"""
        # Get survey submission status
        is_submitted = self.survey_status[self.current_survey].get("submitted", False)
        
        ui.add_head_html(
            f"""<style>
            .q-drawer--right {{ width: 30% !important }}
            .large-textarea .q-field__control {{ height: 100%; }}
            .q-scrollarea__content {{max-width: 100%;}}
            .q-message-container div {{max-width: 100%;}}
            .survey-question {{
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }}
            .survey-question-title {{
                font-weight: bold;
                margin-bottom: 10px;
            }}
            </style>

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.css">

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
            
            <script>
            window.surveySubmitted = {str(is_submitted).lower()};
            
            window.addEventListener('beforeunload', function(e) {{
                if (!window.surveySubmitted) {{
                    e.preventDefault();
                    e.returnValue = '您还没有提交问卷，确定要离开吗？';
                    return e.returnValue;
                }}
            }});
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
            
            # Modify the behavior of the back-to-home button
            async def handle_return():
                if not self.survey_status[self.current_survey].get("submitted", False):
                    ui.notify("请先提交问卷再返回主页", position="center", level="warning", timeout=3000)
                else:
                    ui.navigate.to("/progress")

            ui.button(
                "返回主页",
                icon="chevron_left",
                on_click=handle_return,
            ).props("flat color=white width=200px")

            if self.time_limit:
                async def update_timer():
                    countdown_time = int(
                        self.start_time + SURVEY_MAX_TIME[self.survey_name] - time.time()
                    )
                    if countdown_time >= 0:
                        mins, secs = divmod(countdown_time, 60)
                        hours, mins = divmod(mins, 60)
                        timeformat = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
                        label.set_text(f"当前阶段剩余: {timeformat}")

                        if countdown_time == 60:
                            ui.notify("本阶段还有1分钟结束", position="center", level="info")
                    else:
                        if not self.submitted_before_return:
                            label.set_text("倒计时结束")
                            ui.notify("时间已到，系统将自动提交答案", position="center", level="warning")
                            self.submitted_before_return = True

                            # Auto-save and submit answers
                            async def auto_submit():
                                # Save current answers
                                await self.save_answers()
                                # Mark as submitted
                                await async_add_user_action(
                                    self.username,
                                    f"{self.current_survey}::submit",
                                    {"stage": self.stage, "sname": self.current_survey},
                                )
                                # Update status
                                self.survey_status[self.current_survey]["submitted"] = True
                                await ui.run_javascript("window.surveySubmitted = true;")
                                ui.navigate.to(app.storage.user.get("referrer_path", "/progress"))
                            
                            await auto_submit()

                label = ui.label().classes("text-white px-10")
                ui.timer(1.0, update_timer)

        with ui.row().classes("w-full h-full grid grid-cols-12"):
            with ui.card().classes("grow h-auto grid-cols-subgrid col-span-2"):
                self.build_survey_list()
            
            with ui.card().classes("grow h-auto grid-cols-subgrid col-span-10"):
                self.build_survey_page()
    
    @ui.refreshable
    def build_survey_list(self):
        """构建问卷列表"""
        ui.html("<h3>问卷页面</h3>").classes("markdown-body")
        
        # Display all pages of the current survey
        survey = self.surveys[self.current_survey]
        page_titles = list(survey["questions"].keys())
        
        for i, page_title in enumerate(page_titles):
            button = (
                ui.button(f"第 {i+1} 页: {page_title}")
                .on("click", self.change_page_fn(i))
                .classes("w-full")
            )
            
            if i == self.current_page_index:
                button.props("color=primary")
            else:
                button.props("outline")
    
    def change_page_fn(self, page_index):
        """切换页面的函数"""
        async def fn():
            # Check whether all questions on the current page are answered
            survey = self.surveys[self.current_survey]
            page_titles = list(survey["questions"].keys())
            current_page_title = page_titles[self.current_page_index]
            current_page_questions = survey["questions"][current_page_title]
            
            all_answered = True
            missing_questions = []
            
            for i, question in enumerate(current_page_questions):
                answer_key = f"{current_page_title}_{i}"
                
                if self.current_survey not in self.user_answers or answer_key not in self.user_answers[self.current_survey]:
                    all_answered = False
                    missing_questions.append(i + 1)
                    continue
                
                answer = self.user_answers[self.current_survey][answer_key]
                if answer is None or answer == "" or (isinstance(answer, list) and len(answer) == 0):
                    all_answered = False
                    missing_questions.append(i + 1)
            
            if not all_answered:
                ui.notify(f"请完成第 {', '.join(map(str, missing_questions))} 题后再继续", position="center", level="warning")
                return
            
            # Save answers for the current page
            await async_add_user_action(
                self.username,
                f"{self.current_survey}::answers",
                self.user_answers[self.current_survey],
            )
            
            self.current_page_index = page_index
            self.build_survey_list.refresh()
            self.build_survey_page.refresh()
            
            await async_add_user_action(
                self.username,
                f"{self.current_survey}::page_change",
                {"stage": self.stage, "sname": self.current_survey, "page_index": page_index},
            )
        
        return fn
    
    def change_survey_fn(self, sname):
        """切换问卷的函数"""
        async def fn():
            self.current_survey = sname
            self.current_page_index = 0
            self.current_survey_pages = list(self.surveys[self.current_survey]["questions"].keys())
            self.build_survey_list.refresh()
            self.build_survey_page.refresh()
            
            await async_add_user_action(
                self.username,
                f"{self.current_survey}::click",
                {"stage": self.stage, "sname": self.current_survey},
            )
        
        return fn
    
    @ui.refreshable
    def build_survey_page(self):
        """构建问卷页面"""
        survey = self.surveys[self.current_survey]
        
        with ui.column().classes("w-full p-4"):
            # Survey title and description
            ui.html(f"<h2>{survey['title']}</h2>").classes("markdown-body")
            ui.html(markdown.markdown(survey['description'])).classes("markdown-body")
            
            # Get the current page title and questions
            page_titles = list(survey["questions"].keys())
            current_page_title = page_titles[self.current_page_index]
            current_page_questions = survey["questions"][current_page_title]
            
            # Display current page title
            ui.html(f"<h3>第 {self.current_page_index + 1} 页: {current_page_title}</h3>").classes("markdown-body")
            
            for i, question in enumerate(current_page_questions):
                with ui.card().classes("survey-question w-full"):
                    ui.html(
                        markdown.markdown(
                            f"{i+1}\. {question['text']}", 
                            extensions=["tables", "codehilite", "fenced_code"]
                        )
                    ).classes("markdown-body")
                    
                    # Create input controls based on question type
                    if question["type"] == "text":
                        answer_key = f"{current_page_title}_{i}"
                        default_value = self.user_answers.get(self.current_survey, {}).get(answer_key, "")
                        input_widget = ui.input(value=default_value).classes("w-full")
                        # Attach value change events
                        input_widget.on("update:model-value", lambda e, key=answer_key: self.on_answer_change(key, e))
                    
                    elif question["type"] == "textarea":
                        answer_key = f"{current_page_title}_{i}"
                        default_value = self.user_answers.get(self.current_survey, {}).get(answer_key, "")
                        ui.input(value=default_value, placeholder="请输入你的答案", on_change=lambda e, key=answer_key: self.on_answer_change(key, e)).classes("w-full")
                        
                    elif question["type"] == "single_choice":
                        answer_key = f"{current_page_title}_{i}"
                        default_value = self.user_answers.get(self.current_survey, {}).get(answer_key, None)
                        
                        with ui.column().classes("w-full"):
                            
                            # Handle default value; if it starts with "Other:", select the "Other" option
                            display_value = "其他" if (default_value and default_value.startswith("其他：")) else default_value
                            radio = ui.radio(question["options"], value=display_value).classes("w-full")
                            
                            if "其他" in question["options"]:
                                # Extract the input for the "Other" option from the default value
                                other_input_value = ""
                                if default_value and default_value.startswith("其他："):
                                    other_input_value = default_value[len("其他："):]  # remove the "其他：" prefix
                                
                                other_input = ui.input(value=other_input_value, placeholder="请输入其他选项").classes("w-full")
                                
                                # When typing an "Other" option, auto-select the "Other" radio button
                                async def on_other_input_change(e, radio=radio, key=answer_key):
                                    if e.sender.value:
                                        radio.value = "其他"
                                        # Update the answer to "Other:" + input value
                                        await self.on_answer_change(key, type('Event', (), {'sender': type('Sender', (), {'value': f"其他：{e.sender.value}"})})())
                                    elif radio.value == "其他":
                                        await self.on_answer_change(key, type('Event', (), {'sender': type('Sender', (), {'value': f"其他：{e.sender.value}"})})())

                                
                                # When a radio button is selected
                                async def on_radio_change(e, other_input=other_input, key=answer_key):
                                    if e.sender.value == "其他":
                                        # If "Other" is selected, use the input field value
                                        input_value = other_input.value
                                        await self.on_answer_change(key, type('Event', (), {'sender': type('Sender', (), {'value': f"其他：{input_value}"})})())
                                    else:
                                        # If another option is selected, use the option value directly
                                        other_input.value = ""
                                        await self.on_answer_change(key, e)
                                
                                other_input.on_value_change(on_other_input_change)
                                radio.on("update:model-value", on_radio_change)
                            else:
                                radio.on("update:model-value", lambda e, key=answer_key: self.on_answer_change(key, e))
                            
                    
                    elif question["type"] == "multiple_choice":
                        answer_key = f"{current_page_title}_{i}"
                        default_values = self.user_answers.get(self.current_survey, {}).get(answer_key, [])
                        
                        with ui.column().classes("w-full"):
                            other_checkbox = None
                            
                            # Handle "Other" options in default values
                            other_input_value = ""
                            for value in default_values:
                                if value.startswith("其他："):
                                    other_input_value = value[len("其他："):]  # remove the "其他：" prefix
                                    # Replace the original "Other: xxx" with a simple "Other" option
                                    default_values = [v if not v.startswith("其他：") else "其他" for v in default_values]
                                    break
                            
                            for j, option in enumerate(question["options"]):
                                checkbox = ui.checkbox(option, value=option in default_values).classes("w-full")
                                if option != "其他":
                                    checkbox.on("update:model-value", lambda e, key=answer_key, opt=option: self.on_checkbox_change(key, opt, e))
                                
                                if option == "其他":
                                    other_checkbox = checkbox
                                    other_key = f"{answer_key}_other"
                                    other_input_value = self.user_answers.get(self.current_survey, {}).get(other_key, "")
                                    other_input = ui.input(value=other_input_value, placeholder="请输入其他选项").classes("w-full")
                                    
                                    # When typing an "Other" option, auto-check the "Other" checkbox
                                    async def on_other_input_change(e, checkbox=other_checkbox, key=answer_key, other_key=other_key):
                                        if e.sender.value:
                                            if not checkbox.value:
                                                checkbox.value = True
                                                current_values = self.user_answers.get(self.current_survey, {}).get(key, [])
                                                if "其他" not in current_values:
                                                    current_values.append("其他")
                                                    await self.on_answer_change(key, type('Event', (), {'sender': type('Sender', (), {'value': current_values})})())
                                        # Store the "Other" value under a separate key
                                        await self.on_answer_change(other_key, e)
                                    
                                    # When selecting/deselecting the "Other" checkbox
                                    async def on_other_checkbox_change(e, other_input=other_input, key=answer_key, other_key=other_key):
                                        current_values = self.user_answers.get(self.current_survey, {}).get(key, [])
                                        if e.sender.value:
                                            if "其他" not in current_values:
                                                current_values.append("其他")
                                        else:
                                            if "其他" in current_values:
                                                current_values.remove("其他")
                                            # Clear the "Other" input value
                                            other_input.value = ""
                                            if self.current_survey in self.user_answers and other_key in self.user_answers[self.current_survey]:
                                                del self.user_answers[self.current_survey][other_key]
                                        
                                        await self.on_answer_change(key, type('Event', (), {'sender': type('Sender', (), {'value': current_values})})())
                                    
                                    other_input.on_value_change(on_other_input_change)
                                    checkbox.on("update:model-value", on_other_checkbox_change)
            
            # Navigation buttons
            with ui.row().classes("w-full justify-between mt-4"):
                # Previous page button
                prev_button = ui.button("上一页", icon="chevron_left").on("click", self.prev_page)
                if self.current_page_index == 0:
                    prev_button.props("disabled")
                
                # Save button
                ui.button("保存", icon="save").on(
                    "click", self.save_answers
                )
                
                # Next/submit button
                if self.current_page_index < len(page_titles) - 1:
                    ui.button("下一页", icon="chevron_right").on("click", self.next_page)
                else:
                    ui.button("提交", icon="check").on(
                        "click", lambda: self.submit_survey()
                    )

            ui.run_javascript(
                'MathJax.typesetPromise().catch(err => console.error("Typeset failed: " + err.message));'
            )
    
    async def on_answer_change(self, key, e):
        """当用户修改答案时触发"""
        if self.current_survey not in self.user_answers:
            self.user_answers[self.current_survey] = {}
        
        self.user_answers[self.current_survey][key] = e.sender.value
    
    async def on_checkbox_change(self, key, option, e):
        checked = e.sender.value
        """当用户修改多选框时触发"""
        if self.current_survey not in self.user_answers:
            self.user_answers[self.current_survey] = {}
        
        if key not in self.user_answers[self.current_survey]:
            self.user_answers[self.current_survey][key] = []
        
        current_values = self.user_answers[self.current_survey][key]
        
        if checked and option not in current_values:
            current_values.append(option)
        elif not checked and option in current_values:
            current_values.remove(option)
        
        self.user_answers[self.current_survey][key] = current_values
    
    async def prev_page(self):
        """切换到上一页"""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.build_survey_list.refresh()
            self.build_survey_page.refresh()
    
    async def validate_other_options(self, current_page_title, current_page_questions):
        """验证'其他'选项的输入"""
        for i, question in enumerate(current_page_questions):
            answer_key = f"{current_page_title}_{i}"
            
            if question["type"] in ["single_choice", "multiple_choice"] and "其他" in question["options"]:
                answers = self.user_answers.get(self.current_survey, {})
                main_answer = answers.get(answer_key)
                
                if question["type"] == "single_choice":
                    if isinstance(main_answer, str) and main_answer.startswith("其他："):
                        other_text = main_answer[len("其他："):].strip()
                        if not other_text:
                            return False, i + 1
                elif question["type"] == "multiple_choice":
                    if isinstance(main_answer, list) and "其他" in main_answer:
                        other_key = f"{answer_key}_other"
                        other_value = answers.get(other_key, "")
                        if not other_value:
                            return False, i + 1
        
        return True, None

    async def next_page(self):
        """切换到下一页"""
        survey = self.surveys[self.current_survey]
        page_titles = list(survey["questions"].keys())
        current_page_title = page_titles[self.current_page_index]
        current_page_questions = survey["questions"][current_page_title]
        
        # Check whether all questions on the current page are answered
        all_answered = True
        missing_questions = []
        
        for i, question in enumerate(current_page_questions):
            answer_key = f"{current_page_title}_{i}"
            
            if self.current_survey not in self.user_answers or answer_key not in self.user_answers[self.current_survey]:
                all_answered = False
                missing_questions.append(i + 1)
                continue
            
            answer = self.user_answers[self.current_survey][answer_key]
            if answer is None or answer == "" or (isinstance(answer, list) and len(answer) == 0):
                all_answered = False
                missing_questions.append(i + 1)
        
        if not all_answered:
            ui.notify(f"请完成第 {', '.join(map(str, missing_questions))} 题后再继续", position="center", level="warning")
            return
            
        # Validate "Other" options
        is_valid, question_num = await self.validate_other_options(current_page_title, current_page_questions)
        if not is_valid:
            ui.notify(f"第 {question_num} 题选择了'其他'选项但未填写具体内容", position="center", level="warning")
            return
        
        # Save free-text answers
        await async_add_user_action(
            self.username,
            f"{self.current_survey}::answers",
            self.user_answers[self.current_survey],
        )
        # print(self.user_answers[self.current_survey])
        
        if self.current_page_index < len(page_titles) - 1:
            self.current_page_index += 1
            self.build_survey_list.refresh()
            self.build_survey_page.refresh()
    
    async def save_answers(self):
        """保存用户回答"""
        
        # Update user responses
        if self.current_survey not in self.user_answers:
            self.user_answers[self.current_survey] = {}
                
        # Save to the database
        await async_add_user_action(
            self.username,
            f"{self.current_survey}::answers",
            self.user_answers[self.current_survey],
        )
        
        ui.notify("回答已保存", position="center", level="positive")
    
    async def submit_survey(self):
        """提交问卷"""
        survey = self.surveys[self.current_survey]
        page_titles = list(survey["questions"].keys())
        
        # Check all questions on all pages
        all_answered = True
        missing_pages = {}
        
        for page_title in page_titles:
            page_questions = survey["questions"][page_title]
            missing_questions = []
            
            for i, question in enumerate(page_questions):
                answer_key = f"{page_title}_{i}"
                
                if (self.current_survey not in self.user_answers or 
                    answer_key not in self.user_answers[self.current_survey]):
                    all_answered = False
                    missing_questions.append(i + 1)
                    continue
                
                answer = self.user_answers[self.current_survey][answer_key]
                if answer is None or answer == "" or (isinstance(answer, list) and len(answer) == 0):
                    all_answered = False
                    missing_questions.append(i + 1)
            
            if missing_questions:
                missing_pages[page_title] = missing_questions
        
        if not all_answered:
            error_msg = "以下问题未完成:\n"
            for page_title, questions in missing_pages.items():
                error_msg += f"{page_title}: 第 {', '.join(map(str, questions))} 题\n"
            ui.notify(error_msg, position="center", level="warning")
            return
        
        # Validate "Other" options on all pages
        for page_title in page_titles:
            page_questions = survey["questions"][page_title]
            is_valid, question_num = await self.validate_other_options(page_title, page_questions)
            if not is_valid:
                ui.notify(f"{page_title} 第 {question_num} 题选择了'其他'选项但未填写具体内容", 
                         position="center", level="warning")
                return
        
        # Save to the database
        await async_add_user_action(
            self.username,
            f"{self.current_survey}::answers",
            self.user_answers[self.current_survey],
        )
        
        # Mark as submitted
        await async_add_user_action(
            self.username,
            f"{self.current_survey}::submit",
            {"stage": self.stage, "sname": self.current_survey},
        )
        
        # Update status
        self.survey_status[self.current_survey]["submitted"] = True
        self.build_survey_list.refresh()
        
        # Set the submitted flag so closing the page won't prompt
        await ui.run_javascript("window.surveySubmitted = true;")
        
        ui.notify("问卷已提交", position="center", level="positive")
    
