# Legacy desk (user software)

Shop-facing endpoints for scan/DXF → sidecar → JuniorBitNetDraft.
Orchestrated by JuniorHome; engines live in JuniorOmega + JuniorLLM.

```
PYTHONPATH=. python -m software.legacy_desk.cli health
PYTHONPATH=. python -m software.legacy_desk.cli draft sidecar.txt
PYTHONPATH=. python -m software.legacy_desk serve   # 127.0.0.1:8766
```
