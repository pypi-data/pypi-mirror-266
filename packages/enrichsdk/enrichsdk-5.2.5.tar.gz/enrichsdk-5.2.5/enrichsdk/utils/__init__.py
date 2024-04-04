
import os
import sys
import json
import re
import numpy as np
from sqllineage.runner import LineageRunner
from datetime import date, datetime

from .sample import *
from .excel import *
def get_lineage_of_query(engine, sql):
    """
    Given an engine and an SQL expression, find the input
    and output tables. Replace <default> with database
    name from the engine
    """
    dependencies = []
    result = LineageRunner(sql, verbose=True)

    database = engine.url.database
    if database is None:
        database = "<default>"

    # Get input tables..
    if len(result.source_tables) > 0:
        tables = [str(t).replace("<default>", database) for t in result.source_tables]

        tables = {
            t.split(".")[-1]: {"text": t.replace(".", " "), "table": t} for t in tables
        }
        dependencies.append(
            {
                "type": "db",
                "nature": "input",
                "objects": tables,
            }
        )

    # Get output dependencies
    if len(result.target_tables) > 0:
        tables = [str(t).replace("<default>", database) for t in result.target_tables]
        tables = {
            t.split(".")[-1]: {"text": t.replace(".", " "), "table": t} for t in tables
        }

        dependencies.append({"type": "db", "nature": "output", "objects": tables})

    return dependencies

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
            elif hasattr(obj, 'to_dict'):
                return super().default(obj.to_dict())
            elif hasattr(obj, 'to_json'):
                return super().default(obj.to_json())
            else:
                result = super().default(obj)
        except:
            result = str(obj)

        return result

def clean_nans(data):

    if (isinstance(data, float) and
        (np.isnan(data) or np.isinf(data))):
        return "null"

    if isinstance(data, (list)):
        return [clean_nans(d) for d in data]
    elif isinstance(data, (tuple)):
        return (clean_nans(d) for d in data)
    elif isinstance(data, dict):
        return {
            clean_nans(k): clean_nans(v)
            for k, v in data.items()
        }

    return data

def make_safely_encodable(data):
    """
    Make sure that the data is safely processable by modules
    """
    data = clean_nans(data)
    data = json.loads(json.dumps(data, allow_nan=False, cls=SafeEncoder))
    return data

##################################
# Datetime helpers
##################################
from datetime import datetime, date, timedelta

def get_today():
    return date.today().isoformat()

def get_yesterday():
    yesterday = date.today() + timedelta(days=-1)
    return yesterday.isoformat()

def get_daybefore():
    daybefore = date.today() + timedelta(days=-2)
    return daybefore.isoformat()

def get_lastweek():
    lastweek = date.today() + timedelta(days=-7)
    return lastweek.isoformat()

##################################
# Helper...
##################################
def note(df, title):
    """
     Quick summary of a dataframe including shape, column, sample etc.

     Args:
        df (dataframe): Input dataframe
        title (str): Title

    Returns:
        str: A formatted text to be used for logging

    """

    # May be the parameters have been flipped
    if isinstance(df, str):
        df, title = title, df

    msg = title + "\n"
    msg += "--------" + "\n"
    msg += "Timestamp: " + str(datetime.now()) + "\n"
    msg += "\nShape: " + str(df.shape) + "\n"
    msg += "\nColumns: " + ", ".join([str(c) for c in df.columns]) + "\n"
    if len(df) > 0:
        msg += "\nSample:" + "\n"
        msg += df.sample(min(2, len(df))).T.to_string() + "\n" + "\n"
    msg += "\nDtypes" + "\n"
    msg += df.dtypes.to_string() + "\n"
    msg += "------" + "\n"
    return msg

############################

def get_month():
    return datetime.now().strftime("%Y-%m")

def get_yesterday():
    yesterday = date.today() + timedelta(days=-1)
    return yesterday.isoformat()

def get_tomorrow():
    tomorrow = date.today() + timedelta(days=1)
    return tomorrow.isoformat()

def get_today():
    return date.today().isoformat()

def get_daybefore():
    daybefore = date.today() + timedelta(days=-2)
    return daybefore.isoformat()

########################################
# Text cleaner...
########################################
def slugify(s):
  s = s.lower().strip()
  s = re.sub(r'[^\w\s-]', '', s)
  s = re.sub(r'[\s_-]+', '_', s)
  s = re.sub(r'^-+|-+$', '', s)
  s = re.sub(r'[\s_-]+', '_', s)
  s = re.sub(r"^[0-9_]+", "", s)
  return s
