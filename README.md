# JuniorEngrTools

**Professional Engineering Toolkit Suite**

JuniorEngrTools is a complete, sovereign, local-first engineering toolkit designed for working professionals. It provides production-grade calculators, databases, monitoring, accounting, and intelligent workflows — all built on original BitNet codebase principles for efficient inference where it adds value.

The suite runs on Windows, Mac, and Linux with graceful fallbacks and includes a ready-to-use Streamlit dashboard so you can start working immediately without building the full ecosystem.

## Features

**Core Calculators**
- Motion & Force (A3-style linear actuators, critical speed, belt/gear systems, inertia, acceleration curves)
- Structural & FEA (beam analysis, stress/strain, moment of inertia, basic 3D FEA)
- Bolt Analysis (preload, fatigue, optimization)
- Steam Tables (properties + smart interpolation)
- Advanced Fits, Tolerances & Standards (clearance, tap, keyway, pipe systems)
- Composite Laminate, Unit Conversion, and Formulas

**Databases & References**
- Materials Database (300+ entries with shape/form-dependent properties from ASTM/ASM/ISO specifications)
- Fastener Database + full Bolt Analysis
- Categorized Industry Standards (LR, DNV, BV, ISO, ANSI, API 650, ASME, MIL-SPEC, ISO 9001, GMP, aerospace, piping, and more)

**Documentation & Inventory**
- Bill of Materials (versioned structured + flattened)
- Complete Documentation Suite (redlines, build plans, permits, renders, maintenance logs)
- Parts Inventory with predictive restocking

**Intelligent Layer**
- SovereignBlackboxBrain — the ecosystem’s main second brain for blackbox inference (LLM-style reasoning, quant decisions, AGI orchestration)
- BitNet-powered semantic search, optimization, and anomaly detection
- SovereignLowPowerMonitor for edge-native hardware/instrumentation monitoring and trend analysis
- Long-horizon planning integration for complex projects and maintenance

**Interface & Connectivity**
- Clean Streamlit dashboard for instant use (like JuniorHome)
- Full Obsidian vault port for knowledge management and cross-ecosystem connectivity (JuniorHome, JuniorQuant, JuniorClimbs, etc.)
- Production reports and ledger tracking

## Architecture

- **BitNet-centric**: Original ternary 1.58-bit implementations for efficient inference and optimization
- **Cross-platform**: Windows, Mac, Linux with numpy fallbacks
- **Data layer**: High-density Parquet with schema evolution
- **Sovereign & local-first**: Core runs entirely locally; optional scaling across dispersed infrastructure layers
- **Zero-trust**: Strict 02_Assets isolation
- **Production-grade**: Error handling, logging, performance measurement, and self-adaptation

## Getting Started

### Instant Use (Recommended)
```bash
streamlit run interface/streamlit_dashboard.py
```

The dashboard exposes every calculator, database, report, and the SovereignBlackboxBrain.

### Code Usage
```python
from calculators.bolt_analysis import BoltAnalysisCalculator
calc = BoltAnalysisCalculator()
result = calc.full_analysis(diameter=12, load=5000, material_props=[2700, 276, 310])
print(result)
```

## Integration with the Ecosystem

JuniorEngrTools is designed to work standalone or as part of the broader JuniorCloudllc ecosystem:

- **SovereignBlackboxBrain** — central inference engine (second brain)
- **SovereignLongHorizonAGI** — long-horizon planning and orchestration
- **ConservativeDiversifiedLongTermAllocator** — smart procurement aligned with diversified strategy
- **SovereignLowPowerMonitor** — hardware and suite-wide anomaly detection + trends
- Cross-repo data flow via Parquet (JuniorHome power/telecom, JuniorClimbs spatial, JuniorQuant financial context)

## Philosophy

Engineering is the art of applying published standards, codes, and proven methods. This toolkit helps professionals quickly locate and apply the correct “piece of the puzzle” — whether that’s a material property table, a standard calculation method, or an intelligent recommendation from the second brain.

MIT License. Local where it matters. Built for professionals.

---

Part of the JuniorCloudllc ecosystem. Professional. Sovereign. Intelligent.