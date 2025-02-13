from flask import Flask, jsonify, request, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import threading
import time
import os
import logging
from db import authenticate_user  

load_dotenv()

app = Flask(__name__)

app.config.update({
    'HOST': os.getenv("HOST", "127.0.0.1"),  
    'PORT': int(os.getenv("PORT", 5000)),    
    'URL': os.getenv("URL"),
    'DEBUG_MODE': os.getenv("DEBUG_MODE", "False").lower() == "true",
    'SECRET_KEY': os.getenv("SECRET_KEY")  
})

app.secret_key = app.config["SECRET_KEY"]

options = webdriver.FirefoxOptions()
options.add_argument("--headless")  
driver = webdriver.Firefox(options=options)

currentOtp = ""
sameOtpCount = 0

def get_status(count):
    if count >= 3:
        return "danger"
    elif count == 2:
        return "alert"
    elif count == 1:
        return "warning"
    return "safe"

def fetch_otp():
    global currentOtp, sameOtpCount
    while True:
        try:
            driver.get(app.config["URL"])
            td_elements = driver.find_elements(By.TAG_NAME, "td")

            if len(td_elements) >= 2:
                newOtp = td_elements[1].text  

                if newOtp == currentOtp:
                    sameOtpCount += 1  
                else:
                    sameOtpCount = 0  
                    currentOtp = newOtp  

                logging.info(f"Fetched OTP: {newOtp} | Status: {get_status(sameOtpCount)}")
            else:
                sameOtpCount = 3  
                logging.warning("td elements not found! Status set to danger.")

        except Exception as e:
            logging.error(f"Error: {str(e)}")

        time.sleep(5)

threading.Thread(target=fetch_otp, daemon=True).start()

@app.before_request
def authenticate():
    if request.path in ["/", "/login", "/register"]:  
        return  
    
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized, please log in"}), 401

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if authenticate_user(username, password):
        session["logged_in"] = True
        return jsonify({"message": "Login successful"})
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("logged_in", None)
    return jsonify({"message": "Logged out successfully"})

# @app.route("/register", methods=["POST"])
# def register():
#     from db import add_user  
#     data = request.get_json()
#     username = data.get("username")
#     password = data.get("password")

#     if add_user(username, password):
#         return jsonify({"message": "User registered successfully"})
    
#     return jsonify({"error": "User already exists"}), 400

@app.route("/otp", methods=["GET"])
def get_otp():
    return jsonify({
        "otp": currentOtp,
        "sameOtpCount": sameOtpCount,
        "status": get_status(sameOtpCount)
    })

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG_MODE"])
