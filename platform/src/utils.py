import logging
import time

# from sqlitedict import SqliteDict


def io_he(text):
    return text


def io_rhe(text):
    text = repr(text)
    return io_he(text)


class UnixTimeStampFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return str(int(time.time()))


formatter = UnixTimeStampFormatter("[%(asctime)s] %(levelname)s %(message)s")

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s %(message)s",
#     handlers=[logging.FileHandler("data/app.log"), logging.StreamHandler()],
# )

logger = logging.getLogger()
for handler in logger.handlers:
    handler.setFormatter(formatter)

# db = SqliteDict("data/app.sqlite3")


def log_event(event_type, user, data):
    logger.info(
        "event_type: %r, user: %r, wg: %r, data: %r",
        event_type,
        user,
        data,
    )


# def user_prefix(user):
#     return f"user::{repr(user)}"


# DELIMITER = "::"


# def get_user_state(user, state_key):
#     return db.get(f"{user_prefix(user)}{DELIMITER}{repr(state_key)}")


# def set_user_state(user, state_key, state_value):
#     db[f"{user_prefix(user)}{DELIMITER}{repr(state_key)}"] = state_value
#     db.commit()


# def reset_user_state(user):
#     for key in db.keys():
#         if key.startswith(f"{user_prefix(user)}{DELIMITER}"):
#             del db[key]
#     db.commit()


