# -*- encoding=utf8 -*-
__author__ = "ziyu"

from airtest.core.api import *
import time
from random import random, randint
auto_setup(__file__)
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

def open_workspace():
    wake()
    home()

class Spider: # Prototype for all spiders
    def __init__(self, app_name, keyword, must_include, search_dict): 
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        self.app_name = app_name
        self.keyword = keyword
        self.must_include = must_include # A string that relevant search results must include
        self.search_dict = search_dict
    def click_by_name_if_exists(self, name):
        button = self.poco(name=name) # Search for a button by name
        time.sleep(1)
        if button.exists(): # Click on the button if it exists
            button.click()
    def clear_all_apps(self):
        keyevent("MENU")
        self.click_by_name_if_exists('com.miui.home:id/clearAnimView')
        home()
    def open_nth_app(self, n):
        keyevent("MENU")
        time.sleep(1)
        self.poco(name='com.miui.home:id/task_view_thumbnail')[n].click() # Click on the nth app among all the  apps
    def open_next_app(self):
        self.open_nth_app(1)
    def swipe_right(self):
        start = [0.8 + 0.2 * random(), 0.4 + 0.2 * random()] # Middle right of the screen
        end = [0.2 * random(), 0.4 + 0.2 * random()]
        self.poco.swipe(start, end, duration=0.1 + 0.1 * random()) # Duration is randomized
    def scroll_random_length(self):
        # Scroll down for a random length
        self.poco.scroll(u'vertical', 0.1+0.6*random(), 3*random())
    def launch_app(self, app_name):
        app_button = self.poco(desc=app_name)
        while not app_button.exists(): # Look for the app button until found
            self.swipe_right()
        app_button.click()
    def launch_this_app(self):
        # Open the app that the spider is scraping
        self.launch_app(self.app_name)
    def launch_notes(self, close_yosemite=True):
        # Since poco doesn't have an API for accessing clipboard contents yet, Notes is used to temporarily store the URLs. The URLs stored in Notes have to be manually sent to the computer eventually.
        home()
        self.launch_app("Notes")
        add_button = self.poco(name='com.miui.notes:id/content_add')
        while not add_button.exists():
            keyevent('back')
        add_button.click() # Add new notes
        if close_yosemite: # Close yosemite to be able to manipulate the keyboard if needed 
            self.close_yosemite_input()
        keyevent("BACK")
        home()
    def close_yosemite_input(self):
        self.poco.click([0.5, 0.9375])
        self.poco(text='Yosemite输入法').parent().sibling().child().click()
    def search(self):
        bar = self.poco(name=self.search_dict['bar'])
        bar.wait_for_appearance()
        bar.click()
        self.poco(name=self.search_dict['term']).set_text(self.keyword) # Input the keyword
        self.poco(name=self.search_dict['button']).click()
    def enter(self):
        self.poco.click([0.93, 0.91375]) # Click on the ENTER button
    def paste(self):
        self.poco.click([0.5, 0.654]) # Paste the clipboard contents
    
class XianyuSpider(Spider):
    def __init__(self, keyword, must_include):
        search_dict = {
            'bar': 'com.taobao.idlefish:id/bar_marquee_tx',
            'term': 'com.taobao.idlefish:id/search_term',
            'button': 'com.taobao.idlefish:id/search_button'
        }
        # Inherit from the prototype Spider
        super(XianyuSpider, self).__init__('闲鱼', keyword, must_include, search_dict)
    def scroll_to_next_page(self):
        for i in range(3):
            self.poco.scroll(u'vertical', 0.31, 3*random())
    def collect_all_visible_results(self):
        results = self.poco(textMatches='^(.|\n)*' + self.must_include + '(.|\n)+$') # Only check the search results that contain the string specified by self.must_include
        for result in list(results)[1:]:
            result.click()
            time.sleep(2)
            if not self.poco(text='细选'): # This (细选) is not an actual result, therefore it is skipped
                for i in range(randint(1, 3)):
                    self.scroll_random_length() # Randomly scroll down to imitate real user's behavior
                    time.sleep(randint(1, 3))
                self.copy_url()
                keyevent("BACK")
                time.sleep(2)

    def copy_url(self):
        more_button = self.poco(text='更多')
        if more_button.exists():
            more_button.click()
            self.poco(text='复制链接').click()
            self.open_next_app()
            self.poco(name='com.miui.notes:id/rich_editor').click()
            self.paste()
            for i in range(10):
                self.enter()
            self.open_next_app()

def main():
    keyword = '达达里奥 ' 
    must_include = '达达里奥' # Always make sure that the keyword is not exactly the same as the must_include. Add a space at the end of the keyword if you want them to be the same. Usually must_include doesn't have to be changed.
    xianyu_spider = XianyuSpider(keyword, must_include)
    open_workspace()
    xianyu_spider.clear_all_apps()
    xianyu_spider.launch_notes()
    xianyu_spider.launch_this_app() # Launch Xianyu
    xianyu_spider.search() # Search with the keyword
    for i in range(100):
        xianyu_spider.collect_all_visible_results()
        if i % 20 == 19:
            xianyu_spider.launch_notes(False) # Open new notes since there's a limit for the number of characters that each notes can contain
            xianyu_spider.open_next_app()
        xianyu_spider.scroll_to_next_page()

if __name__ == '__main__':
    main()
