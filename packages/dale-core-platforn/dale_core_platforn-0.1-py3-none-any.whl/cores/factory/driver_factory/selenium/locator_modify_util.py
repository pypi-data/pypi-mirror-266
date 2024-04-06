from cores.const.web import StoreConst
from cores.utils.common.store_util import GetUtil, StoreUtil
from cores.utils.common.logger_util import logger

"""
    Set locator support to store locator for gauge framework
"""


class LocatorModify:

    @staticmethod
    def set_locators(locators_dict, is_distinct_locator: bool = True):
        if GetUtil.scenario_get(StoreConst.LOCATORS):
            if is_distinct_locator:
                org_locators = [
                    *GetUtil.scenario_get(StoreConst.LOCATORS).keys()]
                new_locators = [*locators_dict.keys()]
                for key in new_locators:
                    if not org_locators.count(key) >= 1:
                        StoreUtil.scenario_store(keyword=StoreConst.LOCATORS, data=GetUtil.scenario_get(
                            StoreConst.LOCATORS) | {key: locators_dict[key]})
            else:
                StoreUtil.scenario_store(keyword=StoreConst.LOCATORS,
                                         data=GetUtil.scenario_get(StoreConst.LOCATORS) | locators_dict)
        else:
            StoreUtil.scenario_store(
                keyword=StoreConst.LOCATORS, data=locators_dict)

    @staticmethod
    def modify_sub_locators(source_locator):
        """
            Convert XPATH to full address by sub_locator
        """
        tmp: dict = source_locator.copy()
        for key, value in tmp.items():
            locator_info = list(value)
            if "%(" in locator_info[1]:
                try:
                    key_mapping = value[1].split(")s")[0][2:]
                    locator_info[1] = locator_info[1].replace(
                        f"%({key_mapping})s", tmp[key_mapping][1])
                    tmp[key] = tuple(locator_info)
                except:
                    logger.debug("key_mapping doesn't have sub_locator")
            else:
                continue
        return tmp
