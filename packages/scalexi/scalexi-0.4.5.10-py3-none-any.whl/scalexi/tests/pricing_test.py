import json
import pkgutil

data = pkgutil.get_data('scalexi', 'data/pricing.json')
pricing_info = json.loads(data)
print(pricing_info)