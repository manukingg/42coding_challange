# Two Sum

Difficulty: Easy

## Problem

Given a list of integers `nums` and an integer `target`, return the indices of two different elements whose sum is equal to `target`.

You may assume:

- exactly one valid pair exists
- the same element cannot be used twice

You can return the indices in any order.

## Function Signature

```c
int* twoSum(int* nums, int numsSize, int target, int* returnSize);
```

## Examples

```text
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
```

```text
Input: nums = [3, 2, 4], target = 6
Output: [1, 2]
```

```text
Input: nums = [3, 3], target = 6
Output: [0, 1]
```

## Notes

- Return indices, not the values themselves.
- Your solution should work with duplicate numbers.
- Follow the standard LeetCode C pattern: return a dynamically allocated array of
  two integers and set `*returnSize = 2`.
