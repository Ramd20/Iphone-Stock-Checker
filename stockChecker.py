import os
import time
from datetime import datetime

import pytz
import requests
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

# iPhone Duo (US / A3447)
NightSky256 = "MK1F4LL"
StarWhite256 = "MK1E4LL"

NightSky512 = "MK1H4LL"
StarWhite512 = "MK1G4LL"

NightSky1TB = "MK1L4LL"
StarWhite1TB = "MK1J4LL"

NightSky2TB = "MK1R4LL"
StarWhite2TB = "MK1Q4LL"

partList = [
    NightSky256, StarWhite256,
    NightSky512, StarWhite512,
    NightSky1TB, StarWhite1TB,
    NightSky2TB, StarWhite2TB,
]

partLabels = {
    "MK1F4LL": "MK1F4LL Night Sky 256",
    "MK1E4LL": "MK1E4LL Star White 256",
    "MK1H4LL": "MK1H4LL Night Sky 512",
    "MK1G4LL": "MK1G4LL Star White 512",
    "MK1L4LL": "MK1L4LL Night Sky 1TB",
    "MK1J4LL": "MK1J4LL Star White 1TB",
    "MK1R4LL": "MK1R4LL Night Sky 2TB",
    "MK1Q4LL": "MK1Q4LL Star White 2TB",
}

storeList = {
    "R105": "Oakridge San Jose CA",
    "R039": "Valley Fair Santa Clara CA",
    "R824": "Apple Park Visitor Center Cupertino",
    "R271": "Reston VA",
    "R010": "Tysons Corner VA",
}

last_green = set()


def checkMultipleStores(partList, storeNumber):
    result = {"error": None}
    qs = ["pl=true"]
    for i, partNumber in enumerate(partList):
        qs.append("parts." + str(i) + "=" + partNumber + "%2FA")
    qs.append("store=" + storeNumber)
    url = "https://www.apple.com/shop/retail/pickup-message?" + "&".join(qs)

    try:
        response = requests.get(url, timeout=15)
        print(storeNumber, response.status_code)
        if response.status_code == 200:
            body = response.json()["body"]
            if "stores" not in body:
                result["error"] = "No stores in response"
                return result
            store = body["stores"][0]
            result["name"] = store["storeName"]
            partsAvail = store["partsAvailability"]
            for partNumber in partList:
                key = partNumber + "/A"
                if key in partsAvail:
                    result[partNumber] = partsAvail[key]["pickupDisplay"]
                else:
                    result[partNumber] = "missing"
            return result
        if response.status_code == 541:
            result["error"] = "541 Error"
            return result
        result["error"] = "HTTP " + str(response.status_code)
        return result
    except Exception as e:
        result["error"] = "Exception: " + str(e)
        return result


def sendDiscordMessage(message, ping_everyone=False):
    if not WEBHOOK_URL:
        print("No webhook, skip Discord:")
        print(message)
        return
    payload = {"content": message}
    if ping_everyone:
        payload["allowed_mentions"] = {"parse": ["everyone"]}
    requests.post(WEBHOOK_URL, json=payload)


def formatStockMessage(result, header, store_fallback):
    if result.get("error"):
        return header + " error: " + str(result["error"])
    lines = [header, result.get("name") or store_fallback]
    for part in partList:
        status = result.get(part, "missing")
        mark = "🟢" if status == "available" else "⚪"
        lines.append(mark + " " + partLabels.get(part, part))
    return "\n".join(lines)


def collect_green(storeNumber, result):
    green = set()
    if result.get("error"):
        return green
    for part in partList:
        if result.get(part) == "available":
            green.add((storeNumber, part))
    return green


def ping_new_stock(new_keys):
    if not new_keys:
        return
    sendDiscordMessage("@everyone", ping_everyone=True)


def main():
    global last_green

    stores = ", ".join(storeList.keys())
    print("Starting monitor for " + stores)
    sendDiscordMessage("Bot started monitoring iPhone Duo at " + stores)

    checkCount = 0
    while True:
        checkCount += 1
        eastern = pytz.timezone("US/Eastern")
        now = datetime.now(eastern)
        currentTime = now.strftime("%I:%M:%S %p")

        if now.hour >= 9 and now.hour <= 21:
            now_green = set()

            for storeNumber in storeList:
                result = checkMultipleStores(partList, storeNumber)
                now_green |= collect_green(storeNumber, result)

                header = "Check #" + str(checkCount) + "\nTime: " + currentTime
                sendDiscordMessage(
                    formatStockMessage(result, header, storeList[storeNumber])
                )
                time.sleep(5)

            new_keys = now_green - last_green
            ping_new_stock(new_keys)
            last_green = now_green

            time.sleep(600)
        else:
            time.sleep(3600)


if __name__ == "__main__":
    main()