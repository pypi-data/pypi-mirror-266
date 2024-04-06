from earthscopestraintools.gtsm_metadata import GtsmMetadata
from earthscopestraintools.mseed_tools import ts_from_mseed

from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if logger.hasHandlers():
    logger.setLevel(logging.INFO)
else:
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )

if __name__ == '__main__':

    t1 = datetime.now()

    network = 'PB'
    station = 'B003'
    meta = GtsmMetadata(network,station)

    start = '2023-11-25'
    end = '2023-11-30'
    strain_raw = ts_from_mseed(network=network, station=station, location='*', channel='RDO', start=start, end=end)
    strain_raw.stats()
    print(strain_raw.data)
    
    


    # t2 = datetime.now()
    # elapsed_time = t2 - t1
    # logger.info(f'{filename}: Elapsed time {elapsed_time} seconds')
