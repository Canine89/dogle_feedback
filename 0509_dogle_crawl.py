# 25개구 for문으로 돌려서 카페 정보 크롤링하기

# 문제1. 1페이지 건너뜀 - 키워드 2개 붙였을 시 검색량 부족으로 추정
# issue 1 - 검색량이 특정 개수 이하여서 [장소 더 보기] 누르면 2페이지로 넘어갈 때 -
# issue 2 - 검색량이 1페이지에도 안 들어가서 페이징이 안 될 때 - first has next 수정

import os
from time import sleep
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


def read_page(driver):
    place_lists = driver.find_elements_by_css_selector(
        '#info\.search\.place\.list > li')
    for p in place_lists:  # WebElement
        # print(p.get_attribute('innerHTML'))
        # print("type of p:", type(p))
        store_html = p.get_attribute('innerHTML')
        store_info = BeautifulSoup(store_html, "html.parser")
        # BS -> 분석
        #
        place_name = store_info.select(
            '.head_item > .tit_name > .link_name')
        if len(place_name) == 0:
            continue  # 광고
        place_name = store_info.select(
            '.head_item > .tit_name > .link_name')[0].text
        place_address = store_info.select(
            '.info_item > .addr > p')[0].text
        place_hour = store_info.select(
            '.info_item > .openhour > p > a')[0].text
        place_tel = store_info.select(
            '.info_item > .contact > span')[0].text

        # 사진url 수집
        detail = p.find_element_by_css_selector(
            'div.info_item > div.contact > a.moreview')
        detail.send_keys(Keys.ENTER)

        driver.switch_to.window(driver.window_handles[-1])

        place_photo = ""
        try:
            photo = driver.find_element_by_css_selector(
                'span.bg_present')
            photo_url = photo.get_attribute('style')
            m = re.search('"(.+?)"', photo_url)
            if m:
                place_photo = m.group(1)
            else:
                place_photo = ""
        except:
            place_photo = ""

        try:
            place_hp = driver.find_element_by_css_selector(
                'div.location_present > a.link_homepage').text
        except:
            place_hp = ""

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print(place_name, place_hp)

        file.write(place_name + "|" + place_address + "|" +
                   place_hour + "|" + place_tel + "|" + place_photo + "|" + place_hp + "\n")


##########################################################################
##################### variable related selenium ##########################
##########################################################################
# 검색어 리스트
key_list = ['반려견놀이터', '애견카페', '동물병원', '반려견동반']
area_list = ['서울', '인천', '대구', '부산', '대전', '파주', '일산']
gu_list = ['반려견놀이터']


# csv 파일에 헤더 만들어 주기
for index, gu_name in enumerate(gu_list):
    fileName = 'test.csv'  # index.__str__() + '_' + gu_name + '.'+'csv'
    file = open(fileName, 'w', encoding='utf-8')
    file.write("카페명" + "|" + "주소" + "|" + "영업시간" +
               "|" + "전화번호" + "|" + "대표사진주소" + "|" + "홈페이지" + "\n")
    file.close()                                    # 처음에 csv파일에 칼럼명 만들어주기

    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36   ")
    options.add_argument('lang=ko_KR')
    chromedriver_path = "/usr/local/bin/chromedriver"
    driver = webdriver.Chrome(os.path.join(
        os.getcwd(), chromedriver_path), options=options)  # chromedriver 열기
    driver.get('https://map.kakao.com/')  # 주소 가져오기
    search_area = driver.find_element_by_xpath(
        '//*[@id="search.keyword.query"]')  # 검색 창
    search_area.send_keys("서울 카페")  # 검색어 입력
    driver.find_element_by_xpath(
        '//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)  # Enter로 검색
    driver.implicitly_wait(3)  # 기다려 주자

    # more 버튼이 있는 경우에만 more_page 버튼 누르기
    items = driver.find_elements_by_css_selector(
        "#info\.search\.place\.list .PlaceItem")

    print("cnt", len(items))
    if len(items) <= 11:
        has_more = False
    else:
        has_more = True
        more_page = driver.find_element_by_id("info.search.place.more")
        more_page.send_keys(Keys.ENTER)  # 더보기 누르고
        # driver.implicitly_wait(5) # 기다려 주자
        time.sleep(1)

    if not has_more:
        file = open(fileName, 'a', encoding='utf-8')
        time.sleep(1)

        read_page(driver)

        print('Arrow is Disabled')
        driver.close()
        file.close()

    # next 사용 가능?
    next_btn = driver.find_element_by_id("info.search.page.next")
    has_next = "disabled" not in next_btn.get_attribute("class").split(" ")
    Page = 1

    while has_next and has_more:  # 다음 페이지가 있으면 loop
        # for i in range(2, 6): # 2, 3, 4, 5
        file = open(fileName, 'a', encoding='utf-8')
        time.sleep(1)

        # place_lists = driver.find_elements_by_css_selector('#info\.search\.place\.list > li:nth-child(1)')
        # 페이지 루프
        # info\.search\.page\.no1 ~ .no5
        page_links = driver.find_elements_by_css_selector(
            "#info\.search\.page a")
        pages = [link for link in page_links if "HIDDEN" not in link.get_attribute(
            "class").split(" ")]
        # print(len(pages), "개의 페이지 있음")
        # pages를 하나씩 클릭하면서
        for i in range(1, 6):
            xPath = '//*[@id="info.search.page.no' + str(i) + '"]'
            try:
                page = driver.find_element_by_xpath(xPath)
                page.send_keys(Keys.ENTER)
            except ElementNotInteractableException:
                print('End of Page')
                break
            sleep(3)

            read_page(driver)

            print(i, ' of', ' [ ', Page, ' ] ')
        next_btn = driver.find_element_by_id("info.search.page.next")
        has_next = "disabled" not in next_btn.get_attribute("class").split(" ")

        if not has_next:
            print('Arrow is Disabled')
            driver.close()
            file.close()
            break  # 다음 페이지 없으니까 종료
        else:  # 다음 페이지 있으면
            Page += 1
            next_btn.send_keys(Keys.ENTER)
    print("End of Crawl")
