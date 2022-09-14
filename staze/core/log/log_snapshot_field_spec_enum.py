from enum import Enum


class LogSnapshotFieldSpecEnum(Enum):
    ALWAYS = 'always'
    NEVER = 'never'
    IF_TEST = 'if_test'
    IF_DEV = 'if_dev'
    IF_PROD = 'if_prod'
    IF_TEST_OR_DEV = 'if_test_or_dev'
