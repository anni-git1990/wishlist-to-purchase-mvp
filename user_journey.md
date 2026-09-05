# Myntra Wishlist Confidence MVP — Mobile UI User Journey Specification

Grounding Context: [`myntra_mvp_context.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/myntra_mvp_context.md) and [`implementation_plan.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/implementation_plan.md)

---

## 1. Executive Summary & Mobile UI Scope

This document specifies the end-to-end user journey for the **Myntra Wishlist Confidence Engine (WCE)** focused **exclusively on the Mobile Native UI (iOS & Android)** and smartphone container simulator (`http://localhost:8080`, `http://localhost:8501`, `http://localhost:9090`).

All customer-facing interaction surfaces are engineered as native mobile components (`mobile_app/src/`, `WishlistFitView.swift`, `WishlistFitScreen.kt`):
- **Surface 1**: Native Mobile Wishlist Screen (Chips, Badges, Snippets & Empty States)
- **Surface 2**: Personalized Fit Confidence Detail Bottom Sheet (Peer Evidence & Shrinkage Scale)
- **Surface 3**: Review & Quality Digest Detail Bottom Sheet (Aspect Sentiment Grid & CNN Photos)
- **Surface 5**: Contextual Push Notification Deep-Link Handler (APNs/FCM Universal App Links)

---

## 2. Mobile UI Journey Flow Architecture

```mermaid
graph TD
    subgraph S1 ["Surface 1: Native Mobile Wishlist & Catalog"]
        NAV["App Navigation Header<br/>- Dynamic Body Profile Switcher (Priya/Dev/Ananya)<br/>- Case-Insensitive Search Bar<br/>- Category Filter Pills"]
        GRID["Catalog Product Cards<br/>- Wishlist Heart Button (🤍 / ❤️)<br/>- One-Tap Add to Cart (🛒 Add)"]
        WISH_CARD["Native Wishlist Card<br/>- SizeRecommendationChip (✨ Rec. Size: M 88%)<br/>- QualityDigestSnippet Preview"]
    end

    subgraph S2 ["Surface 2: Fit Confidence Detail Bottom Sheet"]
        FIT_SHEET["Native Slide-Up Drawer<br/>- True-to-Size Match Bar (92%)<br/>- Post-Wash Shrinkage Risk (Low 2%)<br/>- Similar-Body Peer Evidence Feed (5'9\", 72kg)<br/>- Pre-Select Rec. Size & Add to Bag CTA"]
    end

    subgraph S3 ["Surface 3: Review & Quality Digest Bottom Sheet"]
        QUAL_SHEET["Native Slide-Up Drawer<br/>- LLM Traceable Summary<br/>- Aspect Sentiment Grid Badges (Fabric 96%, Color 94%)<br/>- CNN Customer Photo Variant Filters"]
    end

    subgraph S5 ["Surface 5: Contextual Push & Deep Linking"]
        PUSH["APNs / FCM Push Banner<br/>'🔔 3 new similar-height reviews added!'"]
        DEEP_LINK["Universal Link Gateway<br/>myntra://wishlist/detail?itemId=style_10001&sheet=fit"]
    end

    subgraph BAG ["Shopping Bag & Checkout Conversion"]
        CART["Shopping Bag Screen<br/>- Pre-Selected Size M Audit<br/>- Bidirectional Move Bag ➔ Wishlist<br/>- Place Order & Complete Checkout CTA"]
        LOG["Real-Time Flink Attribution<br/>- POST /api/checkout<br/>- Surface 4 Telemetry Logged"]
    end

    NAV --> GRID
    GRID -->|Tap 🤍 Heart| WISH_CARD
    WISH_CARD -->|Tap Fit Chip| FIT_SHEET
    WISH_CARD -->|Tap Quality Snippet| QUAL_SHEET
    WISH_CARD -->|Tap Move to Bag ➔| CART

    FIT_SHEET -->|Tap Pre-Select Size M| CART
    QUAL_SHEET -->|Close Sheet| WISH_CARD

    PUSH -->|Tap Banner| DEEP_LINK
    DEEP_LINK -->|Cold Start Deep Link| FIT_SHEET

    CART -->|Tap Place Order| LOG
```

---

## 3. Step-by-Step Mobile UI Screen Sequence

### Step 1: Catalog Discovery & Dynamic Body Profile Switcher (Home Screen)
*   **Mobile Touchpoint**: Native App Header & Catalog Grid (`/home`).
*   **UI Components**:
    *   **User Body Profile Selector**: Header dropdown allowing instant switching between user body personas:
        *   `👤 Priya (5ft 9in, 72kg)` $\rightarrow$ Baseline size M.
        *   `👤 Dev (6ft 1in, 85kg)` $\rightarrow$ Baseline size XL.
        *   `👤 Ananya (5ft 4in, 55kg)` $\rightarrow$ Baseline size S.
    *   **Case-Insensitive Search**: Live product filter (`searchInput`).
    *   **Category Pills**: Toggable filter chips (`All`, `Men`, `Women`, `Activewear`, `Ethnic`).
    *   **Card Interaction**: Tapping the `🤍` button updates state in real time to `❤️` with a non-blocking in-app toast notification (`❤️ Added to Wishlist!`).

```
+-------------------------------------------------------------+
| 📱 MYNTRA FASHION                        [👤 Priya 5'9" 72kg] |
| [🔍 Search 52 products...                                 ] |
| (All)  (Men)  (Women)  (Activewear)  (Ethnic)               |
+-------------------------------------------------------------+
| +-----------------------+   +-----------------------+       |
| | [Img]                 |   | [Img]                 |       |
| | ROADSTER              |   | HIGHLANDER            |       |
| | Pure Cotton Shirt     |   | Slim Fit Denim Shirt  |       |
| | ₹1,299  ₹2,599        |   | ₹1,499  ₹2,999        |       |
| | [❤️]  [🛒 Add]        |   | [🤍]  [🛒 Add]        |       |
| +-----------------------+   +-----------------------+       |
+-------------------------------------------------------------+
```

---

### Step 2: Surface 1 — Native Mobile Wishlist Screen
*   **Mobile Touchpoint**: Wishlist Tab (`/wishlist`, `Surface 1`).
*   **UI Components**:
    *   **`SizeRecommendationChip`**: Renders `✨ Rec. Size: M (88% match)` in emerald green for high confidence, or `⚠️ Limited Evidence` in amber for fallback items ($< 40$ evidence pts).
    *   **`QualityDigestSnippet`**: 1-line preview box (`"Quality Digest: 100% combed cotton, soft feel... View ➔"`).
    *   **Action CTAs**:
        *   `Move to Bag ➔`: Transfers item to Shopping Bag with pre-selected recommended Size M.
        *   `Remove`: Removes item from Wishlist.
    *   **Empty State View**: When empty, displays a vector heart icon with an actionable button: `Browse 52 Catalog Products ➔`.

```
+-------------------------------------------------------------+
| WISHLIST (1 Item)                                 Surface 1 |
+-------------------------------------------------------------+
| +---------------------------------------------------------+ |
| | [Product Img]  ROADSTER                                 | |
| |                Men Pure Cotton Casual Shirt             | |
| |                ₹1,299                                   | |
| |                [✨ Rec. Size: M  (88% match)]           | |
| |                                                         | |
| | [Digest: 100% combed cotton, soft feel... View ➔]       | |
| |                                                         | |
| | [Move to Bag ➔]                             [Remove]    | |
| +---------------------------------------------------------+ |
+-------------------------------------------------------------+
```

---

### Step 3: Surface 2 — Fit Confidence Detail Bottom Sheet
*   **Mobile Touchpoint**: Native Slide-Up Drawer Overlay (`Surface 2`).
*   **Trigger**: Tapping the `SizeRecommendationChip` on Wishlist or PDP.
*   **UI Components**:
    *   **Confidence Badge**: `HIGH MATCH` tag in top header.
    *   **Match Rationale**: `"Based on order profile & 18 peer reviews."`
    *   **True-to-Size Match Bar**: Visual progress bar (`92%`).
    *   **Post-Wash Shrinkage Bar**: Risk indicator (`Low (2%)` in green).
    *   **Peer Evidence Feed**: Cards showing verified customer feedback matching user body parameters (`Height: 5'9" • Weight: 72kg • Size Bought: M`).
    *   **Primary CTA**: `Pre-Select Rec. Size & Add to Bag` (Populates mobile bag with Size M, closes sheet, shows toast).

```
+-------------------------------------------------------------+
| ==================== SHEET HANDLE ========================= |
| Personalized Fit Confidence                    [HIGH MATCH] |
| Based on order profile & 18 peer reviews.                   |
|                                                             |
| True to Size Match: 92%                                     |
| [████████████████████████████████████████████████░░]        |
|                                                             |
| Post-Wash Shrinkage Risk: Low (2%)                          |
| [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]        |
|                                                             |
| Verified Similar-Body Peer Evidence                         |
| +---------------------------------------------------------+ |
| | Height: 5'9" • Weight: 72kg • Size Bought: M            | |
| | "Fits perfectly across chest and shoulders. Ideal."     | |
| +---------------------------------------------------------+ |
|                                                             |
| [ PRE-SELECT REC. SIZE M & ADD TO BAG                     ] |
+-------------------------------------------------------------+
```

---

### Step 4: Surface 3 — Review & Quality Digest Detail Bottom Sheet
*   **Mobile Touchpoint**: Native Slide-Up Drawer Overlay (`Surface 3`).
*   **Trigger**: Tapping the `QualityDigestSnippet` box.
*   **UI Components**:
    *   **LLM Summary Box**: Bulleted ABSA insights with 100% reverse pointers to customer `review_id`s.
    *   **Aspect Sentiment Grid**: Badges for key clothing aspects:
        *   `🧵 Material & Fabric: 96% Positive`
        *   `🧵 Color Permanence: 94% Positive`
        *   `🧵 Stitching Durability: 92% Positive`
    *   **CNN Photo Carousel**: Customer-uploaded photos passed through brightness/resolution CNN classifier, with size filter (`Filter: Size M`).
    *   **Primary CTA**: `Close Digest Sheet`.

```
+-------------------------------------------------------------+
| ==================== SHEET HANDLE ========================= |
| Verified Quality Digest                                     |
| +---------------------------------------------------------+ |
| | • 100% combed cotton, soft feel, highly breathable.     | |
| | • Color retention rated 4.8/5 across 42 reviews.        | |
| | • Reinforced double-stitching at collar and seams.      | |
| +---------------------------------------------------------+ |
|                                                             |
| Verified Aspect Sentiment Grid                              |
| [🧵 Material: 96%]  [🧵 Color: 94%]  [🧵 Stitching: 92%]   |
|                                                             |
| CNN Customer Photos                     [Filter: Size M]    |
| [Photo 1]  [Photo 2]  [Photo 3]                             |
|                                                             |
| [ CLOSE DIGEST SHEET                                      ] |
+-------------------------------------------------------------+
```

---

### Step 5: Surface 5 — Contextual Push Trigger & Deep-Link Handler
*   **Mobile Touchpoint**: System Notification Banner & App Link Handler (`Surface 5`).
*   **Trigger**: Inventory back-in-stock or new peer review addition (`SIZE_BACK_IN_STOCK` / `NEW_FIT_EVIDENCE`).
*   **Policy Enforced**: Strict **Zero Monetary Rule** (no discount triggers allowed); Redis Frequency Caps (Max 2/week).
*   **Deep-Link Sequence**:
    1. User receives Push Notification: *"🔔 3 new similar-height reviews added for Roadster Shirt!"*
    2. User taps notification banner.
    3. Mobile OS resolves Universal App Link: `myntra://wishlist/detail?itemId=style_10001&sheet=fit`.
    4. App cold-starts directly into Wishlist screen and automatically opens **Surface 2 Fit Detail Sheet**.

---

### Step 6: Shopping Bag & Real-Time Checkout Attribution
*   **Mobile Touchpoint**: Mobile Shopping Bag (`/bag`).
*   **UI Components**:
    *   **Selected Size Audit**: Clear indicator of pre-selected size (`Selected Size: M`).
    *   **Bidirectional Movement**: `Move Bag ➔ Wishlist` button allowing seamless return to Wishlist.
    *   **Checkout Execution**: `Place Order & Complete Checkout` CTA.
    *   **Attribution Event**: Tapping Checkout executes `POST /api/checkout`, emitting a real-time event to Apache Flink and updating **Surface 4 Admin Telemetry** (+4.33% purchaser lift logged).

---

## 4. Mobile User Journey Matrix

| Stage | Mobile Screen | User Interaction | System Response | Mobile Touch Target | Business Impact |
|---|---|---|---|---|---|
| **1. Discovery** | Home Screen (`/home`) | Filter by Category / Profile | Recalculates size matches live | Body Profile Switcher & Category Pills | Establishes fit baseline |
| **2. Wishlisting** | Home / PDP | Tap `🤍` Heart Button | Toggles `❤️` + Toast notification | `🤍` Heart Button | Intent capture |
| **3. Evidence** | Wishlist (`Surface 1`) | View `SizeRecommendationChip` | Displays Size M (88% match) | Size Recommendation Chip | Resolves initial size doubt |
| **4. Fit Audit** | Fit Sheet (`Surface 2`) | Tap Size Chip | Opens drawer with peer reviews | Fit Sheet Overlay | Eliminates size returns |
| **5. Quality Audit** | Quality Sheet (`Surface 3`) | Tap Quality Snippet | Displays Aspect Grid & CNN photos | Quality Snippet Box | Builds material trust |
| **6. Selection** | Wishlist / Fit Sheet | Tap "Pre-Select Size M & Add" | Pre-selects Size M in Cart | "Move to Bag" CTA Button | **+29.5% Add-to-Bag Lift** |
| **7. Conversion** | Shopping Bag | Tap "Place Order & Checkout" | Executes `POST /api/checkout` | Checkout CTA Button | **+4.33% Purchaser Lift** |
