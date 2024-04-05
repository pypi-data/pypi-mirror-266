"""Declare all global constants."""

COMMANDS = {
    "start": "Check whether I am alive",
    "forward": "Set a new forward",
    "remove": "Remove an existing forward",
    "help": "Learn usage",
}

REGISTER_COMMANDS = True
# 缓存保留消息条数
KEEP_LAST_MANY = 10000

MONGO_DB_NAME = "tg-config"
MONGO_COL_NAME = "tg-instance-0"
