from castervoice.lib.imports import *

class IERule(MergeRule):
    pronunciation = "explorer"

    mapping = {
        "edit address | address bar":
            R(Key("a-d")),
        "copy address":
            R(Key("a-d/20, c-c")),
        "show menu":
            R(Key("s-f10")),
        "new window":
            R(Key("c-n")),
        "new folder":
            R(Key("cs-n")),
        "new file":
            R(Key("a-f, w, t")),
        "(show | file | folder) properties":
            R(Key("a-enter")),
        "folder up | get up":
            R(Key("a-up")),
        "get back":
            R(Key("a-left")),
        "get forward":
            R(Key("a-right")),
        "search [<text>]":
            R(Key("a-d, tab:1") + Text("%(text)s")),
        "(navigation | nav | left) pane":
            R(Key("a-d, tab:2")),
        "(center pane | (file | folder) (pane | list))":
            R(Key("a-d, tab:3")),
            # for the sort command below,
            # once you've selected the relevant heading for sorting using the arrow keys, press enter
        "sort [headings]":
            R(Key("a-d, tab:4")),

    }
    extras = [
        Dictation("text"),
        IntegerRefST("n", 1, 1000),
    ]
    defaults = {"n": 1}


context = AppContext(executable="explorer")
control.non_ccr_app_rule(IERule(), context=context)