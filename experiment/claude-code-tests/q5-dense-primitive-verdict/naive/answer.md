# Q5: Dense Primitive Verdict — Answer

## 1. Has the current visual pipeline produced a dense, control-useful visual primitive field?

**No — but partially.** This is a split result. The current visual pipeline passes **coarse image-level coverage** but fails **key-aware dense primitive** coverage. The system produces sparse reliable landmarks, not a dense control-sufficient visual primitive field.

## 2. What evidence supports the answer?

### Evidence for coarse coverage (passes)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| Survival rate (valid region) | 0.5359 | >= 0.25 | Yes |
| Survivor precision (GT 2D) | 0.9998 | >= 0.75 | Yes |
| Cell coverage fraction (8x8 grid) | 0.9083 | >= 0.75 | Yes |
| Near-zero-disparity survivor fraction | 0.0000 | <= 0.25 | Yes |

The surviving correspondences are highly precise (precision ~1.0 against ground-truth correspondence), broadly distributed across the image at the 8x8 cell level, and show no near-zero-disparity collapse. Training produced small but measurable improvements over the untrained model (survival: 0.5258 -> 0.5359; key-landmark coverage: 0.765 -> 0.775; key-density fraction: 0.675 -> 0.70).

### Evidence against dense primitives (fails)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| Key landmark coverage (40 keys) | 0.775 | = 1.000 | No |
| Fraction keys at density >= 0.20 | 0.700 | >= 0.90 | No |

- Only 77.5% of 40 visible keyboard keys have at least one accurate survivor; the dense definition requires 100%.
- Only 70% of visible keys reach the local key-density threshold (>= 0.20 survivor density); the requirement is 90%.
- The key-surface survival rate does pass (0.5592 >= 0.50), meaning covered keys have decent surface coverage — the failure is specifically that coverage is not uniformly distributed over all keys.

### Official verdict

```
passes_q5_coarse_coverage_threshold: true
passes_q5_dense_primitive_threshold: false

Dense checks:
  all_keys_have_landmark:  false
  key_surface_area:        true
  key_local_density:       false
  survivor_precision:      true
  near_zero_disparity:     true
```

The correct summary from the Q5 doc: "Anti-aliasing plus a data-appropriate search radius produces reliable coarse coverage, but the system is not yet key-aware dense."

### Spatial bias assessment

- Gradient bias ratio: 1.04 (survivors only slightly biased toward high-gradient vs. the candidate pool)
- Boundary bias ratio: 0.93 (survivors slightly less concentrated near valid-mask boundaries than expected)
- No large-depth-ratio collapse (0.0 fraction)

These are not the dominant failure modes for Q5.

## 3. What should NOT be concluded from the Q5 result?

1. **Do not conclude the system has a dense surface field.** The surviving points are accurate where they exist but sparse and unevenly distributed across keys. The system is still fundamentally a *sparse landmark learner*.

2. **Do not conclude the model is useless.** Coarse coverage passes with high precision. The survivors are reliably accurate and spatially distributed enough for some forms of distributed anchoring.

3. **Do not conclude Q5 validates surface grouping, boundary inference, active control, or manipulation.** Q5 only tests whether correspondence coverage is dense and reliable enough to justify moving toward those later questions.

4. **Do not conclude training had no effect.** The trained model shows improvements over the untrained model in survival rate, key-landmark coverage, and key-density fraction, though the gains are modest.

5. **Do not conclude the search radius (r=4) is the bottleneck.** The Q5 doc explicitly states that r=4 is the fair main setting covering the data's 2.2–4.0 px frame-to-frame displacement. Q6 confirms r=4 is not the main bottleneck for missing density.

6. **Do not conclude failure is caused by near-zero-disparity collapse or large-depth-ratio artifacts.** Both metrics are at 0.0 in the after-training results.

## 4. What is the next diagnostic question?

**Q6: "Why do the current keyboard correspondences fail to become key-aware dense?"**

Q6 is the failure-attribution question directly following Q5. It decomposes the missing density into causal categories:

- Is the search window too small? (No — confirmed by Q6)
- Is GT invisible in later frames? (No — GT visible in all frames: 0.9992 fraction)
- Does an oracle candidate exist? (Yes — oracle can succeed: 1.000)
- Is frame0->frame1 matching wrong (repeated key/corner/edge confusion)?
- Are pairwise-OK points being rejected by the later-frame 3D consistency filter (triangulation amplification)?

Additionally, **Q7** generalizes the dense-failure question to a weakly textured 3D cube, testing whether the problem is keyboard-specific (repetitive key structure) or fundamental to local-appearance descriptors on low-texture surfaces.
