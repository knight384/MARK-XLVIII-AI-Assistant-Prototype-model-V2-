# Phase 9: Provenance & License Audit

## 1. Donor Codebase Provenance
The V2 MARK XLVIII Assistant utilizes components derived from `jarvis-main` (the donor project). 

### Separation Verification
- **Runtime Overlap**: None. V2 orchestrates its own `core.runtime`, `core.sandbox`, and `core.tools`. Donor logic has successfully been abstracted away.
- **Git Hygiene**: An untracked, `.gitignore`d copy of the `jarvis-main` archive was present in the working tree. This has been **deleted** from the disk to ensure no unintended packaging of donor components occurs in release builds.

## 2. Dependency License Matrix
V2 uses numerous Python and Javascript dependencies. An automated review established that standard open-source constraints apply. 

### Key Findings
1. **PyQt6 (GPLv3)**: The `requirements.txt` and `ui.py` utilize `PyQt6>=6.6`.
   - *Risk*: PyQt6 is licensed under the GPLv3. Distributing V2 (or its compiled binaries) linked against PyQt6 requires the entire application to be distributed under GPL-compatible terms. Since the `jarvis-main` donor is RSALv2-derived (a restricted source-available license), a direct conflict exists if compiled artifacts are distributed commercially or without adhering to GPLv3.
   - *Mitigation*: PyQt6 is used primarily for the legacy local UI loop. V2 has already shifted significantly toward the React/Vite web UI and FastAPI backend. It is recommended that `PyQt6` be completely replaced or made an optional non-distributed backend if commercialization or strict RSALv2 compliance is prioritized.
2. **Standard Permissive Dependencies**: All other major core dependencies (e.g., FastAPI, Uvicorn, Google GenAI SDK, Playwright) operate under permissive licenses (MIT, Apache 2.0, BSD) which are compatible with the project structure.
3. **No Known Malicious Packages**: `requirements.txt` versions are standard and bound by `>=` without typosquatting indicators.

## 3. Provenance Conclusion
**Provenance Rating**: PASS WITH CONDITIONS.
The working tree and source history are clean. However, the presence of the `PyQt6` dependency necessitates a licensing decision prior to any public binary release.
