"""Compile a small Alpha program into an isolated artifact directory."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = Path(tempfile.mkdtemp(prefix="alpha-demo-", dir=ROOT / "build"))
    result = subprocess.run(
        [str(ROOT / "build/alpha"), str(ROOT / "examples/arithmetic.asc")],
        cwd=output, capture_output=True, text=True, timeout=15,
    )
    (output / "compiler.log").write_text(result.stdout)
    (output / "compiler.stderr").write_text(result.stderr)
    if result.returncode or "INPUT NOT VALID" in result.stderr:
        raise SystemExit(f"Compilation failed. See {output}")
    for name in ["quads.txt", "instructions.txt", "tables.txt", "avm_binary.abc"]:
        if not (output / name).is_file():
            raise SystemExit(f"Missing compiler output: {name}")
    print((output / "quads.txt").read_text())
    print(f"Compiler artifacts: {output}")


if __name__ == "__main__":
    main()
