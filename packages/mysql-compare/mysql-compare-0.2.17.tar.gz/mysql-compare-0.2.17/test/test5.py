import datetime
import json
from dataclasses import dataclass

from mysql.connector import MySQLConnection, connect


@dataclass
class Checkpoint:
    checkpoint: dict
    processed: int


json_string = {"checkpoint": {"Abc": datetime.datetime.now(), "asdf": "加快科技"}, "processed": 11111}
json_string2 = {"checkpoint": {"Abc": datetime.datetime.now(), "asdf": "加快科技1"}, "processed": 11111}

x = json.dumps(json_string, ensure_ascii=True, default=str)
x2 = json.dumps(json_string2, ensure_ascii=True, default=str)

print(x)
print(x2)
print(x == x2)
# dct: Checkpoint = Checkpoint(**json.loads(json_string))
# print(dct)

# datat: list[tuple[str, str]] = [("Abc", "date")]


# for k, v in dct.checkpoint.items():
#     for coln, colt in datat:
#         if k == coln:
#             if colt == "date":
#                 dct.checkpoint[k] = datetime.datetime.strptime(v, "%Y-%m-%d")
# print(dct.checkpoint)


# # def read_checkpoint(self):
# #     if os.path.exists(self.checkpoint_file):
# #         with open(self.checkpoint_file, "r", encoding="utf8") as f:
# #             return json.load(f)
# #     else:
# #         return None
