from logger_local.LoggerComponentEnum import LoggerComponentEnum


class GroupsLocalConstants:

    ENGLISH_GROUP_ID = 50001176
    VENTURE_CAPITAL_GROUP_ID = 50001177
    ADVOCATE_GROUP_ID = 50001175
    GROUPS_LOCAL_PYTHON_COMPONENT_ID = 285
    GROUPS_LOCAL_PYTHON_COMPONENT_NAME = "groups-local-python-package"
    DEVELOPER_EMAIL = "tal.g@circ.zone"
    GROUPS_PYTHON_PACKAGE_CODE_LOGGER_OBJECT = {
        'component_id': GROUPS_LOCAL_PYTHON_COMPONENT_ID,
        'component_name': GROUPS_LOCAL_PYTHON_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
        'developer_email': DEVELOPER_EMAIL
    }

    GROUPS_PYTHON_PACKAGE_TEST_LOGGER_OBJECT = {
        'component_id': GROUPS_LOCAL_PYTHON_COMPONENT_ID,
        'component_name': GROUPS_LOCAL_PYTHON_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
        'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
        'developer_email': DEVELOPER_EMAIL
    }
