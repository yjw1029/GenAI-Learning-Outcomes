import csv
import os

import dotenv
import toml
from utils import log_event

dotenv.load_dotenv()


class AppConfig:
    def __init__(self, config_file=None):
        self.defaults = {"chat_tab": {}}

        self.known_settings = {k: list(v.keys()) for k, v in self.defaults.items()}

        if config_file:
            log_event("load_config", None, {"config_file": config_file})
            self.load_config(config_file)

        self.try_load_from_env()

        log_event("init_config", None, self.defaults)

    def load_config(self, config_file):
        try:
            with open(config_file, "r") as f:
                config_data = toml.load(f)

            self._validate_config(config_data)
            self._update_config(config_data)

            if "users" in self.defaults:
                if "auth_file" in self.defaults["users"]:
                    self.defaults["user"] = {}
                    with open(self.defaults["users"]["auth_file"], "r") as f:
                        reader = csv.reader(f)
                        next(reader)  # skip first line
                        for row in reader:
                            user = row[0]
                            password = row[1]
                            vgroup = row[2]
                            comment = row[3]
                            assert (
                                row[0] not in self.defaults["user"]
                            ), f"Duplicate user {user}"
                            assert (
                                vgroup in self._allvgroup()
                            ), f"Unknown vgroup {vgroup} for user {user}"
                            self.defaults["user"][user] = {
                                "password": password,
                                "vgroup": vgroup,
                                "comment": comment,
                            }
        except FileNotFoundError:
            log_event(
                "config_not_found",
                None,
                {"config_file": config_file, "message": "Using default settings."},
            )
        except toml.TomlDecodeError as e:
            log_event(
                "config_not_error",
                None,
                {"config_file": config_file, "message": "TomlDecodeError."},
            )
            raise ValueError(f"Configuration error: {e}. Exiting.")
        except ValueError as e:
            log_event(
                "config_not_error",
                None,
                {"config_file": config_file, "message": "ValueError."},
            )
            raise ValueError(f"Configuration error: {e}. Exiting.")

    def try_load_from_env(self):
        def _from_env(self, env_key, section_key, config_key):
            if env_key in os.environ:
                self.defaults[section_key][config_key] = os.environ[env_key]
                log_event("config_from_env", None, {env_key: os.environ[env_key]})

        _from_env(self, "OPENAI_API_KEY", "chat_tab", "openai_api_key")
        _from_env(self, "OPENAI_BASE_URL", "chat_tab", "openai_base_url")
        _from_env(self, "OPENAI_MODEL", "chat_tab", "openai_model")
        _from_env(self, "OPENAI_API_TYPE", "chat_tab", "openai_api_type")
        _from_env(self, "AZURE_OPENAI_ENDPOINT", "chat_tab", "azure_endpoint")

    def _update_config(self, new_config):
        for key, value in new_config.items():
            if isinstance(value, dict):
                self.defaults[key] = self._update_config_recursive(
                    self.defaults.get(key, {}), value
                )
            else:
                self.defaults[key] = value
        return self.defaults

    @staticmethod
    def _update_config_recursive(target, new_values):
        for key, value in new_values.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                target[key] = AppConfig._update_config_recursive(target[key], value)
            else:
                target[key] = value
        return target

    def _validate_config(self, config_data):
        for section, settings in config_data.items():
            if section not in self.known_settings:
                log_event("config_unknown_section", None, {"section": section})
            for setting in settings:
                if section in self.known_settings:
                    if setting not in self.known_settings[section]:
                        log_event(
                            "config_unknown_setting",
                            None,
                            {"section": section, "setting": setting},
                        )

    def _alluser(self):
        return list(self.defaults["user"].keys())

    def _userinfo(self, user):
        return self.defaults["user"][user]

    def userinfo(self, user):
        return self._userinfo(user)

    def _uservgroup(self, user):
        return self._userinfo(user)["vgroup"]

    def uservgroup(self, user):
        return self._uservgroup(user)

    # def _usergroup(self, user):
    #     vgroup = self._uservgroup(user)
    #     # working_group = get_user_state(user, "working_group")
    #     if working_group is None:
    #         working_group = self.getvgroup(vgroup, "default_group")
    #     return working_group

    def usergroupp(self, user):
        return self._usergroup(user)

    def _allvgroup(self):
        return list(self.defaults["vgroups"].keys())

    def _allgroup(self):
        return list(self.defaults["groups"].keys())

    def _vgroupinfo(self, vgroup):
        return self.defaults["vgroups"][vgroup]

    def _groupinfo(self, group):
        return self.defaults["groups"][group]

    def valid_user_pass(self, user, password):
        if user in self._alluser():
            return self._userinfo(user)["password"] == password
        else:
            return False

    def get(self, section, option):
        try:
            return self.defaults[section][option]
        except KeyError:
            log_event("config_get_error", None, {"section": section, "option": option})

    def getvgroup(self, vgroup, option):
        assert vgroup in self._allvgroup(), f"Unknown vgroup {vgroup}"
        vgcfg = self._vgroupinfo(vgroup)
        _config = {
            "default_group": vgcfg.get("test_group", None),
            "test_group": vgcfg.get("test_group", None),
            "learning_group": vgcfg.get("learning_group", None),
            "a1_group": vgcfg.get("a1_group", None),
            "a2_group": vgcfg.get("a2_group", None),
            "review_group": vgcfg.get("review_group", None),
        }
        return _config[option]

    def getgroup(self, group, section, option):
        assert group in self._allgroup(), f"Unknown group {group}"
        gcfg = self._groupinfo(group)

        _config = {
            "python_tab": {
                "enabled": gcfg.get("python_tab_enabled", False),
            },
            "code_tab": {
                "enabled": gcfg.get("code_tab_enabled", False),
                "available_problem": gcfg.get("code_available_problem", []),
            },
            "math_tab": {
                "enabled": gcfg.get("math_tab_enabled", False),
                "available_problem": gcfg.get("math_available_problem", []),
            },
            "chat_tab": {
                "enabled": gcfg.get("chat_tab_enabled", False),
            },
        }
        return _config[section][option]

    def getuser(self, user, section, option):
        group = self._usergroup(user)
        return self.getgroup(group, section, option)
