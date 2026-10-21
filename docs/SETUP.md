# Build and run

Use Linux or WSL with GCC, Flex, Bison, GNU Make 4.3+, and Python 3. Verified with GCC 13.3, Flex 2.6.4, Bison 3.8.2, and GNU Make 4.3. The retained course sources produce compiler warnings and two Bison shift/reduce conflicts.

```bash
sudo apt-get install build-essential flex bison python3
make
make demo
make check
```

The build creates `build/alpha` and `build/avm`. Generated scanner/parser files and binaries stay under `build/`. The compiler reserves instruction slot zero before emitting the program's instructions.

`make demo` compiles [the arithmetic example](../examples/arithmetic.asc) into a fresh `build/alpha-demo-*` directory. It prints the quads and retains:

| File | Contents |
| --- | --- |
| `quads.txt` | Three-address intermediate code |
| `instructions.txt` | VM opcode and operand listing |
| `tables.txt` | Constant pools and function metadata |
| `avm_binary.abc` | Serialized instructions and pools |
| `compiler.log`, `compiler.stderr` | Symbol output and diagnostics |

The compiler writes these files into its current working directory. For your own input, run the compiler from a separate output directory with an absolute source path. Reusing a directory overwrites its previous output.

`make check` verifies selected quads and instructions, string/number pools, binary framing, malformed-syntax diagnostics, and paths containing spaces. It does not execute the VM. The historical inputs in `tests/fixtures/` are examples for inspection and experiments, not a passing language-conformance suite.

## VM status

The VM compiles, but executing the arithmetic demo currently aborts in an arithmetic stack assertion. Jump dispatch and several logical operations are unfinished. Bytecode emission also has operand-index and host-layout limitations, detailed in the [technical brief](report.pdf).

The original loader expects `../avm_binary.abc` relative to its working directory. To inspect the current failure on Linux:

```bash
mkdir -p build/run/vm
(cd build/run && ../alpha ../../examples/arithmetic.asc)
(cd build/run/vm && ulimit -c 0 && timeout 3 ../../avm)
```

The parser may emit errors yet return zero, so inspect its diagnostics rather than relying on its exit code alone. The supplied demo checks for the parser's invalid-input diagnostic.

## Report

Build `docs/report/main.tex` with pdfLaTeX, twice. [The Overleaf ZIP](report-overleaf.zip) contains `main.tex` and its local figure. The editable diagram source is [architecture.svg](images/architecture.svg).
