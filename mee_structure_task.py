import sys
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace")
import asyncio
from skills.meeseeks.helpers.communication import SharedState
import os
from collections import Counter

async def main():
    shared = SharedState("test-comm-001", "mee_structure")
    
    # Register
    await shared.register("File structure analyzer")
    print("[OK] Registered as structure analyzer")
    
    # Analyze structure
    workspace = "C:/Users/aaron/.openclaw/workspace"
    extensions = Counter()
    dir_count = 0
    
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        dir_count += len(dirs)
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext:
                extensions[ext] += 1
    
    # Share discoveries
    await shared.share_discovery("file_stats", {
        "total_dirs": dir_count,
        "top_extensions": dict(extensions.most_common(5))
    })
    
    # Update progress
    await shared.update_status(progress=50)
    
    # Check peers
    peers = await shared.check_peers()
    print(f"[PEERS] Peers: {list(peers.keys())}")
    
    # Wait a bit for others
    await asyncio.sleep(2)
    
    # Get shared discoveries from ALL workers
    all_discoveries = await shared.get_shared_discoveries()
    print(f"[DISCOVERIES] Total discoveries: {len(all_discoveries)}")
    for d in all_discoveries:
        print(f' - {d["from"]}: {d["type"]}')
    
    # Complete
    await shared.complete(summary=f"Analyzed {dir_count} dirs, top ext: {extensions.most_common(3)}")
    
    # Get final summary
    summary = await shared.summary()
    print(f"[SUMMARY] Workflow summary: {summary}")

asyncio.run(main())
