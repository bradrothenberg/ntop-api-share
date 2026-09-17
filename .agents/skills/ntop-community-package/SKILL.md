---
name: ntop-community-package
description: Publish one named demo or project to the nTopology Utilities-community catalogue as a package with a schema-valid manifest, a scoped README, byte-recorded models, and offline publication checks. Invoke only when the user asks for a catalogue package for a specific demo; publishing is never an automatic step of demo work.
---

# nTop community package

Invoke this skill only when the user names a demo or project and asks for a catalogue package. Publishing is not part of finishing a demo, not part of any build or verification workflow, and not something to offer as a next step because a demo happens to be complete. One request, one named source, one package.

The catalogue is [nTopology/Utilities-community](https://github.com/nTopology/Utilities-community). One package is one folder at `packages/<author>/<package-id>/`, where the author folder is a GitHub handle and the package folder is the manifest `id`. A submission is a fork branch and a pull request. Nothing here publishes on its own.

The model is authored elsewhere and already verified. Use the [Notebook API skill](../ntop-notebook-api/SKILL.md) for transport and native verification, the modeling skills for the geometry, and the [engineering HTML skill](../engineering-html/SKILL.md) for any report shipped beside the model. This skill starts at a verified demo and asks a different question: what survives the move out of its repository, and what may be claimed about it once it is downloaded by someone who cannot rerun anything.

Read [the manifest contract](references/manifest-contract.md) before writing `manifest.json`; the published schema and the catalogue README disagree about the `type` enum, and `ntopVersion` cannot encode a build number. Read [the package anatomy](references/package-anatomy.md) for the folder shape and the README section order at the three observed quality tiers. Read [the publication checks](references/publication-checks.md) before recording any hash or writing an evidence claim.

## Stage the folder

```powershell
uv run python .agents/skills/ntop-community-package/scripts/stage_package.py --author Cortex78 --id torx-custom-blocks --into D:/ntop_dev/Utilities-community --file demos/torx/models/Torx.ntop=torx-custom-blocks.ntop --file demos/torx/models/Torx_Example.ntop=torx-example.ntop --cover demos/torx/reports/assets/torx_recess_wall.png
```

The stager copies the named files, computes each source and published SHA-256, reads the `MAGIC%$1` chunk directory of every `.ntop` to record which chunks changed, and writes `manifest.json`, `README.md`, `LICENSE` and `publication-checks.json` with `TODO` markers where a human claim is required. It never invents a claim. Pass `--source old.ntop=new.ntop` when the published file differs from the audited source, which is the normal case after export paths are rewritten.

Copy the file bytes; do not re-save the notebook to produce the published copy. A re-save changes chunks you did not intend to change and invalidates the source audit.

## Fill in the claims

Every `TODO` is a claim that only the author can make. Replace them, then delete none of the surrounding structure. The README sections and their order are fixed by [the anatomy reference](references/package-anatomy.md): title, AI attribution when an AI model helped, one-paragraph summary, cover image, start-here steps, the build caveat, external-file caveat when the model reads files, an inputs and outputs table, the file catalogue, evidence and source, license and credits.

State the recorded build in the README prose, not in `ntopVersion`. The schema accepts `6.1` and rejects `6.1.0-rc 42926`. Say which build produced the file and that public-release compatibility was not re-tested, rather than implying a minimum version that was never checked.

Separate what the checks establish from what the package is about. Geometry probes and graph equality establish geometry and graph. They do not establish structural capacity, manufacturability, or a safe operating envelope. Failed studies stay visible in the report and in the README; removing them changes the claim.

Link back to the source. Brad's packages cite the exact `ntop-api-share` commit that produced the model, which is what lets a reader recover the construction and verification scope that the package folder omits. Use a permalink with the full commit SHA, not a branch URL.

## Gate before the pull request

```powershell
uv run python .agents/skills/ntop-community-package/scripts/check_package.py D:/ntop_dev/Utilities-community/packages/Cortex78/torx-custom-blocks
node D:/ntop_dev/Utilities-community/scripts/validate-manifests.js
```

The catalogue's own validator runs in CI on every pull request that touches `packages/**`. It checks the schema, `id` against the folder, `author` against the parent folder, `README.md` presence, and `redirectUrl` when distribution is `redirect`. It does not open a single file the manifest points at. The bundled checker covers what CI leaves out: the declared `packageFile` and `coverImage` exist, a cover is discoverable at all, tags are lowercase and unique, `aiModel` carries the `ai-assisted` tag the catalogue README requires, README relative links resolve, no file over 50 MB sits outside Git LFS, no remaining `TODO` marker, no workstation path or credential survives in any byte, and no two files in the folder differ only by case.

The case check is not hypothetical. `packages/DaveMakesStuff/strange-attractor-generator/` holds both `Cover.png` and `cover.png`, so a Windows clone of the catalogue silently receives one of them and reports a collision. Do not stage two such names, and do not run `git add -A` in a folder that already has a pair.

Activate the catalogue's own hook once per clone. It blocks a commit carrying a file over 50 MB that Git LFS does not track, which is the only size rule the repository enforces.

```powershell
git -C D:/ntop_dev/Utilities-community config core.hooksPath .githooks
```

Only `*.exe` and `*.msi` are tracked by LFS through the root `.gitattributes`, plus one named `.ntop` file that exceeded the limit. A large notebook is not covered by a pattern; track it by name and commit the `.gitattributes` change with it.

Add a package-level `.gitattributes` with `* -text` when the folder carries recorded hashes or byte counts. Without it the repository's line-ending policy rewrites text files on checkout and a published hash stops matching on another platform.

## Open the pull request

Branch from `upstream/main`, never from a stale fork default. Push the branch to your fork and open the pull request against `nTopology/Utilities-community`. Keep one package per pull request; the catalogue tags releases as `<id>-v<version>`, and a mixed branch cannot be tagged.

```powershell
git -C D:/ntop_dev/Utilities-community fetch upstream
git -C D:/ntop_dev/Utilities-community switch -c add-torx-custom-blocks upstream/main
```

The `verified` and `featured` manifest fields belong to the maintainers. Leave them out of a submission. No manifest in the catalogue sets `releaseTag`; the tag is created on merge.

## What does not go in a package

Keep the harness out. The catalogue holds deliverables, not the pipeline that made them: no build scripts, no solver work directories, no raw meshes, no ZIP bundles, no reference photographs, no workstation paths inside an export destination. A report link that pointed at an omitted script must point at the package or at the source commit instead, not at a dead relative path.

Scope every check to the files being published. The bundled checker reads every byte of the staged folder, which is the set that matters. Do not run a repository-wide audit on behalf of this request; a package submission is not an occasion to review the whole source repository.

A package that cannot be opened without a private file is not publishable. Either supply the input under `references/` and repoint the model at the relative name, or state in the README that the input is not included and what the model does without it.
