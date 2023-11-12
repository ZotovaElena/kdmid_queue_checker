import logging
import sys
import json 
import os
import time
from http import HTTPStatus
import threading

from fastapi import APIRouter, HTTPException
from fastapi import BackgroundTasks
from fastapi import Depends
from typing import Dict, Any, Union

from web.models import (
    CheckingExpectModel, CheckingResponseModel, ErrorResponseModel
    )
# from web.service import run_check_queue
from core.queue_checker import QueueChecker

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def load_json_file(filename): 
    with open(filename, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

checker = QueueChecker()

class SharedState:
    def __init__(self):
        self.results: Dict[str, Any] = {}

def run_check_queue(kdmid_subdomain, order_id, code, state: SharedState, every_hours=1):
    print('run_check_queue called')
    success_file = order_id + "_" + code + "_success.json"
    error_file = order_id + "_" + code + "_error.json"

    while True:
        checker.check_queue(kdmid_subdomain, order_id, code)
        
        if os.path.isfile(success_file):
            with open(success_file, 'r') as f:
                state.results[order_id] = json.load(f)
        elif os.path.isfile(error_file):
            with open(error_file, 'r') as f:
                state.results[order_id] = json.load(f)
                print(state.results[order_id])
            break  # Stop the iteration when the error file is found

        time.sleep(every_hours*1)
        

def get_shared_state() -> SharedState:
    return SharedState()


api = APIRouter(
    prefix='/queue_checker',
    tags=['KDMID Queue Checker'],
    responses={
        404: {"description": "Not found"}
    }
)

 
@api.post(
    '/check',
    response_model=Union[CheckingResponseModel, ErrorResponseModel],
    status_code=200, 
    responses={
         404: {"description": "Not found"}
    }
)
def do_checking(background_tasks: BackgroundTasks, item: CheckingExpectModel, state: SharedState = Depends(get_shared_state)):
    print('do checking called')
    background_tasks.add_task(run_check_queue, item.kdmid_subdomain, item.order_id, item.code, state, item.every_hours)
    # Wait for the background task to finish
    if item.order_id in state.results:
        return state.results[item.order_id]