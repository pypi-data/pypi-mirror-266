import random
from temp_email_automa.main import TempMail, Email
import requests
from PIL import Image
import re
import time
import datetime
from uuid import uuid4
from typing import Optional, List
import base64


class PixlrApi:
    def __init__(self):
        self.temp_mail = TempMail()
        self.bearer_token: Optional[str] = None
        self._phosus_auth_token: Optional[str] = None

    def register(self) -> bool:
        self.temp_mail.generate_random_email_address()
        email = self.temp_mail.email
        self.email = email
        password = email

        cookies = {
            "country": "US",
            "lang": "en-US",
        }

        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://pixlr.com",
            "referer": "https://pixlr.com/",
            "sec-ch-ua": '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }

        json_data = {
            "email": email,
            "password": password,
            "newsletter": random.choice([True, False]),
            "country": "US",
        }

        response = requests.post(
            "https://pixlr.com/auth/register",
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        # {"status":true,"message":"Registration success; Check your inbox for verification email!"}
        if response.status_code != 200:
            print(f"PixlrApi().register(): Something Went Wrong! {response.text}")
            return False

        response_json = response.json()
        if response_json["status"] is True:
            print(f"PixlrApi().register(): Sucessfully Registered! {response.text}")
            return True

        print(f"PixlrApi().register(): Something Went Wrong! {response_json}")
        return False

    def verify_email(self) -> bool:
        email: Optional[Email] = None
        max_iter = 50
        for _ in range(max_iter):
            time.sleep(1)
            emails = self.temp_mail.get_list_of_emails()
            if emails:
                email = self.temp_mail.get_single_email(emails[0]["id"])
                break

        if not email:
            print(
                "PixlrApi().verify_email(): No Email Found! TODO: Improve On The error Handeling Here!"
            )
            exit(1)
        code = re.search(r"\d{6}", email.body)
        if not code:
            print(
                "PixlrApi().verify_email(): No 6 Digit Code Found In The Email! TODO: Improve On The error Handeling Here!",
                email,
            )
            exit(1)

        print(f"PixlrApi().verify_email() code: {code.group()}")

        cookies = {
            "country": "US",
            "lang": "en-US",
        }

        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://pixlr.com",
            "referer": "https://pixlr.com/",
            "sec-ch-ua": '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }

        json_data = {"email": self.email, "code": code.group()}

        response = requests.post(
            "https://pixlr.com/auth/verify",
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        if response.status_code != 200:
            print(f"PixlrApi().verify_email(): Something Went Wrong! {response.text}")
            return False

        response_json = response.json()
        # {"status":true,"accessToken":"<TOKEN>","refreshToken":"<TOKEN>","message":"Your account has been successfully verified!"}

        if response_json["status"] is True:
            self.bearer_token = response_json["accessToken"]
            print(
                f"PixlrApi().verify_email(): Sucessfully Verified! {self.bearer_token}"
            )
            return True

        print(f"PixlrApi().verify_email(): Something Went Wrong! {response_json}")
        return False

    def generate_image(
        self, width: int, height: int, amount: int, prompt: str
    ) -> List[str]:
        cookies = {
            "country": "",
            "lang": "en-US",
            "__pat": self.bearer_token,
        }

        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://pixlr.com",
            "referer": "https://pixlr.com/image-generator/",
            "sec-ch-ua": '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }

        json_data = {
            "amount": amount,
            "width": width,
            "height": height,
            "prompt": prompt,
            "personal": True,
        }

        response = requests.post(
            "https://pixlr.com/api/openai/generate",
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        if response.status_code != 200:
            print(f"PixlrApi().generate_image(): Something Went Wrong! {response.text}")
            return []

        response_json = response.json()
        image_paths = []
        if response_json["status"] is True:
            print(
                f"PixlrApi().generate_image(): Sucessfully Generated! {len(response_json['data']['images'])} Images!"
            )
            for image in response_json["data"]["images"]:
                image_base64 = image["image"]
                image_base64 = image_base64.split(",")[1]
                image_data = base64.b64decode(image_base64)
                image_path = f"/tmp/{image['id']}.png"
                with open(image_path, "wb") as file:
                    file.write(image_data)
                image_paths.append(image_path)

        return image_paths

    def delete_account(self):
        cookies = {
            "country": "US",
            "lang": "en-US",
            "__pat": self.bearer_token,
        }

        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en;q=0.9",
            "authorization": f"Bearer {self.bearer_token}",
            "content-type": "application/json",
            "origin": "https://pixlr.com",
            "referer": "https://pixlr.com/myaccount/",
            "sec-ch-ua": '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }

        json_data = {
            "reason": f"leavingReasons{random.choice([0,1,2,3])}",
        }

        response = requests.delete(
            "https://pixlr.com/api/myaccount/profile",
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        if response.status_code != 200:
            print(f"PixlrApi().delete_account(): Something Went Wrong! {response.text}")
            return False

        response_json = response.json()
        if response_json["status"] is True:
            print(f"PixlrApi().delete_account(): Sucessfully Deleted! {response.text}")
            return True

        print(f"PixlrApi().delete_account(): Something Went Wrong! {response_json}")
        return False

    def _generate_phosus_auth_token(self) -> Optional[str]:
        cookies = {
            "country": "ZA",
            "lang": "en-US",
            "has-history": "true",
        }

        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en;q=0.9",
            "referer": "https://pixlr.com/express/",
            "sec-ch-ua": '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        }

        response = requests.get(
            "https://pixlr.com/api/auth/ai/remove-background/",
            cookies=cookies,
            headers=headers,
        )

        response_json = response.json()
        if response.status_code != 200 or response_json["status"] is False:
            print(
                f"PixlrApi()._generate_phosus_auth_token(): Something Went Wrong! {response.text}"
            )
            return None

        self._phosus_auth_token = response_json["data"]
        return self._phosus_auth_token

    def _path_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as file:
            image_data = file.read()

        image_base64 = base64.b64encode(image_data)
        # Convert to a string
        image_base64_str = image_base64.decode("utf-8")
        return image_base64_str

    def _base64_to_bytes(self, image_base64: str) -> bytes:
        return base64.b64decode(image_base64)

    def remove_background(self, image_path: str) -> Optional[str]:
        if not self._phosus_auth_token:
            self._generate_phosus_auth_token()

        url = "https://ai.phosus.com/bgremove/v1"
        headers = {"Authorizationtoken": f"{self._phosus_auth_token}"}
        image_base64 = self._path_to_base64(image_path)
        body = {"image_b64": image_base64}

        response = requests.post(url, headers=headers, json=body)

        response_json = response.json()
        if response.status_code != 200 or response_json["ok"] is False:
            print(
                f"PixlrApi().remove_background(): Something Went Wrong! {response.text}"
            )
            return None

        image_base64 = response_json["results"]["mask"]
        image_data = self._base64_to_bytes(image_base64)
        image_path_mask = f"/tmp/{uuid4().hex}.png"
        with open(image_path_mask, "wb") as file:
            file.write(image_data)

        print("PixlrApi().remove_background(): Mask Image Saved!")
        no_bkacground_image = f"/tmp/nbi{uuid4().hex}.png"

        background = Image.open(image_path).convert("RGBA")
        mask = Image.open(image_path_mask).convert("L")
        background.putalpha(mask)
        with open(no_bkacground_image, "wb") as file:
            background.save(file, "PNG")
            print("PixlrApi().remove_background(): Background Image Saved!")

        return no_bkacground_image

    def auto_fix(self, image_path: str) -> Optional[str]:
        if not self._phosus_auth_token:
            self._generate_phosus_auth_token()

        url = "https://ai.phosus.com/autofix/v1"
        headers = {"Authorizationtoken": f"{self._phosus_auth_token}"}
        image_base64 = self._path_to_base64(image_path)
        body = {"image_b64": image_base64}

        response = requests.post(url, headers=headers, json=body)
        response_json = response.json()
        if response.status_code != 200 or response_json["ok"] is False:
            print(f"PixlrApi().auto_fix(): Something Went Wrong! {response.text}")
            return None

        image_base64 = response_json["results"]["output"]
        image_data = self._base64_to_bytes(image_base64)
        image_path_auto_fix = f"/tmp/{uuid4().hex}.png"
        with open(image_path_auto_fix, "wb") as file:
            file.write(image_data)

        print("PixlrApi().auto_fix(): Auto Fix Image Saved!")
        return image_path_auto_fix

    def lowlight_enhance(self, image_path: str) -> Optional[str]:
        if not self._phosus_auth_token:
            self._generate_phosus_auth_token()

        url = "https://ai.phosus.com/lowlight/v1"
        headers = {"Authorizationtoken": f"{self._phosus_auth_token}"}
        image_base64 = self._path_to_base64(image_path)
        body = {"image_b64": image_base64}

        response = requests.post(url, headers=headers, json=body)
        response_json = response.json()
        if response.status_code != 200 or response_json["ok"] is False:
            print(
                f"PixlrApi().lowlight_enhance(): Something Went Wrong! {response.text}"
            )
            return None

        image_base64 = response_json["results"]["image"]
        image_data = self._base64_to_bytes(image_base64)
        image_path_lowlight_enhance = f"/tmp/{uuid4().hex}.png"
        with open(image_path_lowlight_enhance, "wb") as file:
            file.write(image_data)

        print("PixlrApi().lowlight_enhance(): LowLight Enhanced  Image Saved!")
        return image_path_lowlight_enhance

    def super_resolution(self, image_path: str, scale: int) -> Optional[str]:
        if not self._phosus_auth_token:
            self._generate_phosus_auth_token()

        url = "https://ai.phosus.com/sr/v1/submit-job"
        headers = {"Authorizationtoken": f"{self._phosus_auth_token}"}
        image_base64 = self._path_to_base64(image_path)
        body = {"image_b64": image_base64, "scale": scale}

        response = requests.post(url, headers=headers, json=body)
        response_json = response.json()
        if response.status_code != 202 or response_json["ok"] is False:
            print(
                f"PixlrApi().super_resolution(): Something Went Wrong! {response.text}"
            )
            return None

        job_id = response.json()["results"]["id"]
        url = f"https://ai.phosus.com/sr/v1/query-job-status?id={job_id}"
        while True:
            time.sleep(1)
            response = requests.get(url, headers=headers)

            print(
                "PixlrApi().super_resolution() Waiting:"
                + response.json()["results"]["status"]
                + " "
                + str(datetime.datetime.now().timestamp())
            )

            if response.json()["results"]["status"] == "DONE":
                break

        url = "https://ai.phosus.com/sr/v1/get-image?id=" + job_id
        response = requests.get(url, headers=headers)
        response_json = response.json()

        image_base64 = response_json["results"]["output"]
        image_data = self._base64_to_bytes(image_base64)
        image_path_super_resolution = f"/tmp/{uuid4().hex}.png"
        with open(image_path_super_resolution, "wb") as file:
            file.write(image_data)

        print(
            f"PixlrApi().super_resolution(): Scaled Image Up By: {scale}, Image Saved!"
        )
        return image_path_super_resolution

    def style_transfer(self, content_image: str, style_image: str) -> Optional[str]:
        if not self._phosus_auth_token:
            self._generate_phosus_auth_token()

        url = "https://ai.phosus.com/styletransfer/v1"
        headers = {
            "Authorizationtoken": f"{self._phosus_auth_token}",
            "Content-Type": "application/json",
        }
        content_base64_image = self._path_to_base64(content_image)
        style_base64_image = self._path_to_base64(style_image)
        body = {
            "content_image_b64": content_base64_image,
            "style_image_b64": style_base64_image,
        }

        response = requests.post(url, headers=headers, json=body)
        response_json = response.json()
        if response.status_code != 200 or response_json["ok"] is False:
            print(f"PixlrApi().style_transfer(): Something Went Wrong! {response.text}")
            return None

        image_base64 = response_json["results"]["output"]
        image_data = self._base64_to_bytes(image_base64)
        image_path_style_transfer = f"/tmp/{uuid4().hex}.png"
        with open(image_path_style_transfer, "wb") as file:
            file.write(image_data)

        print("PixlrApi().style_transfer(): Style Transfered, Image Saved!")
        return image_path_style_transfer

    def generate_image_caption(self, image_path: str) -> Optional[str]:
        if not self._phosus_auth_token:
            self._generate_phosus_auth_token()

        url = "https://ai.phosus.com/icaption/v1"
        headers = {"Authorizationtoken": f"{self._phosus_auth_token}"}
        image_base64 = self._path_to_base64(image_path)
        body = {"image_b64": image_base64}

        response = requests.post(url, headers=headers, json=body)
        response_json = response.json()
        if response.status_code != 200:
            print(
                f"PixlrApi().generate_image_caption(): Something Went Wrong! {response.text}"
            )
            return None

        caption = response_json["prediction"]
        print("PixlrApi().generate_image_caption(): Caption Generated!")
        return caption

    def generate_image_tags(self, image_path: str) -> Optional[List[str]]:
        if not self._phosus_auth_token:
            self._generate_phosus_auth_token()

        url = "https://ai.phosus.com/ikeyword/v1"
        headers = {"Authorizationtoken": f"{self._phosus_auth_token}"}
        image_base64 = self._path_to_base64(image_path)
        body = {"image_b64": image_base64}

        response = requests.post(url, headers=headers, json=body)
        response_json = response.json()
        if response.status_code != 200:
            print(
                f"PixlrApi().generate_image_tags(): Something Went Wrong! {response.text}"
            )
            return None

        tags = response_json["prediction"]
        print("PixlrApi().generate_image_tags(): Tags Generated!")
        return tags
