import re
import json
from datetime import date, datetime
import numpy as np

class SafeEncoder(json.JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, (datetime, date)):
                result = obj.isoformat()
            elif isinstance(obj, (tuple)):
                result = super().default(list(obj))
            elif isinstance(obj, np.integer):
                return super().default(int(obj))
            elif isinstance(obj, float) and np.isnan(obj):
                return "null"
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                result = super().default(obj)
        except:
            result = str(obj)

        return result

def slugify(s):
  s = s.lower().strip()
  s = re.sub(r'[^\w\s-]', '', s)
  s = re.sub(r'[\s_-]+', '_', s)
  s = re.sub(r'^-+|-+$', '', s)
  return s
