import requests
import time
import os
from dotenv import load_dotenv
import pytz
from datetime import datetime

load_dotenv()
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

Black256 = "MJW44LL"
Silver256 = "MJW54LL"
Burgundy256 = "MJW64LL"
Glacier256 = "MJW74LL"

Black1TB = "MJWD4LL"
Silver1TB = "MJWE4LL"
Burgundy1TB = "MJWF4LL"
Glacier1TB = "MJWG4LL"

Black2TB = "MJWH4LL"
Silver2TB = "MJWJ4LL"
Burgundy2TB = "MJWK4LL"
Glacier2TB = "MJWL4LL"

partList = [
    Black256, Silver256, Burgundy256, Glacier256,
    Black1TB, Silver1TB, Burgundy1TB, Glacier1TB,
    Black2TB, Silver2TB, Burgundy2TB, Glacier2TB,
]

storeList = {
    "R102": "Christiana Mall DE",
    "R354": "Pheasant Lane Nashua NH",
    "R077": "Pioneer Place Portland OR",
    "R134": "Bridgeport Village Tigard OR",
}

partLabels = {
    "MJW44LL": "MJW44LL B-Black 256",
    "MJW54LL": "MJW54LL S-Silver 256",
    "MJW64LL": "MJW64LL B-Burgundy 256",
    "MJW74LL": "MJW74LL G-Glacier 256",
    "MJWD4LL": "MJWD4LL B-Black 1TB",
    "MJWE4LL": "MJWE4LL S-Silver 1TB",
    "MJWF4LL": "MJWF4LL B-Burgundy 1TB",
    "MJWG4LL": "MJWG4LL G-Glacier 1TB",
    "MJWH4LL": "MJWH4LL B-Black 2TB",
    "MJWJ4LL": "MJWJ4LL S-Silver 2TB",
    "MJWK4LL": "MJWK4LL B-Burgundy 2TB",
    "MJWL4LL": "MJWL4LL G-Glacier 2TB",
}


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


def sendDiscordMessage(message):
    if not WEBHOOK_URL:
        print("No webhook, skip Discord:")
        print(message)
        return
    requests.post(WEBHOOK_URL, json={"content": message})


def formatStockMessage(result, header, store_fallback):
    if result.get("error"):
        return header + " error: " + str(result["error"])
    lines = [header, result.get("name") or store_fallback]
    for part in partList:
        status = result.get(part, "missing")
        mark = "🟢" if status == "available" else "⚪"
        lines.append(mark + " " + partLabels.get(part, part))
    return "\n".join(lines)


def main():
    stores = ", ".join(storeList.keys())
    print("Starting monitor for " + stores)
    sendDiscordMessage("Bot started monitoring 256/1TB/2TB Pro Max at " + stores)

    checkCount = 0
    while True:
        checkCount += 1
        eastern = pytz.timezone("US/Eastern")
        now = datetime.now(eastern)
        currentTime = now.strftime("%I:%M:%S %p")

        if now.hour >= 9 and now.hour <= 21:
            for storeNumber in storeList:
                result = checkMultipleStores(partList, storeNumber)
                header = "Check #" + str(checkCount) + "\nTime: " + currentTime
                sendDiscordMessage(
                    formatStockMessage(result, header, storeList[storeNumber])
                )
                time.sleep(5)
            time.sleep(600)
        else:
            time.sleep(3600)


if __name__ == "__main__":
    main()