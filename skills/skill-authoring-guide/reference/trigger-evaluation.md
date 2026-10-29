# Selection Evaluation

Evaluate the complete profile, not isolated words. Use exact expected skill sets when
the selection contract requires them.

- Test an owned request and a faithful paraphrase. Expect the profile to be selected.
- Change the distinguishing input or output to match a nearest neighbor. Expect the
  neighbor, rather than the profile under test, to be selected.
- Test a request that combines two genuinely required concerns. Select both owners
  when both are needed.
- Test owner, support, and reference requests separately. Do not make a reference
  profile appear to own execution.
- Test one case with a misleading file path and another with low-overlap wording.
  Meaning, not the path or shared nouns, must determine selection.
- Test an unrelated request and a request with no applicable skill. Do not force a
  broad-tag match or fallback.

When a case fails, edit the smallest tag, condition, or description that caused the
confusion. Re-run neighboring cases after every edit. Validate support names only
against the complete discovered inventory; class filtering must not hide a valid
support target.
