"""
System diagnostics — logs everything about the process and machine
before and after model loading so you always know exactly what
resources the model occupies.
"""
import os
import platform
import sys

import psutil
import torch
from loguru import logger


def _gb(bytes_: int) -> float:
    return round(bytes_ / (1024 ** 3), 2)


def log_system_info() -> None:
    """Log static machine / OS info once at startup."""
    vm   = psutil.virtual_memory()
    cpu  = psutil.cpu_count(logical=True)
    pcpu = psutil.cpu_count(logical=False)

    logger.info("━━━━━━━━━━  SYSTEM INFO  ━━━━━━━━━━")
    logger.info("Platform        : {}", platform.platform())
    logger.info("Python          : {}", sys.version.split()[0])
    logger.info("Machine         : {}", platform.machine())
    logger.info("Processor       : {}", platform.processor() or "N/A")
    logger.info("Physical CPUs   : {}  |  Logical CPUs : {}", pcpu, cpu)
    logger.info("Total RAM       : {} GB", _gb(vm.total))
    logger.info("Available RAM   : {} GB", _gb(vm.available))
    logger.info("Used RAM        : {} GB  ({:.1f}%)", _gb(vm.used), vm.percent)

    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            logger.info(
                "CUDA GPU [{}]    : {}  |  VRAM: {} GB",
                i,
                props.name,
                _gb(props.total_memory),
            )
    else:
        logger.info("CUDA GPU        : not available — running on CPU")

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def log_process_info(label: str = "") -> dict:
    """
    Log current process resource usage.
    Returns a dict with the snapshot so callers can diff before/after.
    """
    proc = psutil.Process(os.getpid())
    mem  = proc.memory_info()
    vm   = psutil.virtual_memory()

    snapshot = {
        "pid":        proc.pid,
        "rss_gb":     _gb(mem.rss),
        "vms_gb":     _gb(mem.vms),
        "sys_free_gb": _gb(vm.available),
    }

    tag = f"[{label}] " if label else ""
    logger.info("{}PID              : {}", tag, snapshot["pid"])
    logger.info("{}Process RSS      : {} GB  (physical RAM held by this process)", tag, snapshot["rss_gb"])
    logger.info("{}Process VMS      : {} GB  (virtual address space)", tag, snapshot["vms_gb"])
    logger.info("{}System free RAM  : {} GB", tag, snapshot["sys_free_gb"])

    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            alloc = _gb(torch.cuda.memory_allocated(i))
            resv  = _gb(torch.cuda.memory_reserved(i))
            logger.info("{}GPU [{}] allocated: {} GB  |  reserved: {} GB", tag, i, alloc, resv)

    return snapshot


def log_model_memory_delta(before: dict, after: dict) -> None:
    """Log how much RAM the model loading consumed."""
    delta_rss = round(after["rss_gb"] - before["rss_gb"], 2)
    delta_free = round(before["sys_free_gb"] - after["sys_free_gb"], 2)
    logger.info("━━━━━━━━━━  MODEL MEMORY IMPACT  ━━━━━━━━━━")
    logger.info("RAM gained by process   : +{} GB  (RSS delta)", delta_rss)
    logger.info("System free RAM dropped : -{} GB", delta_free)
    logger.info("Model is now PINNED in process {} — will not be released until the server stops.", after["pid"])
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
