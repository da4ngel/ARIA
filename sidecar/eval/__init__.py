"""Measurement that the sidecar itself can run.

`probes.py` lived in `scripts/` until OpenRouter arrived. That was fine while
every measurement was a person running a script and reading the transcript —
but **`providers/adoption.py` runs the same probes from inside the process**,
and the sidecar cannot import from `scripts/`. Copying them would have given
the two paths different definitions of "grounded", which is the one thing that
must not drift: it is the control group that has already rejected two models.

So this is the single source, and `scripts/eval_quality.py` and
`scripts/measure_models.py` import it from here. Nothing in this package
reaches a provider — a probe is a prompt plus predicates over the reply, which
is what keeps the whole battery deterministic.
"""
