# Edge Cases & Corner Scenarios Matrix: Myntra Wishlist Confidence MVP

## Document Overview

This document specifies the complete edge case, boundary condition, and failure recovery matrix for the **Myntra Wishlist Confidence Engine (WCE)**. Grounded in [myntra_mvp_context (1).md](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/myntra_mvp_context%20%281%29.md), [architecture.md](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/architecture.md), and [implementation_plan.md](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/implementation_plan.md), this document details automated fallbacks, system recovery logic, and verification scenarios for every non-happy path.

---

## Matrix Summary by Functional Domain

```
+--------------------------------------------------------------------------------------------------+
|                                  EDGE CASE DOMAINS COVERED                                       |
|                                                                                                  |
| 1. Fit Recommendation & ML Model Scenarios (EC-100 to EC-108)                                   |
| 2. Review & Quality Digest NLP Scenarios (EC-200 to EC-207)                                      |
| 3. Decision Trigger & Notification Scenarios (EC-300 to EC-308)                                  |
| 4. Catalog, Inventory & Multi-Seller Scenarios (EC-400 to EC-406)                                |
| 5. A/B Experimentation & Analytics Event Scenarios (EC-500 to EC-507)                            |
| 6. System Infrastructure & Latency SLA Scenarios (EC-600 to EC-605)                              |
+--------------------------------------------------------------------------------------------------+
```

---

## Section 1: Fit Recommendation & ML Model Edge Cases

### EC-101: Cold-Start User (No Order History or Physical Profile)
*   **Trigger Condition**: User views wishlist item, but has zero past purchases, zero size returns, and has not provided optional height/weight preferences.
*   **Automated System Fallback**:
    1. ML engine assigns evidence score $= 30$ (Size chart availability only).
    2. Confidence level set to `LIMITED_EVIDENCE`.
    3. UI renders status badge *"Limited evidence available"* with standard brand size chart CTA.
    4. Displays generic category fit distribution (e.g., *"82% of buyers say True to Size"*).
*   **User Experience Impact**: Prevents false size guessing. User can manually open the size chart or complete an optional 2-step fit quick check.
*   **Test Protocol**: Execute `test_cold_start_user_recommendation_fallback()`.

---

### EC-102: Polarized / Bimodal Peer Review Evidence
*   **Trigger Condition**: Review fit data shows split consensus (e.g., 48% say *"Runs Small"* and 48% say *"Runs Large"* due to two distinct fabric variants or seller batches).
*   **Automated System Fallback**:
    1. ML engine detects variance score $\sigma^2 > 0.60$.
    2. Suppresses single size recommendation chip.
    3. Displays balanced alert badge: *"Fit varies by individual body structure"*.
    4. Fit detail sheet presents both peer groups side-by-side without hiding disagreement.
*   **User Experience Impact**: Builds trust by presenting honest user disagreement rather than forcing an inaccurate median recommendation.

---

### EC-103: Recommended Size Out of Stock Across All Sellers
*   **Trigger Condition**: ML engine calculates recommended size as `M`, but inventory for size `M` is `0` across all active marketplace sellers.
*   **Automated System Fallback**:
    1. Size chip renders: *"Rec. Size: M (Out of Stock)"* with greyed-out visual state.
    2. CTAs update to: `[ Notify Me When Restocked ]` and `[ View Alternate Size: L ]`.
    3. Alternate size `L` displays fit match percentage (e.g., *"Size L: 72% fit match - Relaxed Fit"*).
*   **User Experience Impact**: Avoids user frustration from adding an unpurchasable item to bag while suggesting viable size alternatives.

---

### EC-104: Recommendation Threshold Boundary Score
*   **Trigger Condition**: User-product fit score lands exactly at $69.5$ evidence points (boundary between `MEDIUM` and `HIGH` confidence).
*   **Automated System Fallback**:
    1. System enforces conservative rounding down: score $< 70.0 \rightarrow \text{Confidence} = \text{MEDIUM}$.
    2. Renders explanation: *"Medium match based on category sizing. Additional peer reviews recommended."*
*   **User Experience Impact**: Protects high-confidence label integrity.

---

### EC-105: User Selects Size Contradicting High-Confidence ML Recommendation
*   **Trigger Condition**: System recommends size `M` (88% match), but user explicitly selects size `XL`.
*   **Automated System Fallback**:
    1. Client accepts user's size choice without blocking Add-To-Bag action.
    2. Fires tracking event `size_recommendation_selected` with properties `recommended_size="M"`, `selected_size="XL"`, `accepted_recommendation=false`.
    3. Displays non-intrusive confirmation toast: *"Size XL selected. Need help? Check fit guide."*
    4. Logs event for offline ML retraining model evaluation.
*   **User Experience Impact**: Respects user autonomy while capturing disagreement data to improve future predictions.

---

## Section 2: Review & Quality Digest NLP Edge Cases

### EC-201: LLM Summary Hallucination / Non-Traceable Output
*   **Trigger Condition**: Aspect summarization engine generates a statement (e.g., *"Fabric contains 5% Spandex"*) that cannot be verified against source review text pointers.
*   **Automated System Fallback**:
    1. Post-generation Traceability Guardrail checks keyword overlap against indexed review text.
    2. Verification score drops below $100\% \rightarrow$ Summary rejected.
    3. Digest service falls back to pre-LLM extractive review snippet list.
    4. Triggers internal alert `LLM_TRACEABILITY_FAIL` to NLP monitoring team.
*   **User Experience Impact**: Eliminates hallucinated material claims.

---

### EC-202: Source Review Deleted or Moderated Post-Digest Generation
*   **Trigger Condition**: A key customer review used in a 24-hour batch quality digest is reported, flagged for abuse, or deleted by the user.
*   **Automated System Fallback**:
    1. Moderation service emits Kafka event `review_deleted` with `review_id`.
    2. Redis cache invalidator instantly purges cached key `digest_style_{productId}`.
    3. Re-summarization pipeline re-evaluates digest excluding deleted `review_id`.
*   **User Experience Impact**: Ensures removed or fraudulent reviews are scrubbed from customer evidence within $< 2$ hours.

---

### EC-203: Product Has Sarcastic or Idiomatic Reviews
*   **Trigger Condition**: Customer leaves review: *"Great shirt if you want to dress up as a balloon"*.
*   **Automated System Fallback**:
    1. Fine-tuned ABSA model evaluates contextual sentiment score (Negative fit aspect: *"Excessively Loose"*).
    2. Filters out sarcastic low-utility phrasing from display text snippets while maintaining underlying sentiment rating.
*   **User Experience Impact**: Prevents confusing or misleading review quotes from appearing in aspect cards.

---

### EC-204: Media Filter False Positive / False Negative
*   **Trigger Condition**: CNN classifier misidentifies a valid close-up fabric texture photo as blurry/low quality, or allows an irrelevant photo (e.g., packing box image).
*   **Automated System Fallback**:
    1. Users can tap `[ Report Photo ]` on the customer media carousel.
    2. Submits event `confidence_feedback_submitted` with `issue_type="IRRELEVANT_MEDIA"`.
    3. Media item automatically hidden when report count $\ge 3$.
*   **User Experience Impact**: User community crowdsourcing acts as a fail-safe for computer vision classification errors.

---

## Section 3: Decision Trigger Layer & Push Notification Edge Cases

### EC-301: Item Purchased on Alternative Device / Store Prior to Trigger Dispatch
*   **Trigger Condition**: User wishlists an item on iOS App, purchases it on Desktop Web, but a `SIZE_BACK_IN_STOCK` push notification is queued for iOS App.
*   **Automated System Fallback**:
    1. Trigger engine evaluates user state immediately prior to APNs/FCM dispatch.
    2. Query checks `wishlist_items` status: `status == 'PURCHASED'`.
    3. Notification suppressed instantly; event logged as `trigger_suppressed_already_purchased`.
*   **User Experience Impact**: Eliminates redundant, annoying notifications for items already bought.

---

### EC-302: Deep Link Opened on Outdated App Version
*   **Trigger Condition**: User receives push notification with deep link `myntra://wishlist/detail?itemId=123&sheet=fit`, but device runs app v17.2 (Fit Detail Sheet introduced in v18.0).
*   **Automated System Fallback**:
    1. Client deep link router fails to match `/detail?sheet=fit` route.
    2. Router gracefully falls back to standard Product Detail Page (PDP) for item `123`.
    3. Displays fallback banner: *"Update Myntra App to view new Fit Confidence features."*
*   **User Experience Impact**: Avoids app crashes or dead links on older app installs.

---

### EC-303: Stock Sells Out Between Push Notification Dispatch and User Tap
*   **Trigger Condition**: Push sent for size `M` restock ($qty = 2$). By the time user taps notification 20 minutes later, item is sold out again.
*   **Automated System Fallback**:
    1. Mobile app handles deep link and fetches real-time inventory for size `M`.
    2. Inventory $= 0 \rightarrow$ Opens Fit Detail Sheet with top banner: *"Size M sold out quickly! We can notify you on the next restock."*
    3. Pre-selects auto-notify toggle.
*   **User Experience Impact**: Contextual explanation prevents user confusion upon landing on an out-of-stock item.

---

### EC-304: Timezone Shift / Quiet Hours Edge Case
*   **Trigger Condition**: User travels from IST (India, UTC+5:30) to EST (New York, UTC-5). Trigger service schedules push at 14:00 IST (which is 03:30 EST local time).
*   **Automated System Fallback**:
    1. Trigger service checks user's last recorded client timezone header `X-User-Timezone`.
    2. Local device time calculated as 03:30 AM (Quiet Hours: 22:00 to 08:00).
    3. Delivery rescheduled to 08:30 AM local time.
*   **User Experience Impact**: Protects user sleep hours regardless of geographical location shifts.

---

## Section 4: Catalog, Inventory & Multi-Seller Edge Cases

### EC-401: Product Removed or Unlisted From Catalog
*   **Trigger Condition**: Saved wishlist product is deactivated, deleted, or marked out-of-catalog by Myntra seller operations.
*   **Automated System Fallback**:
    1. Wishlist service updates item state: `status = 'UNAVAILABLE'`.
    2. Renders item in wishlist as greyed out with label: *"Item no longer available"*.
    3. Fit confidence & review quality badges suppressed completely.
    4. Suppresses all automated triggers for this product ID.
*   **User Experience Impact**: Clean visual indication without orphan microservice API error requests.

---

### EC-402: Inconsistent Sizing Across Multiple Sellers
*   **Trigger Condition**: Shirt `style_3948102` is sold by Seller A (Brand original size scale) and Seller B (Parallel importer with US size scale).
*   **Automated System Fallback**:
    1. Wishlist item scope binds fit recommendation to specific `seller_id` + `sku_id`.
    2. Fit Detail Sheet displays: *"Sizing evidence for seller: Myntra Retail"*.
    3. Switching seller re-fetches seller-specific size chart mapping.
*   **User Experience Impact**: Prevents size recommendation mismatches caused by multi-seller sourcing variances.

---

## Section 5: A/B Experiment & Analytics Event Edge Cases

### EC-501: User Switches Accounts or Shops in Guest Mode
*   **Trigger Condition**: User logged in as `usr_123` (Treatment group) logs out and browses as Guest or logs in as `usr_456` (Control group) on the same mobile device.
*   **Automated System Fallback**:
    1. A/B experiment assignment engine evaluates `user_id`, NOT device ID.
    2. Client clears local L1 cache on logout/account switch.
    3. UI immediately updates to reflect newly active user account's experiment assignment.
*   **User Experience Impact**: Maintains clean experimental group isolation without cross-contamination.

---

### EC-502: Offline Event Queueing & Late Arrival
*   **Trigger Condition**: Mobile app user adds item to wishlist and makes purchase while offline (in subway/tunnel). Events queued locally and synced 3 days later.
*   **Automated System Fallback**:
    1. Event payload contains client-side UTC timestamp `added_timestamp`.
    2. Apache Flink stream processor relies on `added_timestamp` for 30-day window attribution calculation, ignoring event ingest timestamp.
    3. Late events up to 7 days accepted into analytics data warehouse.
*   **User Experience Impact**: Preserves 100% accurate conversion attribution regardless of network connectivity drops.

---

## Section 6: System Infrastructure & Resilience Edge Cases

### EC-601: Redis Cluster Cache Failure
*   **Trigger Condition**: Hot-tier Redis cache cluster experiences node outage or network partition.
*   **Automated System Fallback**:
    1. Wishlist API client circuit breaker trips after $50\text{ms}$ timeout.
    2. Request falls back directly to PostgreSQL read-replica and Feast feature store.
    3. Degrades non-essential ML features if latency exceeds $150\text{ms}$.
    4. Self-healing auto-reconnect retries Redis connection in background.
*   **User Experience Impact**: Core wishlist rendering remains operational even during caching layer outages.

---

### EC-602: Heavy Traffic Spike (Big Billion Days / EORS Flash Sale)
*   **Trigger Condition**: Traffic spikes to $50,000$ requests/sec ($3.3\times$ normal peak SLA).
*   **Automated System Fallback**:
    1. API Gateway enables dynamic rate limiting and shedding of non-critical background logs.
    2. Fit Confidence engine bypasses real-time KNN scoring and serves pre-computed nightly batch size recommendations.
    3. Quality digest falls back to static cached summaries.
*   **User Experience Impact**: Prevents complete site downtime by degrading from real-time ML inference to static pre-computed payloads.

---

## Complete Edge Case Matrix Summary

| Code | Domain | Trigger | Primary Fallback Mechanism | SLA / Recovery Time |
|---|---|---|---|---|
| **EC-101** | Fit ML | Cold-start user | Fallback to brand size chart + generic category stats | $< 10\text{ms}$ |
| **EC-102** | Fit ML | Bimodal fit split | Display split consensus alert; show side-by-side evidence | Instant |
| **EC-103** | Fit ML | Rec. size out of stock | Render size chip disabled + alternative size fit score | Instant |
| **EC-104** | Fit ML | Boundary score (69.5) | Round down to `MEDIUM` confidence | Instant |
| **EC-105** | Fit ML | Size choice mismatch | Accept user choice; log event for ML retraining | Instant |
| **EC-201** | NLP | LLM hallucination | Traceability check fails $\rightarrow$ Fallback to raw quotes | $< 5\text{ms}$ audit |
| **EC-202** | NLP | Review deleted | Invalidate Redis cache; re-summarize without review | $< 2$ hours |
| **EC-203** | NLP | Sarcastic reviews | ABSA sentiment filtering scrubs unhelpful quotes | Batch process |
| **EC-204** | NLP | Media false positive | Tapping `[Report Photo]` hides image after $\ge 3$ reports | Real-time |
| **EC-301** | Triggers | Item already bought | Suppress push notification before APNs/FCM dispatch | Instant |
| **EC-302** | Triggers | Outdated app version | Route deep link to standard PDP with app update banner | Instant |
| **EC-303** | Triggers | Stock sold out pre-tap | Open fit sheet with restock alert toggle pre-selected | Instant |
| **EC-304** | Triggers | Timezone mismatch | Reschedule push to local 08:30 AM quiet hours window | Async |
| **EC-401** | Catalog | Item unlisted | Mark item unavailable; suppress confidence badges & triggers | Real-time |
| **EC-402** | Catalog | Multi-seller sizes | Bind fit score to specific `seller_id` + `sku_id` | Instant |
| **EC-501** | AB Test | Account switch | Clear L1 cache; re-evaluate MurmurHash3 on new user ID | Instant |
| **EC-502** | Analytics | Offline event sync | Flink uses original client UTC timestamp for 30-day attribution | $< 7$ days backfill |
| **EC-601** | Infra | Redis failure | Circuit breaker trips at $50\text{ms} \rightarrow$ Fallback to Postgres DB | $< 50\text{ms}$ fallback |
| **EC-602** | Infra | $50\text{k}$ req/sec spike | Rate limit non-critical calls; serve batch pre-computed ML | Dynamic |
