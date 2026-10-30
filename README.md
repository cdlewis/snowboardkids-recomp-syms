# Snowboard Kids recomp symbols

`dump.toml` and `data_dump.toml` are generated from a matching US decompilation
ELF with N64Recomp. JP dumps and their six manual overrides are in `jp/`. `manual_symbols.toml` records the 8 existing function
additions/overrides that must survive regeneration.

## Automatic regeneration

After a successful US `main` build, `snowboardkids-decomp` sends a
`decomp-updated` repository dispatch containing its commit SHA. This repo's
`Regenerate symbols` workflow checks out that exact commit, rebuilds it using
the private baserom, and runs the decomp's normal ROM hash verification before
generating US symbols (`VERSION=us`). The successful US build dispatches a single update that rebuilds and verifies both regions. Superseded updates are skipped. The workflow commits only changed US and JP `dump.toml` and `data_dump.toml` files to `main`.

The ROM, ELF, extracted assets, and build directories stay on the temporary
GitHub-hosted runner. The workflow does not upload artifacts or build caches.
Only the symbol TOMLs are committed. Function/data entries are sorted by address
and name, so the first automated update will also normalize their ordering.

### Setup

Add these Actions repository secrets to **snowboardkids-recomp-syms**:

- `PRIVATE_REPO_ACCESS`: a token with Contents **read** access to
  `cdlewis/snowboardkids-private` (the same access used by the decomp build).
- `BASEROM_KEY`: the passphrase used by the decomp build to decrypt
  `snowboardkids.z64.gpg`.

Add this Actions repository secret to **snowboardkids-decomp**:

- `SYMBOLS_DISPATCH_TOKEN`: a fine-grained PAT with Contents **write** access
  to `cdlewis/snowboardkids-recomp-syms`, or an equivalent GitHub App token.
  GitHub requires this permission for the repository dispatch endpoint; the
  decomp repo's built-in `GITHUB_TOKEN` cannot dispatch to another repo.

Install the workflow in this repo's default branch before enabling the decomp
sender. Ensure repository rules permit `github-actions[bot]` to push symbol
updates to `main`. No extra token is needed for those pushes: this workflow
requests `contents: write` for its own `GITHUB_TOKEN`.

You can also run `Regenerate symbols` manually from the Actions tab. A manual
run rebuilds the current decomp `main`, including the ROM hash check.

### Local regeneration

With Python 3.11+, a matching ELF, and N64Recomp built at the revision pinned in
the workflow:

```sh
python3 scripts/generate_symbols.py \
  --elf /path/to/snowboardkids.elf \
  --recompiler /path/to/N64Recomp \
  --output /path/to/generated-symbols
```

The script runs the recompiler in a temporary directory and applies the manual
function overrides by section and address. It rejects overrides outside their
section or names that have moved to another address. Review the resulting TOMLs
before replacing the tracked dumps. Keep copyrighted inputs and build outputs
outside this repository.

### Japanese symbols

The JP dumps were generated from decomp `7034de13623519f6c13a3f080a99cde7a0bb229d` using its matching JP ELF.
The ELF SHA-256 was `326ebed3f603e6db921aa0682404335a80d5795a63ec10d08cc8dd3cc524709e`.
Its `.entry` and `.main` bytes are checked against the original JP ROM when validating updates.
Manual function ranges in `jp/manual_symbols.toml` come from the decomp's `symbol_addrs.jp.txt`.

```sh
python3 scripts/generate_symbols.py \
  --elf /path/to/build/jp/snowboardkids.elf \
  --recompiler /path/to/N64Recomp \
  --manual jp/manual_symbols.toml \
  --output jp
```

The private baserom repository must also contain `snowboardkids.jp.z64.gpg`, encrypted with `BASEROM_KEY`.
