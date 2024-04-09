"""
This module is called by auto_generate_testcase_list_from_csv.py:
  1. check_run_test
  2. check_is_valid_ui_format

@author: Wang Lin
"""

import re
import csv
import os
from . import detect_delimiter


def _check_python_method_for_linktest(method_string, csv_file_full_path):
    # Regular expression matching rules:
    # 1. The string begins with `def` followed by a space.
    # 2. Then comes a valid Python method name, starting with a letter or underscore, followed by any number of letters, numbers, or underscores.
    # 3. Then comes zero or more spaces, followed by a left parenthesis.
    # 4. Then comes zero or more spaces, followed by `self`, then a comma and at least one character (representing at least one argument).
    # 5. Then any number of characters (including zero), followed by a right parenthesis.
    # 6. Finally, zero or more spaces, followed by a colon.

    pattern = r'^def\s+run_test\s*\(\s*self\s*,.+?\):.*$'
    match = re.match(pattern, method_string)

    file_base_name = os.path.splitext(csv_file_full_path)[0]

    if match:
        arugments_in_method_string = method_string.replace(" ", "").split("self,")[1].split(")")[0].split(",")

        with open(csv_file_full_path, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=detect_delimiter.detect_delimiter(csv_file_full_path))
            headers = next(reader)  # 读取第一行

            if set(arugments_in_method_string).issubset(set(headers)):
                return arugments_in_method_string
            else:
                miss_arguments_message = (
                    f"\n--- `run_test()` 方法的格式并未满足LinkTest框架的标准要求: ---\n"
                    f" LinkTest 的 DataSet 功能的标准要求: \n"
                    f"  1. CSV 文件及其对应的 Python 文件的文件名必须保持一致\n"
                    f"  2. Python 文件中必须定义 `run_test(self, ...)` 方法, 并且参数列表中除了 `self` 之外, 必须至少还有一个其他参数\n"
                    f"  3. Python 文件中定义的 `run_test()` 方法的所有参数名（除 `self` 参数外), 都必须存在于对应的 CSV 文件的表头（header）中\n\n"
                    f" - {file_base_name}.csv 文件的表头内容为: {headers}\n"
                    f" - {file_base_name}.py 文件中定义的 `run_test()` 方法的参数为: {arugments_in_method_string}\n"
                    f"--- 测试用例文件将不会自动生成。如需更多帮助信息，请运行以下命令：python3 run.py --help csv ---\n"
                )
                print(miss_arguments_message)
                return "miss_arguments"
    else:
        return None


def check_run_test(py_file_full_path):
    '''This function checks if the specified Python file defines the `run_test()` method that meets the DataSet feature
     standards of the LinkTest framework.
     If the method complies with the standards, it returns the parameter list of `run_test()`.
      If the `run_test()` method is not defined in the Python file, it returns `None`.
      If the `run_test()` method is defined but its parameters are incorrect, it returns `miss_arguments`.'''

    with open(py_file_full_path, "r", encoding='utf-8') as py_file_obj:
        check_res = None

        for line in py_file_obj.readlines():
            if line.startswith("#"):
                continue
            # Here, verify whether the parameters in `run_test()` correspond to column names existing in the associated CSV file.
            check_res = _check_python_method_for_linktest(line, py_file_obj.name.replace(".py", ".csv"))
            if type(check_res) == list:
                break
            elif check_res == "miss_arguments":
                break

        return check_res


def check_is_valid_ui_format(s):
    # Regular expression to match 4 spaces and 'self.browser.' at the start of the string
    pattern = r'^ {4}self\.browser\.'
    if re.match(pattern, s):
        return True
    return False


if __name__ == "__main__":
    # test check_is_valid_ui_format
    print("------")
    print(check_is_valid_ui_format('    self.browser.get("https://www.google.com")'))  # return True
    print(check_is_valid_ui_format('    self. browser.get("https://www.google.com")'))  # return False
    print(check_is_valid_ui_format('self.browser.get("https://www.google.com")'))  # return False
    print(check_is_valid_ui_format('     self.browser.get("https://www.google.com")'))  # return False
