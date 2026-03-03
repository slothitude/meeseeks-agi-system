"""
Download Manager Trigger Module
For use by Sloth_rog (Windows) and sloth_pibot (Pi) agents

Provides a simple interface to trigger and manage downloads via aria2 RPC.

Usage:
    from trigger import DownloadManager
    
    dm = DownloadManager()
    
    # Add a download
    result = dm.add_download(
        url="https://example.com/large-file.zip",
        filename="myfile.zip",
        directory="/home/pi/downloads/games"
    )
    print(f"Download ID: {result['gid']}")
    
    # Check status
    status = dm.get_status(result['gid'])
    print(f"Progress: {status['progress']}%")
"""

import requests
import json
from typing import Optional, Dict, List, Any
from datetime import datetime
import os


class DownloadManager:
    """Interface to aria2 RPC for download management."""
    
    def __init__(
        self,
        rpc_host: str = "192.168.0.237",
        rpc_port: int = 6800,
        rpc_secret: str = None,
        default_directory: str = "/home/pi/downloads"
    ):
        """
        Initialize download manager.
        
        Args:
            rpc_host: aria2 RPC host (default: Pi IP)
            rpc_port: aria2 RPC port (default: 6800)
            rpc_secret: RPC secret token (default: from env or 'sloth_download_token')
            default_directory: Default download directory on Pi
        """
        self.rpc_url = f"http://{rpc_host}:{rpc_port}/jsonrpc"
        self.rpc_secret = rpc_secret or os.environ.get("ARIA2_SECRET", "sloth_download_token")
        self.default_directory = default_directory
        self.request_id = 0
    
    def _call(self, method: str, *params) -> Dict[str, Any]:
        """
        Make RPC call to aria2.
        
        Args:
            method: aria2 RPC method name
            *params: Method parameters
            
        Returns:
            Response dict
        """
        self.request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "id": f"agent-{self.request_id}",
            "method": method,
            "params": list(params)
        }
        
        try:
            response = requests.post(
                self.rpc_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise DownloadError(result["error"])
            
            return result.get("result", {})
            
        except requests.exceptions.ConnectionError:
            raise DownloadError(f"Cannot connect to aria2 at {self.rpc_url}")
        except requests.exceptions.Timeout:
            raise DownloadError("RPC request timed out")
    
    def add_download(
        self,
        url: str,
        filename: Optional[str] = None,
        directory: Optional[str] = None,
        connections: int = 4,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Add a download to the queue.
        
        Args:
            url: Download URL
            filename: Output filename (optional)
            directory: Download directory (optional, uses default if not set)
            connections: Number of connections per server (1-16)
            headers: Additional HTTP headers
            
        Returns:
            Dict with 'gid' (download ID) and 'url'
            
        Example:
            >>> dm.add_download("https://example.com/file.zip", filename="myfile.zip")
            {'gid': '2089b05ecca3d829', 'url': 'https://example.com/file.zip'}
        """
        options = {
            "split": str(connections),
            "max-connection-per-server": str(connections)
        }
        
        if filename:
            options["out"] = filename
        
        if directory:
            options["dir"] = directory
        
        if headers:
            # Convert headers dict to aria2 format
            header_list = [f"{k}: {v}" for k, v in headers.items()]
            options["header"] = header_list
        
        result = self._call(
            "aria2.addUri",
            f"token:{self.rpc_secret}",
            [url],
            options
        )
        
        return {
            "gid": result,
            "url": url,
            "filename": filename,
            "directory": directory or self.default_directory
        }
    
    def add_torrent(
        self,
        torrent_path: str,
        directory: Optional[str] = None,
        select_files: Optional[List[int]] = None
    ) -> Dict[str, str]:
        """
        Add a torrent download.
        
        Args:
            torrent_path: Path to .torrent file
            directory: Download directory
            select_files: List of file indices to download (optional)
            
        Returns:
            Dict with 'gid' and info
        """
        with open(torrent_path, "rb") as f:
            torrent_data = f.read()
        
        import base64
        torrent_b64 = base64.b64encode(torrent_data).decode()
        
        options = {}
        if directory:
            options["dir"] = directory
        if select_files:
            options["select-file"] = ",".join(map(str, select_files))
        
        result = self._call(
            "aria2.addTorrent",
            f"token:{self.rpc_secret}",
            torrent_b64,
            [],
            options
        )
        
        return {"gid": result, "torrent": torrent_path}
    
    def add_metalink(
        self,
        metalink_path: str,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a metalink download.
        
        Args:
            metalink_path: Path to .metalink or .meta4 file
            directory: Download directory
            
        Returns:
            Dict with 'gid' list
        """
        with open(metalink_path, "rb") as f:
            metalink_data = f.read()
        
        import base64
        metalink_b64 = base64.b64encode(metalink_data).decode()
        
        options = {}
        if directory:
            options["dir"] = directory
        
        result = self._call(
            "aria2.addMetalink",
            f"token:{self.rpc_secret}",
            metalink_b64,
            [],
            options
        )
        
        return {"gids": result}
    
    def get_status(self, gid: str) -> Dict[str, Any]:
        """
        Get detailed download status.
        
        Args:
            gid: Download ID
            
        Returns:
            Status dict with keys:
            - status: active/waiting/paused/error/complete/removed
            - progress: 0-100 percentage
            - download_speed: bytes/sec
            - total_length: total bytes
            - completed_length: downloaded bytes
            - filename: output filename
            - directory: download directory
            - error_code: error code if failed
            - error_message: error description if failed
        """
        result = self._call(
            "aria2.tellStatus",
            f"token:{self.rpc_secret}",
            gid
        )
        
        # Parse and format status
        status = {
            "gid": gid,
            "status": result.get("status", "unknown"),
            "total_length": int(result.get("totalLength", 0)),
            "completed_length": int(result.get("completedLength", 0)),
            "download_speed": int(result.get("downloadSpeed", 0)),
            "upload_speed": int(result.get("uploadSpeed", 0)),
            "directory": result.get("dir", ""),
            "filename": "",
            "error_code": result.get("errorCode"),
            "error_message": result.get("errorMessage")
        }
        
        # Calculate progress
        if status["total_length"] > 0:
            status["progress"] = round(
                (status["completed_length"] / status["total_length"]) * 100,
                2
            )
        else:
            status["progress"] = 0
        
        # Get filename from files array
        if "files" in result and len(result["files"]) > 0:
            file_info = result["files"][0]
            status["filename"] = file_info.get("path", "").split("/")[-1]
            status["original_url"] = file_info.get("uris", [{}])[0].get("uri", "")
        
        # Format speeds
        status["download_speed_human"] = self._format_bytes(status["download_speed"])
        status["upload_speed_human"] = self._format_bytes(status["upload_speed"])
        status["total_length_human"] = self._format_bytes(status["total_length"])
        status["completed_length_human"] = self._format_bytes(status["completed_length"])
        
        return status
    
    def list_active(self) -> List[Dict[str, Any]]:
        """
        List all active downloads.
        
        Returns:
            List of status dicts
        """
        results = self._call(
            "aria2.tellActive",
            f"token:{self.rpc_secret}"
        )
        
        return [self.get_status(r.get("gid")) for r in results]
    
    def list_waiting(self) -> List[Dict[str, Any]]:
        """
        List all waiting/paused downloads.
        
        Returns:
            List of status dicts
        """
        results = self._call(
            "aria2.tellWaiting",
            f"token:{self.rpc_secret}",
            0,  # offset
            1000  # max
        )
        
        return [self.get_status(r.get("gid")) for r in results]
    
    def list_stopped(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List stopped/completed downloads.
        
        Args:
            max_results: Maximum number of results
            
        Returns:
            List of status dicts
        """
        results = self._call(
            "aria2.tellStopped",
            f"token:{self.rpc_secret}",
            0,  # offset
            max_results
        )
        
        return [self.get_status(r.get("gid")) for r in results]
    
    def pause(self, gid: str) -> bool:
        """
        Pause a download.
        
        Args:
            gid: Download ID
            
        Returns:
            True if successful
        """
        result = self._call(
            "aria2.pause",
            f"token:{self.rpc_secret}",
            gid
        )
        return result == gid
    
    def resume(self, gid: str) -> bool:
        """
        Resume a paused download.
        
        Args:
            gid: Download ID
            
        Returns:
            True if successful
        """
        result = self._call(
            "aria2.unpause",
            f"token:{self.rpc_secret}",
            gid
        )
        return result == gid
    
    def cancel(self, gid: str, delete_files: bool = False) -> bool:
        """
        Cancel and remove a download.
        
        Args:
            gid: Download ID
            delete_files: Whether to delete downloaded files
            
        Returns:
            True if successful
        """
        if delete_files:
            result = self._call(
                "aria2.removeDownloadResult",
                f"token:{self.rpc_secret}",
                gid
            )
        else:
            result = self._call(
                "aria2.remove",
                f"token:{self.rpc_secret}",
                gid
            )
        return result == gid
    
    def purge_completed(self) -> int:
        """
        Remove all completed/error/removed downloads from list.
        
        Returns:
            Number of purged downloads
        """
        before = len(self.list_stopped())
        self._call("aria2.purgeDownloadResult", f"token:{self.rpc_secret}")
        after = len(self.list_stopped())
        return before - after
    
    def get_global_stats(self) -> Dict[str, Any]:
        """
        Get global download statistics.
        
        Returns:
            Stats dict with download/upload speeds and counts
        """
        result = self._call("aria2.getGlobalStat", f"token:{self.rpc_secret}")
        
        return {
            "download_speed": int(result.get("downloadSpeed", 0)),
            "upload_speed": int(result.get("uploadSpeed", 0)),
            "num_active": int(result.get("numActive", 0)),
            "num_waiting": int(result.get("numWaiting", 0)),
            "num_stopped": int(result.get("numStopped", 0)),
            "download_speed_human": self._format_bytes(int(result.get("downloadSpeed", 0))),
            "upload_speed_human": self._format_bytes(int(result.get("uploadSpeed", 0)))
        }
    
    def is_healthy(self) -> bool:
        """
        Check if aria2 is running and responsive.
        
        Returns:
            True if aria2 is healthy
        """
        try:
            stats = self.get_global_stats()
            return True
        except DownloadError:
            return False
    
    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"


class DownloadError(Exception):
    """Exception raised for download manager errors."""
    pass


# Convenience functions for quick usage
def download(url: str, filename: str = None, directory: str = None) -> str:
    """
    Quick download function.
    
    Args:
        url: URL to download
        filename: Output filename (optional)
        directory: Download directory (optional)
        
    Returns:
        Download GID
        
    Example:
        >>> from trigger import download
        >>> gid = download("https://example.com/file.zip", "myfile.zip")
        >>> print(f"Started download: {gid}")
    """
    dm = DownloadManager()
    result = dm.add_download(url, filename=filename, directory=directory)
    return result["gid"]


def status(gid: str) -> Dict[str, Any]:
    """
    Quick status check.
    
    Args:
        gid: Download ID
        
    Returns:
        Status dict
    """
    dm = DownloadManager()
    return dm.get_status(gid)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Manager CLI")
    parser.add_argument("command", choices=["add", "status", "list", "pause", "resume", "cancel", "stats"])
    parser.add_argument("--url", help="URL to download")
    parser.add_argument("--gid", help="Download GID")
    parser.add_argument("--filename", help="Output filename")
    parser.add_argument("--directory", help="Download directory")
    
    args = parser.parse_args()
    
    dm = DownloadManager()
    
    if args.command == "add":
        if not args.url:
            print("Error: --url required for add command")
            exit(1)
        result = dm.add_download(args.url, filename=args.filename, directory=args.directory)
        print(f"Download added: {result['gid']}")
        print(f"File: {result['filename'] or 'auto'}")
        print(f"Directory: {result['directory']}")
    
    elif args.command == "status":
        if not args.gid:
            print("Error: --gid required for status command")
            exit(1)
        status = dm.get_status(args.gid)
        print(json.dumps(status, indent=2))
    
    elif args.command == "list":
        active = dm.list_active()
        waiting = dm.list_waiting()
        print(f"Active: {len(active)}")
        for d in active:
            print(f"  [{d['gid']}] {d['filename']} - {d['progress']}%")
        print(f"\nWaiting: {len(waiting)}")
        for d in waiting[:10]:  # Show first 10
            print(f"  [{d['gid']}] {d['filename']}")
    
    elif args.command == "pause":
        if not args.gid:
            print("Error: --gid required for pause command")
            exit(1)
        dm.pause(args.gid)
        print(f"Paused: {args.gid}")
    
    elif args.command == "resume":
        if not args.gid:
            print("Error: --gid required for resume command")
            exit(1)
        dm.resume(args.gid)
        print(f"Resumed: {args.gid}")
    
    elif args.command == "cancel":
        if not args.gid:
            print("Error: --gid required for cancel command")
            exit(1)
        dm.cancel(args.gid)
        print(f"Cancelled: {args.gid}")
    
    elif args.command == "stats":
        stats = dm.get_global_stats()
        print("Global Statistics:")
        print(f"  Download Speed: {stats['download_speed_human']}/s")
        print(f"  Upload Speed: {stats['upload_speed_human']}/s")
        print(f"  Active: {stats['num_active']}")
        print(f"  Waiting: {stats['num_waiting']}")
        print(f"  Stopped: {stats['num_stopped']}")
