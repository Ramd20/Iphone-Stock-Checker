from stockChecker import (
    checkMultipleStores,
    sendDiscordMessage,
    formatStockMessage,
    partList,
    storeList,
)

store = "R102"
result = checkMultipleStores(partList, store)
print(result)
sendDiscordMessage(formatStockMessage(result, "TEST", storeList[store]))