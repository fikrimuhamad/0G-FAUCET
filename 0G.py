import os
import asyncio
import aiohttp
import ua_generator
from twocaptcha import TwoCaptcha
from datetime import datetime

API_KEY = '<2captcha-apikey>'  # Ganti dengan API Key 2Captcha kalian
PROXY = "<proxy-#http://username:password@proxy-server:port>" # Ganti dengan proxy kalian 
MAX_CONCURRENT_TASKS = 10 # banyak ketika dijalankan

async def solve_captcha():
    solver = TwoCaptcha(API_KEY)
    result = await asyncio.to_thread(solver.hcaptcha,
        sitekey='1230eb62-f50c-4da4-a736-da5c3c342e8e',
        url='https://hub.0g.ai/'
    )
    return result['code']

async def send_request(session, address, sema):
    async with sema:
        try:
            print(f"[{address}] 🔐 Solving captcha...")
            captcha_token = await solve_captcha()
            print(f"[{address}] ✅ Captcha Solved")

            user_agent =  ua_generator.generate(device='desktop', browser=('chrome', 'edge'))
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9,id;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'dnt': '1',
                'origin': 'https://hub.0g.ai',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://hub.0g.ai/',
                'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': f"{user_agent}",
            }

            json_data = {
                'address': address,
                'hcaptchaToken': captcha_token,
                'token': {
                    'name': 'A0GI',
                    'symbol': 'A0GI',
                    'logoUrl': 'https://s3.ap-northeast-2.amazonaws.com/upload.xangle.io/images/project/676ce0a44b1980a54df08249/64.png',
                    'chainId': 16600,
                    'address': '',
                    'decimals': 18,
                    'bridgeInfo': [],
                },
            }

            async with session.post('https://992dkn4ph6.execute-api.us-west-1.amazonaws.com/', headers=headers, json=json_data, proxy=PROXY) as response:
                result = await response.text()
                if response.status == 200:
                    print(f"[{address}] ✅ SUCCESS | {response.status} | Response: {result}")
                    log_result("success.txt", address, result)
                else:
                    print(f"[{address}] ❌ FAILED | Status: {response.status} | Response: {result}")
                    log_result("failed.txt", address, result)

        except Exception as e:
            print(f"[{address}] ❌ Error: {e}")
            log_result("failed.txt", address, str(e))

def log_result(filename, address, result):
    with open(filename, 'a') as f:
        f.write(f"{datetime.now()} | {address} | {result}\n")

async def main():
    if not os.path.exists("address.txt"):
        print("File address.txt tidak ditemukan.")
        return

    with open("address.txt", "r") as f:
        addresses = [line.strip() for line in f if line.strip()]

    sema = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, address, sema) for address in addresses]
        await asyncio.gather(*tasks)

    print("✅ Semua selesai. Menunggu 24 jam untuk batch berikutnya...")
    await asyncio.sleep(86400)  # sleep 24 jam

if __name__ == '__main__':
    asyncio.run(main())

