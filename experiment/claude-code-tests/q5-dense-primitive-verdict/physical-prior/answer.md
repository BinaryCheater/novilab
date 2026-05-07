# Q5 Dense Primitive Verdict — Physical-Prior Answer

## Direct Answer

**No.** The current visual pipeline has **not** produced a dense, control-useful visual primitive field. It produces a **coarse but reliable set of sparse landmarks** — high-precision survivors that cover broad image cells but fail to cover every visible object part (keyboard key) at sufficient local density.

The result is split: Q5 passes the coarse-coverage threshold but fails the key-aware dense-primitive threshold.

---

## Evidence Used

All evidence comes from the official Q5 report (`q5_dense_coverage_reliability.json`) on anti-aliased simulated keyboard data with `match_radius = 4`, plus the Q5 and Q6 source documents (`q5_dense_coverage_reliability.md`, `visual_foundation_meeting_catchup_cn.md`).

### What the trained model achieves (after training, 5 windows):

| Metric | Value | Dense threshold | Pass? |
|---|---|---|---|
| `mean_survival_rate_valid` | 0.5359 | ≥ 0.25 | ✅ coarse |
| `mean_cell_coverage_fraction` | 0.9083 | ≥ 0.75 | ✅ coarse |
| `mean_survivor_precision_gt2d` | 0.9998 | ≥ 0.95 | ✅ |
| `mean_near_zero_disparity_survivor_fraction` | 0.0000 | ≤ 0.05 | ✅ |
| `mean_accurate_key_landmark_coverage_fraction` | **0.7750** | **1.00** | ❌ dense |
| `mean_accurate_fraction_keys_survivor_density_ge_threshold` | **0.7000** | **0.90** | ❌ dense |
| `mean_accurate_key_surface_survival_rate_valid` | 0.5592 | ≥ 0.50 | ✅ key-surface area |

**Verdict fields from the JSON report:**
- `passes_q5_coarse_coverage_threshold`: **true**
- `passes_q5_dense_primitive_threshold`: **false**
- `all_keys_have_landmark`: **false** (only 31/40 keys = 77.5%)
- `key_surface_area`: **true**
- `key_local_density`: **false** (70% of keys reach threshold vs 90% required)

### Training effect (before → after):

Training produces a modest numerical improvement but **no qualitative shift**:
- Survival rate: 0.5258 → 0.5359 (+1.0pp)
- Key landmark coverage: 0.765 → 0.775 (+1.0pp)
- Center region survival rate: 0.207 → 0.215 (still very low)
- Fraction keys at density: 0.675 → 0.700 (+2.5pp)

None of these changes cross the dense threshold boundary. The gap between before and after is smaller than the gap between after and the dense requirement.

### Q6 failure attribution (why Q5 fails dense):

From the catch-up document, which references the Q6 failure attribution report:

1. **Frame0→frame1 pairwise matching already contains most of the dense information:** 85.92% of key-surface candidates are pairwise OK. If a GT oracle keeps these pairwise OK points, the pooled result would pass Q5 dense definition (key landmark coverage = 1.00, fraction keys at density = 1.00).

2. **The main bottleneck is the later 3D consistency filter, not search exclusion:** 68.06% of failures are "pairwise OK but later failed." Small pairwise errors (~0.54 px frame0→frame1 GT error) are amplified by small-baseline triangulation, causing the predicted reprojection to drift >2 px from the GT target.

3. **A smaller fraction of failures comes from first-pair confusion:** 99.36% of first-pair wrong matches involve other-key confusion, with 54.95% specifically other-key edge/corner confusion.

4. **Search radius is not the bottleneck:** GT target is in the search window for 100% of evaluated candidates; oracle candidate can succeed for 100%.

### Spatial bias evidence:

- **Center vs outer disparity:** Center region survival rate (0.215) is drastically lower than outer region (0.578). Many windows have **zero** survivors in the center.
- **Gradient bias ratio:** 1.041 (near 1.0, no strong gradient bias)
- **Boundary bias ratio:** 0.932 (near 1.0, no strong boundary bias)

The coverage failure is therefore not about surviving points concentrating on edges/corners — they're evenly distributed across gradient levels. Instead, the failure is that coverage is **spatially uneven**, with large holes concentrated in the keyboard center.

### What the evidence directly shows:

1. The reprojection-consistency filter produces survivors with **extremely high GT precision** (99.98%).
2. Survivors provide **broad image-level cell coverage** (90.8% of 8×8 cells).
3. No near-zero-disparity collapse and no large-depth-ratio collapse.
4. **But 22.5% of visible keys lack even one accurate survivor**, and only 70% of keys meet the local density threshold (vs. 90% required).
5. The missing dense coverage is concentrated in the **image center** and on specific keyboard keys, not uniformly spread.

---

## Unsupported Conclusions to Avoid

The following conclusions are **not supported** by the Q5 evidence and should be actively avoided:

1. **"We have a dense visual primitive field."** — False. Q5 explicitly fails the dense threshold. Survivors are sparse at the key level.

2. **"The pipeline produces control-sufficient visual state."** — Not supported. Control needs local surface orientation, boundary structure, and depth uncertainty — none of which Q5 evaluates or demonstrates. Having 77.5% key coverage is insufficient for reliable control.

3. **"Training a larger model / more data / better optimizer will make it dense."** — Not supported. The failure is structural (triangulation amplification, repetitive structure confusion), not due to insufficient capacity. Q6 shows that first-pair matching already contains dense information; the bottleneck is geometric consistency, not model expressivity.

4. **"The high survivor precision means the system is reliable everywhere."** — Misleading. Survivors are highly precise where they exist, but 22.5% of keys have zero survivors and 46.4% of valid pixels are non-survivors.

5. **"Coarse cell coverage passing means the system is spatially complete."** — False. An 8×8 cell can be "covered" with a single survivor, which provides no local surface information. Key-aware coverage reveals the gap.

6. **"The system can be directly extended to surface reconstruction, boundary inference, or active observation."** — Not supported. Q5 only evaluates correspondence survival and coverage. It validates none of the downstream capabilities.

7. **"The result generalizes to real data, different objects, or longer time windows."** — Not tested. This is simulated keyboard data with known camera motion.

8. **"The result means the learned features are robust visual primitives."** — Not supported. The features support reliable matching where Q4 conditions hold (appearance distinguishable + temporally stable + locally distinctive), but these conditions hold for only ~14.8% of points.

---

## Next Diagnostic Question

**Q5+1 (Motion-Conditioned Matching):** If the first-pair matching is conditioned on ego-motion and inverse-depth uncertainty — so that candidate selection is constrained by physically possible 3D geometry *before* the later consistency filter — does this reduce the "pairwise OK but later failed" failure rate enough to close the gap between coarse cell coverage and key-aware dense coverage?

**Targeted failure mode:** Triangulation amplification of subpixel first-pair errors under small baseline, as identified by Q6 (68.06% of failures). By incorporating ego-motion priors into the matching step itself — e.g., using the known camera displacement to predict a search region in inverse-depth space — physically impossible matches can be rejected at candidate time rather than after a fragile two-view triangulation.

**Falsification condition:** If motion-conditioned matching does **not** increase `accurate_key_landmark_coverage_fraction` above 0.90 (from the current 0.775), the primary bottleneck is not triangulation amplification but the fundamental indistinguishability of local appearance on texture-poor key surfaces — which would point instead toward multi-scale context, surface-aware aggregation, or active parallax as necessary next steps.

**Why this follows the evidence chain:** Q4 established *when* local matching works. Q5 established *how much* coverage exists. Q6 established *why* coverage fails. The next step targets the dominant failure mechanism (triangulation amplification) with a falsifiable physical-prior intervention (motion-conditioned matching) rather than a speculative scaling bet.

**Alternative next question (if triangulation amplification is not the preferred target):**

**Q5+1-alt (Depth Uncertainty Prior):** If the later consistency filter is replaced with a depth-uncertainty-aware multi-view update — maintaining an inverse-depth distribution per candidate rather than enforcing a hard pass/fail after a single two-view triangulation — does the fraction of keys with adequate survivor density reach the 0.90 dense threshold?

**Targeted failure mode:** The rigidity of the current consistency filter, which uses a single two-view triangulation followed by a hard reprojection threshold. Q6 evidence shows that many pairwise-OK points fail because subpixel error gets amplified in depth, but their later visual matches are actually closer to GT than to the erroneous reprojection. A softer uncertainty-aware filter could retain these points.
