# STOP — unreviewed populated-layer draft, do not run

`make-layer-populated-reader.py` was being drafted by main when the user asked
to stop. It has **not been run**. No `layer-populated-reader.ms` was produced,
parsed, `fileIn`-ed or executed. Its docstring describes an intention, **not**
a verification or authorization.

The draft is unsafe as written and must **not** be run or treated as a template
for live construction or cleanup:

* It discovers the supposed manager witness from the same dependency list by a
  class-name match. That is not an independently retained or authenticated
  witness. A handle roundtrip does not fix this.
* It supplies `rootScene` to a candidate which explicitly requires
  `rootNode == rootWitness[1]`; the live reads showed `rootScene != rootNode`.
  This does not repair the original dependency-identity mismatch.
* It can call `delete node` without a calibrated closed dependency graph or
  independently retained current-attempt witness. The source does not establish
  that no foreign node **or non-node** dependents would be affected.
* Its local reference/stage bookkeeping does not prove survival across a fileIn
  interruption or immediately mirror constructor returns to a separately retained
  witness before risky reads. Name, handle, count or a newly acquired reference
  cannot repair an interrupted identity chain.
* Admission/postchecks and layer deletion lack all the safety, survivor-set and
  stage-specific guarantees required by the P3.1 contract. The draft is not an
  independently reviewed, bounded or verified cleanup protocol.

Preserve it as historical unexecuted work; do not generate its output, weaken
guards, delete it, or reuse it without a new, independently reviewed design.
See `Audit/phase16-p3-controller-incident-2026-11-03f/report.md`,
`Audit/phase16-p3-hardening-independent-2026-11-03f/REPORT.md`, and the
current handoff. P3.1 remains **NOT ACCEPTED**.
