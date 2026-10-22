# Predicted-Endpoint Guidance and Masked Robustness Computation

## 1. The guided velocity field

STL-FM imposes a Signal Temporal Logic (STL) requirement on a pretrained flow-matching (FM) trajectory prior at inference time, without retraining. Generation integrates a single guided velocity field,

    v_guided(τ(s), s) = v_θ(τ(s), s) + λ₀ · ∇̃_τ̂ ρ_φ(τ̂(s))

from a Gaussian sample τ(0), s running from 0 to 1. The first term, v_θ, is the prior's own learned velocity — it moves the iterate toward trajectories that are plausible under the training distribution. The second term is the requirement term: a constant strength λ₀ times a conditioned gradient of the robustness score ρ_φ, which moves the iterate toward trajectories that satisfy the requirement φ. Neither term is trained with knowledge of the other; the prior never sees the requirement, and the requirement never updates the network. This separation is the method's central design choice.

The object this document explains is the second term: specifically, *where* ρ_φ and its gradient are evaluated, and *how* that evaluation is computed efficiently enough to run at every one of the sampler's integration steps.

## 2. The predicted endpoint

The flow runs in flow time s ∈ [0,1], which indexes the generative process and is distinct from physical time t, which indexes the states within a trajectory. At an intermediate flow time s, the current iterate τ(s) is a mixture of the Gaussian start τ(0) and the (unknown) finished trajectory — for small s it is dominated by noise.

Evaluating ρ_φ directly on τ(s) would therefore score a trajectory that is still mostly noise, and the gradient of that score would point toward whatever increases robustness on a noisy signal — a direction with no relation to any plausible trajectory. The method avoids this by evaluating the requirement not on τ(s) itself but on the predicted endpoint,

    τ̂(s) = τ(s) + (1 − s) · v_θ(τ(s), s)

the prior's running estimate, at flow time s, of what the trajectory will look like once integration finishes at s = 1. This identity follows from the geometry of the linear (optimal-transport) interpolation path used throughout: τ̂(s) is the current iterate extrapolated forward to s = 1 using the prior's own current velocity estimate. Because the prior is trained to produce plausible motion, τ̂(s) looks like a plausible trajectory at every flow time s, not only at the end — even though it is, early on, only a rough guess that keeps revising.

The score and its gradient are therefore computed as ρ_φ(τ̂(s)) and ∇_τ̂ ρ_φ(τ̂(s)), never as a function of τ(s) directly. A further detail: τ̂(s) is treated as a leaf of the computation graph when this gradient is taken — the gradient is not backpropagated through the network v_θ itself. This keeps the two roles separate: the prior supplies a plausible trajectory, and the requirement evaluates and scores that trajectory, without the requirement's gradient also reshaping how the network maps noise to trajectories.

## 3. Evaluated once per integration step, not once at the end

The sampler integrates the guided ODE with the Euler method over a fixed number of steps K (for example K = 64 in the reported navigation experiments). At every one of those K steps, the guidance block:

1. forms the predicted endpoint τ̂ from the current iterate and the prior's velocity,
2. evaluates ρ_φ(τ̂) and its gradient ∇_τ̂ ρ_φ(τ̂),
3. masks that gradient to the state coordinates the requirement actually constrains, normalizes its direction, and adds the resulting update, scaled by λ₀, to the prior's velocity for that step.

This means the robustness score is computed K times per generated trajectory, each time on a different, evolving τ̂(s) — not once, after the trajectory is finished. Separately, after integration completes, the *exact* (unsmoothed) robustness is computed once more on the finished trajectory to decide satisfaction for evaluation purposes — the quantity reported as a satisfaction rate. The smoothed score computed during generation and the exact score computed for the final verdict are deliberately different quantities, serving different roles: one must be differentiable to be climbed; the other must be sound to be trusted.

## 4. Computing ρ_φ at each step: the recursive construction

Each of the K evaluations of ρ_φ(τ̂) is itself computed by a fixed, generic procedure: the robustness score is built by structural recursion over the syntax tree of φ. A predicate node becomes a per-timestep margin; a conjunction or disjunction node becomes a min or max of its children's scores; a temporal operator node (Eventually or Always) becomes a max or min of its child's score over the operator's time window; Until is written out explicitly as a max of a min. This recursion is standard — it is the quantitative semantics of STL, differentiated by replacing exact min/max with a smooth surrogate (log-sum-exp, controlled by a sharpness parameter κ) so that automatic differentiation can supply a usable gradient. The construction contains no branch specific to a particular specification: a new requirement is simply a new syntax tree walked by the same recursion, and nothing about the planner is retrained to accommodate it.

## 5. Why the recursion's own internal computation has to be fast

Because this recursion runs K times per trajectory — once per integration step, as the trajectory estimate τ̂(s) changes — how expensive one evaluation is matters a great deal to the total cost of generation. The expensive part is not the recursion over the formula tree itself (which is typically shallow, a handful of nodes), but what happens *inside* each Eventually/Always/Until node: a sliding-window max or min has to be evaluated over the trajectory's time axis.

The earlier differentiable-STL implementation, STLCG, computes this sliding-window reduction recurrently: it walks the signal backward in time, one timestep at a time, maintaining a hidden state that tracks the running best value within the current window — mirroring how a recurrent neural network processes a sequence. This is correct, but it is inherently sequential: step t cannot be computed until step t+1 has been, so the cost scales with the length of the signal and does not parallelize well on a GPU.

## 6. STLCG++'s masking construction

STLCG++, the library this project actually evaluates formulas with (via its JAX interface, stljax), replaces that internal recurrence with a masking construction, modeled on the attention mask used in transformer architectures. For a single temporal operator with window [a,b] applied to a signal s = (s₀, …, s_T):

1. **Unroll.** The 1D signal is padded by the window length K at its end and repeated along a new axis, producing a 2D array in which every column is a shifted copy of the full signal. (Until needs one further dimension, since it combines a min over one subformula's history with a max over when the second subformula becomes true.)

2. **Mask.** A matrix of 0s and 1s, built from a subsignal mask (which keeps, in each column, only entries at or after that column's start time) combined with a time-interval mask (which additionally keeps only entries inside [a,b] relative to that start time), selects exactly the cells relevant to each column. Entries the mask excludes are overwritten with a large positive or negative constant, so they cannot affect the subsequent reduction.

3. **Reduce.** A single column-wise max (for Eventually) or min (for Always) produces the entire robustness trace — the operator's output starting from every timestep at once — in one vectorized tensor operation, rather than T sequential steps.

The resulting computation graph has a fixed shape for a given signal length, regardless of the window size [a,b]; only the mask's entries change when the window changes. This is what additionally allows the window bounds a and b themselves to be made differentiable, by replacing the hard 0/1 mask with a smooth, sigmoid-based version — a capability the recurrent formulation cannot offer, since there the size of the hidden state is tied directly to the window size.

Reported measurements in the STLCG++ paper show the masking approach achieving roughly 85–98% lower computation time than the recurrent approach on GPU across a range of formulas, with computation time that stays close to constant as the signal length grows (the one exception being Until, whose 3D unrolling costs cubic space and can be slower than the recurrent baseline on very long sequences).

## 7. Putting the two parts together

The practical reason these two pieces of the method belong in the same explanation: the predicted-endpoint construction (Section 2–3) requires the robustness score to be evaluated repeatedly, at every one of K integration steps, on a trajectory estimate that is different each time. That repeated-evaluation requirement is only practical because the score itself — the sliding-window max/min inside each temporal operator — can be computed as one fast, parallel tensor operation rather than a sequential walk through time. The masking construction is, in effect, what makes evaluating the requirement K times per generated trajectory computationally reasonable rather than a bottleneck. Neither piece is specific to the other in principle — the predicted-endpoint idea would still be correct with a slower score, and the masking construction is useful independently of predicted-endpoint guidance — but together they are what the guided sampler actually runs, once per step, for every trajectory it generates.

---

*Sources: the predicted-endpoint construction and guided velocity field are this thesis's own method (Chapter 4, "The Guided Velocity Field" and "The Predicted Endpoint"). The quantitative/recursive STL semantics are due to Donzé and Maler (2010), building on Maler and Nickovic's original STL (2004); the differentiable, smoothed version is due to Leung et al. (2021), "Backpropagation through Signal Temporal Logic Specifications." The masking construction is due to Kapoor, Mizuta, Kang, and Leung, "STLCG++: A Masking Approach for Differentiable Signal Temporal Logic Specification" (IEEE RA-L, 2025).*
