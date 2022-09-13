import json
from staze.core.log.log import log


# def test_ecs():
#     def format_log(message: str):
#         a = json.loads(message)
#         print(a)

#     b = log.add(format_log, level='DEBUG', serialize=True)
#     log.debug('test')
#     assert False


def test_dummy():
    log.bind(id=1).debug('Dummy Johnson')
    assert False
