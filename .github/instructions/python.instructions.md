---
description: "Use when changing Python in the sales demo."
applyTo: "ws-part1-github-copilot/labs/starter/**/*.py"
---
- Keep functions small and single-purpose.
- Every behavior change needs a pytest test; keep existing tests passing.
- Errors for bad input go to stderr with a nonzero exit code, never a traceback.
