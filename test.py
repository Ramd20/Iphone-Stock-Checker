from stockChecker import *
import requests
import time

part_number = "MFXH4LL" #hard coded for now 
zip_code = "20171"
# TwoTBSilver = "MFXR4LL"
# TwoTBOrange = "MFXT4LL"
# TwoTBNavy = "MFXU4LL"
TwoTBBlack = "MJWH4LL"
TwoTBBurgundy = "MJWK4LL"
TwoTBSilver = "MJWJ4LL"
zip_code = "19720"

partList = [TwoTBBurgundy, TwoTBBlack, TwoTBSilver]
# Use either endpoint variant

result = checkMultipleStores(partList, "R077")

emojiDict = {
        
}
for part in result:
    if part[0] == "M":
        if result[part] == "available":
            emojiDict[part] = "🟢"
        else:
            emojiDict[part] = "⚪"


                # if currentStatus == "available":
                #     emoji = "🟢"
                # else:
                #     emoji = "⚪"

header =  result["name"]
message = ""

for model in emojiDict:
    message += f"{emojiDict[model]} {model} \n"
#message = f"{emoji} Check #{checkCount}\n Time: {currentTime}\n{currentStatus} at {storeName}"
finalMessage = header + "\n" + message
sendDiscordMessage(finalMessage)