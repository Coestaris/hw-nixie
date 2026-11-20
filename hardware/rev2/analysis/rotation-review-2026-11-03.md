# Nixie rev2 JLCPCB rotation audit — 2026-11-03

This report records the initial inspection and the subsequently authorized application of provisional rotation proposals. The resulting CPL is for placement-preview review, not production release. Native KiCad geometry, manufacturing profiles, and shared compatibility offsets remain unchanged.

## Applied proposals

The components-db and release skills and tools now support evidence-backed placement rotation reviews scoped to one project, board, and reference. SQLite schema 3 stores these decisions separately from shared compatibility reviews. The explicit schema cutover preserved all 7,771 existing rows across 17 tables, with foreign-key and integrity checks passing; a consistent pre-cutover backup is retained at `/tmp/components-before-placement-rotations-2026-11-03.sqlite3`.

Registered [rotation evidence](../../../../../assets/Assembly_Review/nixie_rev2-rotation-review-2026-11-03.json), retaining repository copies of the source screenshot, BOM, CPL, original audit, and subsequent exact-part footprint sources with SHA-256 hashes. The database now contains **59 concrete proposed targets and no unresolved angles**. All targets were imported after inspecting their dry run and applied to [nixie_rev2-rotation-preview-2026-11-03-all.csv](nixie_rev2-rotation-preview-2026-11-03-all.csv). This supersedes the earlier 54-change preview.

- All 106 source references remain present. Exactly 59 angles changed; X/Y coordinates and sides are identical to the retained source CPL.
- U8, U10 and U11 now use 270°; U12 and U13 now use 90°. Exact numbered-pad matching resolved their directions as described below.
- All 59 concrete targets retain `proposed` status pending a fresh JLCPCB preview check. Application of a target is separate from verifying the resulting manufacturer preview.
- Local BOM/CPL validation passes with no findings under the pinned manufacturing profile. Snapshot `2026-10-30` verifies with SHA-256 `81d969aa01d60d4886b9c8a6a21fa3ce6309f81baf3b4864de4b598556fb3202`.
- Rotation validation reports 59 `COMP-ROTATION-002` findings until the resulting JLC preview is checked. Production export remains blocked by this verification requirement.
- The full Python quality gate passes **293 tests**, including stale-input rejection, atomic import, project scoping, preview preservation of unresolved entries, and verified absolute-angle export. Both skill validators and ShellCheck on the quality script pass.

The remaining sections describe the original, pre-application angles. Their current-CPL column refers to the retained input, not the corrected preview.

## Catalog refresh and final five directions

Refreshed all 52 publicly available parts used by this project through the release workflow on 2026-11-03. Exact part C27035627 is still absent from the public assembly catalog: a direct refresh returned that specific unavailable-part error. Its stored timestamp was not falsified. The release workflow used the existing owner-approved private-quote exception in `hardware/rev2/release-warning-suppressions.json`; no new exception was added. Direct component validation still reports its stale timestamp, while the normal release workflow handles this narrowly approved case. The release attempt passed metadata and stopped at the component rotation-review findings, after catalog refresh.

For the previously unresolved directions, retrieved the exact part footprints from the **JLCEDA/EasyEDA Official Library** ([JLCEDA](https://lceda.cn/), [EasyEDA](https://easyeda.com/)), preserving the original API responses and their source/license metadata. Exact LCSC identities and MPNs match the catalog. The source footprint zero axes and pad-1 corners agree with the corresponding models at the original screenshot's retained CPL angles. [KiCad's EasyEDA format documentation](https://dev-docs.kicad.org/en/import-formats/easyeda/) supplies the PCB coordinate scaling.

Transformed every numbered source pad into the bottom-view coordinate frame and compared all four orthogonal rotations against the current board's numbered pads, obtained through `kicad10_tree`. Each selected angle is the unique full-pin match; the next-best rotation has RMS error above 1 mm.

| Reference | Exact part | Original CPL | Applied CPL | Numbered pads checked | Maximum center difference |
|---|---|---:|---:|---:|---:|
| U8 | C7519 / USBLC6-2SC6 | 180° | 270° | 6 | 0.011596 mm |
| U10 | C20617904 / ULN2003AIPWR(UMW) | 180° | 270° | 16 | 0.003258 mm |
| U11 | C20617904 / ULN2003AIPWR(UMW) | 180° | 270° | 16 | 0.003258 mm |
| U12 | C5948 / 74HC595PW,118 | 0° | 90° | 16 | 0.003258 mm |
| U13 | C5948 / 74HC595PW,118 | 0° | 90° | 16 | 0.003258 mm |

The [numbered-pad comparison figure](../../../../../assets/Assembly_Review/nixie_rev2-2026-11-03-numbered-pad-alignment.svg) was rendered and visually inspected. [Machine-readable alignment evidence](../../../../../assets/Assembly_Review/nixie_rev2-2026-11-03-numbered-pad-alignment.json) retains every numbered pad center, candidate residual, selected angle, source URL and hash. This resolves the angle choices; a fresh manufacturer placement preview is still needed to confirm the complete corrected CPL.

## Inputs and database result

Inspected the current board through `kicad10_tree pcb components list --project nixie_rev2 --format json`, and queried assignments and exact compatibility reviews through `components-db`.

The downloaded CPL contains **106 placements**. All 106 X/Y coordinates match the current board, including the CPL's negative Y convention. All 106 angles equal the board angle plus the exact stored review offset, modulo 360. All 106 assignments have an exact matching review; their stored status is `valid`. These status flags do not resolve the visual errors below.

| Reference | Exact LCSC part | Stored offset | Downloaded CPL angle |
|---|---|---:|---:|
| U1 | C5240411 | +270° | 90° |
| U2 | C116490 | +180° | 90° |
| Q1 | C8545 | +180° | 90° |
| Q10 | C15127 | +180° | 0° |

The other 102 stored offsets are 0°. The exporter already applies these offsets in [generate_artifacts.py](../../../../../tools/release/generate_artifacts.py#L1223); fetching the same records again will reproduce the current angles.

The catalog adapter does not obtain a KiCad-to-JLC rotation correction. The database rotation is an explicit review decision for an exact part / footprint / value combination.

## What the screenshot supports

The screenshot shows the bottom face. Several diagonal passives have their model axis across the PCB pads, whereas horizontal and vertical passive axes align. This is consistent with a bottom-side angle sign mismatch. A candidate for symmetric two-terminal parts is:

`candidate JLC angle = -current CPL angle (modulo 180°)`

This is an inference from the screenshot, not a verified conversion rule for every component. Do not apply it blindly to polarized parts or ICs. The current exporter uses `(KiCad angle + stored offset) % 360` for both sides. A model-specific bottom-side mapping may require `(-KiCad angle + independently reviewed model offset) % 360`. Existing additive offsets cannot be assumed to retain their meaning under that change.

| Reference | Current CPL | Provisional candidate | Visible evidence |
|---|---:|---:|---|
| C5 | 0° | 180° | Displayed positive terminal is left; PCB positive pad is right. |
| U1 | 90° | 270° | Body dot is opposite PCB pin-1 mark. |
| U3 | 315° | 135° | Body dot is opposite PCB pin-1 mark. |
| U9 | 270° | 90° | One-lead / two-lead sides are opposite the PCB pad arrangement. |
| Q10 | 0° | 180° | Two rendered leads are on the right; the PCB has two pads on the left. |
| D2 | 180° | 0° | Rendered cathode band is opposite PCB cathode pad 1. |
| D3 | 0° | 180° | Displayed cathode orientation is opposite PCB cathode pad 1. |
| D12 | 0° | 180° | Displayed positive terminal is opposite PCB anode pad 2. |
| U8, U10, U11 | 180° | 90° or 270° | Leads are perpendicular to pad rows; numbered pin mapping must choose direction. |
| U12, U13 | 0° | 90° or 270° | Leads are perpendicular to pad rows; numbered pin mapping must choose direction. |

All candidate angles assume the screenshot was produced with the downloaded CPL. No numeric angle column is visible in the screenshot, so that upload identity cannot be proven from the image alone. The diode/LED entries also depend on the displayed polarity matching the exact JLC model.

Q1 and U2 appear aligned despite their nonzero stored offsets. That is another reason to avoid applying one blanket transform to every current CPL angle.

**Q3, Q4, Q6, Q8, and Q22 have no visible component model.** They share exact part C50229541. The screenshot cannot establish that part's JLC zero orientation. Q2, Q5, Q7, and Q9 need a separate pad/pin review. BT1 and T1 also lack enough unambiguous model-pin information for an exact correction here.

JLCPCB explicitly describes the preview dot as an orientation mark, not a guaranteed pin-1 identifier. See [JLCPCB PCBA FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2). The physical model lead pattern, body mark, PCB numbered pads, and polarity must be reconciled together.

## Extracted audit table

[The retained source audit](../../../../../assets/Assembly_Review/nixie_rev2-2026-11-03-source-audit.csv) contains all 106 references, exact part identities, board angles, stored offsets, downloaded angles, proposed candidates, and limitations. It deliberately uses audit column names rather than manufacturing CPL headers. Blank candidate cells mean unresolved or no correction proposed, not verified zero correction.

- unresolved: 2
- symmetric_axis_unchanged: 30
- inferred_bottom_angle_candidate: 46
- proposed_180_degree_turn: 8
- no_obvious_shape_error: 6
- visible_sot23_needs_review: 4
- model_not_visible: 5
- quarter_turn_required_direction_unverified: 5

A new JLC preview and exact model/pin checks are required before accepting these candidates. Do not replace the stored reviews or release artifacts with this report. Persist accepted findings through the documented review workflow, preserving the other engineering gates and evidence.

## Source hashes

- `/home/taris/Downloads/nixie_rev2-jlcpcb-pnp.csv`: `4623c48a70bcfb8ac13a27fd89095a3f31a84d1cc9246ea8174679fd30b780c6`
- `/home/taris/Downloads/nixie_rev2-jlcpcb-bom.csv`: `9931dd9788d2f084f3bca20451ccf7cb1b1d9ae3f7c553e2d2bfdb5ada4e16ba`
- `/home/taris/Downloads/capture-2026-11-03T14_06_51.727Z.jpg`: `aa47a1deaf433660513b42086692ddefcef152a655f58d13972670545027725a`

