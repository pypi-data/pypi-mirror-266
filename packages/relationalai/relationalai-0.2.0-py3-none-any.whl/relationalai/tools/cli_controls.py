#pyright: reportPrivateImportUsage=false

import io
import os
from re import Pattern
from typing import Any, List, cast
from pathlib import Path
from InquirerPy.base.complex import FakeDocument
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.validation import ValidationError
import rich
from rich.console import Console
import sys
from InquirerPy import inquirer, utils as inquirer_utils
from InquirerPy.base.control import Choice
import time
import threading
import itertools
from ..debugging import jupyter

#--------------------------------------------------
# Style
#--------------------------------------------------

STYLE = inquirer_utils.get_style({
    "fuzzy_prompt": "#e5c07b"
}, False)

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def rich_str(string:str, style:str|None = None) -> str:
    output = io.StringIO()
    console = Console(file=output, force_terminal=True)
    console.print(string, style=style)
    return output.getvalue()

def nat_path(path: Path, base: Path):
    resolved_path = path.resolve()
    resolved_base = base.resolve()
    if resolved_base in resolved_path.parents or resolved_path == resolved_base:
        return resolved_path.relative_to(resolved_base)
    else:
        return resolved_path.absolute()

#--------------------------------------------------
# Dividers
#--------------------------------------------------

def divider(console=None, flush=False):
    div = "\n[dim]---------------------------------------------------\n "
    if console is None:
        rich.print(div)
    else:
        console.print(div)
    if flush:
        sys.stdout.flush()

def abort():
    rich.print()
    rich.print("[yellow]Aborted")
    divider()
    sys.exit(1)

#--------------------------------------------------
# Prompts
#--------------------------------------------------

default_bindings = cast(Any, {
    "interrupt": [
        {"key": "escape"},
        {"key": "c-c"},
        {"key": "c-d"}
    ],
    "skip": [
        {"key": "c-s"}
    ]
})

def prompt(message:str, value:str|None, newline=False) -> str:
    if value:
        return value
    try:
        result:str = inquirer.text(message, keybindings=default_bindings).execute()
    except KeyboardInterrupt:
        abort()
        raise Exception("Unreachable")
    if newline:
        rich.print("")
    return result

def select(message:str, choices:List[str|Choice], value:str|None, newline=False, **kwargs) -> str|Any:
    if value:
        return value
    try:
        result:str = inquirer.select(message, choices, keybindings=default_bindings, **kwargs).execute()
    except KeyboardInterrupt:
        abort()
        raise Exception("Unreachable")
    if newline:
        rich.print("")
    return result

def fuzzy(message:str, choices:List[str], default:str|None = None, multiselect=False, **kwargs) -> str:
    try:
        kwargs["keybindings"] = default_bindings
        if multiselect:
            kwargs["keybindings"] = {
                "toggle": [
                    {"key": "tab"},   # toggle choices
                ],
                "toggle-down": [
                    {"key": "tab", "filter":False},
                ],
            }.update(default_bindings)
            kwargs["multiselect"] = True

        scroll_to_ix = None
        # @FIXME: Future improvement to make it optionally case insensitive
        if default and default in choices:
            scroll_to_ix = choices.index(default)
            default = None

        prompt = inquirer.fuzzy(message, choices=choices, default=default or "", max_height=8, border=True, style=STYLE, **kwargs)
        if scroll_to_ix is not None:
            prompt.content_control.selected_choice_index = scroll_to_ix
        return prompt.execute()
    except KeyboardInterrupt:
        return abort()

def confirm(message:str, default:bool = False) -> bool:
    try:
        return inquirer.confirm(message, default=default, keybindings=default_bindings).execute()
    except KeyboardInterrupt:
        return abort()

def text(message:str, default:str|None = None) -> str:
    try:
        return inquirer.text(message, default=default or "", keybindings=default_bindings).execute()
    except KeyboardInterrupt:
        return abort()

def password(message:str, default:str|None = None) -> str:
    try:
        return inquirer.secret(message, default=default or "", keybindings=default_bindings).execute()
    except KeyboardInterrupt:
        return abort()

def file(message: str, start_path:Path|None = None, pattern:str|Pattern|None = None, default:str|None = None, allow_freeform=False, **kwargs) -> str|None:
    try:
        return FuzzyFile(message, start_path, allow_freeform=allow_freeform, max_height=8, border=True, style=STYLE, **kwargs).execute()
    except KeyboardInterrupt:
        return abort()

class FuzzyFile(inquirer.fuzzy):
    def __init__(self, message: str, initial_path: Path|None = None, allow_freeform = False,  *args, **kwargs):
        self.initial_path = initial_path or Path()
        self.current_path = Path(self.initial_path)
        self.allow_freeform = allow_freeform

        kwargs["keybindings"] = {
            **default_bindings,
            "answer": [
                {"key": os.sep},
                {"key": "enter"},
                {"key": "tab"},
                {"key": "right"}
            ],
            **kwargs.get("keybindings", {})
        }

        super().__init__(message, *args, **kwargs, choices=self._get_choices)

    def _get_prompt_message(self) -> List[tuple[str, str]]:
        pre_answer = ("class:instruction", f" {self.instruction} " if self.instruction else " ")
        result = str(nat_path(self.current_path, self.initial_path))

        if result:
            sep = " " if self._amark else ""
            return [
                ("class:answermark", self._amark),
                ("class:answered_question", f"{sep}{self._message} "),
                ("class:answer", f"{result}{os.sep if not self.status['answered'] else ''}"),
            ]
        else:
            sep = " " if self._qmark else ""
            return [
                ("class:answermark", self._amark),
                ("class:questionmark", self._qmark),
                ("class:question", f"{sep}{self._message}"),
                pre_answer
            ]

    def _handle_enter(self, event: KeyPressEvent) -> None:
        try:
            fake_document = FakeDocument(self.result_value)
            self._validator.validate(fake_document)  # type: ignore
            cc = self.content_control
            if self._multiselect:
                self.status["answered"] = True
                if not self.selected_choices:
                    self.status["result"] = [cc.selection["name"]]
                    event.app.exit(result=[cc.selection["value"]])
                else:
                    self.status["result"] = self.result_name
                    event.app.exit(result=self.result_value)
            else:
                res_value = cc.selection["value"]
                self.current_path /= res_value
                if self.current_path.is_dir():
                    self._update_choices()
                else:
                    self.status["answered"] = True
                    self.status["result"] = cc.selection["name"]
                    event.app.exit(result=str(nat_path(self.current_path, self.initial_path)))
        except ValidationError as e:
            self._set_error(str(e))
        except IndexError:
            self.status["answered"] = True
            res = self._get_current_text() if self.allow_freeform else None
            if self._multiselect:
                res = [res] if res is not None else []
            self.status["result"] = res
            event.app.exit(result=res)
        
    def _get_choices(self, _ = None):
        choices = os.listdir(self.current_path)
        choices.append("..")
        return choices

    def _update_choices(self):
        raw_choices = self._get_choices()
        cc = self.content_control
        cc.selected_choice_index = 0
        cc._raw_choices = raw_choices
        cc.choices = cc._get_choices(raw_choices, None)
        cc._safety_check()
        cc._format_choices()
        self._buffer.reset()

#--------------------------------------------------
# Spinner
#--------------------------------------------------

class Spinner:
    busy = False
    delay = 0.1

    def __init__(self, message="", finished="", delay=None):
        self.message = message
        self.finished = finished
        self.spinner_generator = itertools.cycle([ "▰▱▱▱", "▰▰▱▱", "▰▰▰▱", "▰▰▰▰", "▱▰▰▰", "▱▱▰▰", "▱▱▱▰", "▱▱▱▱" ])
        if delay and float(delay):
            self.delay = delay

    def get_message(self):
        return rich_str(f"[magenta]{next(self.spinner_generator)} {self.message}").strip()

    def get_clear(self, message:str):
        return '\b'* len(message.encode('utf-8'))

    def spinner_task(self):
        while self.busy:
            message = self.get_message()
            sys.stdout.write(message)
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write(self.get_clear(message))
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        if jupyter.ipython:
            message = self.get_message()
            sys.stdout.write(message)
            sys.stdout.flush()
        else:
            threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        if exception is not None:
            return False
        time.sleep(self.delay)
        message = self.get_message()
        sys.stdout.write(self.get_clear(message))
        if self.finished != "":
            final_message = f"[green]▰▰▰▰ {self.finished}"
            final_message += " " * (len(message) - len(final_message))
            rich.print(final_message)
        elif self.finished == "":
            sys.stdout.write(self.get_clear(message))
            sys.stdout.write(" "*len(message.encode('utf-8')))
            sys.stdout.write(self.get_clear(message))
            sys.stdout.flush()
