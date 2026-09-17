# The manifest contract

Every package carries `manifest.json` at its root. The authority is `packages/_schema/manifest.schema.json` in the catalogue, enforced by `scripts/validate-manifests.js` locally and by `.github/workflows/validate.yml` on every pull request touching `packages/**`. The schema sets `additionalProperties: false`, so an unknown key is a failure, not a warning.

## Required fields

| Field | Constraint | Notes |
|---|---|---|
| `id` | `^[a-z0-9][a-z0-9-]*[a-z0-9]$` | Must equal the containing folder name. Kebab-case, no leading or trailing hyphen. |
| `type` | `Notebook`, `Block`, `Connector`, `Script`, `Bundle` | See the enum conflict below. |
| `title` | 2 to 80 characters | Human display title. Sentence case reads better than Title Case in the catalogue. |
| `summary` | 10 to 240 characters | One or two sentences. The catalogue card shows it. |
| `author` | `^[A-Za-z0-9][A-Za-z0-9._-]*$` | Must equal the parent folder name. Case matters: `DaveMakesStuff` and `bradrothenberg` are both live. |
| `version` | `^\d+\.\d+(\.\d+)?([+-][A-Za-z0-9.-]+)?$` | `0.1.0` for a first publication, `1.0.0` once the contract is settled. |
| `ntopVersion` | `^\d+\.\d+(\+\|\.\d+)?$` | `6.1` or `5.43+`. See the build-number trap below. |
| `license` | 2 to 40 characters | An identifier, not a sentence. `MIT` in most packages. |
| `domain` | `Aerospace`, `Additive Manufacturing`, `Medical`, `Mechanical`, `Thermal`, `Simulation`, `Optimization`, `Geometry`, `AI Tools` | One value. Pick the primary one. |
| `complexity` | `Beginner`, `Intermediate`, `Advanced` | |
| `tags` | 1 to 8 items, each 1 to 24 characters | The schema does not enforce case. The catalogue README asks for lowercase search keywords. Practice is inconsistent: 23 tag values across 12 packages are mixed case, including `TPMS`, `Hilbert curve` and `BlendedWingBody`. Write lowercase kebab-case and expect a warning, not a CI failure, if you do not. |
| `preview` | `geometry`, `code`, `graph`, `bundle` | `graph` for a reusable block, `geometry` for a model, `bundle` for a multi-file delivery. |

## Optional fields

`org`, `application`, `coverImage`, `packageFile`, `verified`, `featured`, `releaseTag`, `communitySource`, `distribution`, `redirectUrl`, `aiModel`.

- `coverImage` and `packageFile` are filenames inside the package folder. The schema documents that the catalogue build auto-detects `cover.{png,jpg,jpeg,webp,svg,gif}` and otherwise prefers the first `.ntop`. Declare both explicitly when the folder holds more than one notebook; the implicit first-file rule is an ordering accident, not a choice.
- `distribution` is `download` by default. `redirect` requires `redirectUrl` and is checked by the validator. `request` shows an access form.
- `aiModel` names the model that helped design the package. The catalogue README states that setting it should also add the `ai-assisted` tag so the Browse page can filter. The schema does not enforce that pairing, but all fourteen manifests that set the field honour it, every one of them with `GPT-6 Astra`. The bundled checker treats a missing `ai-assisted` tag as an error.
- `verified` and `featured` are maintainer flags. A submission that sets them is asking the reviewer to delete them.
- `releaseTag` is unused across all published manifests. Tags exist in the repository as `<id>-v<version>`, for example `gear-profile-v1.0.0`, and are created on merge.

## The type enum conflict

The catalogue README lists `"Notebook"`, `"Bundle"`, or `"Installer"`. The schema enum is `Notebook`, `Block`, `Connector`, `Script`, `Bundle`. The schema wins, because it is what CI runs. `Installer` fails validation. The two packages that actually ship an installer, `IntactSimulation/intact-simulation-for-ntop` and `Sileom/sileom-simulate`, both declare `type: "Connector"` with `preview: "bundle"` and carry the `.exe` or `.msi` through Git LFS. Do not copy the README's list.

## The build-number trap

`ntopVersion` cannot express `6.1.0-rc 42926`. The pattern accepts a two-part or three-part number with an optional trailing `+`. A model authored on a release candidate therefore has no truthful field to sit in.

Declare the family in `ntopVersion` and the exact build in README prose, as the published aerospace packages do: state the recorded build, state that the minimum-version field cannot encode it, and state that compatibility with a public release has not been re-tested. Writing `6.1` alone, with no prose, asserts a compatibility claim nobody measured.

## Structural checks beyond the schema

`validate-manifests.js` adds four checks the schema cannot express:

1. `id` equals the folder slug.
2. `author` equals the parent folder name.
3. `README.md` exists in the package folder.
4. `distribution: "redirect"` implies `redirectUrl`.

It stops there. It never opens the `.ntop`, never resolves `packageFile` or `coverImage`, never looks at file sizes, and never reads the README it required. A manifest can pass CI while pointing at a file that does not exist. The bundled `check_package.py` closes that gap before a reviewer has to.

## A worked example

```json
{
  "id": "torx-custom-blocks",
  "type": "Bundle",
  "title": "Torx screw family: seven custom blocks",
  "summary": "Import a seven-block Torx screw assembly as custom block definitions, with recorded spec tables and the recipe check that compares it against nTop's own recording.",
  "author": "Cortex78",
  "version": "0.1.0",
  "ntopVersion": "6.1",
  "license": "MIT",
  "domain": "Mechanical",
  "application": "Geometry",
  "complexity": "Advanced",
  "tags": ["torx", "fasteners", "custom-block", "notebook-api", "iso14579", "ai-assisted"],
  "preview": "geometry",
  "coverImage": "cover.png",
  "packageFile": "torx-custom-blocks.ntop",
  "aiModel": "Claude"
}
```

Field order is not validated. The order above matches the published packages and keeps diffs readable.
