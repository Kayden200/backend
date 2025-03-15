from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = FastAPI()

class LoginRequest(BaseModel):
    email: str
    password: str

class BoostRequest(BaseModel):
    post_link: str
    reaction_type: str

# Store session cookies
SESSION_COOKIES = {}

@app.post("/login")
def login_facebook(data: LoginRequest):
    email, password = data.email, data.password

    try:
        options = uc.ChromeOptions()
        options.headless = True  # Run in headless mode
        driver = uc.Chrome(options=options)

        driver.get("https://m.facebook.com/")
        time.sleep(2)

        # Enter email
        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys(email)

        # Enter password
        password_input = driver.find_element(By.NAME, "pass")
        password_input.send_keys(password + Keys.RETURN)

        time.sleep(5)

        # Check if login was successful
        if "save-device" in driver.current_url:
            session_cookies = driver.get_cookies()
            SESSION_COOKIES[email] = session_cookies
            driver.quit()
            return {"message": "Login successful", "email": email}

        driver.quit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    except Exception as e:
        return {"error": str(e)}

@app.post("/boost")
def boost_reaction(data: BoostRequest, email: str = Form(...)):
    post_link, reaction_type = data.post_link, data.reaction_type

    if email not in SESSION_COOKIES:
        raise HTTPException(status_code=401, detail="Not logged in")

    try:
        options = uc.ChromeOptions()
        options.headless = True
        driver = uc.Chrome(options=options)

        driver.get(post_link)
        time.sleep(3)

        # Click the reaction button
        reaction_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, 'reaction')]")
        for button in reaction_buttons:
            if reaction_type.lower() in button.get_attribute("href"):
                button.click()
                break

        time.sleep(2)
        driver.quit()

        return {"message": f"Boosted with {reaction_type}", "post_link": post_link}

    except Exception as e:
        return {"error": str(e)}
