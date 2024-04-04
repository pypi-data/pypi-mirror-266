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
Module mapping supported QASM gates/operations to pyqir functions.

"""

import pyqir

from .exceptions import Qasm3ConversionError

OPERATOR_MAP = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
    "%": lambda x, y: x % y,
    "==": lambda x, y: x == y,
    "!=": lambda x, y: x != y,
    "<": lambda x, y: x < y,
    ">": lambda x, y: x > y,
    "<=": lambda x, y: x <= y,
    ">=": lambda x, y: x >= y,
    "&&": lambda x, y: x and y,
    "||": lambda x, y: x or y,
    "^": lambda x, y: x ^ y,
    "&": lambda x, y: x & y,
    "|": lambda x, y: x | y,
    "<<": lambda x, y: x << y,
    ">>": lambda x, y: x >> y,
}


def qasm3_expression_op_map(op_name: str, left, right):
    try:
        return OPERATOR_MAP[op_name](left, right)
    except KeyError as exc:
        raise Qasm3ConversionError(f"Unsupported / undeclared QASM operator: {op_name}") from exc


def id_gate(builder, qubits):
    pyqir._native.x(builder, qubits)
    pyqir._native.x(builder, qubits)


# Reference -
# https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.UGate
# https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.PhaseGate
def u3_gate(builder, theta, phi, lam, qubits):
    pyqir._native.rz(builder, lam, qubits)
    pyqir._native.rx(builder, CONSTANTS_MAP["pi"] / 2, qubits)
    pyqir._native.rz(builder, theta + CONSTANTS_MAP["pi"], qubits)
    pyqir._native.rx(builder, CONSTANTS_MAP["pi"] / 2, qubits)
    pyqir._native.rz(builder, phi + CONSTANTS_MAP["pi"], qubits)
    # global phase - e^(i*(phi+lambda)/2) is missing in the above implementation


# Reference -
# https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.U2Gate
def u2_gate(builder, phi, lam, qubits):
    u3_gate(builder, CONSTANTS_MAP["pi"] / 2, phi, lam, qubits)


PYQIR_ONE_QUBIT_OP_MAP = {
    # Identity Gate
    "id": id_gate,
    # Single-Qubit Clifford Gates
    "h": pyqir._native.h,
    "x": pyqir._native.x,
    "y": pyqir._native.y,
    "z": pyqir._native.z,
    # Single-Qubit Non-Clifford Gates
    "s": pyqir._native.s,
    "t": pyqir._native.t,
    "sdg": pyqir._native.s_adj,
    "tdg": pyqir._native.t_adj,
}

PYQIR_ONE_QUBIT_ROTATION_MAP = {
    "rx": pyqir._native.rx,
    "ry": pyqir._native.ry,
    "rz": pyqir._native.rz,
    "U": u3_gate,
    "u3": u3_gate,
    "U3": u3_gate,
    "U2": u2_gate,
    "u2": u2_gate,
}

PYQIR_TWO_QUBIT_OP_MAP = {
    "cx": pyqir._native.cx,
    "CX": pyqir._native.cx,
    "cz": pyqir._native.cz,
    "swap": pyqir._native.swap,
}

PYQIR_THREE_QUBIT_OP_MAP = {
    "ccx": pyqir._native.ccx,
}


def map_qasm_op_to_pyqir_callable(op_name: str):
    try:
        return PYQIR_ONE_QUBIT_OP_MAP[op_name], 1
    except KeyError:
        pass
    try:
        return PYQIR_ONE_QUBIT_ROTATION_MAP[op_name], 1
    except KeyError:
        pass
    try:
        return PYQIR_TWO_QUBIT_OP_MAP[op_name], 2
    except KeyError:
        pass
    try:
        return PYQIR_THREE_QUBIT_OP_MAP[op_name], 3
    except KeyError as exc:
        raise Qasm3ConversionError(f"Unsupported / undeclared QASM operation: {op_name}") from exc


CONSTANTS_MAP = {
    "pi": 3.141592653589793,
    "π": 3.141592653589793,
    "e": 2.718281828459045,
    "tau": 6.283185307179586,
}


def qasm3_constants_map(constant_name: str):
    return CONSTANTS_MAP[constant_name]
