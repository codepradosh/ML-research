import io
import pandas as pd
import io as bytes_io
import sys
import os
import time
import json
import codecs
import logging
import snappy
import multiprocessing
from time import sleep
from time import time
from datetime import timedelta
from typing import Any, Union, set
from multiprocessing.pool import Pool
import rocksdb

import avro.schema as schema
import coloredlogs
from dynaconf import settings
from avro.io import DatumReader, DatumWriter, BinaryDecoder, BinaryEncoder
from icecream import ic
import system
system.path.append("/cs/anomaly/script/stlupdate")
from common_programs import rocksdbmanager as rdbmgr
from common_programs.anomalylogger import get_logger
from common_programs import stlserialisers

# Update DB_FOLDER_TS to the path containing "ts_cluster_table-1.db" database file
DB_FOLDER_TS = '/path/to/your/ts_cluster_table-1.db' 

num_partitions = settings["table_num_partitions"]
custom_offset_key = settings["custom_offset_key"]

stl_logger = get_logger('avro_conversion.log', to_console=True)

append_str = "."

Avro_ser_obj = stlserialiser.CustomFastAvroSerializer(stlserialisers.fast_schema)

Json_ser_obj = stlserialisers.CustomJsonSerializer()

if __name__ == '__main__':
    # Inspect specific key
    key = 'gblp2679651.cpu_wait'

    for partition in range(0, num_partitions, 1):
        db_objects = rdbmgr.DBOpenReadWriter(partition, DB_FOLDER_TS, stl_logger, read_only=True, create_if_missing=False)

        if not db_objects:
            continue
        else:
            stl_logger.info("Successfully opened DB for partition {}".format(partition))
            vt_val = db_objects.retrieve_dbitem(key.encode())
            ic(sys.getsizeof(vt_val))
            if not vt_val:
                continue
            df_tmp = Avro_ser_obj.fastavrodeserialize(vt_val).round(5)
            ic(df_tmp.tail(), df_tmp.shape, sys.getsizeof(df_tmp))
            df_tmp.to_csv("/tmp/df_dump.csv", sep=",", header=True)
