from . import HXLS, VMC

worker_area_registry = {
    "HXLS": HXLS,
    "VMC": VMC
}

def execute_job(area):
    worker = worker_area_registry[area]
    worker.primary_action()