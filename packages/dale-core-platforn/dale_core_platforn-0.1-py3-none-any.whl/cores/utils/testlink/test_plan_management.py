from cores.utils.common.logger_util import logger
from cores.utils.testlink.base_test_link import BaseTestLink


class TestPlan:

    @staticmethod
    def create_new_test_plan(project_name, test_plan_name):
        # Create the test plan
        BaseTestLink.test_link_client.createTestPlan(
            testprojectname=project_name, testplanname=test_plan_name)
        logger.info(
            f"Test Plan '{test_plan_name}' created to project '{project_name}'")

    @staticmethod
    def get_test_plan_by_project_name(project_name, test_plan_name):
        # Get the test plan ID based on the test plan name and project ID
        test_plan_info = BaseTestLink.test_link_client.getTestPlanByName(
            testprojectname=project_name, testplanname=test_plan_name)
        return test_plan_info[0]['id']

    @staticmethod
    def get_all_test_plans(project_id):
        # Get the test plan ID based on the test plan name and project ID
        test_plan_info = BaseTestLink.test_link_client.getProjectTestPlans(
            testprojectid=project_id)

        return test_plan_info

    @staticmethod
    def delete_test_plan_by_id(test_plan_id):
        # Delete the test plan
        BaseTestLink.test_link_client.deleteTestPlan(test_plan_id)
        logger.info(f"Test Plan '{test_plan_id}' deleted successfully")

    @staticmethod
    def clean_all_test_plan(project_id):
        test_plans = TestPlan.get_all_test_plans(project_id=project_id)
        for item in test_plans:
            plan_id = item['id']
            TestPlan.delete_test_plan_by_id(test_plan_id=plan_id)
