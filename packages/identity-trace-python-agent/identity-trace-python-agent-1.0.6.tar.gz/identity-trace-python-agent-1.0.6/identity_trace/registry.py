

_function_registry = {}
__function_registry = {}
__function_processor_map = dict()


def register_frame(frame, execution_context):
    _function_registry[_get_frame_id(frame)] = execution_context


def is_frame_registered(frame):
    return _function_registry.get(_get_frame_id(frame), None)


def remove_frame(frame):
    if _function_registry.get(frame, None):
        del _function_registry[frame]


def _get_frame_id(frame):
    return id(frame)


def register_function(function_name, func):
    __function_registry[function_name] = func


def get_function_by_name(function_name):
    return __function_registry.get(function_name, None)


def register_function_processor(callback):

    __function_processor_map['callback'] = callback


def remove_function_processor_callback():

    try:
        del __function_processor_map['callback']
    except:
        ...

def get_function_processor_callbacks():
    return __function_processor_map.get('callback', None)