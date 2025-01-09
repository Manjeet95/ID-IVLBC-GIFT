import time
import sys
from multiprocessing import Pool, cpu_count
from itertools import combinations

sys.set_int_max_str_digits(0)

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

def calculate_ddt_bitwise_or_precomputed(sms_table, size):
    ddt = [0] * size  # Initialize a list of zeros for each possible column difference
    seen_rows = set()  # Set to track seen rows in DDT

    with Pool(cpu_count()) as pool:
        for input_diff in range(size):
            results = pool.map(calculate_ddt_worker, [(x, input_diff, sms_table) for x in range(size)])
            for output_diff in results:
                ddt[output_diff] |= (1 << input_diff)
    
    # Filter out duplicate rows
    #unique_ddt = []
    #for row in ddt:
    #    if row not in seen_rows:
    #        unique_ddt.append(row)
    #        seen_rows.add(row)

    return ddt #unique_ddt

def print_ddt_summary(ddt, num_entries=2 ** (2)):
    print("DDT Summary:")
    for index, row_mask in enumerate(ddt[:num_entries]):  # Print only the first `num_entries` entries
        print(f"Column {index:2}: {bin(row_mask)}")
    if len(ddt) > num_entries:
        print(f"... {len(ddt) - num_entries} more entries")

def print_ddt_statistics(ddt):
    non_zero_count = sum(1 for row in ddt if row != 0)
    print("DDT Statistics:")
    print(f"Total entries: {len(ddt)}")
    print(f"Non-zero entries: {non_zero_count}")

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
        #print("Covered bits:", bin(covered_bits))
        print("Length of covered bits:", covered_bits.bit_length())

    return selected_columns

if __name__ == "__main__":
    n = int(input("Enter the value of n: "))
    size = 2**(n)
    P = [0, 5, 10, 15, 12, 1, 6, 11, 8, 13, 2, 7, 4, 9, 14, 3]
    
    S = [0x1, 0xa, 0x4, 0xc, 0x6, 0xf, 0x3, 0x9, 0x2, 0xd, 0xb, 0x7, 0x5, 0x0, 0x8, 0xe]
    #S = [0xd, 0x0, 0x8, 0x6, 0x2, 0xc, 0x4, 0xb, 0xe, 0x7, 0x1, 0xa, 0x3, 0x9, 0xf, 0x5]
    # Precompute SMS values
    # Time measurement for precomputing SMS values
    start_time = time.time()
    sms_table = precompute_sms(size, S, P, n)
    print("sms_table = ", sms_table)
    end_time = time.time()
    print(f"Time taken to precompute SMS table: {end_time - start_time:.2f} seconds")

    # Time measurement for calculating DDT
    start_time = time.time()
    # Calculate DDT using bitwise OR with precomputed SMS values
    ddt = calculate_ddt_bitwise_or_precomputed(sms_table, size)
    #print(ddt)
    end_time = time.time()
    print(f"Time taken to calculate DDT: {end_time - start_time:.2f} seconds")
    
    #print_ddt_summary(ddt)  # Print summary of the DDT
    #print_ddt_statistics(ddt)  # Print statistics about the DDT
    print("length of ddt: ", len(ddt))

    # Time measurement for finding minimum columns using greedy approach
    start_time = time.time()
    # Find the minimum columns required
    exact_selected_columns = find_minimum_columns(ddt, n)
    end_time = time.time()
    print(f"Time taken to find minimum columns using greedy approach: {end_time - start_time:.2f} seconds")
    
    # Output the result
    print("Minimum columns required to cover all bits using greedy approach:")
    print(exact_selected_columns)
    print("Minimum selected columns: ", len(exact_selected_columns))
