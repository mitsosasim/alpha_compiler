CC ?= cc
FLEX ?= flex
BISON ?= bison
CFLAGS ?= -std=gnu99 -g
CPPFLAGS += -Icompiler -Ibuild

COMPILER_SRC = compiler/SymTable.c compiler/symtablehash.c compiler/quads.c compiler/stack.c
COMPILER_HDR = $(wildcard compiler/*.h)

.PHONY: all demo check clean
all: build/alpha build/avm

build:
	mkdir -p $@

build/parser.c build/parser.h &: compiler/parser.y | build
	$(BISON) --defines=build/parser.h --output=build/parser.c compiler/parser.y

build/scanner.c: compiler/scanner.l build/parser.h | build
	$(FLEX) --outfile=$@ $<

build/alpha: build/parser.c build/scanner.c $(COMPILER_SRC) $(COMPILER_HDR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ build/parser.c build/scanner.c $(COMPILER_SRC) $(LDFLAGS)

build/avm: vm/avm.c vm/avm.h $(COMPILER_HDR) | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ vm/avm.c $(LDFLAGS)

demo: all
	python3 scripts/demo.py

check: all
	python3 scripts/check.py

clean:
	rm -rf build
