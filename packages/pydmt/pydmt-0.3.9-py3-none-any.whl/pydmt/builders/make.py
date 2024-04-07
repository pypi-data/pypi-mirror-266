"""
This module runs make
"""


from pydmt.utils.filesystem import mkdir_touch
from pydmt.utils.subprocess import check_call_ve

from pydmt.api.one_source_one_target import OneSourceOneTarget

SOURCE_FILE = "Makefile"


class BuilderMake(OneSourceOneTarget):
    def build(self) -> None:
        args = [
            "make",
        ]
        check_call_ve(args)
        mkdir_touch(self.target)
