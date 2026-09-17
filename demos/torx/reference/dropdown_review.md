# Native dropdown / Choice List review

2026-09-15, nTop 6.0.3. Measurement witnesses are `probes/dropdown*`; source-code amendment is `src/lint/rules/R5.js`.

## Measured result

The public input type is **choice**. Native **Choice List** is `core.choice<text>`, accepting one text input per label. Downstream **Select by Choice** is `core.select_by_choice<choice,list_interface>`. A list of integers returns an integer, so family/series/drive codes need no text parsing or guessed property chain.

Five native probes converted and executed: constructor default -> 6; literal selected indices 0,1,2 -> 6,8,10; body Choice List constructor -> 6. All labels are T6, T8, T10. Each notebook has an adjacent exported JSON pair. Exports preserve the constructor/default distinction and all labels.

## Corpus search and complete exemplar

Read master JSON plus binary entries 105 (`core.choice<text>`) and 106 (`core.select_by_choice<choice,list_interface>`). Read full `work/doc_exports/230_7_3-CB---Point-from-Bounding-Box.json`: three public choice inputs each default to a three-label native Choice List; each selects from an inline three-element real list. The full custom-block identity is `user_func_b71d15c8_998e_4947_ba1b_44c29c5dbf30`. Recursive corpus search also found hundreds of Select by Choice uses. Existing catalogue builders use literal choice defaults to retain a selected index. Brief resolves both signatures from the master.

## Authoring forms

Native constructor in public input default:

```json
{
  "name": "Series",
  "type": "choice",
  "contents": {
    "func": "core.choice<text>",
    "id": "series_choices",
    "inputs": [
      {"type":"text","value":{"string":"M2"}},
      {"type":"text","value":{"string":"M2.5"}},
      {"type":"text","value":{"string":"M3"}}
    ]
  }
}
```

Measured constructor default selects the first label. To preserve a selected M3 default while retaining a native choice input:

```json
{"name":"Series","type":"choice","contents":{"type":"choice","value":{"choices":["M2","M2.5","M3"],"selected":2}}}
```

Select the numeric code with `core.select_by_choice<choice,list_interface>` taking this input and `core.list<integer>` of `[0,1,2]`. Wrap the result in a typed integer variable. This same pattern can map labelled drive choices directly to non-contiguous values `[0,6,8,10,...]`.

An explicit body Choice List block is also measured in `dropdown_body.recipe.json`: typed choice variable containing `core.choice<text>(T6,T8,T10)`, then Select by Choice into typed integer output. There is no need to use an integer user input as the visible selector.

## Headless input limitation and measured alternative

`ntopcl -t dropdown_constructor.ntop` fails with `Unrecognized or unsupported type "choice" for input "Drive size"`; it writes no input template. Do not claim direct choice support through scalar `-j`.

`dropdown_scalar.ntop` is a separate scalar test wrapper, importing `dropdown_constructor.json` unchanged. Integer Index chooses among three literal choice values, then calls the public choice-input block. Actual `-j` runs at Index=0,1,2 returned exactly 6,8,10. The wrapper is for testing; public UI remains choice typed.

## R5 correction

Before the amendment R5 falsely rejected the body Choice List as expecting one text input but receiving three; it did not inspect the equivalent constructor in an input default. The root-authorised correction narrowly exempts positive-length argument lists for exact `core.choice<text>`. Empty label lists remain rejected; all other fixed arities are unchanged. The comment names the native measurement witness.

`node projects/torx/probes/dropdown_lint_test.js` passes five semantic cases: one/three Choice labels accepted, zero labels rejected, missing sphere radius rejected, complete sphere accepted. Body Choice List then converted in 1.1 s and executed to integer 6. This is an actual native execution witness, not merely a syntactic regression.

## UI inspection boundary

The choice types, constructor grammar, selected index retention, and integer-selection behaviour are measured in native files and execution. Visual comparison of constructor/default rendering is delegated to the root's existing nTop UI session to avoid concurrent control of the same window. At the time of this report no screenshot has been inspected by this agent; do not treat this report alone as visual verification.

## Probe identities

- Constructor-input block: `user_func_8e06ebd7_6140_43d6_80f0_f05a067a8848<choice>`.
- Literal selected-index-1 block: `user_func_53d3d030_6ed3_4a6b_bae8_c9f01e164438<choice>`.
- Explicit body Choice List: `user_func_ec620f5d_2211_490c_b968_d097c9ab6d60`.

These are probe identities; public Torx should use the same native grammar, not import this demonstration catalogue.
