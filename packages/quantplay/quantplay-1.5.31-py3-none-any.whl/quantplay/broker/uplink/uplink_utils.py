import binascii
import time
import traceback

import pyotp
import requests
from retrying import retry
from selenium.common.exceptions import WebDriverException

from quantplay.exception.exceptions import (
    InvalidArgumentException,
    RetryableException,
    retry_exception,
)
from quantplay.utils.selenium_utils import Selenium


class UplinkUtils:
    auth_url = "https://api.upstox.com/v2/login/authorization/"

    mobile_xpath = '//*[@id="mobileNum"]'
    password_xpath = '//*[@id="container"]/div/div/div[2]/form/div[2]/input'
    get_otp_xpath = '//*[@id="getOtp"]'
    totp_xpath = '//*[@id="otpNum"]'
    continue_xpath = '//*[@id="continueBtn"]'

    @staticmethod
    def check_error(page_source):
        for error_message in [
            "Invalid username or password",
            "Invalid TOTP",
        ]:
            if error_message in page_source:
                raise InvalidArgumentException(error_message)

        if "Check your" in page_source and "one or both are incorrect" in page_source:
            raise InvalidArgumentException(
                f"Check your client_id and redirect_uri; one or both are incorrect"
            )

    @staticmethod
    def generate_access_token(code, api_key, api_secret, redirect_url):
        url = "https://api.upstox.com/v2/login/authorization/token"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "code": code,
            "client_id": api_key,
            "client_secret": api_secret,
            "redirect_uri": redirect_url,
            "grant_type": "authorization_code",
        }

        response = requests.post(url, headers=headers, data=data)
        json_response = response.json()
        return json_response

    @staticmethod
    def get_request_token(
        api_key,
        redirect_url,
        totp_key,
        mobile_number,
        account_pin,
    ):
        try:
            driver = Selenium().get_browser()

            # TODO api should be fetched from configuration
            time.sleep(2)
            url = f"{UplinkUtils.auth_url}dialog?response_type=code&client_id={api_key}&redirect_uri={redirect_url}"
            print("Upstox Url {}".format(url))

            driver.get(url)
            time.sleep(1)
            page_source = driver.page_source
            UplinkUtils.check_error(page_source)

            mobile_element = driver.find_element("xpath", UplinkUtils.mobile_xpath)
            mobile_element.send_keys(mobile_number)
            time.sleep(1)
            get_otp_element = driver.find_element("xpath", UplinkUtils.get_otp_xpath)
            get_otp_element.submit()
            time.sleep(1)

            totp_element = driver.find_element("xpath", UplinkUtils.totp_xpath)
            totp_now = pyotp.TOTP(totp_key).now()
            totp_element.send_keys(totp_now)
            time.sleep(1)

            continue_element = driver.find_element("xpath", UplinkUtils.continue_xpath)
            continue_element.submit()
            time.sleep(1)

            pin_element = driver.find_element("xpath", '//*[@id="pinCode"]')
            pin_element.send_keys(account_pin)
            time.sleep(1)

            continue_element = driver.find_element("xpath", '//*[@id="pinContinueBtn"]')
            continue_element.submit()
            time.sleep(1)

            url = driver.current_url
            print("got upstox url {}".format(url))
            request_token = url.split("code=")[1].split("&")[0]

            driver.close()

            return request_token
        except binascii.Error as e:
            raise InvalidArgumentException("Invalid TOTP key provided")
        except InvalidArgumentException as e:
            raise
        except WebDriverException as e:
            raise RetryableException("Selenium setup need to be fixed")
        except Exception as e:
            print(traceback.print_exc())
            raise RetryableException(str(e))
