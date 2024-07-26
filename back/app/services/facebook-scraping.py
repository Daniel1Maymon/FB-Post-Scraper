from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time, random, json, pickle, os, traceback
from dotenv import load_dotenv
from send_email_with_gmail import send_email

load_dotenv()  # Load environment variables from .env file


file_path = 'facebook_post_links.json'

unwanted_phrases = ['שותף',
                    'שותפ',
                    'מתפנה חדר'
                    'רמת גן',
                    'רמת-גן'
                    'ר"ג',
                    'סטודיו',
                    '2 חד',
                    '4 חד',
                    '5 חד',
                    '6 חד',
                    'גלריה',
                    'ללא מקלט',
                    'אין מקלט',
                    'ללא בע',
                    'אסור בע',
                    'סאבלט'
                    ]

groups = [
            [
                'דירות להשכרה בגבעתיים',
                'https://www.facebook.com/groups/1380680752778760/?sorting_setting=CHRONOLOGICAL'
            ],
            [
               'דירות ברמת גן - גבעתיים להשכרה בעוד חודש +',
                'https://www.facebook.com/groups/1068642559922565/?sorting_setting=CHRONOLOGICAL'
            ],
            [
              'דירות להשכרה רמת גן/גבעתיים במחיר שפוי',
              'https://www.facebook.com/groups/647901439404148/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות להשכרה רמת גן גבעתיים',
                'https://www.facebook.com/groups/1870209196564360/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות להשכרה גבעתיים - רמת גן',
                'https://www.facebook.com/groups/186810449287215/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות להשכרה בגבעתיים ר"ג ותל אביב',
                'https://www.facebook.com/groups/2098391913533248/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות להשכרה בלבד! | גבעתיים בלבד | ללא תיווך.',
                'https://www.facebook.com/groups/1998122560446744/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות בשושו רמת גן/גבעתיים-אין כניסה למתווכים -פרסום דירות ושותפים בלבד!!!!',
                'https://www.facebook.com/groups/1424244737803677/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות להשכרה בגבעתיים',
                'https://www.facebook.com/groups/1380680752778760/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות ללא תיווך להשכרה בגבעתיים ורמת גן שותפים זוגות ויחידים',    
                'https://www.facebook.com/groups/654949551249110/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות להשכרה בגבעתיים',
                'https://www.facebook.com/groups/564985183576779/?sorting_setting=CHRONOLOGICAL'
            ],
            [
                'דירות ללא תיווך להשכרה ברמת גן גבעתיים',
                'https://www.facebook.com/groups/520940308003364/?sorting_setting=CHRONOLOGICAL'
            ]
]

# Function to create a randomized user agent
def get_random_user_agent():
    ua = UserAgent()
    return ua.random

def setup_browser():
    options = webdriver.FirefoxOptions()
    # options = webdriver.ChromeOptions()
    # Uncomment the next line to run in headless mode
    # options.add_argument("--headless")
    
    user_agent = get_random_user_agent()
    # print(f"ua = {user_agent}")
    
    options.set_preference("general.useragent.override", user_agent)
    
    # Optional: Add other preferences to make the browser appear more human
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    options.set_preference("general.platform.override", "")
    
    # Set up proxy if you have one
    # proxy = "your_proxy_address:port"
    # options.add_argument(f'--proxy-server={proxy}')
    
    # Create the browser instance
    browser = webdriver.Firefox(options=options)
    # browser = webdriver.Chrome(options=options)
    
    return browser

def read_links():
    data = []
    
    try:
        # check if file exists
        file_exists = os.path.isfile(file_path)
        
        if file_exists:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
        pass
    
    except Exception as e:
        print(f"Error handling JSON file {file_path}: {e}")    
        
    return data if data else []
    
    
def write_links(links):
    data = []
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False)
            print("URLs has been written into data file")
            
    except Exception as e:
        print(f"Error handling JSON file {file_path}: {e}")    
        

def get_href_from_element(element):
    hrefs = []
    # Find all anchor tags within the element
    anchor_tags = element.find_elements(By.TAG_NAME, 'a')
    for anchor in anchor_tags:
        href = anchor.get_attribute('href')
        if href and 'posts/' in href:
            # Cleaning the url
            href = href.split('/?')[0]
            return href
    return ""
    #         hrefs.append(href)
    # return hrefs[0] if href else "None"


def check_if_link_exists(links, href):
    for link in links:
        if 'posts' + href.split('/posts')[1] in link:
            return True
    return False
    # return 'posts' + href.split('/posts')[1] in links

def post_contain_unnecessary_phrases(post):
    for phrase in unwanted_phrases:
        if phrase in post:
            return True
        
    return False

def process_page(group_name, group_link, browser, attemps=5):
    try:
        print(":: Group name: ")
        print(group_name)
        data = {}
        
        # Login to faceook:
        
        
        # Open the target URL
        browser.get(group_link) 

        
        time.sleep(random.uniform(2, 5))
        # Wait for the specific <ul> element to be present
        element_list = WebDriverWait(driver=browser, timeout=15).until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, 'screen-root')),
                EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
            )
        )
    
        # from bs4 import BeautifulSoup
        # page_source = browser.page_source
        # soup = BeautifulSoup(page_source, 'html.parser')
        # container = soup.find(name='div', attrs={'data-type': 'container'})

        posts = element_list.find_elements(By.XPATH, "//div[@role='article']")
        
        if not posts and attemps > 0:
            browser.refresh()
            process_page(group_name, group_link, browser, attemps-1)
            
        else:
        
            # Filter elements that have a child with data-ad-preview="message"
            filtered_elements = [element for element in posts if element.find_elements(By.XPATH, ".//*[@data-ad-preview='message']")]

            links = []
            links = read_links()
            
            links.append(group_name)
            
            print(":: Save links in local storage ::")
            for element in filtered_elements:
                print(element.text)
                print("--------------------")
                # Adding only links that are not in already save in the links file
                href = get_href_from_element(element)
                if (not post_contain_unnecessary_phrases(element.text)) and (not check_if_link_exists(links, href)):
                    links.append(href)
                # links.append(get_href_from_element(element))
            
            links.append("-------------------------------------------")
                
            # Write group name    
            write_links(group_name)
            
            # Write links to a file
            write_links(links)

            pass


    except TimeoutException:
        print("Timeout occurred while waiting for the element.")
    except NoSuchElementException:
        print("The element was not found in the DOM.")
    except Exception as e:
        print(f"An error occurred: {e}")

def make_login_and_save_cookies(browser, attemps=10):
    
    # Navigate to the Facebook login page
    browser.get('https://www.facebook.com/')
    time.sleep(random.uniform(2, 5))
    
    '''
    1. Wait for the Facebook logo element
    2. Save the body element
    3. Extract Email and Password elements
    4. Click the login button
    5. Save the coockies for the next enteries.
    '''
    
    # Wait for the Facebook logo element
    # try:
    #     logo_image = WebDriverWait(browser, 30).until(
    #         EC.presence_of_element_located((By.XPATH, '//img[@alt="Facebook from Meta"]'))
    #     )
    #     print("Facebook logo image found.")
    # except Exception as e:
    #     print(f"Error while waiting for the image: {e}")
    #     return  # Exit if the logo is not found
    
    # Save the body element
    body = browser.find_element(By.TAG_NAME, 'body')
    
    # Extract Email and Password elements
    email_and_pass_elements = body.find_elements(By.XPATH, "//input[@type='email' or @name='email' or @type='password' or @type='pass']")
    
    username_input = [element for element in email_and_pass_elements if 'email' in  element.accessible_name.lower()][0]
    
    password_input = [element for element in email_and_pass_elements if 'pass' in  element.accessible_name.lower()][0]
    
    # Search for the login button
    login_button_elements = body.find_elements(By.XPATH, "//button[@name='login']")
    
    # if len(login_button_elements) < 1 and attemps > 0:
    #     print(f"len(login_button_elements) = {len(login_button_elements)} < 1")
    #     browser.quit()
    #     time.sleep(random.uniform(2, 5))
    #     # browser.refresh()
    #     browser = setup_browser()
    #     make_login_and_save_cookies(browser, attemps=attemps - 1)
    #     return
    
    if not (password_input or email_and_pass_elements or len(login_button_elements)):
        raise Exception("One of the email, password or login element is missing")
    
    # The login button was founded:
    login_button = login_button_elements[0]
    
    print(":: username_input.send_keys ::")
    facebook_username = os.getenv('FACEBOOK_USERNAME')
    facebook_password = os.getenv('FACEBOOK_PASSWORD')
    
    username_input.send_keys(facebook_username)
    password_input.send_keys(facebook_password)


    time.sleep(random.uniform(5, 6))
    print(":: START :: login_button.click() ::")
    login_button.click()
    print(":: END :: login_button.click() ::")
    time.sleep(random.uniform(2, 5))
            
    print(":: START :: pickle.dump() ::")
    pickle.dump(browser.get_cookies(), open(file="cookies.pkl", mode="wb"))
    print(":: END :: pickle.dump() ::")
    
  
    return

def scraping_posts_from_groups(group_name, group_link, browser, attempts=5):
    process_page(group_name, group_link, browser)

    # Check if CAPTCHA is present, if so change the 'UserAgent'
    # if is_captcha_present(browser):
    #     print("CAPTCHA detected, reloading page...")
    #     time.sleep(random.uniform(1, 5))
    #     browser.quit()
    #     scrape_yad2(attempts - 1)  # Decrement the attempts
    # else:
    #     print("Processing complete, no CAPTCHA detected.")
        


def load_cookies(browser):
    cookies = pickle.load(open(file="cookies.pkl", mode="rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)

def send_posts_to_email():
    posts = read_links()
    
    subject = 'קישורים לדירות מפייסבוק'
    body = posts
    sender = "daniel1maymon@gmail.com"
    recipients = ["daniel1maymon@gmail.com", ]
    password = os.getenv('GMAIL_PASSWORD')
    
    if posts:
        send_email(subject, body, sender=sender, recipients=recipients, password=password)

def main(attempts=10):
    print("::: main :::")
    '''
    1. Login once: Perform the login action and save the cookies.

    2. Reuse cookies and scrap data from facebook grupes: For subsequent visits to pages where you want to remain logged in, load the saved cookies into your Firefox browser session.
    '''

    print("::: setup_browser :::")
    browser = setup_browser()
    try:
        print("::: START :: make_login_and_save_cookies :::")
        make_login_and_save_cookies(browser)
        print("::: END :: make_login_and_save_cookies :::")
        
        print("::: START :: load_cookies :::")
        load_cookies(browser)
        print("::: END :: load_cookies :::")
        
        print(":::  scraping_posts_from_groups :::")
        
        for group in groups:
            print(f"group = |{group}|")
            print(":: START :: scraping_posts_from_groups()")
            scraping_posts_from_groups(group_name=group[0], group_link=group[1], browser=browser)
            print(":: END :: scraping_posts_from_groups()")
            
        send_posts_to_email()
        pass

    except Exception as e:
        traceback.print_exc()  # Print the stack trace for the last error
        print(f"Error <description>: {e}")
        if attempts > 0:
            print(f"Number of attemps = {attempts}")
            browser.quit()
            main(attempts=10)
        
    finally:
        browser.quit()

if __name__ == "__main__":
    main()
    

    