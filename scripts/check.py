"""Check compiler artifacts without claiming VM execution correctness."""
from pathlib import Path
import ctypes
import io
import re
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def compile_source(directory, source):
    path = directory / "input.asc"
    path.write_text(source)
    result = subprocess.run(
        [str(ROOT / "build/alpha"), str(path)], cwd=directory,
        capture_output=True, text=True, timeout=10,
    )
    return result


def read_program(path):
    stream = io.BytesIO(path.read_bytes())

    def scalar(fmt):
        size = struct.calcsize(fmt)
        data = stream.read(size)
        if len(data) != size:
            raise AssertionError("Truncated bytecode")
        return struct.unpack(fmt, data)[0]

    def text():
        size = scalar("@N")
        raw = stream.read(size)
        assert len(raw) == size and raw.endswith(b"\0")
        return raw[:-1].decode()

    assert scalar("@I") == 340200501, "Invalid Alpha bytecode header"
    strings = [text() for _ in range(scalar("@I"))]
    numbers = [scalar("@d") for _ in range(scalar("@I"))]
    libraries = [text() for _ in range(scalar("@I"))]
    for _ in range(scalar("@I")):
        text()
        scalar("@I")
        scalar("@I")
    count = scalar("@I") - 1  # The first instruction slot is reserved.

    class Operand(ctypes.Structure):
        _fields_ = [("type", ctypes.c_uint), ("value", ctypes.c_uint),
                    ("name", ctypes.c_void_p)]

    # The course format uses host-sized operand records plus separate values.
    record_size = struct.calcsize("@I") + 3 * (ctypes.sizeof(Operand) + struct.calcsize("@I"))
    assert len(stream.read()) == count * record_size, "Instruction payload size mismatch"
    return strings, numbers, libraries, count


def main():
    with tempfile.TemporaryDirectory(prefix="alpha checks ") as tmp:
        base = Path(tmp)
        arithmetic = base / "arithmetic"
        arithmetic.mkdir()
        result = compile_source(arithmetic, (ROOT / "examples/arithmetic.asc").read_text())
        assert result.returncode == 0 and "INPUT NOT VALID" not in result.stderr
        quads = (arithmetic / "quads.txt").read_text()
        assert re.search(r"\bmul\s+_t\d+\s+a\s+b\b", quads), "Expected variable multiplication"
        assert re.search(r"\bcall\s+print\b", quads), "Expected print call"
        listing = (arithmetic / "instructions.txt").read_text()
        _, numbers, libraries, count = read_program(arithmetic / "avm_binary.abc")
        assert set(numbers) == {6.0, 7.0} and libraries == ["print"]
        assert count == len(re.findall(r"^\d+\s+\w+_v\b", listing, re.MULTILINE)) == 10
        assert "mul_v" in listing and "callfunc_v" in listing

        literals = base / "literals"
        literals.mkdir()
        result = compile_source(literals, 'x = 4 + 5; print("hello");\n')
        assert result.returncode == 0 and "INPUT NOT VALID" not in result.stderr
        quads = (literals / "quads.txt").read_text()
        assert re.search(r"\badd\s+_t\d+\s+4\.00\s+5\.00\b", quads), "Expected literal addition"
        strings, numbers, libraries, _ = read_program(literals / "avm_binary.abc")
        assert [value.strip('"') for value in strings] == ["hello"]
        assert set(numbers) == {4.0, 5.0} and "print" in libraries

        invalid = base / "invalid"
        invalid.mkdir()
        result = compile_source(invalid, "a = ;\n")
        assert "INPUT NOT VALID" in result.stderr, "Malformed syntax should produce a diagnostic"

    print("PASS: arithmetic quads, call instructions, literal operands, string/number pools, "
          "bytecode framing, syntax diagnostics, and paths containing spaces")


if __name__ == "__main__":
    main()
