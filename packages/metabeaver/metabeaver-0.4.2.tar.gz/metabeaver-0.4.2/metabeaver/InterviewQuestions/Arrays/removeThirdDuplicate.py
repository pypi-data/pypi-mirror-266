"""

We have an array in ascending order.
The task is to remove duplicates in-place.
The first duplicate is allowed! There should not be more than two of the same number in the array.
[1, 1] is allowed, but [1, 1, 1] is not.
The elements order should be kept the same.

The array length must not change.
e.g [1, 1, 1, 2, 2, 2] should become [1, 1, 2, 2, _, _]

Return k, the count of elements, after removal of the third duplicate or greater.

A new array must not be created.
Modify the array in-place, using O(1) memory.

"""
def removeDuplicates(nums):

    # If not a valid array, and None was passed, return 0
    if not nums:
        return 0

    # Count of unique elements and their first duplicate
    count = 1
    # Count of duplicates for the current unique element
    duplicate_count = 0

    # Compare pairs and start removing them when the *second* duplicate is found.
    for i in range(1, len(nums)):

        # Check whether elements are identical and then reference count of duplicates
        if nums[i] == nums[i - 1] and i != '_':
            duplicate_count += 1
            if duplicate_count <= 1:
                # If less than or equal to 1 duplicate, update the array
                count += 1
        else:
            # If a new unique element is encountered
            duplicate_count = 0
            count += 1

        if duplicate_count > 1:
            # If the duplicate count is greater than one, delete duplicate, add "_" to array end
            nums.pop(i)
            nums.append('_')
            i = i - 1

        print(i)
        print(nums)

    return [nums, count]

testArray = [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5]
print(removeDuplicates(testArray))


def removeDuplicates(nums):
    if not nums:
        return 0

    count = 1
    duplicate_count = 0

    i = 1  # Start from the second element

    while i < len(nums):
        if nums[i] == nums[i - 1]:
            duplicate_count += 1
            if duplicate_count <= 1:
                count += 1
            else:
                nums.pop(i)
                nums.append('_')
        else:
            duplicate_count = 0
            count += 1

        i += 1

    return [nums, count]

testArray = [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5]
print(removeDuplicates(testArray))