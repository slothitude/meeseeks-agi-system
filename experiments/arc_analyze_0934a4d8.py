#!/usr/bin/env python3
"""
Analyze the relationship between 8-block and output for task 0934a4d8
"""

import numpy as np

def analyze_pair(input_grid, expected_output, name):
    input_grid = np.array(input_grid)
    expected_output = np.array(expected_output)
    
    print(f"\n{'='*60}")
    print(f"Analyzing: {name}")
    print(f"{'='*60}")
    
    # Find 8-block bounding box
    rows_with_8 = set()
    cols_with_8 = set()
    for i in range(input_grid.shape[0]):
        if 8 in input_grid[i, :]:
            rows_with_8.add(i)
    for j in range(input_grid.shape[1]):
        if 8 in input_grid[:, j]:
            cols_with_8.add(j)
    
    min_row, max_row = min(rows_with_8), max(rows_with_8)
    min_col, max_col = min(cols_with_8), max(cols_with_8)
    
    print(f"8-block bounding box: rows {min_row}-{max_row}, cols {min_col}-{max_col}")
    print(f"8-block size: {max_row-min_row+1}x{max_col-min_col+1}")
    print(f"Expected output size: {expected_output.shape[0]}x{expected_output.shape[1]}")
    
    # Extract the 8-block region
    extracted = input_grid[min_row:max_row+1, min_col:max_col+1]
    
    print(f"\nExtracted region (8-block bounding box):")
    print(extracted)
    
    print(f"\nExpected output:")
    print(expected_output)
    
    # Check if expected output appears anywhere in the input
    print(f"\nSearching for expected output pattern in input...")
    
    for i in range(input_grid.shape[0] - expected_output.shape[0] + 1):
        for j in range(input_grid.shape[1] - expected_output.shape[1] + 1):
            region = input_grid[i:i+expected_output.shape[0], j:j+expected_output.shape[1]]
            if np.array_equal(region, expected_output):
                print(f"  FOUND at row {i}, col {j}")
                break
        else:
            continue
        break
    else:
        print("  NOT FOUND as direct match")
    
    # Check what's unique about the output
    print(f"\nUnique colors in expected output: {np.unique(expected_output)}")
    print(f"Unique colors in 8-block region: {np.unique(extracted)}")
    
    # Check the row indices where output might come from
    print(f"\nChecking if output rows come from specific positions...")
    for out_row in range(expected_output.shape[0]):
        for in_row in range(input_grid.shape[0]):
            if np.array_equal(input_grid[in_row, min_col:max_col+1], expected_output[out_row, :]):
                print(f"  Output row {out_row} = Input row {in_row}")
                break
        else:
            # Check if it's a match with some transformation
            for in_row in range(input_grid.shape[0]):
                if np.array_equal(input_grid[in_row, min_col:max_col+1][::-1], expected_output[out_row, :]):
                    print(f"  Output row {out_row} = Input row {in_row} (reversed)")
                    break

# Training example 1
train1_input = [[3, 1, 1, 9, 5, 6, 7, 1, 1, 4, 5, 7, 3, 9, 9, 1, 1, 9, 9, 3, 7, 5, 4, 1, 1, 7, 6, 5, 9, 1], [1, 3, 9, 5, 6, 5, 1, 7, 4, 1, 7, 5, 4, 3, 1, 3, 3, 1, 3, 4, 5, 7, 1, 4, 7, 1, 5, 6, 5, 9], [6, 9, 3, 1, 7, 1, 5, 6, 9, 9, 1, 4, 9, 1, 1, 4, 4, 1, 1, 9, 4, 1, 9, 9, 6, 5, 1, 7, 1, 3], [9, 1, 1, 3, 1, 7, 6, 5, 9, 9, 4, 1, 1, 3, 4, 1, 1, 4, 3, 1, 1, 4, 9, 9, 5, 6, 7, 1, 3, 1], [6, 6, 6, 7, 3, 1, 5, 9, 3, 4, 9, 1, 6, 7, 2, 5, 5, 2, 7, 6, 1, 9, 4, 3, 9, 5, 1, 3, 7, 6], [6, 6, 7, 6, 1, 3, 9, 1, 9, 3, 1, 3, 7, 6, 5, 2, 2, 5, 6, 7, 3, 1, 3, 9, 1, 9, 3, 1, 6, 7], [6, 7, 6, 6, 1, 9, 3, 1, 9, 1, 1, 4, 6, 9, 6, 7, 7, 6, 9, 6, 4, 1, 1, 9, 1, 3, 9, 1, 6, 6], [7, 6, 6, 6, 9, 6, 1, 3, 1, 3, 4, 1, 9, 6, 7, 6, 6, 7, 6, 9, 1, 4, 3, 1, 3, 1, 8, 8, 8, 8], [1, 4, 9, 9, 3, 9, 9, 1, 1, 1, 6, 1, 5, 2, 5, 5, 5, 5, 2, 5, 1, 6, 1, 1, 1, 9, 8, 8, 8, 8], [4, 1, 9, 9, 4, 3, 1, 3, 1, 1, 1, 6, 2, 5, 5, 5, 5, 5, 5, 2, 6, 1, 1, 1, 3, 1, 8, 8, 8, 8], [5, 7, 1, 4, 9, 1, 1, 4, 2, 2, 1, 1, 5, 5, 5, 2, 2, 5, 5, 5, 1, 1, 2, 2, 4, 1, 8, 8, 8, 8], [7, 5, 4, 1, 1, 3, 4, 1, 2, 1, 1, 1, 5, 5, 2, 5, 5, 2, 5, 5, 1, 1, 1, 2, 1, 4, 3, 1, 1, 4], [3, 4, 9, 1, 6, 7, 6, 9, 7, 6, 3, 3, 1, 1, 6, 1, 1, 6, 1, 1, 3, 3, 6, 7, 9, 6, 7, 6, 1, 9], [9, 3, 1, 3, 7, 6, 9, 6, 6, 7, 3, 3, 1, 1, 1, 6, 6, 1, 1, 1, 3, 3, 7, 6, 6, 9, 6, 7, 3, 1], [9, 1, 1, 4, 2, 5, 6, 7, 3, 3, 7, 6, 1, 2, 1, 1, 1, 1, 2, 1, 6, 7, 3, 3, 7, 6, 5, 2, 4, 1], [1, 3, 4, 1, 5, 2, 7, 6, 3, 3, 6, 7, 2, 2, 1, 1, 1, 1, 2, 2, 7, 6, 3, 3, 6, 7, 2, 5, 1, 4], [1, 3, 4, 1, 5, 2, 7, 6, 3, 3, 6, 7, 2, 2, 1, 1, 1, 1, 2, 2, 7, 6, 3, 3, 6, 7, 2, 5, 1, 4], [9, 1, 1, 4, 2, 5, 6, 7, 3, 3, 7, 6, 1, 2, 1, 1, 1, 1, 2, 1, 6, 7, 3, 3, 7, 6, 5, 2, 4, 1], [9, 3, 1, 3, 7, 6, 9, 6, 6, 7, 3, 3, 1, 1, 1, 6, 6, 1, 1, 1, 3, 3, 7, 6, 6, 9, 6, 7, 3, 1], [3, 4, 9, 1, 6, 7, 6, 9, 7, 6, 3, 3, 1, 1, 6, 1, 1, 6, 1, 1, 3, 3, 6, 7, 9, 6, 7, 6, 1, 9], [7, 5, 4, 1, 1, 3, 4, 1, 2, 1, 1, 1, 5, 5, 2, 5, 5, 2, 5, 5, 1, 1, 1, 2, 1, 4, 3, 1, 1, 4], [5, 7, 1, 4, 9, 1, 1, 4, 2, 2, 1, 1, 5, 5, 5, 2, 2, 5, 5, 5, 1, 1, 2, 2, 4, 1, 1, 9, 4, 1], [4, 1, 9, 9, 4, 3, 1, 3, 1, 1, 1, 6, 2, 5, 5, 5, 5, 5, 5, 2, 6, 1, 1, 1, 3, 1, 3, 4, 9, 9], [1, 4, 9, 9, 3, 9, 9, 1, 1, 1, 6, 1, 5, 2, 5, 5, 5, 5, 2, 5, 1, 6, 1, 1, 1, 9, 9, 3, 9, 9], [7, 6, 6, 6, 9, 6, 1, 3, 1, 3, 4, 1, 9, 6, 7, 6, 6, 7, 6, 9, 1, 4, 3, 1, 3, 1, 6, 9, 6, 6], [6, 7, 6, 6, 1, 9, 3, 1, 9, 1, 1, 4, 6, 9, 6, 7, 7, 6, 9, 6, 4, 1, 1, 9, 1, 3, 9, 1, 6, 6], [6, 6, 7, 6, 1, 3, 9, 1, 9, 3, 1, 3, 7, 6, 5, 2, 2, 5, 6, 7, 3, 1, 3, 9, 1, 9, 3, 1, 6, 7], [6, 6, 6, 7, 3, 1, 5, 9, 3, 4, 9, 1, 6, 7, 2, 5, 5, 2, 7, 6, 1, 9, 4, 3, 9, 5, 1, 3, 7, 6], [9, 1, 1, 3, 1, 7, 6, 5, 9, 9, 4, 1, 1, 3, 4, 1, 1, 4, 3, 1, 1, 4, 9, 9, 5, 6, 7, 1, 3, 1], [6, 9, 3, 1, 7, 1, 5, 6, 9, 9, 1, 4, 9, 1, 1, 4, 4, 1, 1, 9, 4, 1, 9, 9, 6, 5, 1, 7, 1, 3]]
train1_output = [[6, 9, 6, 6], [9, 3, 9, 9], [3, 4, 9, 9], [1, 9, 4, 1]]

analyze_pair(train1_input, train1_output, "Training Example 1")
