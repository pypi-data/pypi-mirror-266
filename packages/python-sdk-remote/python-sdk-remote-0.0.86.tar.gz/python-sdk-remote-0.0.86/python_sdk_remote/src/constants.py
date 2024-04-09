import os

from logger_local.LoggerComponentEnum import LoggerComponentEnum

PYTHON_SDK_LOCAL_COMPONENT_ID = 184
PYTHON_SDK_LOCAL_COMPONENT_NAME = 'python_sdk_local'

ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")
BRAND_NAME = os.getenv("BRAND_NAME")
LOGZIO_TOKEN = os.getenv("LOGZIO_TOKEN")
# TODO Shall Can we use python-sdk function to get the value from Environment?
# TODO Shall we get the value from environment here of send the value to the function as @akiva-skolnik did?
GOOGLE_PORT_FOR_AUTHENTICATION = os.getenv("PORT_FOR_AUTHENTICATION")

OBJECT_TO_INSERT_CODE = {
    'component_id': PYTHON_SDK_LOCAL_COMPONENT_ID,
    'component_name': PYTHON_SDK_LOCAL_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'sahar.g@circ.zone'
}

OBJECT_TO_INSERT_TEST = {
    'component_id': PYTHON_SDK_LOCAL_COMPONENT_ID,
    'component_name': PYTHON_SDK_LOCAL_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': 'sahar.g@circ.zone'
}
