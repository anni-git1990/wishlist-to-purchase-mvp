# Myntra Wishlist Confidence MVP — Product and Implementation Context

## 1. Document Purpose

This document converts the feature-prioritization and MVP-validation slides into implementation context for product, design, engineering, data, QA and analytics teams.

The MVP should help high-intent users resolve fit and quality uncertainty inside Myntra and purchase at least one wishlisted product within 30 days, without discounts or other monetary incentives.

## 2. Business Objective

Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it.

### Primary business metric

**30-day Wishlist Purchaser Rate**

```text
Unique users purchasing at least one wishlisted item within 30 days
------------------------------------------------------------------------
Unique users adding at least one item to their wishlist
```

### Product outcome

Users gain enough confidence about fit and product quality to move a wishlisted item to the bag and complete the purchase without leaving Myntra for additional validation.

## 3. Validated Research Context

### Research base

- Survey responses: **34**
- Interviews: **6**
- Personas retained: **2**
  - Priya: Fit-Conscious Shopper
  - Dev: Quality and Review Validator

### Observed wishlist behavior

- **74%** added a product to their wishlist recently.
- **82%** revisited a wishlisted product at least once.
- **65%** revisited wishlisted products two or more times.
- **59%** used the wishlist while interested but still undecided.
- **82%** researched products outside Myntra.
- **82%** checked product reviews.
- **65%** checked customer photos.
- **32%** identified fit confidence as a potential purchase trigger.
- **100%** of interview participants remained interested in the saved product.
- **100%** of interview participants used external validation.
- Fit and size concerns appeared in **50%** of interviews.
- Quality and review concerns appeared in **67%** of interviews.

### Decision-matrix priority

| Problem area | Decision-matrix score | Priority |
|---|---:|---|
| Fit and size confidence | 24 | Primary |
| Quality and review confidence | 22 | Secondary |
| Product comparison | 18 | Later phase |
| Styling support | 14 | Later phase |

## 4. Problem Statement

High-intent users save products but delay purchase because fit, size, material quality and review information is incomplete, inconsistent or difficult to evaluate. They repeatedly revisit the wishlist and leave Myntra to check competitors, search engines, brand websites, friends or social platforms.

The primary gap is not lack of product interest. It is insufficient purchase confidence inside Myntra.

## 5. MVP Scope Summary

### Number of feature groups

The MVP contains **3 feature groups** with **10 core capabilities**.

| Feature group | Core capabilities | Status |
|---|---:|---|
| Fit Confidence Layer | 3 | Prioritized MVP feature |
| Review and Quality Digest | 3 | Prioritized MVP feature |
| Decision Trigger Layer | 4 | Cross-feature MVP enabler; hypothesis to validate |

### Phase-two feature

**Smart Wishlist Compare** remains outside the first MVP. It ranked third in the RICE analysis and should be evaluated after fit and quality confidence features have been tested.

### Explicitly out of scope

- Discounts, coupons, cashback or monetary incentives
- Full virtual try-on
- Automated styling or complete-look generation
- Comparing every product across external competitors
- Changes to checkout, payments or delivery operations
- Rebuilding Myntra's complete recommendation engine

## 6. Feature Requirements

### Feature 1: Fit Confidence Layer

#### User problem

Users are unsure which size will fit because brand sizing, fit reviews, stretch and post-wash behavior are inconsistent or unclear.

#### Core capabilities

1. **Personalized size recommendation**
   - Recommend the most suitable available size.
   - Use available profile, previous order, return and brand-size information.
   - Display a confidence level such as High, Medium or Limited evidence.
   - Explain the recommendation using plain language.

2. **Similar-body fit evidence**
   - Surface reviews and customer media from people with relevant fit attributes.
   - Show whether customers found the item small, true to size or large.
   - Do not expose another customer's personal information.

3. **Fit, stretch and post-wash summary**
   - Summarize recurring feedback about fit, stretch, shrinkage and comfort.
   - Link each summary theme back to supporting reviews.
   - Show “Insufficient evidence” when the review threshold is not met.

#### Expected user outcome

The user can select a size with greater confidence and move the item from wishlist to bag.

#### Acceptance criteria

- A recommendation is shown only when minimum evidence requirements are met.
- Recommendation confidence and supporting reasons are visible.
- The selected size is still validated against current inventory.
- Users can mark the recommendation as helpful or inaccurate.
- The experience has a clear fallback when profile or review data is insufficient.

### Feature 2: Review and Quality Digest

#### User problem

Users cannot easily determine whether actual material, durability and appearance match product images and descriptions.

#### Core capabilities

1. **Positive and negative review summary**
   - Summarize the most repeated positive and negative themes.
   - Separate verified observations from subjective opinions.
   - Display the number of reviews used and the last-updated date.

2. **Verified customer media**
   - Prioritize authentic customer photos and videos.
   - Allow users to filter media by product variant where possible.
   - Provide a direct route to the original review.

3. **Material and durability highlights**
   - Summarize feedback about fabric, finishing, color accuracy, construction and durability.
   - Avoid claims that are not supported by product data or reviews.
   - Show conflicting evidence instead of hiding disagreement.

#### Expected user outcome

The user can validate quality without visiting another platform.

#### Acceptance criteria

- Every generated summary is traceable to supporting reviews.
- Positive and negative evidence is presented together.
- Products with limited review evidence show an explicit warning.
- Reported or removed reviews are excluded from future summaries.
- Users can provide feedback on summary usefulness or accuracy.

### Feature 3: Decision Trigger Layer

#### Role in the MVP

This is a supporting capability across Fit Confidence and Review and Quality Digest. It should not be treated as a fourth competing solution.

#### Core capabilities

1. Notify users when relevant new customer reviews or photos are available.
2. Notify users when their selected size is back in stock or inventory becomes limited.
3. Show a “Your confidence questions may now be answered” message when new fit or quality evidence becomes available.
4. Send an occasion reminder only when the user has explicitly provided an occasion or reminder date.

#### Trigger rules

- Send only when the update is relevant to a wishlisted item.
- Deep-link to the exact item and updated confidence information.
- Respect notification permissions and channel preferences.
- Apply frequency caps to prevent repeated messages.
- Suppress triggers after purchase, wishlist removal or product unavailability.
- Do not use price drops, coupons or discount messaging in this MVP.

#### Expected user outcome

Users return when useful evidence has changed and can immediately continue the purchase decision.

## 7. Pages and Surfaces

The MVP requires **4 designed surfaces**: **3 customer-facing surfaces** and **1 internal reporting dashboard**.

### Customer-facing surfaces

| # | Page or surface | Type | Main content |
|---|---|---|---|
| 1 | Enhanced Wishlist Page | Existing page modified | Confidence status, recommended size, quality summary preview, evidence updates and add-to-bag action |
| 2 | Fit Confidence Detail Sheet | New detail surface | Size recommendation, confidence explanation, similar-body evidence, fit/stretch/post-wash summary and feedback action |
| 3 | Review and Quality Detail Sheet | New detail surface | Positive/negative themes, verified customer media, material and durability evidence and original-review links |

### Reused existing surfaces

- Product Detail Page: receives deep links from the wishlist and notifications.
- Bag: receives the selected product and size after the confidence step.
- Existing notification infrastructure: sends approved trigger messages.

### Internal surface

| # | Page or surface | Users | Main content |
|---|---|---|---|
| 4 | MVP Experiment and Quality Dashboard | Product, analytics, engineering and operations | Experiment results, feature engagement, model quality, notification performance and guardrail monitoring |

## 8. End-to-End User Journey

### Primary journey

1. User discovers a product and adds it to the wishlist.
2. Myntra records the wishlist timestamp, product, selected variant and available size context.
3. User revisits the wishlist.
4. Wishlist displays confidence information:
   - Fit recommendation and evidence for applicable apparel.
   - Review and quality summary for supported products.
5. User opens the relevant confidence detail sheet.
6. User reviews the recommendation, evidence and limitations.
7. User selects a size or product variant.
8. User adds the wishlisted product to the bag.
9. User completes checkout.
10. Analytics links the purchase to the original wishlist event and calculates whether it occurred within 30 days.

### Trigger-assisted journey

1. User saves a product but does not purchase it.
2. New relevant evidence or an inventory event becomes available.
3. Trigger service verifies relevance, consent, frequency cap and suppression rules.
4. User receives a non-monetary notification.
5. Notification deep-links to the exact updated confidence section.
6. User reviews the new evidence and proceeds to the bag or dismisses the message.

### Fallback journey

When evidence is insufficient:

- Do not generate a confident recommendation.
- Display “Limited evidence available.”
- Show the brand size chart and available verified reviews.
- Allow the user to request notification when more evidence becomes available.
- Continue to support the normal wishlist and product-detail journey.

## 9. Proposed Experiment

### Hypothesis

If users receive relevant fit and quality evidence inside the wishlist, supported by contextual non-monetary triggers, then more users will purchase at least one wishlisted product within 30 days.

### Eligible population

- Users who recently added an eligible apparel product to the wishlist.
- Users who have not purchased or removed the saved product.
- Products with sufficient inventory and minimum fit or review evidence.
- Users eligible for required personalization and notification processing.

### Experiment groups

| Group | Experience |
|---|---|
| Control | Current wishlist experience |
| Treatment | Fit Confidence Layer + Review and Quality Digest + eligible contextual triggers |

### Randomization

- Randomize at user level to avoid the same user seeing control and treatment experiences.
- Keep a user in the same group throughout the experiment.
- Check balance across platform, new/repeat customer, product category and historical purchase activity.

### Duration and sample size

- Indicative run time: **4–6 weeks**.
- Final duration depends on the 30-day outcome window, traffic and required statistical power.
- Calculate sample size using the current baseline conversion rate, chosen minimum detectable effect, 80% or higher power and the agreed significance level.
- Do not use the survey percentages as the production conversion baseline.

### Ship decision

Launch only when:

- The primary metric shows a statistically and practically meaningful improvement.
- Key guardrails remain within pre-agreed thresholds.
- Fit recommendations and review summaries meet quality standards.
- Results are not limited to one narrow or unstable segment.

## 10. Analytics Event Tracking

### Required events

| Event | Required properties |
|---|---|
| `wishlist_item_added` | user_id, product_id, variant_id, wishlist_timestamp, source_surface |
| `wishlist_viewed` | user_id, session_id, wishlist_item_count, experiment_group |
| `wishlist_item_revisited` | user_id, product_id, days_since_added, revisit_count |
| `fit_confidence_impression` | product_id, recommended_size, confidence_level, evidence_count |
| `fit_confidence_opened` | product_id, entry_surface, experiment_group |
| `size_recommendation_selected` | product_id, recommended_size, selected_size, accepted_recommendation |
| `quality_digest_impression` | product_id, review_count, media_count, summary_version |
| `quality_digest_opened` | product_id, entry_surface, experiment_group |
| `customer_evidence_opened` | product_id, evidence_type, review_id |
| `confidence_feedback_submitted` | product_id, feature, helpful, issue_type |
| `wishlist_trigger_sent` | product_id, trigger_type, channel, trigger_timestamp |
| `wishlist_trigger_opened` | product_id, trigger_type, channel, time_to_open |
| `wishlist_item_added_to_bag` | product_id, size, days_since_wishlist, experiment_group |
| `wishlisted_item_purchased` | order_id, product_id, days_since_wishlist, experiment_group |
| `wishlisted_item_returned` | order_id, product_id, return_reason, experiment_group |

### Event-quality requirements

- Use a stable wishlist-add timestamp for 30-day attribution.
- Deduplicate repeated client and server events.
- Validate event parity across Android, iOS and web.
- Exclude test accounts and internal traffic.
- Document late purchases, cancellations and returns consistently.

## 11. Reporting Framework

### Reporting views

The internal dashboard should contain five views:

1. Executive experiment summary
2. Conversion funnel
3. Feature engagement
4. Model and content quality
5. Guardrail and operational health

### Reporting cadence

| Cadence | Purpose |
|---|---|
| Daily | Instrumentation health, crashes, latency, notification failures and severe guardrail breaches |
| Weekly | Experiment exposure, feature engagement, funnel movement, segment balance and early directional trends |
| End of experiment | Statistical analysis, practical impact, segment consistency, guardrails and ship/no-ship decision |
| 30–60 days after rollout | Sustained conversion, repeat usage, return behavior and model-quality monitoring |

## 12. Metrics

### Primary metric

#### 30-day Wishlist Purchaser Rate

```text
Users who purchase at least one wishlisted item within 30 days
----------------------------------------------------------------
Users who add at least one item to their wishlist
```

Report:

- Control rate
- Treatment rate
- Absolute percentage-point lift
- Relative lift
- Confidence interval
- Statistical significance
- Sample size per group

### Supporting metrics

| Metric | Definition | Why it matters |
|---|---|---|
| Wishlist Revisit Rate | Users revisiting the wishlist ÷ users adding an item | Measures return to the decision space |
| Two-or-More Revisit Rate | Users revisiting at least twice ÷ users adding an item | Identifies persistent consideration behavior |
| Wishlist-to-Bag Conversion | Wishlisted items added to bag ÷ eligible wishlisted items viewed | Measures movement toward purchase |
| Revisit-to-Purchase Conversion | Users purchasing after a revisit ÷ users who revisit | Connects repeated interest with conversion |
| Fit Confidence Open Rate | Fit-detail opens ÷ fit-confidence impressions | Measures feature relevance |
| Size Recommendation Acceptance | Users selecting recommended size ÷ users receiving a recommendation | Measures recommendation adoption |
| Quality Digest Open Rate | Digest opens ÷ digest impressions | Measures demand for quality evidence |
| Customer Evidence Engagement | Customer media/review opens ÷ digest opens | Measures evidence use |
| Trigger Open Rate | Trigger opens ÷ delivered triggers | Measures trigger relevance |
| Trigger-to-Bag Conversion | Triggered users adding item to bag ÷ users opening trigger | Measures action after notification |
| Time to Purchase | Median days from wishlist addition to purchase | Measures decision speed |

### Guardrail metrics

| Metric | Definition | Risk controlled |
|---|---|---|
| Overall Return Rate | Returned wishlisted-item orders ÷ delivered wishlisted-item orders | Prevents low-quality conversion growth |
| Size-Related Return Rate | Size/fit returns ÷ delivered apparel orders from the feature | Detects poor fit recommendations |
| Cancellation Rate | Cancelled feature-attributed orders ÷ feature-attributed orders | Detects premature or mistaken purchases |
| Recommendation Disagreement Rate | Users selecting a different size ÷ users shown a recommendation | Detects weak recommendation relevance |
| Incorrect Recommendation Feedback | Inaccurate fit reports ÷ fit feedback submissions | Monitors model quality |
| Summary Issue Rate | Reported quality-summary issues ÷ digest opens | Detects misleading summaries |
| Notification Opt-Out Rate | Users disabling notifications after exposure ÷ notified users | Controls notification fatigue |
| Trigger Dismissal Rate | Dismissed trigger interactions ÷ trigger impressions | Detects irrelevant messaging |
| Wishlist Page Latency | P50, P95 and P99 page-load time | Prevents performance degradation |
| Feature Error Rate | Failed feature requests ÷ total feature requests | Controls technical reliability |

### Important measurement limitation

External research cannot be measured directly unless Myntra has appropriate consented instrumentation. Use internal proxies such as product-page exits, long inactivity after a wishlist revisit or voluntary user feedback. Do not label these proxies as confirmed competitor visits.

## 13. Data and Service Dependencies

### Data inputs

- Wishlist additions, removals, revisits and timestamps
- Product catalog and variant attributes
- Brand and product size charts
- Current inventory by size and variant
- Previous purchases, selected sizes and size-related returns
- Customer profile and optional fit preferences
- Verified reviews, review ratings and review text
- Customer photo and video metadata
- Product return reasons
- Notification permission and preference status

### Services

- Wishlist service
- Product catalog service
- Inventory service
- Review and media service
- Recommendation or fit-scoring service
- Summary-generation service
- Notification and deep-link service
- Experiment-assignment service
- Analytics event pipeline

### Indicative interfaces

```text
GET  /wishlist/{userId}/confidence
GET  /products/{productId}/fit-confidence
GET  /products/{productId}/quality-digest
POST /products/{productId}/confidence-feedback
POST /wishlist/triggers/evaluate
```

Final endpoint names and payloads must follow Myntra's internal API standards.

## 14. Quality, Privacy and Safety Requirements

- Do not infer or expose sensitive body information.
- Use explicit consent for optional profile or body-fit attributes.
- Allow users to edit or remove stored fit preferences.
- Explain why a size was recommended.
- Do not present low-confidence predictions as facts.
- Generated summaries must remain traceable to source reviews.
- Exclude abusive, fraudulent, removed or low-quality content.
- Apply review-count and freshness thresholds.
- Encrypt personal data in transit and at rest.
- Follow existing retention, deletion and access-control policies.
- Maintain accessibility for screen readers, text scaling and color contrast.

## 15. Edge Cases

- Product has no reviews or insufficient verified reviews.
- Available reviews contradict each other.
- Size chart is missing or outdated.
- Recommended size is out of stock.
- User has no purchase or return history.
- Product has multiple sellers or inconsistent variants.
- Review summary changes after a review is removed.
- Product is removed from the catalog after a trigger is scheduled.
- User purchases from another session before the trigger is sent.
- User removes the product from the wishlist.
- Notification is opened after the product becomes unavailable.
- User receives different recommendations across devices.

## 16. Indicative Delivery Plan

This plan is an implementation assumption and should be adjusted after engineering discovery.

| Phase | Indicative duration | Deliverables |
|---|---:|---|
| Discovery and data audit | 1–2 weeks | Data availability, evidence thresholds, baseline metrics, event taxonomy and technical design |
| Instrumentation foundation | 1–2 weeks | Wishlist attribution, experiment assignment, event validation and dashboard skeleton |
| Fit Confidence MVP | 2–3 weeks | Recommendation service integration, fit detail surface, fallback states and feedback |
| Review and Quality Digest MVP | 2–3 weeks | Summary service, evidence linking, verified media and quality feedback |
| Decision Trigger Layer | 1–2 weeks | Trigger rules, notification templates, suppression, frequency caps and deep links |
| QA and controlled rollout | 1–2 weeks | Functional QA, model/content QA, performance testing and staged exposure |
| Experiment | 4–6 weeks | Control/treatment evaluation and ship decision |

## 17. Team Responsibilities

| Role | Primary responsibility |
|---|---|
| Product Manager | Scope, prioritization, metric definitions, experiment and ship decision |
| Product Designer | Wishlist states, evidence hierarchy, detail surfaces, fallbacks and accessibility |
| Mobile/Web Engineering | UI integration, events, deep links and performance |
| Backend Engineering | Confidence APIs, trigger rules, inventory and wishlist integration |
| Data Science/ML | Fit scoring, review summarization, confidence levels and quality evaluation |
| Data Engineering | Feature inputs, event pipeline, attribution and dashboard datasets |
| Analytics | Baseline, MDE, sample size, experiment analysis and segment checks |
| QA | Functional, integration, cross-platform, notification and edge-case testing |
| Trust/Operations | Review quality, reported content and escalation workflows |

## 18. Definition of Done

The MVP is ready for experiment when:

- All three feature groups meet functional acceptance criteria.
- Fit and quality outputs show confidence and evidence limitations.
- Analytics events pass cross-platform validation.
- User-level experiment assignment is stable.
- The primary metric can be calculated end to end.
- Dashboard views are available before exposure begins.
- Frequency caps, opt-outs and suppression rules work correctly.
- P95 latency and error rates remain within agreed limits.
- Privacy, accessibility and content-quality reviews are complete.
- Control and treatment experiences pass QA.
- Experiment sample size and MDE are approved.

## 19. Post-MVP Decision Path

### If the MVP succeeds

- Roll out gradually by category and user segment.
- Improve recommendation coverage and confidence.
- Add Smart Wishlist Compare as a phase-two experiment.
- Evaluate styling or occasion support only after confidence features demonstrate value.

### If conversion improves but returns worsen

- Stop or limit rollout.
- Audit recommendation confidence, category performance and return reasons.
- Raise evidence thresholds before retesting.

### If engagement improves but purchase does not

- Review whether evidence is understandable and actionable.
- Test placement, explanation and add-to-bag continuity.
- Reassess whether the trigger reaches users at the right moment.

### If no meaningful improvement occurs

- Do not add more features immediately.
- Review event accuracy, feature exposure and segment fit.
- Conduct follow-up interviews with exposed users.
- Revisit the problem hypothesis before expanding scope.

## 20. Final Product Direction

The first MVP should not attempt to solve every wishlist problem. It should validate one clear causal chain:

```text
Wishlist interest
→ fit and quality uncertainty
→ confidence evidence inside Myntra
→ relevant non-monetary trigger
→ add to bag
→ purchase within 30 days
```

The MVP succeeds only when it increases qualified purchases without increasing returns, cancellations, notification fatigue or misleading recommendations.
