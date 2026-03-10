from __future__ import annotations

ERROR_SEVERITY = {
    "Pass": 0,
    "WrongResult": 1,
    "RuntimeError": 2,
    "SchemaError": 3,
    "SyntaxError": 4,
    "Timeout": 5,
    "FormatError": 6,
}

FEEDBACK_DESCRIPTIONS = {
    "F0": "Minimal: PASS/FAIL only",
    "F1": "EngineError: include SQLite engine error text when present",
    "F2": "OutputDiff: include row counts and sample differences",
    "F3": "SelfDebug: ask for brief diagnosis before revised SQL",
}
