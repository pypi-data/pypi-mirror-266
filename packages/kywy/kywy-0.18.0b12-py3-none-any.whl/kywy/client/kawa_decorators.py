import datetime
from typing import List

from kywy.client.kawa_types import Types


def inputs(**kwargs):
    def decorator_set_inputs(func):
        func.inputs = [{'name': k, 'type': python_type_to_kawa_type(v)} for k, v in kwargs.items()]
        return func

    return decorator_set_inputs


def outputs(**kwargs):
    def decorator_set_outputs(func):
        func.outputs = [{'name': k, 'type': python_type_to_kawa_type(v)} for k, v in kwargs.items()]
        return func

    return decorator_set_outputs


def secrets(**kwargs):
    def decorator_set_secret_mapping(func):
        func.secrets = kwargs
        return func

    return decorator_set_secret_mapping


def python_type_to_kawa_type(python_type):
    if python_type == str:
        return Types.TEXT
    if python_type == float:
        return Types.DECIMAL
    if python_type == int:
        return Types.INTEGER
    if python_type == datetime.date:
        return Types.DATE
    if python_type == datetime.datetime:
        return Types.DATE_TIME
    if python_type == bool:
        return Types.BOOLEAN
    if python_type == List[float]:
        return Types.LIST_OF_DECIMALS

    raise Exception('This type is not yet available: {}'.format(python_type))
