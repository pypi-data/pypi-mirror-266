# Copyright (C) 2023 qBraid
#
# This file is part of the qBraid-SDK
#
# The qBraid-SDK is free software released under the GNU General Public License v3
# or later. You can redistribute and/or modify it under the terms of the GPL v3.
# See the LICENSE file in the project root or <https://www.gnu.org/licenses/gpl-3.0.html>.
#
# THERE IS NO WARRANTY for the qBraid-SDK, as per Section 15 of the GPL v3.

"""
Module defining Pennylane OpenQASM conversions

"""
from pennylane.tape import QuantumTape


def pennylane_to_qasm2(tape: QuantumTape) -> str:
    """Converts a PennyLane tape to OpenQASM 2.0

    Args:
        tape (QuantumTape): input PennyLane tape

    Returns:
        str: OpenQASM 2.0 representation of the tape

    """
    return tape.to_openqasm()
