import copy
import json

# 基本形状有以下9种简化图形（*代表图形中央，箭头代表管道），其他形状可以由基本形状旋转得到
# 0    ×
#        ↘

# 1      ↗
#      ×
#        ↘

# 2 ↖
#      ×
#        ↘

# 3    ↑
#      ×
#   ↙   ↘

# 4 ↖ ↑
#      ×
#        ↘

# 5 ↖ ↑
#      ×
#      ↓ ↘

# 6    ↑
#      ×
#   ↙ ↓ ↘

# 7 ↖ ↑
#      ×
#   ↙ ↓ ↘

# 8 ↖ ↑ ↗
#      ×
#   ↙ ↓ ↘

# 用数组记录每种立方块在6个方向的凸出（格式：[x, y, z, -x, -y, -z]）
# 如[1,1,1,1,1,1]，意味着只有在所有方向都有凸出，3d透视如下：
#   ↖ ↑ ↗
#      ×
#   ↙ ↓ ↘

# 如[1,0,0,0,1,1]，意味着只有在x、-y、-z方向凸出，3d透视如下：
#        ↗
#      ×
#      ↓ ↘

# 6个方向的索引：
DIR_X = 0
DIR_Y = 1
DIR_Z = 2
DIR_X_NEG = 3
DIR_Y_NEG = 4
DIR_Z_NEG = 5

# 9种基本形状各自可能的数组如下：
BASIC_INTERFACESS = [
    # 0
    [
        [1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 1],
    ],
    # 1
    [
        [1, 1, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 1],
        [0, 1, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 1],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 1, 0, 1, 0],
        [0, 0, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 1],
        [0, 0, 0, 0, 1, 1],
    ],
    # 2
    [
        [1, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 1],
    ],
    # 3
    [
        [1, 1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0],
        [1, 0, 0, 0, 1, 1],
        [0, 1, 1, 1, 0, 0],
        [0, 1, 0, 1, 0, 1],
        [0, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1],
    ],
    # 4
    [
        [1, 1, 0, 1, 0, 0],
        [1, 0, 1, 1, 0, 0],
        [1, 0, 0, 1, 1, 0],
        [1, 0, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 0],
        [0, 1, 1, 0, 1, 0],
        [0, 1, 0, 0, 1, 1],
        [1, 0, 1, 0, 0, 1],
        [0, 0, 1, 1, 0, 1],
        [0, 1, 1, 0, 0, 1],
        [0, 0, 1, 0, 1, 1],
    ],
    # 5
    [
        [1, 1, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 1],
        [0, 1, 1, 0, 1, 1],
    ],
    # 6
    [
        [1, 1, 1, 1, 0, 0],
        [1, 1, 1, 0, 1, 0],
        [1, 1, 1, 0, 0, 1],
        [1, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 1],
        [1, 0, 1, 1, 1, 0],
        [1, 0, 1, 0, 1, 1],
        [1, 0, 0, 1, 1, 1],
        [0, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 0, 1],
        [0, 1, 0, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
    ],
    # 7
    [
        [1, 1, 1, 1, 1, 0],
        [1, 1, 0, 1, 1, 1],
        [1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1],
        [0, 1, 1, 1, 1, 1],
    ],
    # 8
    [
        [1, 1, 1, 1, 1, 1],
    ],
]


def init_sols():
    global elements, out_interfacess, row_cnt, col_cnt, floor_cnt, cnt_per_floor, sols, validated_coords
    for k in range(floor_cnt):
        sols[k] = {}
        for i in range(row_cnt):
            sols[k][i] = {}
            for j in range(col_cnt):
                sols[k][i][j] = []
                # 找出当前元素是哪个基本形状
                ele_idx = cnt_per_floor * k + col_cnt * i + j
                basic_idx = int(elements[ele_idx])
                # 找出当前元素外部接口的可能性
                out_interfaces = out_interfacess[k][i][j]
                # 找出当前元素有多少种可能的对外接口
                in_interfaces = BASIC_INTERFACESS[basic_idx]
                # 看当前元素有多少个可能的对外接口符合外部接口，记录在sols[k][i][j]
                for in_interface in in_interfaces:
                    is_all_co_fulfilled = True
                    # x y z -x -y -z六个方向对比
                    for co_idx in range(6):
                        if in_interface[co_idx] not in out_interfaces[co_idx]:
                            is_all_co_fulfilled = False
                            break

                    if is_all_co_fulfilled:
                        sols[k][i][j].append(in_interface)

    # 筛选只有一种可能性的立方块周围的立方块的可能性
    old_one_cnt = -1
    new_one_cnt = 0
    while old_one_cnt != new_one_cnt:
        old_one_cnt = new_one_cnt
        new_one_cnt = 0
        print(222)
        for k1 in range(floor_cnt):
            for i1 in range(row_cnt):
                for j1 in range(col_cnt):
                    print(sols[k1][i1][j1])

        for k in range(floor_cnt):
            for i in range(row_cnt):
                for j in range(col_cnt):
                    if len(sols[k][i][j]) == 1:
                        if [k, i, j] not in validated_coords:
                            validated_coords.append([k, i, j])

                        new_one_cnt += 1
                        res = is_adjacencys_fulfilled(sols, k, i, j, k, i, j)
                        sols = replace_sub_dicts(sols, res)

        print(333)
        for k1 in range(floor_cnt):
            for i1 in range(row_cnt):
                for j1 in range(col_cnt):
                    print(sols[k1][i1][j1])


def validate_sols(var_sols):
    print(993)
    global row_cnt, col_cnt, floor_cnt
    for k in range(floor_cnt):
        for i in range(row_cnt):
            for j in range(col_cnt):
                for delta in range(1, -2, -2):
                    adjacent_j = j + delta
                    if 0 <= adjacent_j < col_cnt:
                        # 对比同层同行相邻列的-x方向、当前元素的x方向
                        if delta > 0:
                            if var_sols[k][i][j][0][DIR_X] != var_sols[k][i][adjacent_j][0][DIR_X_NEG]:
                                return False

                        # 对比同层同列上一行的x方向、当前元素的-x方向
                        if delta < 0:
                            if var_sols[k][i][j][0][DIR_X_NEG] != var_sols[k][i][adjacent_j][0][DIR_X]:
                                return False

                    adjacent_i = i + delta
                    if 0 <= adjacent_i < row_cnt:
                        # 对比同层同列相邻行的-y方向、当前元素的y方向
                        if delta > 0:
                            if var_sols[k][i][j][0][DIR_Y] != var_sols[k][adjacent_i][j][0][DIR_Y_NEG]:
                                return False

                        # 对比同层同列上一行的y方向、当前元素的-y方向
                        if delta < 0:
                            if var_sols[k][i][j][0][DIR_Y_NEG] != var_sols[k][adjacent_i][j][0][DIR_Y]:
                                return False

                    adjacent_k = k + delta
                    if 0 <= adjacent_k < floor_cnt:
                        # 对比同行同列相邻层的-z方向、当前元素的z方向
                        if delta > 0:
                            if var_sols[k][i][j][0][DIR_Z] != var_sols[adjacent_k][i][j][0][DIR_Z_NEG]:
                                print(991, k, i, j)
                                return False

                        # 对比同层同列上一行的z方向、当前元素的-z方向
                        if delta < 0:
                            if var_sols[k][i][j][0][DIR_Z_NEG] != var_sols[adjacent_k][i][j][0][DIR_Z]:
                                print(992, k, i, j)
                                return False

    return True


def create_sub_dicts(obj, floor_idx, row_idx, col_idx):
    if floor_idx not in obj:
        obj[floor_idx] = {}
    if row_idx not in obj[floor_idx]:
        obj[floor_idx][row_idx] = {}
    if col_idx not in obj[floor_idx][row_idx]:
        obj[floor_idx][row_idx][col_idx] = []

    return obj


def replace_sub_dicts(big_obj, small_obj):
    for f in small_obj.keys():
        for r in small_obj[f].keys():
            for c in small_obj[f][r].keys():
                big_obj[f][r][c] = copy.deepcopy(small_obj[f][r][c])

    return big_obj


def append_sub_dicts(big_obj, small_obj):
    for f in small_obj.keys():
        for r in small_obj[f].keys():
            for c in small_obj[f][r].keys():
                big_obj = create_sub_dicts(big_obj, f, r, c)
                for arr in small_obj[f][r][c]:
                    if arr not in big_obj[f][r][c]:
                        big_obj[f][r][c].append(arr)

    return big_obj


# 看当前元素对外接口是否符合周围元素的对外接口
def is_adjacencys_fulfilled(var_sols, floor_idx, row_idx, col_idx, exc_floor_idx, exc_row_idx, exc_col_idx):
    global row_cnt, col_cnt, floor_cnt
    tmp_sols = {}
    for idx, sol in enumerate(var_sols[floor_idx][row_idx][col_idx]):
        is_adjacencys_fulfilled = True
        tmp_sol = {}
        for delta in range(1, -2, -2):
            adjacent_j = col_idx + delta
            # adjacent_j != exc_col_idx是为了避免重复检查
            if 0 <= adjacent_j < col_cnt and adjacent_j != exc_col_idx:
                tmp_sol = create_sub_dicts(tmp_sol, floor_idx, row_idx, adjacent_j)
                # 对比同层同行相邻列的-x方向、当前元素的x方向
                if delta > 0:
                    is_found = False
                    for var_sol in var_sols[floor_idx][row_idx][adjacent_j]:
                        if sol[DIR_X] == var_sol[DIR_X_NEG]:
                            is_found = True
                            tmp_sol[floor_idx][row_idx][adjacent_j].append(var_sol)

                    if not is_found:
                        is_adjacencys_fulfilled = False
                        break

                # 对比同层同列上一行的x方向、当前元素的-x方向
                if delta < 0:
                    is_found = False
                    for var_sol in var_sols[floor_idx][row_idx][adjacent_j]:
                        if sol[DIR_X_NEG] == var_sol[DIR_X]:
                            is_found = True
                            tmp_sol[floor_idx][row_idx][adjacent_j].append(var_sol)

                    if not is_found:
                        is_adjacencys_fulfilled = False
                        break

            adjacent_i = row_idx + delta
            # adjacent_i != exc_row_idx是为了避免重复检查
            if 0 <= adjacent_i < row_cnt and adjacent_i != exc_row_idx:
                tmp_sol = create_sub_dicts(tmp_sol, floor_idx, adjacent_i, col_idx)
                # 对比同层同列相邻行的-y方向、当前元素的y方向
                if delta > 0:
                    is_found = False
                    for var_sol in var_sols[floor_idx][adjacent_i][col_idx]:
                        if sol[DIR_Y] == var_sol[DIR_Y_NEG]:
                            is_found = True
                            tmp_sol[floor_idx][adjacent_i][col_idx].append(var_sol)

                    if not is_found:
                        is_adjacencys_fulfilled = False
                        break

                # 对比同层同列上一行的y方向、当前元素的-y方向
                if delta < 0:
                    is_found = False
                    for var_sol in var_sols[floor_idx][adjacent_i][col_idx]:
                        if sol[DIR_Y_NEG] == var_sol[DIR_Y]:
                            is_found = True
                            tmp_sol[floor_idx][adjacent_i][col_idx].append(var_sol)

                    if not is_found:
                        is_adjacencys_fulfilled = False
                        break

            adjacent_k = floor_idx + delta
            # adjacent_k != exc_floor_idx是为了避免重复检查
            if 0 <= adjacent_k < floor_cnt and adjacent_k != exc_floor_idx:
                tmp_sol = create_sub_dicts(tmp_sol, adjacent_k, row_idx, col_idx)
                # 对比同行同列相邻层的-z方向、当前元素的z方向
                if delta > 0:
                    is_found = False
                    for var_sol in var_sols[adjacent_k][row_idx][col_idx]:
                        if sol[DIR_Z] == var_sol[DIR_Z_NEG]:
                            is_found = True
                            tmp_sol[adjacent_k][row_idx][col_idx].append(var_sol)

                    if not is_found:
                        is_adjacencys_fulfilled = False
                        break

                # 对比同层同列上一行的z方向、当前元素的-z方向
                if delta < 0:
                    is_found = False
                    for var_sol in var_sols[adjacent_k][row_idx][col_idx]:
                        if sol[DIR_Z_NEG] == var_sol[DIR_Z]:
                            is_found = True
                            tmp_sol[adjacent_k][row_idx][col_idx].append(var_sol)

                    if not is_found:
                        is_adjacencys_fulfilled = False
                        break

        if is_adjacencys_fulfilled:
            print(995, idx)
            for k in range(floor_cnt):
                for i in range(row_cnt):
                    for j in range(col_cnt):
                        if k in tmp_sol and i in tmp_sol[k] and j in tmp_sol[k][i]:
                            print(k, i, j, tmp_sol[k][i][j])
            append_sub_dicts(tmp_sols, tmp_sol)

    # 只要var_sols[floor_idx][row_idx][col_idx]有一个可能性，可以符合周围的所有对外接口，那么tmp_sols就不为空
    print(994, floor_idx, row_idx, col_idx, var_sols[floor_idx][row_idx][col_idx], tmp_sols.keys())
    for k in range(floor_cnt):
        for i in range(row_cnt):
            for j in range(col_cnt):
                if k in tmp_sols and i in tmp_sols[k] and j in tmp_sols[k][i]:
                    print(k, i, j, tmp_sols[k][i][j])
    return tmp_sols


def get_sols(var_sols):
    global row_cnt, col_cnt, floor_cnt, sols, validated_coords
    # 如果validated_coords的大小=floor_cnt*row_cnt*col_cnt，意味着所有元素都已经找到解，判断是否接口全部符合，如果是返回True
    print(992, len(validated_coords))
    if len(validated_coords) == floor_cnt * row_cnt * col_cnt:
        print(999)
        if validate_sols(var_sols):
            sols = var_sols
            return True
        else:
            return False

    # 找最小可能性的立方块，遍历它（1视为已确定的立方块）
    min_in_interface_cnt = 99
    min_prob_k = -1
    min_prob_i = -1
    min_prob_j = -1
    for k in range(floor_cnt):
        for i in range(row_cnt):
            for j in range(col_cnt):
                interface_cnt = len(var_sols[k][i][j])
                if interface_cnt < min_in_interface_cnt and [k, i, j] not in validated_coords:
                    min_in_interface_cnt = interface_cnt
                    min_prob_k = k
                    min_prob_i = i
                    min_prob_j = j

    for sol in var_sols[min_prob_k][min_prob_i][min_prob_j]:
        print(111, min_prob_k, min_prob_i, min_prob_j, sol)
        new_sols = copy.deepcopy(var_sols)
        is_all_fulfilled = True
        for delta in range(1, -2, -2):
            adjacent_j = min_prob_j + delta
            if 0 <= adjacent_j < col_cnt:
                # 对比同层同行相邻列的-x方向、当前元素的x方向
                if delta > 0:
                    is_found = False
                    new_sol = []
                    for var_sol in var_sols[min_prob_k][min_prob_i][adjacent_j]:
                        if sol[DIR_X] == var_sol[DIR_X_NEG]:
                            is_found = True
                            new_sol.append(var_sol)

                    new_sols[min_prob_k][min_prob_i][adjacent_j] = new_sol.copy()
                    if not is_found:
                        is_all_fulfilled = False
                        break

                # 对比同层同列上一行的x方向、当前元素的-x方向
                if delta < 0:
                    is_found = False
                    new_sol = []
                    for var_sol in var_sols[min_prob_k][min_prob_i][adjacent_j]:
                        if sol[DIR_X_NEG] == var_sol[DIR_X]:
                            is_found = True
                            new_sol.append(var_sol)

                    new_sols[min_prob_k][min_prob_i][adjacent_j] = new_sol.copy()
                    if not is_found:
                        is_all_fulfilled = False
                        break

            adjacent_i = min_prob_i + delta
            if 0 <= adjacent_i < row_cnt:
                # 对比同层同列相邻行的-y方向、当前元素的y方向
                if delta > 0:
                    is_found = False
                    new_sol = []
                    for var_sol in var_sols[min_prob_k][adjacent_i][min_prob_j]:
                        if sol[DIR_Y] == var_sol[DIR_Y_NEG]:
                            is_found = True
                            new_sol.append(var_sol)

                    new_sols[min_prob_k][adjacent_i][min_prob_j] = new_sol.copy()
                    if not is_found:
                        is_all_fulfilled = False
                        break

                # 对比同层同列上一行的y方向、当前元素的-y方向
                if delta < 0:
                    is_found = False
                    new_sol = []
                    for var_sol in var_sols[min_prob_k][adjacent_i][min_prob_j]:
                        if sol[DIR_Y_NEG] == var_sol[DIR_Y]:
                            is_found = True
                            new_sol.append(var_sol)

                    new_sols[min_prob_k][adjacent_i][min_prob_j] = new_sol.copy()
                    if not is_found:
                        is_all_fulfilled = False
                        break

            adjacent_k = min_prob_k + delta
            if 0 <= adjacent_k < floor_cnt:
                # 对比同行同列相邻层的-z方向、当前元素的z方向
                if delta > 0:
                    is_found = False
                    new_sol = []
                    for var_sol in var_sols[adjacent_k][min_prob_i][min_prob_j]:
                        if sol[DIR_Z] == var_sol[DIR_Z_NEG]:
                            is_found = True
                            new_sol.append(var_sol)

                    new_sols[adjacent_k][min_prob_i][min_prob_j] = new_sol.copy()
                    if not is_found:
                        is_all_fulfilled = False
                        break

                # 对比同层同列上一行的z方向、当前元素的-z方向
                if delta < 0:
                    is_found = False
                    new_sol = []
                    for var_sol in var_sols[adjacent_k][min_prob_i][min_prob_j]:
                        if sol[DIR_Z_NEG] == var_sol[DIR_Z]:
                            is_found = True
                            new_sol.append(var_sol)

                    new_sols[adjacent_k][min_prob_i][min_prob_j] = new_sol.copy()
                    if not is_found:
                        is_all_fulfilled = False
                        break

        # sol[min_prob_k][min_prob_i][min_prob_j]的改变和周围立方块没有冲突
        if is_all_fulfilled:
            is_all_adjacencys_fulfilled = True
            # sol[min_prob_k][min_prob_i][min_prob_j]的改变，筛掉了周围立方块一部分的可能性
            # 要看看剩下的这些可能性和他们周围的立方块有没有冲突，如果没有，新的sol[min_prob_k][min_prob_i][min_prob_j]视为合法解
            tmp_sols = copy.deepcopy(new_sols)
            for delta in range(-2, -2, -2):
            # for delta in range(1, -2, -2):
                adjacent_j = min_prob_j + delta
                if 0 <= adjacent_j < col_cnt:
                    res = is_adjacencys_fulfilled(new_sols, min_prob_k, min_prob_i, adjacent_j, min_prob_k, min_prob_i, min_prob_j)
                    if len(res.keys()) == 0:
                        is_all_adjacencys_fulfilled = False
                        break

                    tmp_sols = replace_sub_dicts(tmp_sols, res)

                adjacent_i = min_prob_i + delta
                if 0 <= adjacent_i < row_cnt:
                    res = is_adjacencys_fulfilled(new_sols, min_prob_k, adjacent_i, min_prob_j, min_prob_k, min_prob_i, min_prob_j)
                    if len(res.keys()) == 0:
                        is_all_adjacencys_fulfilled = False
                        break

                    tmp_sols = replace_sub_dicts(tmp_sols, res)

                adjacent_k = min_prob_k + delta
                if 0 <= adjacent_k < floor_cnt:
                    res = is_adjacencys_fulfilled(new_sols, adjacent_k, min_prob_i, min_prob_j, min_prob_k, min_prob_i, min_prob_j)
                    if len(res.keys()) == 0:
                        is_all_adjacencys_fulfilled = False
                        break

                    tmp_sols = replace_sub_dicts(tmp_sols, res)

            if is_all_adjacencys_fulfilled:
                print(996)
                validated_coords.append([min_prob_k, min_prob_i, min_prob_j])
                tmp_sols[min_prob_k][min_prob_i][min_prob_j] = [sol]
                if get_sols(tmp_sols):
                    print(998)
                    return True
                else:
                    validated_coords.pop()

    print(997)
    return False


# 打印3d透视图
def get_3d_str(var_sol):
    upper_str = ""
    # 3d图上层：-x、z、-y方向
    if var_sol[DIR_X_NEG] == 1 or var_sol[DIR_Z] == 1 or var_sol[DIR_Y_NEG] == 1:
        if var_sol[DIR_X_NEG] == 1:
            upper_str += "↖ "
        else:
            upper_str += "   "

        if var_sol[DIR_Z] == 1:
            upper_str += "↑"
        else:
            upper_str += " "

        if var_sol[DIR_Y_NEG] == 1:
            upper_str += " ↗"

    middle_str = "   ×"
    lower_str = ""
    # 3d图下层：y、-z、x方向
    if var_sol[DIR_Y] == 1 or var_sol[DIR_Z_NEG] == 1 or var_sol[DIR_X] == 1:
        if var_sol[DIR_Y] == 1:
            lower_str += "↙ "
        else:
            lower_str += "   "

        if var_sol[DIR_Z_NEG] == 1:
            lower_str += "↓"
        else:
            lower_str += " "

        if var_sol[DIR_X] == 1:
            lower_str += " ↘"

    return "{}\r{}\r{}\r".format(upper_str, middle_str, lower_str)


question_start_idx = 20
question_cnt = 1
for question_num in range(question_start_idx, question_start_idx + question_cnt):
    # questions/{0}.csv是题目数组
    with open("questions/{0}.csv".format(question_num), 'r', encoding='utf-8') as question_file:
        elements = question_file.readlines()
        ele_cnt = len(elements)
        row_cnt = 2
        col_cnt = 2
        floor_cnt = 2
        if ele_cnt == 12:
            row_cnt = 3
            col_cnt = 2
        elif ele_cnt == 18:
            row_cnt = 3
            col_cnt = 3
        elif ele_cnt == 27:
            row_cnt = 3
            col_cnt = 3
            floor_cnt = 3
        elif ele_cnt == 36:
            row_cnt = 3
            col_cnt = 4
            floor_cnt = 3
        elif ele_cnt == 48:
            row_cnt = 4
            col_cnt = 4
            floor_cnt = 3

        cnt_per_floor = row_cnt * col_cnt
        sols = {}
        validated_coords = []
        step_idx = 0
        with open("interfaces/{0}-{1}-{2}.json".format(row_cnt, col_cnt, floor_cnt), 'r',
                  encoding='utf-8') as interface_file:
            # interface_file记录的是每个立方块在6个方向接触到的、来自于其他立方块凸出的可能性（每个元素的格式：[x, y, z, -x, -y, -z]）
            # 如[[1, 0], [0], [0], [0], [0], [0]]，意味着只有在x方向可能会接触到凸出，其他方向不可能会接触凸出
            interfacess = json.load(interface_file)
            out_interfacess = {}
            for k in range(floor_cnt):
                out_interfacess[k] = {}
                for i in range(row_cnt):
                    out_interfacess[k][i] = {}
                    for j in range(col_cnt):
                        ele_idx = cnt_per_floor * k + col_cnt * i + j
                        out_interfacess[k][i][j] = interfacess[ele_idx]

            init_sols()
            print(1000)
            for k in range(floor_cnt):
                for i in range(row_cnt):
                    for j in range(col_cnt):
                        print(k, i, j, sols[k][i][j])

            get_sols(sols)
            with open("answers/{0}.txt".format(question_num), "w", encoding="utf-8") as answer_file:
                for k in range(floor_cnt):
                    for i in range(row_cnt):
                        for j in range(col_cnt):
                            print(k, i, j, sols[k][i][j])
                            step_idx += 1
                            answer_file.write("\r{:0>2d}.第{}层 第{}行 第{}列 3d透视图如下：\r"
                                              .format(step_idx, k + 1, i + 1, j + 1))
                            answer_file.write(get_3d_str(sols[k][i][j][0]))
