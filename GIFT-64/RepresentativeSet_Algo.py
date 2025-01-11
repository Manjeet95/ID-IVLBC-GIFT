import time
import sys
from multiprocessing import Pool, cpu_count
from itertools import combinations

sys.set_int_max_str_digits(0)

def apply_sbox(input_bits, sbox):
    return sbox[input_bits]

def apply_permutation(input_bits, permutation, n):
    output_bits = 0
    for i in range(n):
        if input_bits & (1 << i):
            output_bits |= (1 << permutation[i])
    return output_bits
    
def SPS(input_value, sbox, permutation, n):
    blocks = [(input_value >> (4 * i)) & 0xF for i in range(n // 4)]
    
    # Apply the S-box to each 4-bit block
    substituted_blocks = [apply_sbox(block, sbox) for block in blocks]
    
    # Combine the substituted blocks into a single 16-bit value
    substituted_value = 0
    for i in range(n // 4):
        substituted_value |= (substituted_blocks[i] << (4 * i))
    
    # Apply the permutation to the 16-bit substituted value
    state_value = apply_permutation(substituted_value, permutation, n)

    # Split state_value into four 4-bit blocks
    blocks = [(state_value >> (4 * i)) & 0xF for i in range(n // 4)]
    
    # Apply the S-box to each 4-bit block
    substituted_blocks = [apply_sbox(block, sbox) for block in blocks]

    # Combine the substituted blocks into a single 16-bit value
    output_value = 0
    for i in range(n // 4):
        output_value |= (substituted_blocks[i] << (4 * i))
    
    return output_value

def precompute_sps_worker(args):
    x, sbox, P, n = args
    return SPS(x, sbox, P, n)

def precompute_sps(size, sbox, P, n):
    with Pool(cpu_count()) as pool:
        sps_table = pool.map(precompute_sps_worker, [(x, sbox, P, n) for x in range(size)])
    return sps_table

def calculate_ddt_worker(args):
    x, input_diff, sps_table = args
    return sps_table[x] ^ sps_table[x ^ input_diff]

def calculate_ddt_bitwise_or_precomputed(sps_table, size):
    ddt = [0] * size  # Initialize a list of zeros for each possible column difference

    with Pool(cpu_count()) as pool:
        for input_diff in range(size):
            results = pool.map(calculate_ddt_worker, [(x, input_diff, sps_table) for x in range(size)])
            for output_diff in results:
                ddt[output_diff] |= (1 << input_diff)
    return ddt

def print_ddt_summary(ddt, num_entries=2 ** (10)):
    print("DDT Summary:")
    for index, row_mask in enumerate(ddt[:num_entries]):
        print(f"Column {index:2}: {bin(row_mask)}")
    if len(ddt) > num_entries:
        print(f"... {len(ddt) - num_entries} more entries")

def find_minimum_columns(ddt, n):
    target = (1 << (2**n)) - 1  # All bits set to 1
    covered_bits = 0
    selected_columns = []

    while covered_bits != target:
        # Find the column that covers the most new bits
        best_column = -1
        best_new_coverage = 0

        for i, column in enumerate(ddt):
            new_coverage = column | covered_bits
            # Newly covered bits (use bitwise AND to isolate new bits)
            newly_covered_bits = new_coverage & ~covered_bits  # Only the new bits

            # Count the number of newly covered bits using bit_count()
            new_bit_count = newly_covered_bits.bit_count()

            # Update if this column covers more new bits
            if new_bit_count > best_new_coverage:
                best_new_coverage = new_bit_count
                best_column = i

        if best_column == -1:
            print("No combination found to cover all bits!")
            return []

        # Update covered_bits and add the selected column
        covered_bits |= ddt[best_column]
        selected_columns.append(best_column)
    if covered_bits == target:
        print("All bits covered!")
        print("Length of covered bits:", covered_bits.bit_length())

    return selected_columns

if __name__ == "__main__":
    n = int(input("Enter the value of n: "))
    size = 2**(n)
    
    P = [0, 5, 10, 15, 12, 1, 6, 11, 8, 13, 2, 7, 4, 9, 14, 3]
    
    #S = [0x1, 0xa, 0x4, 0xc, 0x6, 0xf, 0x3, 0x9, 0x2, 0xd, 0xb, 0x7, 0x5, 0x0, 0x8, 0xe] # S-box
    S = [0xd, 0x0, 0x8, 0x6, 0x2, 0xc, 0x4, 0xb, 0xe, 0x7, 0x1, 0xa, 0x3, 0x9, 0xf, 0x5] # Inverse S-box
    
    # Precompute SPS values
    start_time = time.time()
    sps_table = precompute_sps(size, S, P, n)
    print("sps_table = ", sps_table)
    end_time = time.time()
    print(f"Time taken to precompute SPS table: {end_time - start_time:.2f} seconds")

    # Time measurement for calculating DDT
    start_time = time.time()
    # Calculate DDT using bitwise OR with precomputed SPS values
    ddt = calculate_ddt_bitwise_or_precomputed(sps_table, size)
    end_time = time.time()
    print(f"Time taken to calculate DDT: {end_time - start_time:.2f} seconds")
    
    print_ddt_summary(ddt) # Print only the first `num_entries=2 ** (10)` entries
    print("length of ddt: ", len(ddt))

    # Time measurement for finding minimum columns using greedy approach
    start_time = time.time()
    
    # Find the minimum columns required
    exact_selected_columns = find_minimum_columns(ddt, n)
    end_time = time.time()
    print(f"Time taken to find minimum columns using greedy approach: {end_time - start_time:.2f} seconds")
    
    # Output
    print("Minimum columns required to cover all bits using greedy approach:")
    print(exact_selected_columns)
    print("Minimum selected columns: ", len(exact_selected_columns))
