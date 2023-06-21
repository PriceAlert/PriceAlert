from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
browser = webdriver.Chrome(ChromeDriverManager().install())
# url='https://www.amazon.in/Samsung-Storage-Battery-Octa-Core-Processor/dp/B0BZCR6TNK/ref=sr_1_1_sspa?crid=2DT5CJFGDVIZQ&keywords=smartphone&qid=1687021709&sprefix=smartphon%2Caps%2C396&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1'
url='https://www.amazon.in/TOZO-T6-Bluetooth-Headphones-Waterproof/dp/B0BVHPKZLR/ref=sr_1_1_sspa?crid=NH24CX5FF7I5&keywords=headphones&qid=1687023843&sprefix=headphon%2Caps%2C293&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1'
browser.get(url)
browser.maximize_window()
item_og_price = browser.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[2]/span/span[1]/span/span/span[2]')
print(item_og_price.text)
# 


