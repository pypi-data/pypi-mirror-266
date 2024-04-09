"""
This module is used to:
  Auto-generate the test case list based on the .csv and corresponding .py files.

If you need to use a dataSet (currently only supporting CSV format), please define it as follows:
  1. Create a CSV file using a comma ("," or '\t') as the separator.
  2. In the same directory as the CSV file, create a .py file with the same name. This .py file must define a `run_test(self, param...)` method.

For example:
  1. testLogin.csv file content:
        username,password
        user1,password1
        user2,password2

  2. testLogin.py file content:
        from common.test_login import login  # Import the specific business logic handling method

        def run_my_test(self, username, password):  # Define the received parameters (parameters must be defined in the CSV columns)
            self.logger.info("start run_test()...")
            login(self, username, password)

  -----> If executed correctly, the framework will generate a file (testLogin_case_list_auto_generated_by_csv.py) that conforms to the framework's running standards based on testLogin.csv and testLogin.py.

  Note: Similar to the __init__.py file, each time the script is executed, it will generate the latest auto_generated_by_csv.py file based on the corresponding .csv and .py files.

  The content of testLogin_case_list_auto_generated_by_csv.py:

      from linktest.api_testcase import APITestCase
      from tests.api.csv_dataset import testLoginDataSet

      class testLoginDataSet_1(APITestCase):
          tag = "testLoginDataSet"

          def run_test(self):
              username = 'user1'
              password = 'password1'

              testLoginDataSet.run_test(self, username, password)

      class testLoginDataSet_2(APITestCase):
          tag = "testLoginDataSet"

          def run_test(self):
              username = 'user2'
              password = 'password2'

              testLoginDataSet.run_test(self, username, password)

@author: Wang Lin
"""

import os
import csv
import traceback

from . import get_project_info
from . import detect_delimiter
from . import re_func
import pandas as pd

# from .framework_log import framework_logger



PROJECT_INFO = get_project_info.get_project_info()
TESTS_PACKAGE_PATH = PROJECT_INFO.project_path + os.sep + PROJECT_INFO.testcase_package_name

def process_csv_file(csv_file_full_path, is_ui_testcase, arguments_in_run_test_method, tag_name=''):
    with open(csv_file_full_path) as f:
        # f_csv = csv.DictReader(f, delimiter=detect_delimiter.detect_delimiter(csv_file_full_path))
        # reversed_f_csv = [row for row in f_csv]

        f_csv = pd.read_csv(csv_file_full_path, quoting=3, delimiter=detect_delimiter.detect_delimiter(csv_file_full_path))
        csv_keys = f_csv.keys()
        csv_values = f_csv.values
        reversed_f_csv = []

        for i in range(len(csv_values)):
            dict_data = {}
            for j in range(len(csv_values[i])):
                dict_data[csv_keys[j]] = csv_values[i][j]
            reversed_f_csv.append(dict_data)

        generate_testcase_list_by_csv(csv_file_full_path, reversed_f_csv, is_ui_testcase, arguments_in_run_test_method, tag_name=tag_name)


def generate_testcase_list_by_csv(file_name, rows, is_ui_testcase, arguments_in_run_test_method=[], tag_name=''):
    py_file_name = file_name.split(".")[0] + ".py"
    class_name = py_file_name.split(".")[0].split(os.sep)[-1]
    new_file_lines = []
    for index, row in enumerate(rows, 1):
        # Generate a class for each row
        if is_ui_testcase:
            new_file_lines.append(f"\n\nclass {class_name}_{index}(UITestCase):\n")
        else:
            new_file_lines.append(f"\n\nclass {class_name}_{index}(APITestCase):\n")
        new_file_lines.append(f'    tag = "{class_name}, {tag_name}"\n\n')

        # Generate a run_test function for each row
        new_file_lines.append("    def run_test(self):\n")

        for param, value in row.items():
            if param in arguments_in_run_test_method:
                new_file_lines.append(f"        {param} = {repr(value)} \n")

        new_file_lines.append(f"\n        {class_name}.run_test(self, {', '.join([k for k in row.keys() if k in arguments_in_run_test_method])})")

    # Write all lines to the output Python file
    with open(file_name.split(".")[0] + "_case_list_auto_generated_by_csv.py", "a") as f:
        f.writelines(new_file_lines)
        print(
            f" --- Generated {len(rows)} test cases based on the Python (.py) file and its associated CSV (.csv) file located at: " + file_name.split(".")[0])

def auto_generate_testcase_list_from_csv(call_by_doctor=False):
    # fetch all the test cases which in tests package and organize test cases
    for directory_path, directory_names, file_names in os.walk(TESTS_PACKAGE_PATH, topdown=True):
        csv_files = []

        directory_path = directory_path.replace(PROJECT_INFO.project_path + os.sep, "")

        for file_name in file_names:
            file_full_name = os.path.join(directory_path, file_name)
            if file_full_name.startswith(PROJECT_INFO.testcase_package_name + os.sep + "android" + os.sep):
                continue

            if file_full_name.split(".")[-1] == "csv":
                csv_files.append(file_full_name.split(".csv")[0].split(os.sep)[-1])

        # It's only necessary to check for the existence of a corresponding Python file if a CSV file is present.
        if len(csv_files) > 0:
            for file_name in file_names:
                file_full_name = os.path.join(directory_path, file_name)

                if file_name.split(".")[-1] == "py" and file_name != "__init__.py" and\
                        file_name.split(".")[0] in csv_files:
                    try:
                        os.remove(PROJECT_INFO.project_path + os.sep + directory_path + os.sep + file_name.split(".")[
                            0] + "_case_list_auto_generated_by_csv.py")
                    except BaseException:
                        pass

                    has_run_test_flag = False

                    check_res = re_func.check_run_test(PROJECT_INFO.project_path + os.sep + directory_path + os.sep + file_name)

                    if type(check_res) == list:
                        has_run_test_flag = True
                    elif check_res == 'miss_arguments':
                        continue

                    if not has_run_test_flag:
                        message = (
                            f"\n--- {PROJECT_INFO.project_path + os.sep + file_full_name} 文件中没有找到合法的 `run_test(self, ...)` 方法 ---\n"
                            f" LinkTest 的 DataSet 功能的标准要求: \n"
                            f"  1. CSV 文件及其对应的 Python 文件的文件名必须保持一致\n"
                            f"  2. Python 文件中必须定义 `run_test(self, ...)` 方法, 并且参数列表中除了 `self` 之外, 必须至少还有一个其他参数\n"
                            f"  3. Python 文件中定义的 `run_test()` 方法的所有参数名（除 `self` 参数外), 都必须存在于对应的 CSV 文件的表头（header）中\n"
                            f"--- 测试用例文件将不会自动生成。如需更多帮助信息，请运行以下命令：python3 run.py --help csv ---\n"
                        )
                        print(message)

                        continue

                    with open(PROJECT_INFO.project_path + os.sep + directory_path + os.sep + file_name.split(".")[
                        0] + "_case_list_auto_generated_by_csv.py", "w") as f:
                        f.write("from %s import %s\n" % (directory_path.replace(os.sep, "."), file_name.split(".")[0]))

                    is_ui_testcase = False
                    # First, parse the Python (.py) file. If `self.browser` is present in the file, it indicates that `UITestCase` needs to be imported.
                    with open(PROJECT_INFO.project_path + os.sep + directory_path + os.sep + file_name.split(".")[
                        0] + ".py", "r", encoding='utf-8') as py_file_obj:
                        for line in py_file_obj.readlines():
                            if re_func.check_is_valid_ui_format(line):
                                is_ui_testcase = True
                                # import UTTestCase
                                with open(PROJECT_INFO.project_path + os.sep + directory_path + os.sep +
                                          file_name.split(".")[
                                              0] + "_case_list_auto_generated_by_csv.py", "a") as f:
                                    f.write("from linktest.ui_testcase import UITestCase")
                                break

                    if not is_ui_testcase:
                        # import APITestCase
                        with open(PROJECT_INFO.project_path + os.sep + directory_path + os.sep +
                                  file_name.split(".")[
                                      0] + "_case_list_auto_generated_by_csv.py", "a") as f:
                            f.write("from linktest.api_testcase import APITestCase")

                    csv_file_full_path = PROJECT_INFO.project_path + os.sep + directory_path + os.sep + \
                                         file_name.split('.')[0] + ".csv"


                    # Parse the Python (.py) file and check if `tag = "tagName"` is present. If so, it indicates that the automatically generated test case should also be set with the user-defined `tagName`.
                    tag_name = ''
                    with open(PROJECT_INFO.project_path + os.sep + directory_path + os.sep + file_name.split(".")[
                        0] + ".py", "r", encoding='utf-8') as py_file_obj:
                        for line in py_file_obj.readlines():
                            if line.replace(" ", "").startswith("tag="):
                                tag_name = line.replace(" ", "").split("=")[1].replace('"', "").replace("'", "").replace("\n", "")
                                break

                    process_csv_file(csv_file_full_path, is_ui_testcase, check_res, tag_name=tag_name)


if __name__ == "__main__":
    auto_generate_testcase_list_from_csv()
