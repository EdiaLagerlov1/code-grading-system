"""Python code analysis and line counting."""

import ast
from pathlib import Path
from typing import Dict, List


class CodeAnalyzer:
    """Analyze Python code files."""

    @staticmethod
    def find_python_files(repo_dir: Path) -> List[Path]:
        """Find all Python files in repository.

        Args:
            repo_dir: Repository directory

        Returns:
            List of Python file paths
        """
        return list(repo_dir.rglob("*.py"))

    @staticmethod
    def count_code_lines(file_path: Path) -> int:
        """Count actual code lines (excluding comments, docstrings, blank lines).

        Args:
            file_path: Path to Python file

        Returns:
            Number of code lines
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse AST to exclude comments and docstrings
            tree = ast.parse(content, filename=str(file_path))

            # Get line numbers with actual code
            code_lines = set()
            for node in ast.walk(tree):
                if hasattr(node, "lineno"):
                    code_lines.add(node.lineno)

            return len(code_lines)

        except (SyntaxError, UnicodeDecodeError):
            # If AST parsing fails, fall back to simple line count
            return CodeAnalyzer._count_lines_simple(file_path)

    @staticmethod
    def _count_lines_simple(file_path: Path) -> int:
        """Simple line count fallback.

        Args:
            file_path: Path to file

        Returns:
            Number of non-empty lines
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0

    @staticmethod
    def analyze_repository(repo_dir: Path) -> Dict[str, int]:
        """Analyze Python files in repository.

        Args:
            repo_dir: Repository directory

        Returns:
            Dictionary with analysis results:
                - total_lines: Total Python code lines
                - lines_within_limit: Lines in files <= 150 lines
                - files_over_limit: Number of files > 150 lines
                - total_files: Total Python files
        """
        python_files = CodeAnalyzer.find_python_files(repo_dir)

        total_lines = 0
        lines_within_limit = 0
        files_over_limit = 0

        for py_file in python_files:
            line_count = CodeAnalyzer.count_code_lines(py_file)
            total_lines += line_count

            if line_count <= 150:
                lines_within_limit += line_count
            else:
                files_over_limit += 1

        return {
            "total_lines": total_lines,
            "lines_within_limit": lines_within_limit,
            "files_over_limit": files_over_limit,
            "total_files": len(python_files),
        }

    @staticmethod
    def calculate_grade(analysis: Dict[str, int]) -> float:
        """Calculate grade based on analysis.

        Args:
            analysis: Analysis results from analyze_repository()

        Returns:
            Grade (0-100)
        """
        if analysis["total_lines"] == 0:
            return 0.0

        ratio = analysis["lines_within_limit"] / analysis["total_lines"]
        return round(ratio * 100, 2)
