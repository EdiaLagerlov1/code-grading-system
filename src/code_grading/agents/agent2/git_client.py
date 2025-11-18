"""Git repository operations."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class GitClient:
    """Git repository operations wrapper."""

    @staticmethod
    def clone_repo(repo_url: str, target_dir: Optional[Path] = None) -> Path:
        """Clone git repository to target directory.

        Args:
            repo_url: Git repository URL
            target_dir: Target directory (creates temp dir if None)

        Returns:
            Path to cloned repository

        Raises:
            subprocess.CalledProcessError: If git clone fails
        """
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix="repo_"))

        target_dir.mkdir(parents=True, exist_ok=True)

        # Clone with depth 1 (shallow clone for speed)
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
            check=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        return target_dir

    @staticmethod
    def cleanup_repo(repo_dir: Path) -> None:
        """Remove cloned repository directory.

        Args:
            repo_dir: Directory to remove
        """
        if repo_dir.exists():
            shutil.rmtree(repo_dir, ignore_errors=True)
