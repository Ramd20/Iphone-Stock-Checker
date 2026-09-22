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

partList = [
    Black256, Silver256, Burgundy256, Glacier256,
    Black1TB, Silver1TB, Burgundy1TB, Glacier1TB,
]

storeList = {
    "R102": "Christiana Mall DE",
    "R354": "Pheasant Lane Nashua NH",
    "R027": "Rockingham Park Salem NH",
    "R631": "Mall of New Hampshire Manchester NH",
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
}


def checkMultipleStores(partList, storeNumber):
    availabilityDiction = {
        "error": None,
    }
    for partNumber in partList:
        storeUrl = (
            "https://www.apple.com/shop/retail/pickup-message"
            "?pl=true&parts.0=" + partNumber + "%2FA&store=" + storeNumber
        )
        try:
            response = requests.get(storeUrl, timeout=10)
            print(response.status_code)
            if response.status_code == 200:
                data = response.json()
                body = data["body"]

                if "stores" in body:
                    specificStore = body["stores"][0]
                    availability = specificStore["partsAvailability"][partNumber + "/A"]["pickupDisplay"]
                    availabilityDiction[partNumber] = availability
                    availabilityDiction["name"] = specificStore["storeName"]
                else:
                    availabilityDiction["error"] = "No stores in response"
                    return availabilityDiction

            elif response.status_code == 541:
                availabilityDiction["error"] = "541 Error"
                return availabilityDiction
            else:
                availabilityDiction["error"] = "HTTP " + str(response.status_code)
                return availabilityDiction
        except Exception as e:
            availabilityDiction["error"] = "Exception: " + str(e)
            return availabilityDiction

    return availabilityDiction


def sendDiscordMessage(message):
    if not WEBHOOK_URL:
        print("No webhook, skip Discord:")
        print(message)
        return
    requests.post(WEBHOOK_URL, json={"content": message})


def main():
    parts = ", ".join(partList)
    stores = ", ".join(storeList.keys())
    print("Starting monitor for stores " + stores + ", " + parts)
    sendDiscordMessage("Bot started monitoring 256 Pro Max at " + stores)

    checkCount = 0
    while True:
        checkCount += 1
        eastern = pytz.timezone("US/Eastern")
        pauseTime = datetime.now(eastern)
        currentTime = datetime.now(eastern).strftime("%I:%M:%S %p")

        if pauseTime.hour >= 9 and pauseTime.hour <= 21:
            for storeNumber in storeList:
                result = checkMultipleStores(partList, storeNumber)
                label = storeList[storeNumber]
                if result.get("error"):
                    sendDiscordMessage(
                        "Check #" + str(checkCount) + " " + label + " error: " + str(result["error"])
                    )
                    continue

                store_name = result.get("name") or label
                lines = [
                    "Check #" + str(checkCount),
                    "Time: " + currentTime,
                    store_name,
                ]
                for part in partList:
                    status = result.get(part, "missing")
                    mark = "🟢" if status == "available" else "⚪"
                    part_label = partLabels.get(part, part)
                    lines.append(mark + " " + part_label)
                sendDiscordMessage("\n".join(lines))
            time.sleep(600)
        else:
            time.sleep(3600)

def formatStockMessage(result, header, store_fallback):
    if result.get("error"):
        return header + " error: " + str(result["error"])
    store_name = result.get("name") or store_fallback
    lines = [header, store_name]
    for part in partList:
        status = result.get(part, "missing")
        mark = "🟢" if status == "available" else "⚪"
        lines.append(mark + " " + partLabels.get(part, part))
    return "\n".join(lines)

if __name__ == "__main__":
    main()