# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
import json
import traceback
from abc import abstractmethod

from selenium.common import TimeoutException, WebDriverException, NoSuchWindowException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_driver(chrome_options_args=None, proxy_ip=None, **kwargs):
    # 关于chromedriver的问题，请仔细阅读：https://chromedriver.chromium.org/home

    if chrome_options_args is None:
        chrome_options_args = ["--headless",  # 以无头模式启动
                               "--disable-gpu",  # 禁用GPU加速
                               "--no-sandbox",  # 以沙盒模式运行
                               "--disable-dev-shm-usage"  # 禁用/dev/shm使用
                               ]
    chrome_options = webdriver.ChromeOptions()
    if proxy_ip:
        # 去掉proxy_ip中的空白字符
        proxy_ip = "".join(proxy_ip.split())
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = proxy_ip  # 代理服务器的IP地址和端口号
        proxy.ssl_proxy = proxy_ip
        chrome_options.add_argument(f'--proxy-server=http://{proxy_ip}')

    for option in chrome_options_args:
        chrome_options.add_argument(option)

    # driver = webdriver.Chrome(options=chrome_options)

    driver_manager_kwargs = kwargs.get("driver_manager_kwargs")
    if driver_manager_kwargs == None:
        driver_manager_kwargs = {}

    # 获取driver
    service = Service(executable_path=ChromeDriverManager(
        **driver_manager_kwargs
    ).install())
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    return driver


class ResponseError:
    def __init__(self, status="", msg="", screen="", collect_link=""):
        self.status = status
        self.msg = msg
        self.screen = screen
        self.collect_link = collect_link

    def to_dict(self):
        return self.__dict__

    def to_str(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)


@abstractmethod
def wait_for_specified_element(driver, waiting_class_name, page_empty_tips_class=None, wait_seconds=120,
                               web_interrupt_texts=[]):
    # todo 该方法需要重构
    current_url = driver.current_url
    webdriverErrorMsg = ResponseError(status="", collect_link=current_url)
    try:

        # 页面阻断处理
        if web_interrupt_texts:
            # 等待页面加载出div，最多10秒钟，每0.5秒检查一次页面是否出现了指定元素
            wait1 = WebDriverWait(driver, wait_seconds, poll_frequency=0.5)
            # 等待直到页面出现名为"my_element"的元素
            element1 = wait1.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            element1_text = element1.text
            # 去掉element1_text中的空白字符，包括空格、换行符、制表符等
            element1_text = "".join(element1_text.split())
            element1_text = element1_text.lower().replace(" ", "").replace("\n", "").replace("\t", "")

            for web_interrupt_text in web_interrupt_texts:
                web_interrupt_text = "".join(web_interrupt_text.split())
                web_interrupt_text = web_interrupt_text.lower().replace(" ", "").replace("\n", "").replace("\t", "")

                if web_interrupt_text in element1_text:
                    webdriverErrorMsg.status = "WEB_INTERRUPT"
                    webdriverErrorMsg.screen = get_driver_screenshot(driver)
                    webdriverErrorMsg.msg = f"页面出现了阻断信息：{web_interrupt_text}"
                    return webdriverErrorMsg

        # 页面为空的处理
        page_empty_tip = None
        try:
            if page_empty_tips_class:
                page_empty_tip = driver.find_element(By.CLASS_NAME, page_empty_tips_class)

            if page_empty_tips_class and page_empty_tip:
                webdriverErrorMsg.status = "PAGE_HAS_NO_JOB"
                webdriverErrorMsg.screen = get_driver_screenshot(driver)
                webdriverErrorMsg.msg = "页面内没有职位信息"
                return webdriverErrorMsg
        except Exception as e:
            pass

        # 等待最多10秒钟，每0.5秒检查一次页面是否出现了指定元素
        wait = WebDriverWait(driver, wait_seconds, poll_frequency=0.5)
        # 等待直到页面出现名为"my_element"的元素
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, waiting_class_name)))
        return None
    except TimeoutException as e:
        # 在页面内获取"空页面"的元素
        page_empty_tip = None
        if page_empty_tips_class:
            try:
                page_empty_tip = driver.find_element(By.CLASS_NAME, page_empty_tips_class)
                if page_empty_tip:
                    webdriverErrorMsg.status = "PAGE_HAS_NO_JOB"
                    webdriverErrorMsg.screen = get_driver_screenshot(driver)
                    webdriverErrorMsg.msg = "页面内没有职位信息"
                    return webdriverErrorMsg
                else:
                    tb = traceback.format_exc()
                    webdriverErrorMsg.screen = get_driver_screenshot(driver)
                    webdriverErrorMsg.msg = f"获取职位详情信息超时，可能是代理ip失效了，或者页面结构发生了变化，{wait_seconds}秒内没有获取到class={waiting_class_name}元素。 详细跟踪信息：\n{tb}"

            except Exception as e:
                pass
        else:
            tb = traceback.format_exc()
            webdriverErrorMsg.screen = get_driver_screenshot(driver)
            webdriverErrorMsg.msg = f"获取职位详情信息超时，可能是代理ip失效了，或者页面结构发生了变化，{wait_seconds}秒内没有获取到class={waiting_class_name}元素。 详细跟踪信息：\n{tb}"


    except WebDriverException as e:
        msg = e.msg
        tb = traceback.format_exc()
        # logger.error(f"代理服务器出现问题，或者地址有误。 详细跟踪信息：\n{msg}")
        webdriverErrorMsg.screen = get_driver_screenshot(driver)
        webdriverErrorMsg.msg = f"代理服务器出现问题，或者地址有误。 详细跟踪信息：\n{msg}"
    except Exception as e:
        # 获取当前文件的当前行号
        line = traceback.format_exc().split("\n")[-2]
        tb = traceback.format_exc()
        # logger.error(f"发生未知异常。请到[{line}]捕捉并处理异常 。 详细跟踪信息：\n{tb}")
        webdriverErrorMsg.status = "UNKNOWN_ERROR"
        webdriverErrorMsg.screen = get_driver_screenshot(driver)
        webdriverErrorMsg.msg = f"发生未知异常。请到[{line}]捕捉并处理异常 。 详细跟踪信息：\n{tb}"

    return webdriverErrorMsg


def get_driver_screenshot(driver):
    screenshot = ""
    try:
        screenshot = driver.get_screenshot_as_base64()
    except NoSuchWindowException as e:
        # logger.error(f"获取截图失败，窗口已经关闭。")
        print(f"获取截图失败，窗口已经关闭。")
        pass
    return screenshot


'''
使用方法
首次使用的时候需要科学上网，它会自动的下载最新的浏览器内核

from pystools import SeleniumWebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


chrome_options_args = [
    # "--headless",  # 以无头模式启动
    "--disable-gpu",  # 禁用GPU加速
    "--no-sandbox",  # 以沙盒模式运行
    "--disable-dev-shm-usage",  # 禁用/dev/shm使用
    "--lang=en_US.UTF-8"
]
                             
driver = SeleniumWebDriver.get_driver(chrome_options_args=chrome_options_args)

driver.get(use_url)
# 等待页面加载出div，最多10秒钟，每0.5秒检查一次页面是否出现了指定元素
wait = WebDriverWait(driver, 10, poll_frequency=0.5)
waite_for = "hyxxy"
waite_for_by = By.CLASS_NAME
print(f"use url: {use_url}  waite for [{waite_for_by}]:[{waite_for}] ")

try:
    element = wait.until(EC.presence_of_element_located((waite_for_by, waite_for)))
except Exception as e:
    # print(e)
    tb = traceback.format_exc()
    error_msg = f"waite for [{waite_for_by}]:[{waite_for}] error  \n{tb} \n\n"
    raise Exception(f"driver wait异常，url:{url}, {error_msg}")

# 获取视觉页面上的信息
html = element.get_attribute('outerHTML')

# 使用BeautifulSoup获取指定的元素
content_box = BeautifulSoup(html, 'html.parser')
cate_els = content_box.find_all("div", class_="catdalei")


driver.quit()

'''