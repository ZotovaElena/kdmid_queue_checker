import logging
import sys
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from web.models import (
    CheckingExpectModel, CheckingResponseModel
    )
from web.service import run_check_queue

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


api = APIRouter(
    prefix='/queue_checker',
    tags=['KDMID Queue Checker'],
    responses={
        404: {"description": "Not found"}
    }
)

## MATCH 
@api.post(
    '/check',
    response_model=CheckingResponseModel,
    status_code=200, 
    responses={
         404: {"description": "Not found"}
    }
)

def get_item_mapping(item:CheckingExpectModel):
    message, status = run_check_queue(item.kdmid_subdomain, item.order_id, item.code, item.every_hours)
    return message, status