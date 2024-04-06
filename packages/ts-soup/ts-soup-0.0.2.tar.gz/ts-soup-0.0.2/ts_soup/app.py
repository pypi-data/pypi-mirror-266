import argparse
import datetime
import importlib
import os
import sys
import types

from dateutil.relativedelta import relativedelta

parser = argparse.ArgumentParser()
parser.add_argument('--table',default=[],nargs='+')
parser.add_argument('--time',default=[],nargs='+')
args = parser.parse_args()

from ts_soup.common import __init



def run_sync(db_infos:dict, sync_start_from=None, sync_delay:int=1):
    if sync_start_from is None:
        sync_start_from = {'months': 3}
    sync_end = datetime.datetime.now() + relativedelta(days=sync_delay)
    sync_start = (sync_end - relativedelta(**sync_start_from)).strftime('%Y-%m-%d')
    sync_end = sync_end.strftime('%Y-%m-%d')
    TO_UPDATE_TABLES = __init(args.table, args.time, sync_start, sync_end, db_infos)
    cwd = os.getcwd()
    sys.path.append(os.path.join(cwd,'funcs'))
    funcs = importlib.import_module('boundary_funcs')
    for table in TO_UPDATE_TABLES:
        # if 'raw_bid_distribution' not in table:
        #     continue
        exec(f"funcs.{table}()")
    #检测是否异常
    from ts_soup.common import EXECUTE_STATE
    if not EXECUTE_STATE:
        raise Exception("同步异常")



if __name__ == '__main__':
    pass
