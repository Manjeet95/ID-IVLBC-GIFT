import sys
import os
from gurobipy import GRB, read
import itertools
from itertools import product
from collections import defaultdict
from multiprocessing import Pool, cpu_count

def apply_matrix_to_column(matrix, input_value, n):
    input_value = input_value & ((1 << n) - 1)
    blocks = []
    for i in range(4):
        shift_amount = 12 - 4 * i
        block = (input_value >> shift_amount) & 0xF
        blocks.append(block)
    result = 0
    for row in range(4):
        row_value = 0
        for col in range(4):
            if matrix[row][col] == 1:
                row_value ^= blocks[col]
        result |= (row_value << (12 - 4 * row))
    return result

def SMS(input_value, sbox, MC, n):
    blocks = [(input_value >> (4 * i)) & 0xF for i in range(n // 4)]
    substituted_blocks = [sbox[block] for block in blocks]
    substituted_value = 0
    for i in range(n // 4):
        substituted_value |= (substituted_blocks[i] << (4 * i))
    state_value = apply_matrix_to_column(MC, substituted_value, n)
    blocks = [(state_value >> (4 * i)) & 0xF for i in range(n // 4)]
    substituted_blocks = [sbox[block] for block in blocks]
    output_value = 0
    for i in range(n // 4):
        output_value |= (substituted_blocks[i] << (4 * i))
    return output_value

def precompute_sms_worker(args):
    x, sbox, MC, m = args
    return SMS(x, sbox, MC, m)

def precompute_sms(size, sbox, MC, m):
    with Pool(cpu_count()) as pool:
        sms_table = pool.map(precompute_sms_worker, [(x, sbox, MC, m) for x in range(size)])
    return sms_table

def calculate_ddt_worker(args):
    x, input_diff, sms_table = args
    return sms_table[x] ^ sms_table[x ^ input_diff]

def calculate_ddt(sms_table, size, representatives):
    ddt = defaultdict(list)
    with Pool(cpu_count()) as pool:
        for input_diff in representatives:
            buf = ''
            if (input_diff%(5)==0):
                print(input_diff)
            results = list(set(pool.map(calculate_ddt_worker, [(x, input_diff, sms_table) for x in range(size)])))
            ddt[input_diff] = results
    return ddt


if __name__ == "__main__":
    m = 16
    S = [0x0, 0xf, 0xe, 0x5, 0xd, 0x3, 0x6, 0xc, 0xb, 0x9, 0xa, 0x8, 0x7, 0x4, 0x2, 0x1]
    MC = [
        [0, 1, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
    ]
    size = 2 ** (m)
    representatives = [5774, 10413, 9647, 10415, 6636, 36263, 26527, 21198, 54010, 11038, 8168, 48377, 47849, 49593, 40941, 47644, 35566, 27165, 31630, 50078, 26769, 37778, 39273, 32733, 36345, 55722, 39047, 31947, 40094, 47276, 570, 17016, 687, 8234, 8367, 8714, 8864, 10767, 10992, 17949, 298, 302, 307, 4138, 4142, 4147, 4618, 4622, 4768, 4832, 4867, 4912, 0, 38, 275, 282, 1092, 4115, 4123, 4355, 4363, 4400, 4528, 16452, 16480, 17412, 17472, 17476]
    representatives.sort()
    sms_table = precompute_sms(size, S, MC, m)
    ddt = calculate_ddt(sms_table, size, representatives[:16])
    print(f"representatives = {representatives} with length = {len(representatives)}")
    for i in ddt.keys():
        print(f"ddt[{i}] = {len(ddt[i])}")
    #print(ddt)
    H = defaultdict(list)
    for i in ddt.keys():
        H[i] = ddt[i]
        for j in ddt.keys():
            if j != i:
                ddt[j] = [x for x in ddt[j] if x not in H[i]] 
    total = 0
    for i in H.keys():
        print(f"H[{i}] = {len(H[i])}")
        total = total + len(H[i])
    print("total = ", total)
    
    print("H = ", H)
