"""
WebDriverWrapper 类说明文档
作者：Lin Wang

概述：
WebDriverWrapper 类是一个对 Selenium WebDriver (特别是 Chrome 类) 的扩展，用于在执行 Web UI 测试时自动记录 webdriver 操作。
当调用常用的方法，如 get、find_element、click 等时，这些操作将自动记录到 logger 中。

使用说明：
1. 导入 WebDriverWrapper 类：
   从 webdriver_wrapper 模块导入 WebDriverWrapper 类。

2. 创建 WebDriverWrapper 实例：
   在测试框架中，使用 WebDriverWrapper 类替换原来的 Chrome webdriver 实例。将 logger 对象和其他所需参数传入 WebDriverWrapper 的构造函数中。

示例代码：

from selenium.webdriver import ChromeOptions
from webdriver_wrapper import WebDriverWrapper

class MyTestCase:
    def __init__(self, logger):
        self.logger = logger
        chrome_options = ChromeOptions()
        # 使用 WebDriverWrapper 替换原来的 webdriver 实例
        self.browser = WebDriverWrapper(self.logger, options=chrome_options)

    def run_test(self):
        self.browser.get("https://www.bing.com")
        # 其他测试代码

功能说明：
1. _log_action 方法：
   用于记录操作到 logger。在为其他 webdriver 方法添加日志记录功能时，可以调用此方法。

2. 常用方法的日志记录功能：
   WebDriverWrapper 类已经为以下方法添加了日志记录功能：
   - get
   - find_element
   - find_elements
   - execute_script

   根据需要，您可以继续为其他 webdriver 方法添加日志记录功能，只需在 WebDriverWrapper 类中重写这些方法并调用 _log_action() 即可。
"""
import typing
from typing import List
from typing import Dict
from typing import Optional
from typing import Union

from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.common.timeouts import Timeouts

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from selenium.webdriver.remote.webelement import WebElement
from typing import Union, Any


class WebElementWrapper:
    def __init__(self, element, logger):
        self.element = element
        self.logger = logger

    def _log_action(self, action, *args):
        msg = f"--- WebElement Action: '{action}' with args: {', '.join(map(str, args))}"
        self.logger.info(msg)

    def send_keys(self, *value):
        self._log_action("send_keys", *value)
        self.element.send_keys(*value)

    def click(self):
        self._log_action("click")
        self.element.click()

    def clear(self):
        self._log_action("clear")
        self.element.clear()

    def tag_name(self) -> str:
        self._log_action("tag_name")
        return self.element.tag_name

    def submit(self):
        self._log_action("submit")
        self.element.submit()

    def text(self) -> str:
        self._log_action("text")
        return self.element.text

    def get_property(self, name) -> Union[str, bool, WebElement, dict]:
        self._log_action("get_property", name)
        return self.element.get_property(name)

    def get_dom_attribute(self, name) -> str:
        self._log_action("get_dom_attribute", name)
        return self.element.get_attribute(name)

    def get_attribute(self, name) -> Union[str, None]:
        self._log_action("get_attribute", name)
        return self.element.get_attribute(name)

    def is_selected(self) -> bool:
        self._log_action("is_selected")
        return self.element.is_selected()

    def is_enabled(self) -> bool:
        self._log_action("is_enabled")
        return self.element.is_enabled()

    def is_displayed(self) -> bool:
        self._log_action("is_displayed")
        return self.element.is_displayed()

    def location_once_scrolled_into_view(self) -> dict:
        self._log_action("location_once_scrolled_into_view")
        return self.element.location_once_scrolled_into_view

    def size(self) -> dict:
        self._log_action("size")
        return self.element.size

    def value_of_css_property(self, property_name) -> str:
        self._log_action("value_of_css_property", property_name)
        return self.element.value_of_css_property(property_name)

    def location(self) -> dict:
        self._log_action("location")
        return self.element.location

    def rect(self) -> dict:
        self._log_action("rect")
        return self.element.rect

    def screenshot_as_base64(self) -> str:
        self._log_action("screenshot_as_base64")
        return self.element.screenshot_as_base64

    def screenshot_as_png(self) -> bytes:
        self._log_action("screenshot_as_png")
        return self.element.screenshot_as_png

    def screenshot(self, filename) -> bool:
        self._log_action("screenshot", filename)
        return self.element.screenshot(filename)

    def parent(self):
        self._log_action("parent")
        return self.element.parent

    def id(self) -> str:
        self._log_action("id")
        return self.element.id

    def find_element(self, by=By.ID, value=None) -> WebElement:
        self._log_action("find_element", by, value)
        return self.element.find_element(by, value)

    def find_elements(self, by=By.ID, value=None) -> List[WebElement]:
        self._log_action("find_elements", by, value)
        return self.element.find_elements(by, value)

    def __hash__(self) -> int:
        self._log_action("__hash__")
        return self.element.__hash__()

    # todo:可以继续封装 WebElement 的其他方法


class WebDriverWrapper(Chrome):
    def __init__(self, logger, *args, **kwargs):
        self.logger = logger
        super().__init__(*args, **kwargs)

    def _log_action(self, action, *args):
        msg = f"--- WebDriver Action: '{action}' with args: {', '.join(map(str, args))}"
        self.logger.info(msg)

    def get(self, url):
        self._log_action("get", url)
        super().get(url)

    def find_element(self, by=By.ID, value=None):
        self._log_action("find_element", by, value)
        element = super().find_element(by, value)
        return WebElementWrapper(element, self.logger)

    def find_elements(self, by=By.ID, value=None):
        self._log_action("find_elements", by, value)
        return super().find_elements(by, value)

    def execute_script(self, script, *args):
        self._log_action("execute_script", script, *args)
        return super().execute_script(script, *args)

    # def execute(self, driver_command: str, params: dict = None) -> dict:
    #     self._log_action("execute", driver_command, params)
    #     return super().execute(driver_command, params)

    def execute_async_script(self, script: str, *args):
        self._log_action("execute_async_script", script, *args)
        return super().execute_async_script(script, *args)

    def title(self) -> str:
        self._log_action("title")
        return super().title

    # def create_web_element(self, element_id: str) -> WebElement:
    #     self._log_action("create_web_element", element_id)
    #     return super().create_web_element(element_id)

    def start_session(self, capabilities: dict) -> None:
        self._log_action("start_session", capabilities)
        super().start_session(capabilities)

    def current_url(self) -> str:
        self._log_action("current_url")
        return super().current_url

    def page_source(self) -> str:
        self._log_action("page_source")
        return super().page_source

    def close(self) -> None:
        self._log_action("close")
        super().close()

    def quit(self) -> None:
        self._log_action("quit")
        super().quit()

    def current_window_handle(self) -> str:
        self._log_action("current_window_handle")
        return super().current_window_handle

    def window_handles(self) -> List[str]:
        self._log_action("window_handles")
        return super().window_handles

    def maximize_window(self) -> None:
        self._log_action("maximize_window")
        super().maximize_window()

    def fullscreen_window(self) -> None:
        self._log_action("fullscreen_window")
        super().fullscreen_window()

    def minimize_window(self) -> None:
        self._log_action("minimize_window")
        super().minimize_window()

    def get_cookie(self, name) -> typing.Optional[typing.Dict]:
        self._log_action("get_cookie", name)
        return super().get_cookie(name)

    def refresh(self) -> None:
        self._log_action("refresh")
        super().refresh()

    def forward(self) -> None:
        self._log_action("forward")
        super().forward()

    def back(self) -> None:
        self._log_action("back")
        super().back()

    def print_page(self, print_options: Optional[PrintOptions] = None) -> str:
        self._log_action("print_page", print_options)
        return super().print_page(print_options)

    def get_cookies(self) -> List[dict]:
        self._log_action("get_cookies")
        return super().get_cookies()

    def add_cookie(self, cookie_dict) -> None:
        self._log_action("add_cookie", cookie_dict)
        super().add_cookie(cookie_dict)

    def delete_cookie(self, name) -> None:
        self._log_action("delete_cookie", name)
        super().delete_cookie(name)

    def delete_all_cookies(self) -> None:
        self._log_action("delete_all_cookies")
        super().delete_all_cookies()

    def implicitly_wait(self, time_to_wait: float) -> None:
        self._log_action("implicitly_wait", time_to_wait)
        super().implicitly_wait(time_to_wait)

    def set_script_timeout(self, time_to_wait: float) -> None:
        self._log_action("set_script_timeout", time_to_wait)
        super().set_script_timeout(time_to_wait)

    def set_page_load_timeout(self, time_to_wait: float) -> None:
        self._log_action("set_page_load_timeout", time_to_wait)
        super().set_page_load_timeout(time_to_wait)

    # todo 可以继续在此处添加其他 WebDriver 方法的日志记录功能
