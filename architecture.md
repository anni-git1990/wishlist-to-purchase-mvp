# Architecture Specification: Myntra Wishlist Confidence MVP

## Document Metadata

| Attribute | Value |
|---|---|
| System Name | Myntra Wishlist Confidence Engine (WCE) |
| Target Release | MVP v1.0 |
| Context Reference | [myntra_mvp_context (1).md](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/myntra_mvp_context%20%281%29.md) |
| Architecture Status | APPROVED FOR IMPLEMENTATION |
| Primary Objective | Resolve fit & quality uncertainty to convert wishlist items into purchases within 30 days |

---

## 1. System Overview & Core Architectural Principles

### 1.1 Purpose & Executive Summary
The **Myntra Wishlist Confidence Engine (WCE)** is an enterprise microservice extension designed to reduce purchase friction for high-intent shoppers. By surfacing personalized size recommendations, similar-body fit evidence, NLP-generated quality digests, and verified customer media directly within the Wishlist interface, the platform addresses the primary drivers of purchase hesitation without resorting to monetary discounts.

```
+-----------------------------------------------------------------------------------+
|                                  BUSINESS HYPOTHESIS                              |
| High-Intent Wishlist Saver  --->  Fit & Quality Evidence  --->  Confidence Boost  |
|                                                                        |          |
|  30-Day Wishlist Purchaser Rate Increase  <---  Move to Bag & Checkout <---+          |
+-----------------------------------------------------------------------------------+
```

### 1.2 Core Architectural Principles

1. **Non-Blocking Read Path & Sub-100ms Latency**: Wishlist core rendering must never be blocked by ML model evaluation or heavy NLP aggregation. Confidence metadata is pre-computed, cached asynchronously, and served with a P95 latency limit of `< 100ms`.
2. **Graceful Fallback & Degradation Hierarchy**: If ML inference, user profile data, or review density falls below confidence thresholds, the system seamlessly degrades to brand size charts and standard review lists without UI breakage or false guidance.
3. **Traceability & Model Explainability**: All AI/NLP-generated summaries (fit notes, stretch warnings, material durability highlights) must maintain strict reverse-traceability IDs pointing to verified source reviews.
4. **Privacy-by-Design & Anonymity**: User body attributes and fit preferences are stored in encrypted user feature stores. Social proof and peer evidence explicitly scrub all Personally Identifiable Information (PII) before client delivery.
5. **Decoupled Event-Driven Architecture**: User actions, inventory changes, and new customer reviews trigger asynchronous events via Apache Kafka, ensuring low coupling between the core E-Commerce Engine, ML Pipelines, and Notification Gateway.

---

## 2. High-Level System Architecture & Component Topology

The diagram below illustrates the end-to-end multi-tier architecture spanning Client Surfaces, API Gateway, Core Microservices, ML Pipelines, Storage Infrastructure, and Analytics.

```mermaid
graph TB
    subgraph Client Surfaces [Client Layer]
        iOS[iOS App - Swift/UIKit]
        Android[Android App - Kotlin/Jetpack]
        Web[Web App - React/Next.js]
        Dash[Internal Experiment Dashboard]
    end

    subgraph Gateway [API & Routing Layer]
        APIGW[Kong / Envoy API Gateway]
        AuthService[OAuth2 / JWT Token Service]
        ExpRouter[A/B Routing & Feature Flags]
    end

    subgraph Microservices [Core Microservice Layer]
        WishlistSvc[Wishlist Core Service]
        FitSvc[Fit & Size Recommendation Service]
        DigestSvc[Review & Quality Digest Service]
        TriggerSvc[Decision Trigger & Notification Engine]
        FeedbackSvc[Confidence Feedback Service]
    end

    subgraph ML_NLP [ML & Intelligence Layer]
        FitML[Fit Recommendation Model API]
        ReviewNLP[Aspect-Based Sentiment & Summarization LLM Engine]
        MediaScorer[Customer Media Authenticity Classifier]
    end

    subgraph DataStorage [Data & Storage Layer]
        RedisCache[(Redis Cluster - Hot Tier Cache)]
        WishlistDB[(PostgreSQL - Core Wishlist DB)]
        FeatureStore[(Feast / Redis - User & Product Feature Store)]
        MongoDigest[(MongoDB - Review Summaries & Media Metadata)]
        Kafka[Apache Kafka - Event Streaming Backbone]
    end

    subgraph Analytics [Data Engineering & Reporting]
        Flink[Apache Flink - Real-time Attribution]
        Snowflake[(Snowflake / BigQuery - Data Warehouse)]
        Metabase[Internal Reporting & Experiment Dashboard]
    end

    %% Routing
    iOS --> APIGW
    Android --> APIGW
    Web --> APIGW
    Dash --> APIGW

    APIGW --> AuthService
    APIGW --> ExpRouter
    ExpRouter --> WishlistSvc
    ExpRouter --> FitSvc
    ExpRouter --> DigestSvc
    ExpRouter --> TriggerSvc
    ExpRouter --> FeedbackSvc

    %% Service Interconnects
    WishlistSvc --> RedisCache
    WishlistSvc --> WishlistDB

    FitSvc --> FeatureStore
    FitSvc --> FitML
    FitSvc --> RedisCache

    DigestSvc --> MongoDigest
    DigestSvc --> ReviewNLP
    DigestSvc --> RedisCache

    TriggerSvc --> Kafka
    TriggerSvc --> RedisCache

    FeedbackSvc --> Kafka
    FeedbackSvc --> MongoDigest

    %% Event Streams
    WishlistSvc -.->|Wishlist Events| Kafka
    FitSvc -.->|Inference Events| Kafka
    DigestSvc -.->|Digest Impression Events| Kafka
    Kafka --> Flink
    Flink --> Snowflake
    Snowflake --> Metabase
```

---

## 3. Client Architecture & UI Surfaces

The MVP requires **4 dedicated surfaces**: 3 customer-facing client surfaces and 1 internal experiment reporting dashboard.

```
+-----------------------------------------------------------------------------------+
|                            CLIENT SURFACES & NAVIGATION                           |
|                                                                                   |
|  [ Enhanced Wishlist Page ]  ----(Tap Fit Card)----> [ Fit Detail Sheet ]         |
|             |                                                                     |
|             +-----------------(Tap Quality)-----> [ Quality Digest Sheet ]        |
|             |                                                                     |
|             +-----------------(Add to Bag)------> [ Myntra Shopping Bag ]         |
+-----------------------------------------------------------------------------------+
```

### 3.1 Enhanced Wishlist Page (Surface 1 - Existing Modified)
*   **Role**: Primary discovery & decision hub.
*   **UI Components**:
    *   `ConfidenceStatusBadge`: Displays "High Fit Match", "Medium Fit Match", or "Limited Evidence".
    *   `SizeRecommendationChip`: Inline chip displaying "Rec. Size: M (85% match)".
    *   `QualitySummarySnippet`: 1-line aspect summary (e.g., "Fabric: 100% Cotton, True to size, Post-wash shrink < 2%").
    *   `TriggerBanner`: Highlights new evidence or low stock alerts (e.g., "3 new reviews from buyers with your fit added").
    *   `QuickAddToBagCTA`: Contextual add-to-bag pre-selected with recommended size.

### 3.2 Fit Confidence Detail Sheet (Surface 2 - New Surface)
*   **Role**: Resolves brand sizing, fit variation, and post-wash uncertainty.
*   **UI Components**:
    *   `PersonalizedSizeWidget`: Explains size choice based on previous orders, returns, and brand scale.
    *   `FitAttributeBars`: Visual meters for Fit (Runs Small <-> True to Size <-> Runs Large), Stretch (Low <-> High), Post-Wash Shrinkage.
    *   `PeerEvidenceFeed`: Filtered, anonymized review quotes from users with similar height/weight/fit profiles.
    *   `FeedbackActionRow`: "Was this recommendation accurate? [Yes] [No]".

### 3.3 Review & Quality Detail Sheet (Surface 3 - New Surface)
*   **Role**: Validates fabric, finish, color accuracy, and construction durability.
*   **UI Components**:
    *   `AspectSentimentGrid`: Key-value aspect cards highlighting positive & negative clusters (e.g., "+ Soft Material", "- Color Fades Slightly").
    *   `VerifiedMediaCarousel`: High-resolution customer photos/videos filtered by product variant (color/size).
    *   `DurabilityScorecard`: Aggregated rating on stitch quality, fabric weight, and color fidelity.
    *   `SourceReviewLink`: Direct jump anchor to original customer reviews.

### 3.4 MVP Experiment & Quality Dashboard (Surface 4 - Internal Web Admin)
*   **Role**: Real-time experiment monitoring, conversion funnel analysis, ML guardrail alerts.
*   **Built With**: React / Next.js + Tailwind CSS + Recharts / D3.js interfacing with Snowflake/BigQuery.
*   **Key Views**:
    1.  *Executive Experiment Summary*: 30-day Wishlist Purchaser Rate, Control vs Treatment Lift, Statistical Significance ($p$-value), Sample Size.
    2.  *Funnel Conversion Analytics*: Wishlist View $\rightarrow$ Detail Sheet Open $\rightarrow$ Rec Size Selected $\rightarrow$ Bag Add $\rightarrow$ 30-Day Purchase.
    3.  *Feature Engagement & Adoption*: Open rates, media tap-through rates, feedback submission volumes.
    4.  *ML Model & Content Audit*: Recommendation disagreement rate, inaccuracy report volume, summary hallucination audit logs.
    5.  *Guardrail Monitoring*: Size-related return rate spikes, order cancellation rates, push notification opt-out trends, API P95 latency.

---

## 4. Microservices Architecture & Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Customer (App/Web)
    participant GW as API Gateway / Router
    participant WVC as Wishlist Service
    participant FCS as Fit Confidence Service
    participant QDS as Quality Digest Service
    participant Cache as Redis Cluster Cache
    participant Kafka as Kafka Event Bus

    User->>GW: GET /api/v1/wishlist/{userId}/confidence
    GW->>WVC: Fetch Wishlist Items
    WVC->>Cache: Multi-Get Cached Confidence Metadata

    alt Cache Hit (90%+ cases)
        Cache-->>WVC: Return Pre-computed Confidence Payloads
    else Cache Miss
        WVC->>FCS: Fetch Fit Recommendation (Product List, UserId)
        FCS-->>WVC: Fit Payloads & Confidence Scores
        WVC->>QDS: Fetch Quality Digest (Product List)
        QDS-->>WVC: Quality Summaries & Media
        WVC->>Cache: Asynchronously Cache Aggregated Result (TTL: 1hr)
    end

    WVC-->>GW: Consolidated Wishlist & Confidence Payload
    GW-->>User: Render Enhanced Wishlist UI
    WVC-.->|Emit Event: wishlist_viewed| Kafka
```

---

## 5. REST & OpenAPI 3.0 API Specifications

All endpoints enforce OAuth 2.0 Bearer Authentication (`Authorization: Bearer <JWT>`), HTTPS TLS 1.3, standard `X-Correlation-ID` header propagation, and strict JSON response formatting.

### 5.1 Endpoint: `GET /api/v1/wishlist/{userId}/confidence`
Fetches all wishlist items enriched with fit recommendations, quality digests, and evidence trigger flags.

#### Request Headers
```http
GET /api/v1/wishlist/usr_98745210/confidence HTTP/1.1
Host: api.myntra.com
Authorization: Bearer eyJhbGciOiJKV1QiLC...
X-Correlation-ID: c8f64e04-8ed9-4e04-8ed9-fa08da19b605
X-App-Platform: iOS
X-App-Version: 18.4.0
```

#### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "userId": "usr_98745210",
    "experimentGroup": "TREATMENT_FIT_QUALITY_V1",
    "wishlistCount": 3,
    "items": [
      {
        "wishlistItemId": "witem_00192837",
        "productId": "style_3948102",
        "brandName": "Roadster",
        "productTitle": "Men Pure Cotton Slim Fit Casual Shirt",
        "addedTimestamp": "2026-08-20T10:15:30Z",
        "daysInWishlist": 15,
        "selectedVariant": {
          "skuId": "sku_991823",
          "size": "M",
          "color": "Navy Blue",
          "inStock": true,
          "availableQuantity": 4
        },
        "fitConfidence": {
          "confidenceLevel": "HIGH",
          "recommendedSize": "M",
          "fitMatchPercentage": 88,
          "explanation": "Fits true to size based on 4 previous shirt purchases from Roadster with zero returns.",
          "hasSimilarBodyEvidence": true,
          "evidenceCount": 42,
          "summary": {
            "fitScale": "TRUE_TO_SIZE",
            "stretch": "MODERATE",
            "shrinkageRisk": "LOW"
          }
        },
        "qualityDigest": {
          "reviewCount": 184,
          "mediaCount": 26,
          "overallQualityScore": 4.4,
          "summaryPreview": "100% breathable cotton, minimal color fading after 5 washes.",
          "topPositiveAspect": "Fabric Softness",
          "topNegativeAspect": "Button Stitching Strength",
          "lastUpdated": "2026-09-01T04:00:00Z"
        },
        "decisionTrigger": {
          "triggerActive": true,
          "triggerType": "NEW_FIT_EVIDENCE",
          "message": "3 buyers with your exact fit left reviews yesterday.",
          "deepLinkUrl": "myntra://wishlist/detail?itemId=witem_00192837&sheet=fit"
        }
      }
    ]
  }
}
```

---

### 5.2 Endpoint: `GET /api/v1/products/{productId}/fit-confidence`
Fetches deep evidence, size chart mapping, and peer reviews for the Fit Confidence Detail Sheet.

#### Request Parameters
*   `productId` (path, string, required): Unique product catalog ID.
*   `userId` (query, string, optional): User ID for personalized profiling.

#### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "productId": "style_3948102",
    "personalization": {
      "confidenceLevel": "HIGH",
      "recommendedSize": "M",
      "primaryReason": "Matches your physical profile (178cm, 74kg) and past order 'Roadster Oxford Shirt (M)'.",
      "alternativeSize": "L",
      "alternativeReason": "Choose L if you prefer a relaxed fit around shoulders."
    },
    "fitMetrics": {
      "sampleSize": 128,
      "sizeDistribution": {
        "runsSmall": 12,
        "trueToSize": 81,
        "runsLarge": 7
      },
      "stretchRating": "MEDIUM_FLEX",
      "postWashBehavior": "Pre-shrunk fabric, negligible shrinkage (< 1.5%)."
    },
    "peerReviews": [
      {
        "reviewId": "rev_771920",
        "anonymousUserTag": "Fit Profile: 177cm / 73kg",
        "purchasedSize": "M",
        "fitFeedback": "TRUE_TO_SIZE",
        "rating": 5,
        "headline": "Fits perfectly across chest",
        "commentSnippet": "I was worried about shoulder tightness, but M fits spot on. Washing in cold water maintained shape.",
        "verifiedBuyer": true,
        "createdAt": "2026-08-28T14:22:10Z"
      }
    ],
    "fallbackState": {
      "isFallbackActive": false,
      "brandSizeChartUrl": "https://assets.myntassets.com/sizecharts/roadster_men_shirts.json"
    }
  }
}
```

---

### 5.3 Endpoint: `GET /api/v1/products/{productId}/quality-digest`
Fetches aspect-based sentiment summaries, verified customer photos/videos, and durability highlights.

#### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "productId": "style_3948102",
    "totalReviewsAnalyzed": 184,
    "lastDigestGeneration": "2026-09-01T04:00:00Z",
    "aspectSummaries": [
      {
        "aspect": "Fabric & Material",
        "sentiment": "POSITIVE",
        "confidenceScore": 0.94,
        "summary": "100% combed cotton, soft feel, breathable for summer wear.",
        "supportingReviewIds": ["rev_771920", "rev_881203", "rev_991024"]
      },
      {
        "aspect": "Color Permanence",
        "sentiment": "NEUTRAL",
        "confidenceScore": 0.82,
        "summary": "Navy blue shade matches studio photos. Minor fading reported after 10+ machine washes.",
        "supportingReviewIds": ["rev_551029", "rev_663110"]
      },
      {
        "aspect": "Stitching & Buttons",
        "sentiment": "NEGATIVE",
        "confidenceScore": 0.76,
        "summary": "5% of buyers noted loose thread on the bottom sleeve button.",
        "supportingReviewIds": ["rev_331002"]
      }
    ],
    "verifiedCustomerMedia": [
      {
        "mediaId": "med_994821",
        "mediaType": "IMAGE",
        "thumbnailUrl": "https://image.myntassets.com/reviews/med_994821_thumb.jpg",
        "fullUrl": "https://image.myntassets.com/reviews/med_994821_large.jpg",
        "variantSize": "M",
        "variantColor": "Navy Blue",
        "upvoteCount": 34,
        "sourceReviewId": "rev_771920"
      }
    ]
  }
}
```

---

### 5.4 Endpoint: `POST /api/v1/products/{productId}/confidence-feedback`
Captures user feedback on size recommendation and quality digest accuracy.

#### Request Body
```json
{
  "userId": "usr_98745210",
  "feature": "FIT_CONFIDENCE",
  "recommendedSize": "M",
  "selectedSize": "L",
  "helpful": false,
  "issueType": "RECOMMENDED_TOO_SMALL",
  "userComment": "I have broad shoulders, recommended M would have been tight."
}
```

#### Response (202 Accepted)
```json
{
  "status": "accepted",
  "message": "Feedback captured for model retraining."
}
```

---

### 5.5 Endpoint: `POST /api/v1/wishlist/triggers/evaluate`
Internal scheduled microservice trigger engine endpoint evaluating notification eligibility.

#### Request Body
```json
{
  "productId": "style_3948102",
  "triggerEventType": "NEW_SIMILAR_BODY_REVIEWS",
  "evidenceThresholdMet": true,
  "minNewReviews": 3
}
```

#### Response (200 OK)
```json
{
  "status": "success",
  "usersEvaluated": 1420,
  "notificationsQueued": 185,
  "suppressedByCap": 310,
  "suppressedByOptOut": 45
}
```

---

## 6. Machine Learning & Data Pipeline Architecture

```mermaid
flowchart LR
    subgraph DataInputs [Feature Ingestion]
        Orders[Purchase & Return History]
        SizeCharts[Brand Size Charts]
        Reviews[Raw Reviews & Ratings]
        Media[Customer Uploaded Media]
        UserProfiles[User Body Profiles]
    end

    subgraph Pipelines [Offline & Stream Processing]
        FeatureEng[Spark Feature Pipeline]
        FitModelTrain[Fit Prediction Training XGBoost]
        LLMSummarizer[Aspect NLP & ABSA Model]
        MediaFilter[CNN Media Quality Classifier]
    end

    subgraph FeatureServing [Serving Layer]
        Feast[(Feast Feature Store)]
        RedisStore[(Redis Inference Cache)]
        VectorDB[(Milvus / Pinecone Vector DB)]
    end

    Orders --> FeatureEng
    UserProfiles --> FeatureEng
    SizeCharts --> FeatureEng
    FeatureEng --> FitModelTrain
    FitModelTrain --> Feast

    Reviews --> LLMSummarizer
    LLMSummarizer --> VectorDB
    LLMSummarizer --> RedisStore

    Media --> MediaFilter
    MediaFilter --> RedisStore
```

### 6.1 Fit Recommendation ML Engine

#### Feature Engineering Vector
```python
# Conceptual User-Product Fit Feature Vector
user_fit_vector = {
    "user_id": "usr_98745210",
    "height_cm": 178,
    "weight_kg": 74,
    "chest_cm": 98,
    "waist_cm": 82,
    "brand_order_history": {
        "Roadster": {"M": {"purchased": 4, "returned_size": 0}},
        "Nike": {"L": {"purchased": 2, "returned_size": 1}}
    },
    "category_return_rate_size": 0.02
}

product_fit_vector = {
    "product_id": "style_3948102",
    "brand_id": "brand_roadster",
    "category": "Men_Shirts",
    "size_chart": {"S": 92, "M": 98, "L": 104, "XL": 110},
    "aggregated_fit_reviews": {
        "runs_small_pct": 0.09,
        "true_to_size_pct": 0.84,
        "runs_large_pct": 0.07
    }
}
```

#### Confidence Threshold Logic
```python
def calculate_fit_confidence(user_vector, product_vector):
    evidence_score = 0
    
    # 1. Past Brand Purchase Matches (+40 pts)
    if has_successful_brand_purchase(user_vector, product_vector["brand_id"]):
        evidence_score += 40
        
    # 2. Similar Body Type Reviews (+30 pts)
    matching_peer_reviews = count_matching_body_reviews(user_vector, product_vector)
    if matching_peer_reviews >= 5:
        evidence_score += 30
    elif matching_peer_reviews >= 2:
        evidence_score += 15
        
    # 3. Size Chart Data Availability (+30 pts)
    if product_vector.get("size_chart"):
        evidence_score += 30

    # Output Confidence Level Assignment
    if evidence_score >= 70:
        return "HIGH", recommend_size_knn(user_vector, product_vector)
    elif evidence_score >= 40:
        return "MEDIUM", recommend_size_heuristic(user_vector, product_vector)
    else:
        return "LIMITED_EVIDENCE", None  # Fallback to standard brand chart
```

---

### 6.2 Review & Quality Digest NLP Pipeline
1.  **Aspect-Based Sentiment Analysis (ABSA)**: Deconstructs raw review sentences into predefined aspects: `Material/Fabric`, `Color Accuracy`, `Stitching/Durability`, `Stretch/Flexibility`, `Post-Wash Condition`.
2.  **Extractive & Abstractive Summarization**: Utilizes a fine-tuned LLaMA-3 / Mistral 7B quantized model running on internal GPU clusters to generate concise, factual 1-line aspect summaries.
3.  **Traceability Indexing**: Every output text snippet stores strict pointers to `review_ids`. Hallucination checks verify that 100% of keywords in the summary exist in source reviews.
4.  **Verified Media Filtering Pipeline**: OpenCV + CNN Classifier scores customer photos for brightness, blur, resolution, and nudity/inappropriateness before publishing to the customer photo carousel.

---

## 7. Data Models & Relational Schema (PostgreSQL & MongoDB)

### 7.1 PostgreSQL Relational Schema (Core Wishlist & Fit Metadata)

```sql
-- Core Wishlist Items Table
CREATE TABLE wishlist_items (
    wishlist_item_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    sku_id VARCHAR(64) NOT NULL,
    added_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revisit_count INT DEFAULT 0,
    last_revisited_timestamp TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) DEFAULT 'ACTIVE', -- ACTIVE, MOVED_TO_BAG, REMOVED, PURCHASED
    experiment_group VARCHAR(64) NOT NULL,
    CONSTRAINT idx_user_product UNIQUE (user_id, product_id)
);

CREATE INDEX idx_wishlist_user ON wishlist_items(user_id, status);
CREATE INDEX idx_wishlist_product ON wishlist_items(product_id);

-- User Fit Profiles Table
CREATE TABLE user_fit_profiles (
    user_id VARCHAR(64) PRIMARY KEY,
    height_cm NUMERIC(5,2),
    weight_kg NUMERIC(5,2),
    preferred_fit_style VARCHAR(32), -- SLIM, REGULAR, LOOSE
    consent_given BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fit Recommendation Logs Table (For Audit & Retraining)
CREATE TABLE fit_recommendation_logs (
    recommendation_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    recommended_size VARCHAR(16) NOT NULL,
    confidence_level VARCHAR(32) NOT NULL,
    confidence_score NUMERIC(5,2) NOT NULL,
    selected_size VARCHAR(16),
    recommendation_accepted BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_fit_log_user_prod ON fit_recommendation_logs(user_id, product_id);

-- Decision Trigger Audit Table
CREATE TABLE notification_trigger_logs (
    trigger_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    trigger_type VARCHAR(64) NOT NULL, -- NEW_FIT_EVIDENCE, BACK_IN_STOCK, LOW_INVENTORY
    channel VARCHAR(32) NOT NULL, -- PUSH, SMS, IN_APP
    sent_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    opened_timestamp TIMESTAMP WITH TIME ZONE,
    converted_to_bag BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_trigger_user ON notification_trigger_logs(user_id, sent_timestamp);
```

### 7.2 MongoDB Document Schema (Review Summaries & Customer Media)

```json
// Collection: product_quality_digests
{
  "_id": "digest_style_3948102",
  "productId": "style_3948102",
  "summaryVersion": 1.4,
  "reviewThresholdMet": true,
  "totalReviewsAnalyzed": 184,
  "aspects": [
    {
      "aspectName": "Fabric & Material",
      "sentiment": "POSITIVE",
      "summaryText": "100% combed cotton, soft feel, breathable for summer wear.",
      "supportingReviews": ["rev_771920", "rev_881203"]
    },
    {
      "aspectName": "Post-Wash Shrinkage",
      "sentiment": "POSITIVE",
      "summaryText": "Pre-shrunk fabric, negligible shrinkage (< 1.5%).",
      "supportingReviews": ["rev_551029"]
    }
  ],
  "verifiedMedia": [
    {
      "mediaId": "med_994821",
      "url": "https://image.myntassets.com/reviews/med_994821_large.jpg",
      "thumbnailUrl": "https://image.myntassets.com/reviews/med_994821_thumb.jpg",
      "variantSize": "M",
      "variantColor": "Navy Blue",
      "qualityScore": 0.95,
      "sourceReviewId": "rev_771920"
    }
  ],
  "updatedAt": "2026-09-01T04:00:00Z"
}
```

---

## 8. Event-Driven Architecture & Analytics Pipeline

### 8.1 Analytics Event Taxonomies
All events are published to Kafka topic `analytics.wishlist.events.v1` in JSON format.

```
+----------------------------------------------------------------------------------+
|                            KAFKA EVENT PIPELINE                                  |
|                                                                                  |
| [Client SDKs] --(JSON Payload)--> [Kafka Ingestion Topic]                       |
|                                         |                                        |
|                                         v                                        |
|                             [Apache Flink Stream Processor]                      |
|                                         |                                        |
|                +------------------------+------------------------+               |
|                |                                                 |               |
|                v                                                 v               |
|     [Real-Time Trigger Engine]                       [Snowflake Warehouse]       |
|   (Evaluates frequency caps & pushes)             (Aggregates 30-Day Conversion) |
+----------------------------------------------------------------------------------+
```

#### Complete Event Catalog (15 Required Metrics Events)

| # | Event Name | Core Payload Attributes | Trigger Point |
|---|---|---|---|
| 1 | `wishlist_item_added` | `user_id`, `product_id`, `variant_id`, `timestamp`, `source_surface` | User taps heart icon |
| 2 | `wishlist_viewed` | `user_id`, `session_id`, `wishlist_count`, `experiment_group` | Wishlist screen load |
| 3 | `wishlist_item_revisited` | `user_id`, `product_id`, `days_since_added`, `revisit_count` | 2nd+ view of item |
| 4 | `fit_confidence_impression` | `product_id`, `recommended_size`, `confidence_level`, `evidence_count` | Fit chip rendered |
| 5 | `fit_confidence_opened` | `product_id`, `entry_surface`, `experiment_group` | Fit sheet opened |
| 6 | `size_recommendation_selected`| `product_id`, `recommended_size`, `selected_size`, `is_match` | User selects size |
| 7 | `quality_digest_impression` | `product_id`, `review_count`, `media_count`, `summary_version` | Digest snippet rendered |
| 8 | `quality_digest_opened` | `product_id`, `entry_surface`, `experiment_group` | Quality sheet opened |
| 9 | `customer_evidence_opened` | `product_id`, `evidence_type`, `review_id` | Media item tapped |
| 10 | `confidence_feedback_submitted`| `product_id`, `feature`, `helpful`, `issue_type` | User taps feedback |
| 11 | `wishlist_trigger_sent` | `product_id`, `trigger_type`, `channel`, `timestamp` | Push notification dispatched |
| 12 | `wishlist_trigger_opened` | `product_id`, `trigger_type`, `channel`, `time_to_open_sec` | Push notification tapped |
| 13 | `wishlist_item_added_to_bag` | `product_id`, `size`, `days_since_wishlist`, `experiment_group` | Taps Add to Bag |
| 14 | `wishlisted_item_purchased` | `order_id`, `product_id`, `days_since_wishlist`, `experiment_group` | Order confirmation |
| 15 | `wishlisted_item_returned` | `order_id`, `product_id`, `return_reason`, `experiment_group` | Return processed |

#### JSON Schema Sample: `wishlisted_item_purchased`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WishlistedItemPurchasedEvent",
  "type": "object",
  "properties": {
    "eventId": { "type": "string", "format": "uuid" },
    "eventName": { "type": "string", "const": "wishlisted_item_purchased" },
    "timestamp": { "type": "string", "format": "date-time" },
    "userId": { "type": "string" },
    "orderId": { "type": "string" },
    "productId": { "type": "string" },
    "selectedSize": { "type": "string" },
    "recommendedSize": { "type": "string" },
    "daysSinceWishlistAdd": { "type": "integer" },
    "experimentGroup": { "type": "string" },
    "wasPurchasedWithin30Days": { "type": "boolean" }
  },
  "required": ["eventId", "eventName", "timestamp", "userId", "orderId", "productId", "daysSinceWishlistAdd", "experimentGroup", "wasPurchasedWithin30Days"]
}
```

---

## 9. Decision Trigger Engine Rules & Anti-Fatigue Policies

The Decision Trigger Layer operates on strict non-monetary rules to re-engage users without discount dependency.

```
+-----------------------------------------------------------------------------------+
|                            TRIGGER EVALUATION PIPELINE                            |
|                                                                                   |
|  [ Event Input ] --> [ Check Relevance ] --> [ Check Stock ]                      |
|                                                      |                            |
|  [ Dispatch Push ] <-- [ Pass Frequency Cap ] <-- [ Check User Opt-Out ]          |
+-----------------------------------------------------------------------------------+
```

### 9.1 Trigger Rule Matrix

| Trigger Type | Qualification Threshold | Target Channel | Deep Link Anchor |
|---|---|---|---|
| `NEW_FIT_EVIDENCE` | $\ge 3$ new verified reviews matching user's size profile added since last revisit | Push / In-App Banner | `myntra://wishlist/detail?itemId={id}&sheet=fit` |
| `SIZE_BACK_IN_STOCK` | Recommended size restocked ($qty \ge 2$) | Push Notification | `myntra://wishlist/detail?itemId={id}&action=add_bag` |
| `LOW_INVENTORY_ALERT` | Saved variant inventory drops below $\le 3$ units | In-App Highlight | `myntra://wishlist/detail?itemId={id}` |
| `OCCASION_REMINDER` | User explicitly set occasion date minus 5 days | In-App Push | `myntra://wishlist/detail?itemId={id}` |

### 9.2 Anti-Fatigue & Frequency Cap Policies
*   **Global Cap**: Maximum **2 notifications per user per week** across all wishlist triggers.
*   **Item Level Cap**: Maximum **1 notification per wishlisted product every 14 days**.
*   **Quiet Hours**: No push notifications dispatched between **22:00 and 08:00 local time**.
*   **Suppression Rules**:
    *   Immediate suppression if product purchased or removed from wishlist.
    *   Immediate suppression if recommended size is out of stock.
    *   Immediate suppression if user disabled wishlist notifications in profile.
*   **Zero Monetary Messaging Policy**: System strictly rejects any trigger payload containing price drops, promo codes, or coupon references.

---

## 10. Security, Privacy & Compliance Architecture

1. **PII Anonymization & Differential Privacy**: Peer reviews on the Fit Confidence Detail Sheet scrub exact names and show aggregated profile tags (e.g., *"Customer with similar height (175-180cm)"*).
2. **Explicit Consent Framework**: Fit attribute collection (height, weight, fit preference) requires explicit opt-in with standard GDPR/DPDP compliant consent UI. Users can wipe fit data at any time via `DELETE /api/v1/user/fit-profile`.
3. **Traceability & Content Moderation**: Summaries derived from flagged or removed reviews are automatically purged within 2 hours via a Kafka `review_deleted` consumer pipeline.
4. **Data Encryption**:
    *   **In Transit**: Mandatory TLS 1.3 for API calls and internal gRPC communication.
    *   **At Rest**: AES-256 encryption for PostgreSQL DB instances and S3/GCS customer media buckets.

---

## 11. Non-Functional Requirements (NFRs) & Performance SLAs

```
+-----------------------------------------------------------------------------------+
|                                PERFORMANCE TARGETS                                |
|                                                                                   |
|    Wishlist API Latency (P95)     : < 100 ms                                      |
|    Service Uptime                 : 99.9% Availability                           |
|    Cache Hit Rate Target          : > 92% Redis Hits                              |
|    Event Ingestion Throughput     : 15,000 events/sec peak                        |
+-----------------------------------------------------------------------------------+
```

### 11.1 Key Performance Metrics & SLAs

| Requirement Domain | Metric Target | Monitoring Mechanism |
|---|---|---|
| **API Latency (Wishlist)** | P50 $< 45\text{ms}$, P95 $< 100\text{ms}$, P99 $< 250\text{ms}$ | Prometheus / Datadog APM |
| **API Availability** | $99.9\%$ Uptime ($< 43$ mins downtime/month) | AWS Route53 / PagerDuty |
| **Cache Hit Ratio** | $\ge 92\%$ for pre-computed confidence objects | Redis Enterprise Metrics |
| **Event Pipeline Latency** | $< 2$ seconds from client tap to Snowflake ingest | Apache Flink Metrics |
| **ML Inference Latency** | $< 35\text{ms}$ for real-time KNN scoring | Triton Inference Server |

### 11.2 Scalability & Caching Strategy
*   **Pre-Computation Engine**: Nightly batch jobs pre-calculate fit recommendations for top 20% wishlisted products across active user cohorts.
*   **Multi-Tier Caching**:
    *   *L1 Client Memory Cache*: Short-lived 5-minute TTL on mobile client.
    *   *L2 Distributed Redis Cluster*: Cluster mode enabled with 1-hour TTL for aggregated confidence payloads. Cache invalidated on new order, review addition, or stock change.

---

## 12. Edge Cases & System Fallback Matrix

| Edge Case Scenario | Failure Detection | Automated System Fallback Behavior |
|---|---|---|
| **Product has zero reviews** | Review count $= 0$ | Suppress Review Digest badge. Show standard brand description & "Be the first to review" prompt. |
| **Conflicting Review Feedback** | ABSA sentiment variance $> 0.6$ | Display balanced view showing both perspectives (e.g., *"70% report true to size, 30% report runs small"*). Do not hide disagreement. |
| **Size Chart Missing/Outdated** | Catalog size chart missing flag | Suppress personalized size score. Display "Limited evidence available" with standard customer reviews. |
| **Recommended Size Out of Stock** | `availableQuantity == 0` | Render recommended size with "Out of Stock" state + "Notify when available" CTA. Pre-select next best available fit if confidence score $> 75\%$. |
| **Cold Start User (No Order History)**| User profile empty | Prompt optional 2-step fit quick check (Height/Weight) or fallback to aggregate product sizing metrics. |
| **Stale Summary post Review Removal** | Kafka `review_deleted` event | Invalidate Redis key `digest_style_{id}` immediately. Schedule background re-summarization job. |

---

## 13. Experiment Setup & A/B Randomization Framework

```
+-----------------------------------------------------------------------------------+
|                                 A/B EXPERIMENT SETUP                              |
|                                                                                   |
|   Target Population : High-Intent Wishlist Users with Eligible Apparel Items      |
|   Randomization Unit: User ID Hash (MurmurHash3)                                  |
|                                                                                   |
|   [ Control Group (50%) ]   ---> Standard Wishlist Experience                     |
|   [ Treatment Group (50%) ] ---> Fit Confidence + Review Digest + Triggers        |
+-----------------------------------------------------------------------------------+
```

### 13.1 Randomization & Stratification
*   **Unit of Randomization**: `user_id` hashing using `MurmurHash3(user_id + "wishlist_v1_salt") % 100`.
*   **Allocation Split**: 50% Control, 50% Treatment.
*   **Stratification Variables**: Device OS (iOS vs Android vs Web), Historical Purchasing Frequency (High / Low / Zero), Target Category (Men's Apparel, Women's Apparel).

### 13.2 Primary Experiment Metric Formulation

$$\text{30-Day Wishlist Purchaser Rate} = \frac{\text{Unique Users Purchasing } \ge 1 \text{ Wishlisted Item within 30 Days}}{\text{Unique Users Adding } \ge 1 \text{ Item to Wishlist during Experiment Window}}$$

---

## 14. Observability, Alerting & Guardrail Dashboards

```mermaid
graph TD
    subgraph MetricsCollectors [Telemetry Ingestion]
        Prometheus[Prometheus - System Metrics]
        Datadog[Datadog - APM Logs & Traces]
        SnowflakeQuery[Snowflake - Business Metrics]
    end

    subgraph Dashboards [Internal Dashboard Surfaces]
        ExecDash[Executive Summary View]
        FunnelDash[Funnel & Conversion View]
        MLAuditDash[ML Quality & Audit View]
        GuardrailDash[Operational Guardrails View]
    end

    subgraph Alerting [Alert Manager]
        PagerDuty[PagerDuty Escalation]
        SlackAlerts[Slack #wishlist-alerts]
    end

    Prometheus --> GuardrailDash
    Datadog --> GuardrailDash
    SnowflakeQuery --> ExecDash
    SnowflakeQuery --> FunnelDash
    SnowflakeQuery --> MLAuditDash

    GuardrailDash -.->|Breach Threshold| PagerDuty
    GuardrailDash -.->|Warning Threshold| SlackAlerts
```

### 14.1 Guardrail Breach Alert Rules

```yaml
# Prometheus Alerting Rule Definition
groups:
  - name: wishlist_confidence_guardrails
    rules:
      - alert: HighSizeReturnRateSpike
        expr: (sum(rate(wishlisted_item_returned{reason="FIT_ISSUE"}[24h])) / sum(rate(wishlisted_item_purchased[24h]))) > 0.08
        for: 6h
        labels:
          severity: critical
        annotations:
          summary: "Size-related return rate exceeded 8% guardrail threshold!"

      - alert: NotificationOptOutSpike
        expr: (sum(rate(notification_opt_outs{source="wishlist_trigger"}[1h])) / sum(rate(wishlist_trigger_sent[1h]))) > 0.03
        for: 2h
        labels:
          severity: warning
        annotations:
          summary: "Wishlist trigger notification opt-out rate exceeded 3%!"

      - alert: HighWishlistApiLatency
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="wishlist-service"}[5m])) by (le)) > 0.25
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Wishlist API P95 latency exceeded 250ms SLA!"
```

---

## 15. Implementation & Delivery Roadmap

```mermaid
gantt
    title Implementation Roadmap (12 Weeks Total)
    dateFormat  YYYY-MM-DD
    section Discovery & Foundations
    Data Audit & Taxonomy Design     :a1, 2026-09-07, 14d
    Instrumentation & Kafka Setup    :a2, 2026-09-21, 14d
    section Core Feature Development
    Fit Confidence Engine MVP        :b1, 2026-10-05, 21d
    Review & Quality Digest MVP      :b2, 2026-10-12, 21d
    Decision Trigger Engine         :b3, 2026-10-26, 14d
    section Testing & Rollout
    QA, Security & Performance Load  :c1, 2026-11-09, 14d
    Controlled A/B Experiment Run    :c2, 2026-11-23, 28d
```

---

## 16. Definition of Done (DoD) Checklist

- [ ] All API contracts implemented according to OpenAPI 3.0 specs and verified with automated integration tests.
- [ ] Sub-100ms P95 latency SLA validated under peak simulated load (15,000 req/sec).
- [ ] All 15 analytics tracking events instrumented and verified for schema parity across iOS, Android, and Web.
- [ ] A/B Experiment MurmurHash3 randomization verified with 0% cross-group leakage.
- [ ] Graceful fallback states fully tested for zero-review, out-of-stock, and missing size chart scenarios.
- [ ] Privacy controls, fit data deletion endpoint, and PII anonymization audited and approved by Security & Compliance team.
- [ ] Executive and Guardrail Dashboards live in internal reporting portal with automated PagerDuty alert triggers.

---

## 17. Architecture Sign-Off & Document Ownership

| Role | Name / Team | Approval Status | Date |
|---|---|---|---|
| Lead System Architect | Architecture Review Board | APPROVED | 2026-09-04 |
| Principal Product Manager | Product & Strategy Team | APPROVED | 2026-09-04 |
| Data Science Lead | ML & Personalization Team | APPROVED | 2026-09-04 |
| Engineering Manager | Mobile & Core Platform | APPROVED | 2026-09-04 |
