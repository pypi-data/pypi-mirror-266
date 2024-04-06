from .base_test_link import BaseTestLink
from cores.utils.common.logger_util import logger


class Build:
    def __init__(self, test_plan_id):
        self.test_plan_id = test_plan_id

    def create_new_build_version(self, build_name, build_notes: str = ""):
        # Create the build version in the specified test plan'
        build_id = BaseTestLink.test_link_client.createBuild(
            testplanid=self.test_plan_id, buildname=build_name, buildnotes=build_notes)
        logger.info(f"Version '{build_name}' created to test plan")

        return build_id

    def get_build(self, build_name):
        # Get the build ID based on the build name and test plan ID
        build_info = BaseTestLink.test_link_client.getBuildByName(
            self.test_plan_id, build_name)
        return build_info[0]['id']
