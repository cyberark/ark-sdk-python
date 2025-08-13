#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import argparse
from typing import List

import argcomplete
import urllib3

from ark_sdk_python.actions import ArkAction, ArkCacheAction, ArkConfigureAction, ArkLoginAction, ArkProfilesAction, ArkServiceExecAction
from ark_sdk_python.common.ark_version import __version__

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=__version__)
    subparsers = parser.add_subparsers(dest="action")
    subparsers.required = True

    actions: List[ArkAction] = [
        ArkConfigureAction(),
        ArkLoginAction(),
        ArkServiceExecAction(),
        ArkProfilesAction(),
        ArkCacheAction(),
    ]

    for action in actions:
        action.define_action(subparsers)
    argcomplete.autocomplete(parser)
    args: argparse.Namespace = parser.parse_args()
    for action in actions:
        if action.can_run_action(args.action, args):
            action.run_action(args)


if __name__ == "__main__":
    main()
