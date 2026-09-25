#!/usr/bin/env python3
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from calculators.shop_case import blacktail_screen
print(json.dumps(blacktail_screen(), indent=2))
