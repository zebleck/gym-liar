import logging
logger = logging.getLogger(__name__)

def pop_slice(lis, n):
    tem = lis[:int(n)]
    del lis[:int(n)]
    return tem
