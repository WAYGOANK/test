# nums = [2,7,11,15]
# target = 9
# for index, i in enumerate(nums):
#     for j in range(index + 1, len(nums)):
#         if i + nums[j] == target:
#             print(f"[{i}, {nums[j]}]")
import re
color = '"款式： IO7548-900"'
data = re.search("款式： ([A-Za-z0-9-]*)", color).group(1)
print(data)