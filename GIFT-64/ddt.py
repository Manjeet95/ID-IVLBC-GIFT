import sys
import os
from gurobipy import GRB, read
import itertools
from itertools import product
from collections import defaultdict
from multiprocessing import Pool, cpu_count

def apply_sbox(input_bits, sbox):
    return sbox[input_bits]

def apply_permutation(input_bits, permutation, n):
    """Applies the permutation to a 16-bit input."""
    output_bits = 0
    for i in range(n):
        # Extract the i-th bit from input_bits and place it at the new position
        if input_bits & (1 << i):
            output_bits |= (1 << permutation[i])
    return output_bits
    
def SMS(input_value, sbox, permutation, n):
    blocks = [(input_value >> (4 * i)) & 0xF for i in range(n // 4)]
    
    # Apply the S-box to each 4-bit block
    substituted_blocks = [apply_sbox(block, sbox) for block in blocks]
    
    # Combine the substituted blocks into a single 16-bit value
    substituted_value = 0
    for i in range(n // 4):
        substituted_value |= (substituted_blocks[i] << (4 * i))
    
    # Apply the permutation to the 16-bit substituted value
    state_value = apply_permutation(substituted_value, permutation, n)

    # Split input_value into four 4-bit blocks
    blocks = [(state_value >> (4 * i)) & 0xF for i in range(n // 4)]
    
    # Apply the S-box to each 4-bit block
    substituted_blocks = [apply_sbox(block, sbox) for block in blocks]

    # Combine the substituted blocks into a single 16-bit value
    output_value = 0
    for i in range(n // 4):
        output_value |= (substituted_blocks[i] << (4 * i))
    
    return output_value

def precompute_sms_worker(args):
    x, sbox, P, n = args
    return SMS(x, sbox, P, n)

def precompute_sms(size, sbox, P, n):
    with Pool(cpu_count()) as pool:
        sms_table = pool.map(precompute_sms_worker, [(x, sbox, P, n) for x in range(size)])
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
    P = [0, 5, 10, 15, 12, 1, 6, 11, 8, 13, 2, 7, 4, 9, 14, 3]
    
    S = [0x1, 0xa, 0x4, 0xc, 0x6, 0xf, 0x3, 0x9, 0x2, 0xd, 0xb, 0x7, 0x5, 0x0, 0x8, 0xe]
    #S = [0xd, 0x0, 0x8, 0x6, 0x2, 0xc, 0x4, 0xb, 0xe, 0x7, 0x1, 0xa, 0x3, 0x9, 0xf, 0x5] # Inverse
    size = 2 ** (m)
    representatives = [0, 13, 161, 2039, 2480, 4354, 7901, 14777, 30427, 37113, 39359, 40025, 40461, 40861]  # <-- ddt2
    #[0, 2006, 2105, 2821, 4133, 12299, 15871, 25552, 30590, 31199, 31868, 32160, 34527, 37043] # <-- ddt1
    sms_table = precompute_sms(size, S, P, m)
    ddt = calculate_ddt(sms_table, size, representatives)
    #print(ddt)
    print(f"representatives = {len(representatives)}")
    for i in ddt.keys():
        print(f"ddt[{i}] = {len(ddt[i])}")
    
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
    #print("H = ", H)

    X = [x for x in range(size)]
    for i in ddt.keys():
        X = [x for x in X if x not in ddt[i]]

    if not X:
        print("X is empty")
    else:
        print("X is not empty \n X = ", X, " with length = ", len(X))
    print("H = ", H)
        
    
        
