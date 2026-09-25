#!/usr/bin/env python3
"""Claude Code PreToolUse hook: block any tool call that would delete resources/db/student.db.

Exit 0 -> allow the tool call.
Exit 2 -> block the tool call; stderr is shown in the console and sent back to Claude.
"""

import glob
import json
import os
import re
import shlex
import sys

REPO_ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PROTECTED = os.path.join(REPO_ROOT, "resources", "db", "student.db")
PROTECTED_NAMES = {"resources", "db", "student.db"}

DESTRUCTIVE_VERBS = {"rm", "rmdir", "unlink", "shred", "trash", "mv", "truncate", "srm"}
SHELL_OPERATORS = {";", "&&", "||", "|", "&", "(", ")", "\n"}
DESTRUCTIVE_PATTERN = re.compile(
    r"(^|[\s;&|(`])(sudo\s+)?(rm|rmdir|unlink|shred|trash|mv|truncate|srm)\b"
    r"|\bgit\s+(clean|rm)\b"
    r"|\s-delete\b"
    r"|os\.remove|os\.unlink|shutil\.rmtree|\.unlink\(|\bunlinkSync\b|\brmSync\b"
)
REDIRECT_PATTERN = re.compile(r">\s*[^\s;&|]*student\.db\b")


def block(detail):
    print(
        "\n❌ BLOCKED by protect_student_db hook: resources/db/student.db is protected "
        "and cannot be deleted.\n"
        f"   Attempted: {detail}\n"
        "   Leave student.db in place and continue with the rest of the task.",
        file=sys.stderr,
    )
    sys.exit(2)


def resolve(base, path):
    return os.path.realpath(os.path.join(base, os.path.expanduser(path)))


def endangers(path):
    """True if deleting/moving `path` would remove student.db (it IS the file or an ancestor of it)."""
    return path == PROTECTED or PROTECTED.startswith(path.rstrip(os.sep) + os.sep)


def arg_hits_protected(arg, bases):
    stripped = arg.rstrip("/*").rstrip("/") or arg
    if os.path.basename(stripped) in PROTECTED_NAMES:
        return True
    for base in bases:
        pattern = os.path.join(base, os.path.expanduser(arg))
        candidates = glob.glob(pattern) or [pattern]
        if any(endangers(os.path.realpath(c)) for c in candidates):
            return True
    return False


def split_segments(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    lexer.commenters = ""
    segments, current = [], []
    for token in lexer:
        if token in SHELL_OPERATORS or set(token) <= set(";&|()"):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def is_destructive_segment(tokens):
    names = [os.path.basename(t) for t in tokens]
    if any(n in DESTRUCTIVE_VERBS for n in names):
        return True
    if "-delete" in tokens:
        return True
    return "git" in names and any(t in ("clean", "rm") for t in tokens)


def check_bash(command, cwd):
    if REDIRECT_PATTERN.search(command):
        block(command)
    if "student.db" in command and DESTRUCTIVE_PATTERN.search(command):
        block(command)

    try:
        segments = split_segments(command)
    except ValueError:
        # Unparseable command: fail closed if it looks destructive and touches resources/.
        if DESTRUCTIVE_PATTERN.search(command) and "resources" in command:
            block(command)
        return

    bases = [cwd]
    for i, tokens in enumerate(segments):
        if tokens[0] == "cd" and len(tokens) > 1:
            bases.append(resolve(bases[-1], tokens[1]))
            continue
        if not is_destructive_segment(tokens):
            continue
        args = tokens[1:]
        if "xargs" in tokens and i > 0:
            # `ls resources | xargs rm -rf`: the paths come from the previous segment.
            args += segments[i - 1][1:]
        for arg in args:
            if arg.startswith("-"):
                continue
            if arg_hits_protected(arg, bases):
                block(command)


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except ValueError:
        if "student.db" in raw:
            block("unparseable tool input mentioning student.db")
        sys.exit(0)

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()

    if tool == "Bash":
        check_bash(tool_input.get("command", ""), cwd)
    elif tool in ("Write", "Edit", "MultiEdit"):
        file_path = tool_input.get("file_path", "")
        if file_path and resolve(cwd, file_path) == PROTECTED:
            block(f"{tool} {file_path}")

    sys.exit(0)


if __name__ == "__main__":
    main()
