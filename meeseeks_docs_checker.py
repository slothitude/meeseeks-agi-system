import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace")
import asyncio
from skills.meeseeks.helpers.communication import SharedState
import os

async def main():
    shared = SharedState("test-comm-001", "mee_docs")
    
    # Register
    await shared.register("Documentation checker")
    print("OK Registered as docs checker")
    
    # Check documentation
    workspace = "C:/Users/aaron/.openclaw/workspace"
    doc_files = []
    
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for f in files:
            if f.upper().startswith('README') or f.upper().startswith('SKILL') or 'GUIDE' in f.upper():
                doc_files.append(os.path.join(root, f))
                await shared.share_discovery("doc_file", {
                    "file": f,
                    "path": os.path.join(root, f)
                })
    
    # Update progress
    await shared.update_status(progress=50, doc_count=len(doc_files))
    
    # Check peers
    peers = await shared.check_peers()
    print(f"Peers: {list(peers.keys())}")
    
    # Wait for others
    await asyncio.sleep(3)
    
    # Get ALL shared discoveries
    all_discoveries = await shared.get_shared_discoveries()
    print(f"Total discoveries: {len(all_discoveries)}")
    
    # Group by worker
    by_worker = {}
    for d in all_discoveries:
        worker = d['from']
        if worker not in by_worker:
            by_worker[worker] = []
        by_worker[worker].append(d['type'])
    
    print("Discoveries by worker:")
    for worker, types in by_worker.items():
        print(f"  {worker}: {types}")
    
    # Complete
    await shared.complete(summary=f"Found {len(doc_files)} documentation files")
    
    # Final summary
    summary = await shared.summary()
    print(f"Workflow summary: {summary}")

asyncio.run(main())
