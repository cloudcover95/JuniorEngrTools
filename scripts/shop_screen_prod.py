#!/usr/bin/env python3
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from calculators.shop_case import screen
print(json.dumps(screen(), indent=2))
