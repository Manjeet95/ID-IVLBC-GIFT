# IDs-IVLBC-GIFT
For finding IDs, our employed method has the following three steps:
- Partitioning the set
- Pairwise examination
- Identification of IDs

## IVLBC:
- RepresentativeSet_Algo.py: This is the source code of our introduced algorithm to find the representative set.
  
- ddt.py: This is used for computing the partition table whose keys are the elements of the representative set. In this, we only consider first 16 elements from the representative set (after sorting the representative set) and find the corresponding partition table.
  
- IVLBC_Potential_Pairs_MILP.py: Write the representative set and its partition table at positions 'representatives' and 'ddt' in 'IVLBC_Potential_Pairs_MILP.py' and 'IVLBC_IDs_MILP.py', respectively. Here, we only consider those input and output differences, which consists of exactly one active 16-bit block. For considering such differences, we choose the representative pairs by dividing the input representatives tuples into 16 parts. We have done it to run the code within the available resources. Finally, this code provides the potential pairs that may contain IDs within the selected search space.
  
- IVLBC_IDs_MILP.py: Use the above potential pairs (from each part) in 'IVLBC_IDs_MILP.py' at the position 'non_feasible_diff'. Then, we execute the code and get the IDs within all 16 parts. Finally, adding all the IDs in all parts, we have total IDs.  
  
## GIFT:
- RepresentativeSet_Algo.py: This is source code of our introduced algorithm to find the representative set.
  
- ddt.py: This is used for computing the partition table whose keys are the elements of the representative set. In this, we only consider first 14 elements from representative sets (after sorting representative sets) for input and output differences. Here, we find the corresponding partition tables.
  
- GIFT_Potential_Pairs_MILP.py: Write representative sets and their partition tables in 'GIFT_Potential_Pairs_MILP.py' at positions 'in_rep and out_rep' and 'ddt1 and ddt2' in 'GIFT_Potential_Pairs_MILP.py' and 'GIFT_IDs_MILP.py', respectively. Here, we only consider those input and output differences, which consists of exactly one active 16-bit block. For considering such differences, we choose the representative pairs by dividing the input representatives tuples into 14 parts. We have done it to run the code within the available resources. Finally, this code provides the potential pairs that may contain IDs.
   
- GIFT_IDs_MILP.py: Use the above potential pairs (from each part) in 'GIFT_IDs_MILP.py' at the position 'non_feasible_diff'. Then, we execute the code and get the IDs within all 14 parts. Finally, adding all the IDs in all parts, we have total IDs within the selected search space.  
