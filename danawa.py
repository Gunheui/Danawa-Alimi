from selenium import webdriver
import time
import smtplib
from email.mime.text import MIMEText
from google.cloud import vision
import io


dir = './chromedriver'


#상품 검색 및 그래프 가격 추출
def Search(Product):
    driver.find_element_by_xpath('//*[@id="AKCSearch"]').clear()
    driver.find_element_by_xpath('//*[@id="AKCSearch"]').send_keys(Product)
    driver.find_element_by_xpath('//*[@id="srchFRM_TOP"]/fieldset/div[1]/button').click()
    driver.implicitly_wait(5)
    count = 1
    try:
        while(1):
            try:
                title = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[3]/div[2]/div[8]/div[2]/div[2]/div[3]/ul/li['+ str(count) +']/div/div[2]/p/a').text
            except:
                title = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[3]/div[2]/div[9]/div[2]/div[2]/div[3]/ul/li['+ str(count) +']/div/div[2]/p/a').text
            if (Product in title.lower()):
                try:
                    driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[3]/div[2]/div[8]/div[2]/div[2]/div[3]/ul/li['+ str(count) +']/div/div[2]/p/a').click()
                except:
                    driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[3]/div[2]/div[9]/div[2]/div[2]/div[3]/ul/li['+ str(count) +']/div/div[2]/p/a').click()
                driver.implicitly_wait(5)
                break
            count += 1
    except:
        try:
            driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[3]/div[2]/div[8]/div[2]/div[2]/div[3]/ul/li[1]/div/div[2]/p/a').click()
        except:
            driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[3]/div[2]/div[9]/div[2]/div[2]/div[3]/ul/li['+ str(count) +']/div/div[2]/p/a').click()
    tabs = driver.window_handles
    driver.switch_to_window(tabs[1])
    driver.find_element_by_xpath('//*[@id="graphAreaSmall"]/canvas[7]').screenshot(Product + '.png')

#최저가 그래프 가격 추출
def detect_text(path):
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    res = ""
    for text in texts:
        res = str(text.description)
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return int(res.replace(',',""))
#현재 다나와 최저가
def CurrLowPrice():
    LowPrice = 0
    try:
        LowPrice = int(driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/span[2]/a/em').text.replace(',',""))
    except:
        try:
            LowPrice = int(driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/span[2]/a/em').text.replace(',',""))
        except:
            try:
                LowPrice = int(driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div/span[2]/a/em').text.replace(',',""))
            except:
                print("해당 상품이 현재 품절입니다.")
                LowPrice = 99999
    return LowPrice

#가격 비교
def CalcPrice(LowPrice,CurrLowPrice):
    state = 0
    if (LowPrice > CurrLowPrice):
        print("역대 최저가!")
        state = 1
    elif(LowPrice == CurrLowPrice):
        print("최저가!")
        state = 2
    else:
        print("아직은 비쌉니다.")
    return state

#메일 보내기
def SendMail(Product,state,UserMail):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()     
    smtp.starttls() 
    smtp.login('ID', 'Password')
    Product_state = ""
    if state == 1:
        Product_state = "역대 최저가"
    elif state == 2:
        Product_state = "최저가"
    msg = MIMEText("어서 상품을 구매하러 가볼까요? \n" + driver.current_url)
    msg['Subject'] = Product + '가 현재 ' + Product_state + "입니다!"
    msg['To'] = UserMail
    smtp.sendmail('Email', UserMail, msg.as_string())
    smtp.quit()

#메인
if __name__ == "__main__":
    Product = input("제품이름을 입력해주세요 : ")
    UserMail = input("이메일주소를 입력해주세요 : ")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.maximize_window()
    driver.get("http://www.danawa.com/")
    Search(Product)
    # print(type(detect_text(Product + ".png")))
    LowPrice = detect_text(Product + ".png")
    while(1):
        curr_lowPrice = CurrLowPrice()
        state = CalcPrice(LowPrice,curr_lowPrice)
        if state == 0:
            time.sleep(300)
            driver.refresh()
            driver.implicitly_wait(10)
            continue
        SendMail(Product,state,UserMail)
        print("메일을 성공적으로 보냈습니다. 프로그램을 종료합니다.")
        break
    



 
