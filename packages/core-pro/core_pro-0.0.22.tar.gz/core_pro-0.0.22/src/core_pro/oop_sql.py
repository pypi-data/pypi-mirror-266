import os
from time import sleep
import pandas as pd
import polars as pl
import trino
from tqdm import tqdm
from colorama import Fore
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from .ultilities import make_dir


class DataPipeLine:
    def __init__(
            self,
            query_or_dir: str,
            save_path: str | Path = None,
    ):
        self.query = query_or_dir
        self.status = f'{Fore.LIGHTBLUE_EX}🤖 JDBC:{Fore.RESET}'
        self.save_path = save_path
        if self.save_path:
            make_dir(self.save_path.parent)

    def run_presto_to_df(self, polars: bool = True):
        # connection
        username, password = os.environ['PRESTO_USER'], os.environ['PRESTO_PASSWORD']
        conn = trino.dbapi.connect(
            host='presto-secure.data-infra.shopee.io',
            port=443,
            user=username,
            catalog='hive',
            http_scheme='https',
            source=f'(50)-(vnbi-dev)-({username})-(jdbc)-({username})-(SG)',
            auth=trino.auth.BasicAuthentication(username, password)
        )
        cur = conn.cursor()

        # logging
        thread = ThreadPoolExecutor(1)
        async_result = thread.submit(cur.execute, self.query)

        bar_queue = tqdm()
        while not async_result.done():
            memory = cur.stats.get('peakMemoryBytes', 0) * 10 ** -9
            perc = 0
            stt = cur.stats.get('state', '')
            if stt == "RUNNING":
                perc = round((cur.stats.get('completedSplits', 0) * 100.0) / (cur.stats.get('totalSplits', 0)), 2)
            status = (f"🤖 JDBC Status: {stt} {perc}%, Memory {memory:,.0f}GB")
            bar_queue.set_description(status)
            bar_queue.update(1)
            sleep(5)
        bar_queue.close()
        records = cur.fetchall()

        # result
        if polars:
            df = pl.DataFrame(records, schema=[i[0] for i in cur.description])
            if self.save_path:
                df.write_parquet(self.save_path)
        else:
            df = pd.DataFrame(records, columns=[i[0] for i in cur.description])
            if self.save_path:
                df.to_parquet(self.save_path, index=False, compression='zstd')

        print(f"{self.status} Data Shape: {df.shape}")
        return df
