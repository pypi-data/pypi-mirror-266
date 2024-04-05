# Brute force solution where we compare every ith element with every other element
def nestedLoopFindBest(arr):

    bestBuyDay = 0
    bestSellDay = 0
    currentMax = 0

    for i in range(len(arr)):
        for j in range(i + 1, len(arr) -1):
            if arr[j] - arr[i] > currentMax:
                bestBuyDay = i
                bestSellDay = j
                currentMax = arr[j] - arr[i]

    return [bestBuyDay, bestSellDay, currentMax]

arr = [7,1,5,3,6,4]
indicesAndAmount = nestedLoopFindBest(arr)


#
def maxProfit(prices):
    if not prices or len(prices) < 2:
        return 0

    min_price = prices[0]
    max_profit = 0

    for price in prices[1:]:
        # Update the minimum price if the current price is lower
        min_price = min(min_price, price)

        # Update the maximum profit if selling at the current price gives a better profit
        max_profit = max(max_profit, price - min_price)

    return max_profit


# Example usage:
prices1 = [7, 1, 5, 3, 6, 4]
print(maxProfit(prices1))  # Output: 5












