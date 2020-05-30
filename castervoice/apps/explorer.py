from castervoice.lib.imports import *
from castervoice.lib import lex

class IERule(MergeRule):
    pronunciation = "explorer"

    mapping = {
        "edit address | address bar":
            R(Key("a-d")),
        "copy address":
            R(Key("a-d/20, c-c")),
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
            
        "(edit in|editing) notepad":
            R(Function(lex.current_file_command, command=r"C:\Program Files\Notepad++\notepad++.exe {}")),
            
        "subversion [<folder>] difference":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:diff /path:{}")),
        "subversion [<folder>] log":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:log /path:{}")),
        "subversion [<folder>] blame":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:blame /path:{}")),
        "subversion [<folder>] browser":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:repobrowser /path:{}")),
        "subversion [<folder>] properties":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:properties /path:{}")),
        "subversion [<folder>] commit":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:commit /path:{}")),
        "subversion [<folder>] revert":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:revert /path:{}")),
        "subversion [<folder>] update":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:update /path:{}")),
        "subversion [<folder>] add":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:add /path:{}")),
        "subversion [<folder>] delete":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:remove /path:{}")),
        "subversion [<folder>] rename":
            R(Function(lex.current_file_command, extra={"folder"}, command="TortoiseProc.exe /command:rename /path:{}")),
        "console here":
            R(Function(lex.current_file_command, folder=True, command="C:\\Program Files\\ConEmu\\ConEmu64.exe -dir \"{}\"")),
    }
    extras = [
        Dictation("text"),
        IntegerRefST("n", 1, 1000),
        Choice("folder", {
            "folder": True,
        }),
    ]
    defaults = {"n": 1}


context = AppContext(executable="explorer")
control.non_ccr_app_rule(IERule(), context=context)