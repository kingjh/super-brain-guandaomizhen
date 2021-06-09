import sys

row_cnt = int(sys.argv[1])
col_cnt = int(sys.argv[2])
floor_cnt = int(sys.argv[3])

# 生成不同题目下，每个立方块天然的对外接口的可能性，以2*3*2的题目为例，立方块如下图编号（3d透视）：
#    07
# 10 |   08
# |  |11     09
# |  |    12  |
# |  01       |
# 04     02   |
#     05     03
#         06

# 以格式：[x, y, z, -x, -y, -z]，记录在每个方向可能面对的接口数
# 例如01号立方块在-x、-y、-z方向，可能面对的接口数都只有0，其他方向可以是0或1，记录为[[0, 1], [0, 1], [0, 1], [0], [0], [0]]
interfacess = []
for k in range(floor_cnt):
    for i in range(row_cnt):
        for j in range(col_cnt):
            # 行、列、高取1、0、-1，判断当前元素对外的接口
            interfaces = []
            for delta in range(1, -2, -2):
                adjacent_j = j + delta
                if adjacent_j == col_cnt:
                    interfaces.append([0])
                elif adjacent_j < 0:
                    interfaces.append([0])
                else:
                    interfaces.append([0, 1])

                adjacent_i = i + delta
                if adjacent_i == row_cnt:
                    interfaces.append([0])
                elif adjacent_i < 0:
                    interfaces.append([0])
                else:
                    interfaces.append([0, 1])

                adjacent_k = k + delta
                if adjacent_k == floor_cnt:
                    interfaces.append([0])
                elif adjacent_k < 0:
                    interfaces.append([0])
                else:
                    interfaces.append([0, 1])

            interfacess.append(interfaces)

with open("interfaces/{0}-{1}-{2}.json".format(row_cnt, col_cnt, floor_cnt), 'w', encoding='utf-8') as interfaces_file:
    interfaces_file.write(str(interfacess))
