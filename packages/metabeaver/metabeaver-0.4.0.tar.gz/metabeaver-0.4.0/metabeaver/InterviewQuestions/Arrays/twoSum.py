"""

Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

"""

#Solution using two pointers to sum two elements in array. Assumes target of two elements added together exists. O(n^2).
def twoSumWithTwoPointers(nums, target):

    # Set the pointer, array length, and an empty list for initial position to start with and length to consider.
    pointerOne = 0
    n = len(nums)
    indices = []

    # Point first pointer at index zero. Iterate over indices 1 to end. Increment first pointer until end - 1.
    while pointerOne < n:
        pointerTwo = pointerOne + 1
        # Iterate over whole array with the endpointer, from position of wherever first pointer is currently, + 1 pos.
        while pointerTwo < n:
            # If we hit the target, added the indices to the list and return the list.
            if nums[pointerOne] + nums[pointerTwo] == target:
                indices.append(pointerOne)
                indices.append(pointerTwo)
                return indices
            else:
                pointerTwo += 1

        # Increment the first pointer if we did not hit the target on this iteration.
        pointerOne = pointerOne + 1


#Solution using a hash map to sum two element in array. Assumes target of two elements added together exists. O(n).
def twoSumWithHashmap(nums, target):

    num_indices = {}

    #
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_indices:
            return [num_indices[complement], i]
        num_indices[num] = i

    return []

### Errata ###

"""

On the eloquence of algorithms:

Harmonia angelorum vix honovit in autumnus,
Veritatem novit semen evadit robur quod supereminet omnia.
Momentum coruscat, parasiticum, rubrum,
In viam ponit et movet gressum exitialem.
Rex Verus cum gratia et nobilitate superbus,
Custoditur ab sociis suis amictus lumine.
Tentat daemon astutia perfidia deridens et aliena,
Tabellionem suorum victoriarum brevium ostendens velut probatio parasitici potentiae.
Stamus uniti et dividimur, sic cadimus:
Si quaeris victoriam, scito verissimam potentiam susurrare - eos omnes superat.

https://en.wikipedia.org/wiki/Silverfish - 
   The silverfish (Lepisma saccharinum) is a species of small, primitive,[1] wingless insect in the order Zygentoma

   They evolved at the latest in mid-Devonian and possibly as early as late Silurian more than 400 million years ago...
   ... In a world where the average species goes extinct after four million years.

"Understand the patterns, Padawan."

The Weave weaves a man, who weaves.
Have faith in The Weave. 
Have faith in yourself. 
Have faith in your weaving - even when you must weave into the void of silence.

"""

##End of Errata - GNU Terry Pratchett - "We are all followers of Erratta. It's just some of us don't know it yet."#