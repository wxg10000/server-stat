# _*_ coding: utf-8 _*_


import sys
import io

import time
from selenium import webdriver
from selenium.webdriver import ActionChains

if __name__ == '__main__':

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码

    # 建立Phantomjs浏览器对象，括号里是phantomjs.exe在你的电脑上的路径
    browser = webdriver.PhantomJS('/Users/edz/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')

    # 登录页面
    url = r'https://account.aliyun.com/login/login.htm'

    # 访问登录页面
    browser.get(url)

    browser.switch_to_frame('alibaba-login-box')  # 需先跳转到iframe框架

    # 等待一定时间，让js脚本加载完毕
    browser.implicitly_wait(5)
    browser.save_screenshot('picture1.png')
    print(browser.title)

    # 输入用户名
    username = browser.find_element_by_id('fm-login-id')
    print(username)
    username.send_keys('数猎天下')

    # 输入密码
    password = browser.find_element_by_name('password')
    password.send_keys('Dat@Hunter8')

    # # 选择“学生”单选按钮
    # student = browser.find_element_by_xpath('//input[@value="student"]')
    # student.click()

    # 定位元素的源位置
    element = browser.find_element_by_id("nc_1_n1z")
    # 定位元素要移动到的目标位置
    target = browser.find_element_by_id("nc_1_scale_text")
    # 执行元素的拖放操作
    ActionChains(browser).drag_and_drop(element, target).perform()

    # 点击“登录”按钮
    login_button = browser.find_element_by_name('submit-btn')
    login_button.submit()
    time.sleep(10)

    # 网页截图
    browser.save_screenshot('picture2.png')
    # 打印网页源代码
    print(browser.page_source.encode('utf-8').decode())

    browser.quit()
