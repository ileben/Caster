from castervoice.lib.imports import *


class AndroidStudioRule(MergeRule):
    pronunciation = "android studio"

    mapping = {
        "run app|resume app":
            R(Key("s-f10")),
        "stop running":
            R(Key("c-f2")),
        "build app":
            R(Key("c-f9")),
    }
    extras = [
        Dictation("text"),
        Dictation("mim"),
        IntegerRefST("n", 1, 1000),
    ]
    defaults = {"n": 1, "mim": ""}


context = AppContext(executable="studio64")
control.non_ccr_app_rule(AndroidStudioRule(), context=context)
