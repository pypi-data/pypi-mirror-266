"""Utilities to compile possibly incomplete Python source code."""

from __future__ import annotations

def compile_command(source: str, filename: str = "<input>", symbol: str = "single"):
    """Compile a command and determine whether it is incomplete

    The 'completeness' determination is slightly different than in standard Python
    (it's whatever the internal function ``mp_repl_continue_with_input`` does).
    In particular, it's important that the code not end with a newline character
    or it is likely to be treated as a complete command."""
