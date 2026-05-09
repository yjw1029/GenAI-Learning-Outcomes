import json
import time
from datetime import datetime

import pytz
from database import (
    async_add_user_action_wtime,
    async_recover_item_by_id,
    async_remove_action_by_id,
    get_async_all_actions_sorted,
)
from nicegui import app, run, ui

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


class AdminPageBuilder:
    def __init__(self, cfg, user=None):
        self.cfg = cfg

        self.user = user
        self.username = user.get("username")

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
            with ui.row().classes("col-start-1 col-end-11 bg-white p-4"):
                with ui.row().classes("w-full"):
                    ui.markdown(content="##### 进度历史")

                with ui.row().classes("w-full"):
                    ui.markdown(content="**选择用户**")

                with ui.row().classes("w-full"):
                    self.user_select = ui.select(
                        list(self.cfg.defaults["user"].keys()),
                        label="请选择用户",
                        with_input=True,
                    ).classes("w-1/3")

                with ui.row().classes("w-full"):
                    ui.markdown(content="**添加阶段**")

                with ui.row().classes("w-full grid grid-cols-12 items-center"):
                    with ui.column().classes("col-span-2"):
                        stage = ui.select(
                            options=[S0, S1, S2, S3, S4, S5, S6, S7, S8, S9], label="阶段"
                        ).classes("w-full")

                    with ui.column().classes("col-span-2"):
                        timestamp = ui.input(
                            label="进入时间 (默认为当前时间)", value=None
                        ).classes("w-full")

                    with ui.column().classes("col-span-2"):
                        add_button = ui.button(icon="add").props("flat dense")

                with ui.row().classes("w-full items-center"):
                    ui.markdown(content="**点击删除按钮删对应历史，点击历史id查看完整value**")
                    refresh_button = ui.button(icon="refresh").props("flat dense")

                with ui.row().classes("w-full items-center"):
                    self.show_deleted = ui.checkbox("展示已删除进度历史")

                with ui.row().classes("w-full"):
                    columns = [
                        {
                            "name": "id",
                            "label": "ID",
                            "field": "id",
                            "required": True,
                            "sortable": True,
                            "align": "left",
                        },
                        {
                            "name": "name",
                            "label": "Name",
                            "field": "name",
                            "required": True,
                            "sortable": True,
                            "align": "left",
                        },
                        {
                            "name": "time",
                            "label": "Time",
                            "field": "time",
                            "sortable": True,
                            "align": "left",
                        },
                        {
                            "name": "deleted",
                            "label": "Deleted",
                            "field": "deleted",
                            "sortable": True,
                            "align": "left",
                        },
                        {
                            "name": "value",
                            "label": "Value",
                            "field": "value",
                            "sortable": True,
                            "align": "left",
                        },
                    ]
                    with ui.table(columns, rows=[], row_key="id").classes(
                        "w-full bordered"
                    ) as self.hist_table:
                        self.hist_table.add_slot(
                            "header",
                            r"""
                            <q-tr :props="props">
                                <q-th auto-width />
                                <q-th v-for="col in props.cols" :key="col.name" :props="props">
                                    {{ col.label }}
                                </q-th>
                            </q-tr>
                        """,
                        )
                        self.hist_table.add_slot(
                            "body",
                            r"""
                            <q-tr :props="props">
                                <q-td auto-width>
                                    <q-btn @click="$parent.$emit('del', props)" icon="delete" flat dense color='red' v-if="!props.row.deleted" />
                                    <q-btn @click="$parent.$emit('restore', props)" icon="restore" flat dense color='green' v-else/>
                                </q-td>
                                <q-td v-for="col in props.cols" :key="col.name" :props="props" @click="col.name === 'id' ? props.expand = !props.expand : ''">
                                    {{ col.value }}
                                </q-td>
                            </q-tr>
                            <q-tr v-show="props.expand" :props="props">
                                <q-td colspan="100%">
                                    <div class="text-left">{{ props.row.full_value }}</div>
                                </q-td>
                            </q-tr>
                        """,
                        )

                china_tz = pytz.timezone("Asia/Shanghai")

                async def retrieve_histroy():
                    rows = []
                    response = await get_async_all_actions_sorted(
                        self.user_select.value
                    )
                    for i in response:
                        if self.show_deleted.value or not i.deleted:
                            utc_time = datetime.utcfromtimestamp(i.timestamp)
                            utc_time = utc_time.replace(tzinfo=pytz.utc)
                            china_time = utc_time.astimezone(china_tz)
                            time_str = china_time.strftime("%Y-%m-%d %H:%M:%S")
                            value = json.dumps(i.value, ensure_ascii=False)
                            rows.append(
                                {
                                    "id": i.id,
                                    "name": i.action,
                                    "deleted": i.deleted,
                                    "value": value[:20] + "...",
                                    "time": time_str,
                                    "full_value": value,
                                }
                            )
                    self.hist_table.update_rows(rows)
                    # ui.table(columns=columns, rows=rows, row_key='name')

                async def delete_history(msg):
                    await async_remove_action_by_id(msg.args["row"]["id"])
                    await retrieve_histroy()

                async def restore_history(msg):
                    await async_recover_item_by_id(msg.args["row"]["id"])
                    await retrieve_histroy()

                async def add_history():
                    if stage.value:
                        await async_add_user_action_wtime(
                            self.user_select.value,
                            action="progress",
                            value={"stage": stage.value, "admin": True},
                            timestamp=timestamp.value
                            if timestamp.value
                            else int(time.time()),
                        )
                        await retrieve_histroy()
                    else:
                        ui.notify("请选择阶段")

                self.user_select.on("update:model-value", retrieve_histroy)
                self.hist_table.on("del", delete_history)
                self.show_deleted.on("update:model-value", retrieve_histroy)
                self.hist_table.on("restore", restore_history)

                refresh_button.on_click(retrieve_histroy)
                add_button.on_click(add_history)
