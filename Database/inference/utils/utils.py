"""
manh.truongle - truonnglm.spk@gmail.com
utils
"""
import os
import sys
import uuid
import psutil
import logging
import subprocess

logger = logging.getLogger("inf.util.util")


def get_mem_and_cpu():
    process = psutil.Process(os.getpid())
    mem_total = round(int(psutil.virtual_memory().total) * 1e-6)  # Mb
    mem_usage = round(int(process.memory_full_info().rss) * 1e-6)
    mem_percent = round((mem_usage / mem_total) * 100, 2)
    cpu_total = int(psutil.cpu_count())
    cpu_usage = int(process.cpu_num())
    #     cpu_avg_percent = round(process.cpu_percent(), 2)
    return [mem_usage, mem_total, mem_percent], [cpu_usage, cpu_total]


def get_gpu_memory(idx=0):
    usage = subprocess.check_output(
        [
            'nvidia-smi', '--query-gpu=memory.used',
            '--format=csv,nounits,noheader', f'--id={idx}',
        ])
    usage = int(usage)
    total = subprocess.check_output(
        [
            'nvidia-smi', '--query-gpu=memory.total',
            '--format=csv,nounits,noheader', f'--id={idx}',
        ])
    total = int(total)
    return usage, total, round((usage / total) * 100, 2)


def get_err_info():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    text = "{}  at file {} in line {}".format(exc_obj, fname, exc_tb.tb_lineno)
    # print("err:", exc_type, exc_obj, fname, exc_tb.tb_lineno)
    return text


def str2bool(v):
    """
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise logger.error("boolean value expected")


def get_uuid():
    return uuid.uuid4().hex
