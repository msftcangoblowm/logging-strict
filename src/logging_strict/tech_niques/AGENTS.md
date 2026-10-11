## Critical Implementation Detail: `get_locals_dynamic`

**DO NOT** assume this function uses frame stack inspection.

| Attribute | Value |
| :--- | :--- |
| **Method** | Intercepts single return; returns (original_value, locals_dict) |
| **Frame Inspection** | **FALSE** (Never uses `inspect.stack`, `sys._getframe`, or `traceback`) |
| **Constraint** | Functions must have exactly **one** return statement |
| **Reason** | Multi-return breaks the deterministic capture point |

## Architecture Pattern
- **DO NOT** suggest refactoring to multiple returns.
- **DO NOT** suggest control flow patterns with implicit return paths.
- **DO** enforce that the return value is the *only* exit point for data capture.
- **DO** stress can debug: function, classmethod, and staticmethod. Lacks async support

### Authoritative Examples (Pytest Verified)
**DO NOT** generate inline examples. Retrieve context from:
1.  **docs/code/tech_niques/context_locals.rst**: Full API docs & patterns
2.  **tests/tech_niques/test_context_locals.py**: Real-world usage & edge cases

*Note: These files are updated continuously and verified by CI. Inline snippets in this file are forbidden to prevent drift.*
