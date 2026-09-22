import requests
import json
import time
import os
from dotenv import load_dotenv
import pytz
from datetime import datetime

load_dotenv()
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
TwoTBBlack = "MJWH4LL"
TwoTBBurgundy = "MJWK4LL"
TwoTBSilver = "MJWJ4LL"
zip_code = "19720"

Orange256 = "MJW64LL"
Silver256 = "MFXG4LL"
Navy256 = "MFXJ4LL"

partList = [TwoTBBlack, TwoTBBurgundy, TwoTBSilver]
# Use either endpoint variant
#MFXP4LL/A -> 1tb Orange
#MFXN4LL -> 1tb Silver
#MFXG4LL -> 256GB Silver
#MFXR4LL ->2tb Silver

#christiana store -> R102
#Reston store -> R271
#Portland Pioneer Place -> R077
storeNumber = "R077"


def checkSingleStore(partNumber, storeNumber):
    storeUrl = f"https://www.apple.com/shop/retail/pickup-message?pl=true&parts.0={partNumber}%2FA&store={storeNumber}"
    try:
        response = requests.get(storeUrl, timeout=10)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            body = data["body"]

            if "stores" in body:
                specificStore = body["stores"][0]
                availability = specificStore["partsAvailability"][partNumber + "/A"]["pickupDisplay"]
                return {
                    "status": availability,
                    "name": specificStore["storeName"],
                    "error": None
                }
            else:
                return {
                    "status": "error",
                    "name": None,
                    "error": "No stores in response"
                }

        elif response.status_code == 541:
            return {
                "status": "error",
                "name": None,
                "error": "541 - Rate Limited"
            }
        else:
            return {
                "status": "error",
                "name": None,
                "error": "HTTP " + str(response.status_code)
            }
    except Exception as e:
        return {
            "status": "error",
            "name": None,
            "error": "Exception: " + str(e)
        }


def checkMultipleStores(partList, storeNumber):
    availabilityDiction = {
        "error": None,
    }
    for partNumber in partList:
        storeUrl = f"https://www.apple.com/shop/retail/pickup-message?pl=true&parts.0={partNumber}%2FA&store={storeNumber}"
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
    response = requests.post(WEBHOOK_URL, json={"content": message})


def main():
    parts = ", ".join(partList)
    print("Starting monitor for store " + storeNumber + ", " + parts)
    sendDiscordMessage("Bot started monitoring " + parts + " at store " + storeNumber)
    checkCount = 0

    while True:
        checkCount += 1

        eastern = pytz.timezone("US/Eastern")
        pauseTime = datetime.now(eastern)
        currentTime = datetime.now(eastern).strftime("%I:%M:%S %p")
        if pauseTime.hour >= 9 and pauseTime.hour <= 21:
            result = checkMultipleStores(partList, storeNumber)
            if result["error"]:
                errorMessage = result["error"]
                message = "Check #" + str(checkCount) + " (Error): " + errorMessage
                sendDiscordMessage(message)
            else:
                emojiDict = {}

                for part in result:
                    if part[0] == "M":
                        if result[part] == "available":
                            emojiDict[part] = "GREEN"
                        else:
                            emojiDict[part] = "WHITE"

                store_name = result["name"]
                header = "Check #" + str(checkCount) + "\nTime: " + currentTime + "\n" + store_name
                message = ""

                for model in emojiDict:
                    message += emojiDict[model] + " " + model + "\n"

                finalMessage = header + "\n" + message
                sendDiscordMessage(finalMessage)

            time.sleep(600)
        else:
            time.sleep(3600)


if __name__ == "__main__":
    main()