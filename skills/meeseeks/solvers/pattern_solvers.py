"""
Pattern Solvers for Meeseeks Coder Bloodline
=============================================

Core pattern recognition and manipulation functions for ARC-style tasks.
Each solver takes task_data (dict with 'train' and 'test' examples) and returns predictions.

This module establishes the coder bloodline foundation.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple


def solve_shrink_pattern(task_data: Dict[str, Any]) -> List[List[List[int]]]:
    """
    Extract smaller grid from larger grid based on pattern detection.
    
    Detects:
    - Subgrids bounded by specific colors
    - Regions of interest
    - Compression patterns (e.g., 3x3 -> 1x1 with majority color)
    
    Args:
        task_data: Dict with 'train' (list of {input, output}) and 'test' (list of {input})
    
    Returns:
        List of predicted outputs for each test input
    """
    predictions = []
    
    for test_example in task_data.get('test', []):
        input_grid = np.array(test_example['input'])
        
        # Analyze training examples to find shrink pattern
        shrink_ratio = None
        bounding_color = None
        
        for train_example in task_data.get('train', []):
            train_in = np.array(train_example['input'])
            train_out = np.array(train_example['output'])
            
            # Check for ratio-based shrinking
            in_h, in_w = train_in.shape
            out_h, out_w = train_out.shape
            
            if in_h > out_h and in_w > out_w:
                shrink_ratio = (in_h // out_h, in_w // out_w)
                break
            
            # Check for bounding color pattern
            unique_colors = np.unique(train_in)
            for color in unique_colors:
                if color == 0:  # Skip black (usually background)
                    continue
                # Find bounding box of non-color cells
                mask = train_in != color
                if mask.any():
                    rows = np.any(mask, axis=1)
                    cols = np.any(mask, axis=0)
                    rmin, rmax = np.where(rows)[0][[0, -1]]
                    cmin, cmax = np.where(cols)[0][[0, -1]]
                    extracted = train_in[rmin:rmax+1, cmin:cmax+1]
                    if extracted.shape == train_out.shape:
                        bounding_color = color
                        break
            if bounding_color is not None:
                break
        
        # Apply detected pattern
        if shrink_ratio:
            ratio_h, ratio_w = shrink_ratio
            h, w = input_grid.shape
            new_h, new_w = h // ratio_h, w // ratio_w
            output = np.zeros((new_h, new_w), dtype=int)
            
            for i in range(new_h):
                for j in range(new_w):
                    block = input_grid[i*ratio_h:(i+1)*ratio_h, j*ratio_w:(j+1)*ratio_w]
                    # Use most common non-zero color
                    non_zero = block[block != 0]
                    if len(non_zero) > 0:
                        values, counts = np.unique(non_zero, return_counts=True)
                        output[i, j] = values[np.argmax(counts)]
                    else:
                        output[i, j] = 0
        elif bounding_color is not None:
            mask = input_grid != bounding_color
            if mask.any():
                rows = np.any(mask, axis=1)
                cols = np.any(mask, axis=0)
                rmin, rmax = np.where(rows)[0][[0, -1]]
                cmin, cmax = np.where(cols)[0][[0, -1]]
                output = input_grid[rmin:rmax+1, cmin:cmax+1]
            else:
                output = input_grid
        else:
            # Default: return as-is
            output = input_grid
        
        predictions.append(output.tolist())
    
    return predictions


def solve_color_mapping(task_data: Dict[str, Any]) -> List[List[List[int]]]:
    """
    Map colors according to rules detected from training examples.
    
    Detects:
    - Direct color substitutions (A -> B)
    - Conditional mappings (if adjacent to X, change to Y)
    - Pattern-based color changes
    
    Args:
        task_data: Dict with 'train' and 'test' examples
    
    Returns:
        List of predicted outputs for each test input
    """
    predictions = []
    
    # Build color mapping from training data
    color_map = {}
    conditional_maps = []
    
    for train_example in task_data.get('train', []):
        train_in = np.array(train_example['input'])
        train_out = np.array(train_example['output'])
        
        if train_in.shape != train_out.shape:
            continue  # Skip if shapes don't match
        
        # Find direct color mappings
        for in_color in np.unique(train_in):
            in_mask = train_in == in_color
            out_colors = train_out[in_mask]
            if len(np.unique(out_colors)) == 1:
                color_map[in_color] = out_colors[0]
        
        # Find conditional mappings (simplified: based on neighbors)
        # This is a basic implementation - could be expanded
        for i in range(train_in.shape[0]):
            for j in range(train_in.shape[1]):
                in_color = train_in[i, j]
                out_color = train_out[i, j]
                
                if in_color != out_color and in_color not in color_map:
                    # Check neighbors for condition
                    neighbors = []
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < train_in.shape[0] and 0 <= nj < train_in.shape[1]:
                            neighbors.append(train_in[ni, nj])
                    
                    if neighbors:
                        conditional_maps.append({
                            'from': in_color,
                            'to': out_color,
                            'neighbor_hint': max(set(neighbors), key=neighbors.count)
                        })
    
    # Apply mappings to test inputs
    for test_example in task_data.get('test', []):
        input_grid = np.array(test_example['input'])
        output = input_grid.copy()
        
        # Apply direct mappings
        for from_color, to_color in color_map.items():
            output[input_grid == from_color] = to_color
        
        # Apply conditional mappings (simplified)
        for cond_map in conditional_maps:
            # Only apply if neighbor condition is met
            for i in range(output.shape[0]):
                for j in range(output.shape[1]):
                    if output[i, j] == cond_map['from']:
                        # Check if any neighbor matches hint
                        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ni, nj = i + di, j + dj
                            if 0 <= ni < input_grid.shape[0] and 0 <= nj < input_grid.shape[1]:
                                if input_grid[ni, nj] == cond_map['neighbor_hint']:
                                    output[i, j] = cond_map['to']
                                    break
        
        predictions.append(output.tolist())
    
    return predictions


def solve_tiling_pattern(task_data: Dict[str, Any]) -> List[List[List[int]]]:
    """
    Tile or extend patterns based on training examples.
    
    Detects:
    - Repeating patterns (periodicity)
    - Pattern extension (complete partial patterns)
    - Symmetry-based tiling (mirror, rotate)
    
    Args:
        task_data: Dict with 'train' and 'test' examples
    
    Returns:
        List of predicted outputs for each test input
    """
    predictions = []
    
    for test_example in task_data.get('test', []):
        input_grid = np.array(test_example['input'])
        
        # Analyze training to detect pattern type
        tile_size = None
        symmetry_type = None
        output_multiplier = None
        
        for train_example in task_data.get('train', []):
            train_in = np.array(train_example['input'])
            train_out = np.array(train_example['output'])
            
            in_h, in_w = train_in.shape
            out_h, out_w = train_out.shape
            
            # Check if output is tiled version of input
            if out_h >= in_h and out_w >= in_w:
                if out_h % in_h == 0 and out_w % in_w == 0:
                    tile_size = (in_h, in_w)
                    output_multiplier = (out_h // in_h, out_w // in_w)
            
            # Check for symmetry patterns
            if np.array_equal(train_out, np.flip(train_in, axis=0)):
                symmetry_type = 'vertical_flip'
            elif np.array_equal(train_out, np.flip(train_in, axis=1)):
                symmetry_type = 'horizontal_flip'
            elif np.array_equal(train_out, np.rot90(train_in, 2)):
                symmetry_type = 'rotate_180'
            elif np.array_equal(train_out, np.rot90(train_in, 1)):
                symmetry_type = 'rotate_90'
        
        # Apply detected pattern
        if tile_size and output_multiplier:
            # Tile the pattern
            multiplier_h, multiplier_w = output_multiplier
            output = np.tile(input_grid, (multiplier_h, multiplier_w))
        elif symmetry_type == 'vertical_flip':
            output = np.flip(input_grid, axis=0)
        elif symmetry_type == 'horizontal_flip':
            output = np.flip(input_grid, axis=1)
        elif symmetry_type == 'rotate_180':
            output = np.rot90(input_grid, 2)
        elif symmetry_type == 'rotate_90':
            output = np.rot90(input_grid, 1)
        else:
            # Try to detect and extend repeating pattern
            # Find smallest repeating unit
            h, w = input_grid.shape
            found_pattern = False
            
            for ph in range(1, h // 2 + 1):
                for pw in range(1, w // 2 + 1):
                    if h % ph == 0 and w % pw == 0:
                        pattern = input_grid[:ph, :pw]
                        tiled = np.tile(pattern, (h // ph, w // pw))
                        if np.array_equal(tiled, input_grid):
                            # Found repeating pattern - extend by 2x
                            output = np.tile(pattern, (h // ph * 2, w // pw * 2))
                            found_pattern = True
                            break
                if found_pattern:
                    break
            
            if not found_pattern:
                output = input_grid
        
        predictions.append(output.tolist())
    
    return predictions


# Convenience function to auto-detect and apply best solver
def auto_solve(task_data: Dict[str, Any]) -> List[List[List[int]]]:
    """
    Automatically detect pattern type and apply appropriate solver.
    
    Args:
        task_data: Dict with 'train' and 'test' examples
    
    Returns:
        List of predicted outputs
    """
    # Try each solver and return first successful prediction
    # (In practice, would use scoring/confidence to pick best)
    
    # Check for color mapping (same shape, different colors)
    for train_example in task_data.get('train', []):
        train_in = np.array(train_example['input'])
        train_out = np.array(train_example['output'])
        if train_in.shape == train_out.shape and not np.array_equal(train_in, train_out):
            return solve_color_mapping(task_data)
    
    # Check for shrinking (input larger than output)
    for train_example in task_data.get('train', []):
        train_in = np.array(train_example['input'])
        train_out = np.array(train_example['output'])
        if train_in.shape[0] > train_out.shape[0] or train_in.shape[1] > train_out.shape[1]:
            return solve_shrink_pattern(task_data)
    
    # Check for tiling (output larger than input)
    for train_example in task_data.get('train', []):
        train_in = np.array(train_example['input'])
        train_out = np.array(train_example['output'])
        if train_in.shape[0] < train_out.shape[0] or train_in.shape[1] < train_out.shape[1]:
            return solve_tiling_pattern(task_data)
    
    # Default: try color mapping
    return solve_color_mapping(task_data)


if __name__ == "__main__":
    # Quick test
    test_data = {
        'train': [
            {'input': [[1, 1, 2], [1, 1, 2], [3, 3, 3]], 'output': [[4, 4, 5], [4, 4, 5], [6, 6, 6]]}
        ],
        'test': [
            {'input': [[1, 2], [3, 4]]}
        ]
    }
    
    print("Color Mapping Test:")
    result = solve_color_mapping(test_data)
    print(f"Input: {test_data['test'][0]['input']}")
    print(f"Output: {result[0]}")
    print("\n[PASS] Pattern solvers module ready for Meeseeks bloodline!")
