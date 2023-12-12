import os
import sys
from pyfiglet import figlet_format
from termcolor import cprint
import time
from colorama import init

init(strip=not sys.stdout.isatty())
from prompt_toolkit import prompt
from PyInquirer.prompt import prompt
from utils.menu_options import MANAGE_STRATEGIES_MENU, MenuOption
from termcolor import colored
import shutil

STARTING_POINT = "Main Menu"
NOT_SUPPORTED = "Not Supported"


class CryptoBountyBotCLI:
    def __init__(self) -> None:
        self.menu_stack = []
        self.menu_dict = MenuOption.get_inst_dict()

    def check_dir(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists("data/logs", exist_ok=True):
            os.makedirs("data/logs", exist_ok=True)
        if not os.path.exists("data/keys", exist_ok=True):
            pass

    def start(self):
        self.show_logo()
        self.push_by_name(STARTING_POINT)

    def handle_answ(self, answ: dict):
        if not answ:
            return self.handle_exit()

        selected_option = answ[self.menu_stack[-1]]
        if selected_option == "Exit":
            return self.handle_exit()
        elif selected_option == "Back":
            return self.handle_back()
        else:
            self.handle_selected_option(selected_option)

    def handle_selected_option(self, selected_option: str):
        menu_item = self.find_menu_item_by_name(selected_option)
        menu_item.call_funcs()
        self.push(menu_item)

    def handle_back(self):
        self.pop()

    def handle_exit(self):
        exit(0)

    def cll_funcs(self, funcs: list):
        for func in funcs:
            func()

    def cll_funcs_async(self, async_funcs: list):
        for func in async_funcs:
            func()

    def find_menu_item_by_name(self, menu_name: str) -> MenuOption | None:
        if menu_name not in self.menu_dict:
            not_supp = self.find_menu_item_by_name(NOT_SUPPORTED)
            not_supp.msg = f"{menu_name} is not supported yet"
            return not_supp

        return self.menu_dict[menu_name]

    def replace(self, menu_item: MenuOption):
        self.pop()
        self.push(menu_item)

    def pop(self):
        if len(self.menu_stack) > 0:
            self.menu_stack.pop()
            curr_menu = self.find_menu_item_by_name(self.menu_stack[-1])
            self.show(curr_menu)
        else:
            print("cannot go back any further")

    def push_by_name(self, menu_name: str):
        menu_item = self.find_menu_item_by_name(menu_name)
        if menu_item:
            self.push(menu_item)
        else:
            menu_item = self.find_menu_item_by_name(self.menu_stack[-1])
            self.show(menu_item)

    def push(self, menu_item: MenuOption):
        self.menu_stack.append(menu_item.name)
        self.show(menu_item)

    def show(self, menu_item: MenuOption):
        answ = prompt(menu_item.to_question(), style=menu_item.style)
        self.clr_lst_line()
        self.handle_answ(answ)

    def clr_lst_line(self):
        print(
            "\033[A                                                                    \033[A"
        )

    def show_logo(self):
        os.system("cls" if os.name == "nt" else "clear")
        terminal_width, _ = shutil.get_terminal_size()
        welcome_txt = figlet_format(
            "Welcome to",
            font="small",
            justify="center",
            width=terminal_width,
        )
        name_txt = figlet_format(
            "CryptoBountyBot",
            font="big",
            justify="center",
            width=terminal_width,
        )
        vers_txt = figlet_format(
            "Version 0.1.0",
            font="small",
            justify="center",
            width=terminal_width,
        )
        cprint(welcome_txt, "white")
        cprint(name_txt, "green")
        cprint(vers_txt, "white")
        print(colored("Created by: @pstemporowski", "green"))
