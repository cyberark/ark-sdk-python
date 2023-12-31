import argparse
import sys

if sys.platform != 'win32':
    try:
        import readline  # pylint: disable=unused-import
    except ImportError:
        pass
from enum import Enum
from typing import Dict, Final, List, Optional

import inquirer
import inquirer.render.console._password
import inquirer.render.console._path
import inquirer.render.console._text
from colorama import init
from inquirer.render import ConsoleRender
from inquirer.themes import Theme, load_theme_from_dict

from ark_sdk_python.common.ark_system_config import ArkSystemConfig
from ark_sdk_python.models import ArkException

init()

ARK_INQUIRER_THEME: Final[Theme] = load_theme_from_dict(
    {
        'Question': {'mark_color': 'bold_green', 'brackets_color': 'bold_white', 'default_color': 'bold_white'},
        'Editor': {'opening_prompt_color': 'bright_black'},
        'Checkbox': {
            'selection_color': 'bold_black_on_bright_green',
            'selection_icon': '❯',
            'selected_icon': '◉',
            'selected_color': 'bold_green',
            'unselected_color': 'normal',
            'unselected_icon': '◯',
        },
        'List': {'selection_color': 'bold_black_on_bright_green', 'selection_cursor': '❯', 'unselected_color': 'normal'},
    }
)


class ArkInquirerRender(ConsoleRender):
    # pylint: disable=keyword-arg-before-vararg,protected-access
    def __init__(self, event_generator=None, *args, **kwargs):
        super().__init__(event_generator=event_generator, theme=ARK_INQUIRER_THEME, *args, **kwargs)

    def render(self, question, answers=None):
        question.answers = answers or {}

        if question.ignore:
            return question.default

        clazz = self.render_factory(question.kind)
        render = clazz(question, terminal=self.terminal, theme=self._theme, show_default=question.show_default)
        if isinstance(
            render, (inquirer.render.console._text.Text, inquirer.render.console._password.Password, inquirer.render.console._path.Path)
        ):
            render.current = ''
        self.clear_eos()

        try:
            a = self._event_loop(render)
            if not a and question.default:
                a = question.default
            elif not a and question.name in answers:
                a = answers[question.name]
            return a
        finally:
            print('')

    def _print_header(self, render):
        base = render.get_header()

        header = base[: self.width - 9] + '...' if len(base) > self.width - 6 else base
        default_value = '{normal} ({default})'.format(default=render.question.default, normal=self.terminal.normal)
        show_default = render.question.default and render.show_default
        header += default_value if show_default else ''
        msg_template = '{t.move_up}{t.clear_eol}{tq.brackets_color}{tq.mark_color}?{tq.brackets_color} {msg}{t.normal}'

        escaped_current_value = str(render.get_current_value()).replace('{', '{{').replace('}', '}}')
        self.print_str(
            f'\n{msg_template} {escaped_current_value}',
            msg=header,
            lf=not render.title_inline,
            tq=self._theme.Question,
        )


class ArkArgsFormatter:
    @staticmethod
    def color(text: str, fore: str = '', style: str = '', back: str = '') -> str:
        from colorama import Style

        if not ArkSystemConfig.is_coloring():
            return text
        return f'{fore}{style}{back}{text}{Style.RESET_ALL}'

    @staticmethod
    def print_colored(text: str, fore: str = '', style: str = '', back: str = '') -> None:
        if ArkSystemConfig.is_interactive() or ArkSystemConfig.is_allowing_output():
            sys.stdout.write(ArkArgsFormatter.color(text, fore, style, back) + '\n')
            sys.stdout.flush()

    @staticmethod
    def print_success(text) -> None:
        from colorama import Fore

        return ArkArgsFormatter.print_colored(text, fore=Fore.GREEN)

    @staticmethod
    def print_success_bright(text) -> None:
        from colorama import Fore, Style

        return ArkArgsFormatter.print_colored(text, fore=Fore.GREEN, style=Style.BRIGHT)

    @staticmethod
    def print_failure(text) -> None:
        from colorama import Fore

        return ArkArgsFormatter.print_colored(text, fore=Fore.RED)

    @staticmethod
    def print_warning(text) -> None:
        from colorama import Fore

        return ArkArgsFormatter.print_colored(text, fore=Fore.YELLOW)

    @staticmethod
    def print_normal(text) -> None:
        return ArkArgsFormatter.print_colored(text)

    @staticmethod
    def print_normal_bright(text) -> None:
        from colorama import Style

        return ArkArgsFormatter.print_colored(text, style=Style.BRIGHT)

    @staticmethod
    def get_arg(
        args: argparse.Namespace,
        key: str,
        prompt: str,
        existing_val: Optional[str] = None,
        hidden: bool = False,
        prioritize_existing_val: bool = False,
        empty_value_allowed: bool = False,
    ) -> Optional[str]:
        from colorama import Fore, Style

        val: str = ''
        if hasattr(args, key):
            while val == '':
                val = getattr(args, key)
                if val == None and existing_val != None and existing_val != '':
                    val = existing_val
                if prioritize_existing_val and existing_val != None:
                    val = existing_val
                prompts = []
                if val != None:
                    if isinstance(val, Enum):
                        val = val.value
                    if hidden:
                        prompts.append(inquirer.Password('answer', message=prompt))
                    else:
                        prompts.append(inquirer.Text('answer', message=prompt, default=val, show_default=True))
                    answers = inquirer.prompt(prompts, render=ArkInquirerRender())
                    if not answers:
                        raise ArkException('Failed to get answer')
                    new_val = answers['answer']
                    if new_val != None and new_val != '':
                        val = new_val
                else:
                    if hidden:
                        prompts.append(inquirer.Password('answer', message=prompt, show_default=True))
                    elif empty_value_allowed:
                        prompts.append(inquirer.Text('answer', message=f'{prompt} <Optional>', validate=True))
                    else:
                        prompts.append(inquirer.Text('answer', message=prompt))
                    answers = inquirer.prompt(prompts, render=ArkInquirerRender())
                    if not answers:
                        raise ArkException('Failed to get answer')
                    val = answers['answer']
                if val == '' and not empty_value_allowed:
                    sys.stdout.write(ArkArgsFormatter.color('Value cannot be empty', fore=Fore.RED, style=Style.BRIGHT) + '\n')
                sys.stdout.flush()
                if empty_value_allowed and val == '':
                    val = None
                    break
        return val

    @staticmethod
    def get_bool_arg(
        args: argparse.Namespace, key: str, prompt: str, existing_val: bool = None, prioritize_existing_val: bool = False
    ) -> Optional[bool]:
        val = getattr(args, key)
        if prioritize_existing_val and existing_val != None:
            val = existing_val
        answers = inquirer.prompt([inquirer.Confirm('answer', message=prompt, default=val)], render=ArkInquirerRender())
        if not answers:
            raise ArkException('Failed to get bool answer')
        return answers['answer']

    @staticmethod
    def get_switch_arg(
        args: argparse.Namespace,
        key: str,
        prompt: str,
        possible_vals: List[str],
        existing_val: str = None,
        prioritize_existing_val: bool = False,
    ) -> Optional[str]:
        val = getattr(args, key)
        if prioritize_existing_val and existing_val != None:
            val = existing_val
        answers = inquirer.prompt(
            [inquirer.List('switch', prompt, choices=possible_vals, default=val, carousel=True)], render=ArkInquirerRender()
        )
        if not answers:
            raise ArkException('Failed to get switch answer')
        return answers['switch']

    @staticmethod
    def get_checkbox_args(
        args: argparse.Namespace,
        keys: List[str],
        prompt: str,
        possible_vals: List[str],
        existing_vals: Dict[str, str] = None,
        prioritize_existing_val: bool = False,
    ) -> Optional[List[str]]:
        vals = []
        for key in keys:
            val = getattr(args, key)
            if prioritize_existing_val and key in existing_vals:
                val = existing_vals[key]
            if val:
                vals.append(val)
        answers = inquirer.prompt(
            [inquirer.Checkbox('boxes', prompt, choices=possible_vals, default=vals, carousel=True)], render=ArkInquirerRender()
        )
        if not answers:
            raise ArkException('Failed to get checkbox answer')
        return answers['boxes']
