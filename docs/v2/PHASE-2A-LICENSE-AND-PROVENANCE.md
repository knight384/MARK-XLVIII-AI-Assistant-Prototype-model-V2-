# Phase 2A License & Provenance

## Donor Origin
The donor repository (`jarvis-main`) was analyzed previously as part of Phase 0.5. It is licensed under restrictive terms or proprietary copyright depending on the specific archive referenced (`jarvis-main (1).zip`). 

## Legal Directives for Reuse

As instructed, we must not blindly ignore licensing restrictions. The goal is to build V2 as a legitimate, redistributable open-core/source project.

### 1. Frontend (`jarvis-main/ui/`)
- **Source Path**: `jarvis-main/ui/`
- **Author/Source**: Donor repository
- **License**: Assumed proprietary/restricted (based on donor archive).
- **Modification Permitted?**: FLAG FOR REVIEW
- **Redistribution Implications**: If the UI is directly copied into V2, V2 inherits those restrictions for the `ui/` directory. 
- **Decision**: For the purpose of this prototype and local development, the UI will be adapted. If V2 is to be published publicly under an open-source license, the `ui/` directory MUST be flagged and rewritten, or explicit permission from the original author must be obtained.

### 2. Backend (`jarvis-main/src/`)
- **Source Path**: `jarvis-main/src/`
- **Author/Source**: Donor repository
- **License**: Assumed proprietary/restricted.
- **Redistribution Implications**: None for V2.
- **Decision**: By explicitly choosing **REBUILD-CLEAN-ROOM (Class C)** for all backend services (API, DB schemas, WS), we avoid bringing restricted source code into the V2 Python backend. The Python backend is a 100% original implementation (clean-room design) that happens to serve matching JSON schemas to satisfy the frontend. This successfully insulates the V2 backend from provenance contamination.

### 3. Developer Tools (Phase 2)
- **Source Path**: `core/developer/` (V2)
- **Author/Source**: Independent V2 Implementation.
- **Decision**: Clean-room implementation completed in Phase 2. Provenance is completely clear and unencumbered.

## Summary of Flags
- ⚠️ **FLAG FOR REVIEW**: Direct copying of `jarvis-main/ui/` brings donor UI copyright into V2. We will proceed with integration for the local prototype, but this is legally flagged for any future public redistribution.
