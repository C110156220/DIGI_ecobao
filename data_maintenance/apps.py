from django.apps import AppConfig
# from models import *

class DataMaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_maintenance'

class getPreivewonGoogle():
    def search_and_scrape_reviews(self,query):
        from selenium import webdriver
        import time
        from selenium.webdriver.common.keys import Keys

        # 初始化瀏覽器
        driver = webdriver.Chrome()

        # 打開Google Maps網站
        driver.get("https://www.google.com/maps")

        # 定位搜尋欄位並輸入搜尋內容
        search_box = driver.find_element_by_name("q")
        search_box.send_keys(query)
        search_box.submit()

        # 等待一些時間以讓結果載入
        driver.implicitly_wait(10)

        # 在這裡可以模擬點擊地點、抓取評論等操作
        # 等待一些時間以讓結果載入
        time.sleep(5)

        # 在搜索結果中點擊第一個結果（你可以根據需要修改）
        result = driver.find_element_by_css_selector("h3[data-result-index='0'] a")
        result.click()

        # 等待一些時間以讓評論載入
        time.sleep(5)

        # 擷取評論
        reviews = []
        review_elements = driver.find_elements_by_css_selector("span.section-review-text")
        for review_element in review_elements:
            reviews.append(review_element.text)

        # 顯示評論
        for i, review in enumerate(reviews):
            print(f"Review {i + 1}: {review}")
        # 關閉瀏覽器
        driver.quit()


if __name__ == "__main__":
    ob = getPreivewonGoogle()
    ob.search_and_scrape_reviews('趙家南部肉粽')