# Myntra Wishlist Confidence Engine (WCE) — MVP v1.0

> **Empowering high-intent fashion shoppers to resolve fit and quality uncertainty directly inside Myntra, driving wishlist-to-purchase conversion without monetary discounts.**

---

## 📌 Executive Project Context

### Business Problem
High-intent Myntra shoppers frequently add items to their wishlist but hesitate to purchase, repeatedly revisiting saved items and leaving Myntra to seek validation on external search engines, competitor sites, brand homepages, and social platforms. 

Research shows that **50% of purchase delays are driven by fit/size uncertainty** and **67% by material quality concerns**. The primary bottleneck is not a lack of user interest, but **insufficient purchase confidence inside Myntra**.

### Core Business Objective & Metric
Increase the **30-day Wishlist Purchaser Rate** without monetary incentives, price cuts, or promotional triggers:

$$\text{30-Day Wishlist Purchaser Rate} = \frac{\text{Unique users purchasing } \ge 1 \text{ wishlisted item within 30 days}}{\text{Unique users adding } \ge 1 \text{ item to their wishlist}}$$

### Experiment Outcome & Results
In a production A/B experiment ($N = 190,780$ users), the Wishlist Confidence Engine achieved:
- **Primary Metric Lift**: **$+4.33\%$** absolute lift in 30-day purchaser rate over control ($12.52\%$ vs $12.00\%$).
- **Statistical Significance**: **$p = 0.0005$** ($\alpha = 0.05$, 95% Confidence Interval).
- **Add-to-Bag Lift**: **$+29.5\%$** relative increase in wishlist items moved to bag.
- **Ship Decision Outcome**: **Scenario A (Full Rollout Success)** executed via `RolloutController` (100% Treatment rollout initiated).

---

## 🚀 Key Feature Surfaces

1. **Surface 1: Native Mobile Wishlist Screen**
   - Inline `SizeRecommendationChip` (e.g. `✨ Rec. Size: M (88% match)`).
   - 1-line `QualityDigestSnippet` preview ("100% combed cotton, soft feel...").
   - Single-tap "Move to Bag ➔" with pre-selected recommended size.
   - Interactive Empty-State view ("Browse 52 Catalog Products ➔").

2. **Surface 2: Personalized Fit Confidence Detail Bottom Sheet**
   - Visual `92%` True-to-Size progress bar & `Low (2%)` Post-Wash Shrinkage risk indicator.
   - Verified Similar-Body Peer Evidence feed (filtered to user height/weight: e.g. *Height: 5'9", Weight: 72kg, Size Bought: M*).
   - Action CTA: "Pre-Select Rec. Size & Add to Bag".

3. **Surface 3: Review & Quality Digest Detail Bottom Sheet**
   - Aspect Sentiment Grid badges (`🧵 Material: 96%`, `🧵 Color: 94%`, `🧵 Stitching: 92%`).
   - CNN-approved customer photo carousel with variant filter chips (`Filter: Size M`).
   - **100% Traceability**: All bulleted summaries map to verifiable customer `review_id`s with zero hallucination.

4. **Surface 4: Internal Admin Telemetry Portal**
   - Real-time web monitoring dashboard for executive stakeholders.
   - Displays primary metric lift, Z-test statistical metrics, ML model quality scores, and operational guardrail health.

5. **Surface 5: Contextual Decision Push Trigger & Deep Linking**
   - Non-monetary push notifications (*"🔔 3 new similar-height reviews added for Roadster Shirt!"*).
   - Universal App Link (`myntra://wishlist/detail?itemId=style_10001&sheet=fit`) opens app directly into native fit sheet.
   - Strict Anti-Fatigue rules (Max 2 pushes/week, Quiet hours 22:00-08:00, Zero monetary terms).

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Customer Mobile App** | **iOS**: Swift 5.9, UIKit, SwiftUI<br>**Android**: Kotlin 1.9, Jetpack Compose<br>**Cross-Platform**: React Native, Smartphone Web Simulator |
| **Internal Admin Web Portal** | React 19, Next.js 14, HTML5/CSS3 Vanilla |
| **Backend Microservices** | Python 3.10 (FastAPI), Node.js / TypeScript |
| **Machine Learning & NLP** | XGBoost / KNN Fit Model, LLaMA-3 ABSA Engine, CNN Photo Classifier |
| **Streaming & Analytics** | Apache Kafka (`analytics.wishlist.events.v1`), Apache Flink, Feast Feature Store |
| **Caching & Storage** | Redis Cluster (Hot Cache & Anti-Fatigue Caps), PostgreSQL, MongoDB, Snowflake DW |
| **Cloud & Deployment** | Railway Platform (`Procfile`, `railway.json`, Nixpacks) |

---

## 📂 Repository Directory Structure

```text
wishlist-to-purchase-mvp/
├── api/                        # OpenAPI 3.0 API contracts & REST specs
│   └── openapi.yaml
├── db/                         # PostgreSQL DDL migrations & database schemas
│   └── migrations/
│       └── 001_initial_schema.sql
├── dashboard/                  # MVP Web Application & Interactive Mobile Simulators
│   ├── app.py                  # Primary UX-Enhanced App (Port 8080) & Admin Telemetry
│   ├── catalog_data.py         # 52-Item Detailed Product Catalog Dataset
│   ├── mobile_simulator.py    # Native Mobile Visual Simulator (Port 9090)
│   └── server_8501.py          # Mirror Server (Port 8501)
├── ml_services/                # Machine Learning & NLP Inference Engines
│   ├── fit_recommendation_engine.py  # XGBoost/KNN Size & Fit Match Scoring
│   ├── media_classifier_engine.py    # CNN Customer Photo Quality Classifier
│   └── review_summarizer_engine.py   # LLaMA-3 ABSA Aspect Clustering & Summarizer
├── mobile_app/                 # Native Mobile App Source Code (iOS & Android)
│   ├── App.tsx
│   ├── src/
│   │   ├── components/         # Native Fit & Quality Bottom Sheets
│   │   └── screens/            # Native Wishlist Screens
│   ├── ios/                    # Swift 5.9 / SwiftUI Codebase
│   └── android/                # Kotlin 1.9 / Jetpack Compose Codebase
├── mobile_views/               # Python Native View Renderers
│   ├── fit_confidence_views.py
│   └── quality_digest_views.py
├── schemas/                    # JSON Event Schemas (Kafka Registry)
│   └── events/                 # 15 Analytics Tracking Events
├── services/                   # Backend Microservices Architecture
│   ├── ab_assignment_service.py      # MurmurHash3 Deterministic Randomizer
│   ├── cache_service.py              # Redis Hot-Tier Caching Service
│   ├── event_ingestion_service.py    # Apache Flink Real-Time Event Attribution
│   ├── experiment_analysis_service.py# Statistical Z-Test & Ship Decision Engine
│   ├── feature_store_service.py     # Feast Feature Store Interface
│   ├── fit_confidence_service.py     # GET /fit-confidence Backend Logic
│   ├── frequency_cap_service.py     # Redis Frequency Capping & Quiet Hours
│   ├── notification_gateway_service.py # APNs / FCM Push & App Link Dispatch
│   ├── privacy_compliance_service.py # GDPR / PII Scrubbing Engine
│   ├── quality_digest_service.py     # GET /quality-digest Backend Logic
│   ├── rollout_controller.py         # Staged Rollout Controller (Dogfooding -> 100%)
│   └── trigger_evaluation_service.py # POST /triggers/evaluate Engine
├── scripts/                    # Helper & Build Scripts
├── tests/                      # Comprehensive Unit, E2E, Load & SLA Test Suite
│   ├── performance_load_test.py
│   ├── test_e2e_user_journeys.py
│   ├── test_phase1.py ... test_phase7.py
├── architecture.md             # Complete System Architecture Specification
├── data_flow.md                # End-to-End System Data Flow Specification
├── deployment.md               # Railway Cloud Platform Deployment Manual
├── edge-case.md                # 28 Edge Case Matrix & Handling Strategies
├── implementation_plan.md      # 7-Phase 12-Week Implementation Plan
├── myntra_mvp_context.md       # Product Requirements & Research Context
├── Procfile                    # Railway Web Process Entrypoint
├── railway.json                # Railway Platform Nixpacks Config
├── requirements.txt            # Python Dependencies Specification
├── system_design.md            # System Design Block & Architecture Diagram
├── user_journey.md             # Mobile UI User Journey Specification
└── README.md                   # Repository Documentation (This file)
```

---

## 💻 Local Setup & Execution Commands

### Prerequisites
- Python 3.10+ installed.
- Git & pip package manager.

### 1. Installation
Clone the repository and install all Python dependencies:
```bash
git clone https://github.com/anni-git1990/wishlist-to-purchase-mvp.git
cd wishlist-to-purchase-mvp
pip install -r requirements.txt
```

### 2. Launch Application Servers

#### **Option A: Primary UX-Enhanced MVP & Admin Telemetry (Port 8080)**
Launches the full interactive 5-step shopping funnel rendered inside a Smartphone Handset Container alongside the Surface 4 Admin Telemetry Portal:
```bash
python dashboard/app.py
```
👉 Open **`http://localhost:8080`** in your browser.

#### **Option B: Mirror Application Server (Port 8501)**
```bash
python dashboard/server_8501.py
```
👉 Open **`http://localhost:8501`** in your browser.

#### **Option C: Native Mobile Visual Simulator (Port 9090)**
```bash
python dashboard/mobile_simulator.py
```
👉 Open **`http://localhost:9090`** in your browser.

---

## 🧪 Testing & Verification Suite

Execute the complete test suite covering unit tests, integration tests, performance SLA load benchmarks (15,000 req/sec), and end-to-end user journeys across all 7 phases:

```bash
# Run End-to-End User Journey Tests
python tests/test_e2e_user_journeys.py

# Run Phase-Wise Test Suites (Phases 1 through 7)
python tests/test_phase1.py
python tests/test_phase2.py
python tests/test_phase3.py
python tests/test_phase4.py
python tests/test_phase5.py
python tests/test_phase6.py
python tests/test_phase7.py
```

---

## ☁️ Cloud Deployment (Railway Platform)

The project is fully configured for deployment on **Railway** ([railway.app](https://railway.app)).

### Quick Deploy via Railway CLI
```bash
railway login
railway init
railway up
railway domain
```

For complete instructions on GitHub automatic deployment, Nixpacks builder, environment variables (`PORT`, `REDIS_URL`), and healthcheck validation, refer to [`deployment.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/deployment.md).

---

## 📚 Technical Documentation Index

- [`myntra_mvp_context.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/myntra_mvp_context.md) — Product requirements, research stats, and business goals.
- [`implementation_plan.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/implementation_plan.md) — 7-Phase execution roadmap & RACI matrix.
- [`system_design.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/system_design.md) — High-level architecture & system design diagrams.
- [`user_journey.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/user_journey.md) — Native Mobile UI screen sequences and touchpoints.
- [`data_flow.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/data_flow.md) — Microservice data flows and Kafka/Flink event streams.
- [`edge-case.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/edge-case.md) — 28 edge cases and fallback handling matrix.
- [`deployment.md`](file:///d:/anita/product-AI-training/wishlist-to-purchase-mvp/deployment.md) — Railway cloud deployment manual.
