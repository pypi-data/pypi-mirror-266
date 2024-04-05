# pyright: reportUnusedFunction=false

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from functools import partial
from typing import Any

import attrs
import cattrs
from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text.html import HTML
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts.progress_bar import ProgressBar, ProgressBarCounter, formatters
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import ValidationError, Validator
from questionary import Choice
from questionary import confirm as _confirm
from questionary import password as _password
from questionary import path as _path
from questionary.prompts.common import InquirerControl, Separator, create_inquirer_layout
from questionary.question import Question

from . import pkg_models


class AttrsFieldValidator(Validator):
    "One-off validators for attrs fields."

    def __init__(self, attribute: attrs.Attribute[object], converter: cattrs.Converter) -> None:
        self._field_name = attribute.name
        self._FieldWrapper = attrs.make_class(
            '_FieldWrapper',
            {
                self._field_name: attrs.field(
                    default=attribute.default,
                    validator=attribute.validator,
                    repr=attribute.repr,
                    hash=attribute.hash,
                    init=attribute.init,
                    metadata=attribute.metadata,
                    type=attribute.type,
                    converter=attribute.converter,
                    kw_only=attribute.kw_only,
                    eq=attribute.eq,
                    order=attribute.order,
                    on_setattr=attribute.on_setattr,
                )
            },
        )
        self._converter = converter

    def validate(self, document: Document) -> None:
        try:
            self._converter.structure({self._field_name: document.text}, self._FieldWrapper)
        except Exception as exc:
            raise ValidationError(
                0, '\n'.join(cattrs.transform_error(exc, format_exception=lambda e, _: str(e)))
            ) from exc


class PkgChoice(Choice):
    def __init__(self, *args: Any, pkg: pkg_models.Pkg, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pkg = pkg


qstyle = Style(
    [
        ('qmark', 'fg:ansicyan'),
        ('question', 'bold'),
        ('answer', 'fg: nobold'),
        ('skipped-answer', 'fg:ansiyellow'),
        ('highlight-sub', 'fg:ansimagenta'),
    ]
)


SKIP = ()
skip = Choice([('underline', 's'), ('', 'kip')], SKIP)

confirm = partial(_confirm, qmark='?', style=qstyle)
path = partial(_path, qmark='>', style=qstyle)
password = partial(_password, style=qstyle)


def checkbox(message: str, choices: Sequence[Choice], **inquirer_kwargs: Any) -> Question:
    def get_prompt_tokens():
        tokens: list[tuple[str, str]] = [('class:question', message)]
        if ic.is_answered:
            tokens.append(('class:answer', '  done'))
        else:
            tokens.append(
                (
                    'class:instruction',
                    '  (use arrow keys to move, <space> to select, <o> to open in browser'
                    ' and <enter> to continue)',
                )
            )
        return tokens

    ic = InquirerControl(
        choices,
    )
    bindings = KeyBindings()

    @bindings.add(Keys.ControlQ, eager=True)
    @bindings.add(Keys.ControlC, eager=True)
    def abort(event: KeyPressEvent):
        event.app.exit(exception=KeyboardInterrupt, style='class:aborting')

    @bindings.add(' ', eager=True)
    def toggle(event: KeyPressEvent):
        pointed_choice = ic.get_pointed_at().value
        if pointed_choice in ic.selected_options:
            ic.selected_options.remove(pointed_choice)
        else:
            ic.selected_options.append(pointed_choice)

    @bindings.add('i', eager=True)
    def invert(event: KeyPressEvent):
        inverted_selection = [
            c.value
            for c in ic.choices
            if not isinstance(c, Separator)
            and c.value not in ic.selected_options
            and not c.disabled
        ]
        ic.selected_options = inverted_selection

    @bindings.add(Keys.Down, eager=True)
    @bindings.add('j', eager=True)
    def move_cursor_down(event: KeyPressEvent):
        ic.select_next()
        while not ic.is_selection_valid():
            ic.select_next()

    @bindings.add(Keys.Up, eager=True)
    @bindings.add('k', eager=True)
    def move_cursor_up(event: KeyPressEvent):
        ic.select_previous()
        while not ic.is_selection_valid():
            ic.select_previous()

    @bindings.add(Keys.ControlM, eager=True)
    def set_answer(event: KeyPressEvent):
        ic.is_answered = True
        event.app.exit(result=[c.value for c in ic.get_selected_values()])

    @bindings.add('o', eager=True)
    def open_url(event: KeyPressEvent):
        choice = ic.get_pointed_at()
        if isinstance(choice, PkgChoice):
            import webbrowser

            webbrowser.open(choice.pkg.url)

    @bindings.add(Keys.Any)
    def default(event: KeyPressEvent):
        # Disallow inserting other text
        pass

    layout = create_inquirer_layout(ic, get_prompt_tokens, **inquirer_kwargs)
    return Question(Application(layout=layout, key_bindings=bindings, style=qstyle))


def select(
    message: str,
    choices: Sequence[str] | Sequence[Choice],
    initial_choice: str | Choice | None = None,
    **inquirer_kwargs: Any,
) -> Question:
    def get_prompt_tokens():
        tokens: list[tuple[str, str]] = [('class:qmark', '- '), ('class:question', message)]
        if ic.is_answered:
            answer = ic.get_pointed_at()
            title = answer.title
            assert title
            tokens.extend(
                [
                    ('', ' '),
                    (
                        'class:skipped-answer' if answer is skip else 'class:answer',
                        ''.join(t[1] for t in title) if isinstance(title, list) else title,
                    ),
                ]
            )
        return tokens

    ic = InquirerControl(
        choices,
        use_indicator=False,
        initial_choice=initial_choice,
    )
    bindings = KeyBindings()

    @bindings.add(Keys.ControlQ, eager=True)
    @bindings.add(Keys.ControlC, eager=True)
    def abort(event: KeyPressEvent):
        event.app.exit(exception=KeyboardInterrupt, style='class:aborting')

    @bindings.add(Keys.Down, eager=True)
    @bindings.add('j', eager=True)
    def move_cursor_down(event: KeyPressEvent):
        ic.select_next()
        while not ic.is_selection_valid():
            ic.select_next()

    @bindings.add(Keys.Up, eager=True)
    @bindings.add('k', eager=True)
    def move_cursor_up(event: KeyPressEvent):
        ic.select_previous()
        while not ic.is_selection_valid():
            ic.select_previous()

    @bindings.add(Keys.ControlM, eager=True)
    def set_answer(event: KeyPressEvent):
        ic.is_answered = True
        event.app.exit(result=ic.get_pointed_at().value)

    @bindings.add('o', eager=True)
    def open_url(event: KeyPressEvent):
        choice = ic.get_pointed_at()
        if isinstance(choice, PkgChoice):
            import webbrowser

            webbrowser.open(choice.pkg.url)

    if skip in ic.choices:

        @bindings.add('s', eager=True)
        def skip_question(event: KeyPressEvent):
            ic.pointed_at = -1
            set_answer(event)

    @bindings.add(Keys.Any)
    def default(event: KeyPressEvent):
        # Disallow inserting other text
        pass

    layout = create_inquirer_layout(ic, get_prompt_tokens, **inquirer_kwargs)
    return Question(Application(layout=layout, key_bindings=bindings, style=qstyle))


def ask(question: Question) -> Any:
    return asyncio.run(question.application.run_async())


def _format_mb(value: int):
    return f'{value / 2 ** 20:.1f}'


class _DownloadProgress(formatters.Progress):
    template = '<current>{current:>3}</current>/<total>{total:>3}</total>MB'

    def format(self, progress_bar: ProgressBar, progress: ProgressBarCounter[object], width: int):
        return HTML(self.template).format(
            current=_format_mb(progress.items_completed),
            total=_format_mb(progress.total) if progress.total is not None else '?',
        )


def make_progress_bar() -> ProgressBar:
    "``ProgressBar`` with download progress expressed in megabytes."
    return ProgressBar(
        formatters=[
            formatters.Label(),
            formatters.Text(' '),
            formatters.Percentage(),
            formatters.Text(' '),
            formatters.Bar(),
            formatters.Text(' '),
            _DownloadProgress(),
            formatters.Text(' '),
            formatters.Text('eta [', style='class:time-left'),
            formatters.TimeLeft(),
            formatters.Text(']', style='class:time-left'),
            formatters.Text(' '),
        ],
    )
