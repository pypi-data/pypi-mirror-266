from logger_local.LoggerComponentEnum import LoggerComponentEnum


ACTION_ITEMS_LOCAL_PYTHON_COMPONENT_ID = 283
ACTION_ITEMS_LOCAL_PYTHON_COMPONENT_NAME = "action-item-local-python-package"
DEVELOPER_EMAIL = "tal.g@circ.zone"
ACTION_ITEMS_PYTHON_PACKAGE_CODE_LOGGER_OBJECT = {
    'component_id': ACTION_ITEMS_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': ACTION_ITEMS_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}


ACTION_ITEMS_PYTHON_PACKAGE_TEST_LOGGER_OBJECT = {
    'component_id': ACTION_ITEMS_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': ACTION_ITEMS_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': DEVELOPER_EMAIL
}
