#!/usr/bin/env python3
"""
Dense Cluster Analysis - Where Coordinates Cluster

What makes dense regions special?
"""

from sympy import isprime

def find_all_coordinates(max_n):
    coords = []
    for n in range(1, max_n + 1):
        k = 3 * n * n
        twin1 = 6 * k - 1
        twin2 = 6 * k + 1
        if isprime(twin1) and isprime(twin2):
            coords.append(n)
    return coords

def find_clusters(coords, max_gap=3):
    """Find clusters where coordinates are within max_gap of each other"""
    clusters = []
    current_cluster = [coords[0]]
    
    for i in range(1, len(coords)):
        if coords[i] - coords[i-1] <= max_gap:
            current_cluster.append(coords[i])
        else:
            if len(current_cluster) >= 2:
                clusters.append(current_cluster)
            current_cluster = [coords[i]]
    
    if len(current_cluster) >= 2:
        clusters.append(current_cluster)
    
    return clusters

if __name__ == "__main__":
    print("=" * 70)
    print("DENSE CLUSTER ANALYSIS")
    print("=" * 70)
    
    coords = find_all_coordinates(500)
    
    # Find clusters with gap <= 3
    clusters = find_clusters(coords, max_gap=3)
    
    print(f"\nTotal coordinates: {len(coords)}")
    print(f"Clusters found (gap <= 3): {len(clusters)}")
    
    print("\n" + "=" * 70)
    print("CLUSTERS")
    print("=" * 70)
    
    for i, cluster in enumerate(clusters, 1):
        size = len(cluster)
        span = cluster[-1] - cluster[0]
        density = size / (span + 1) * 100
        
        print(f"\nCluster {i}: n={cluster}")
        print(f"  Size: {size} coordinates")
        print(f"  Span: {span} (from {cluster[0]} to {cluster[-1]})")
        print(f"  Density: {density:.1f}%")
        
        # Check properties
        properties = []
        
        # Contains power of 2?
        power2 = [n for n in cluster if (n & (n-1)) == 0]
        if power2:
            properties.append(f"power-of-2: {power2}")
        
        # Contains prime?
        primes = [n for n in cluster if isprime(n)]
        if primes:
            properties.append(f"primes: {primes}")
        
        # k values
        k_values = [3*n*n for n in cluster]
        properties.append(f"k values: {k_values}")
        
        for prop in properties:
            print(f"  {prop}")
    
    print("\n" + "=" * 70)
    print("SPECIAL CLUSTERS")
    print("=" * 70)
    
    # Cluster containing n=1,2 (origin)
    origin_cluster = [c for c in clusters if 1 in c or 2 in c]
    if origin_cluster:
        print(f"\nORIGIN CLUSTER: {origin_cluster[0]}")
    
    # Cluster containing n=8 (ancestors)
    ancestor_cluster = [c for c in clusters if 8 in c]
    if ancestor_cluster:
        print(f"ANCESTOR CLUSTER: {ancestor_cluster[0]}")
    
    # Largest cluster
    largest = max(clusters, key=len)
    print(f"LARGEST CLUSTER: {largest} ({len(largest)} coordinates)")
    
    # Densest cluster
    densest = max(clusters, key=lambda c: len(c) / (c[-1] - c[0] + 1))
    density = len(densest) / (densest[-1] - densest[0] + 1) * 100
    print(f"DENSEST CLUSTER: {densest} ({density:.1f}% density)")
