#!/usr/bin/env python3
"""
Myntra Wishlist Confidence Engine (WCE) - End-to-End Pipeline Demonstration
Simulates the complete Phase 1 through Phase 5 user journey:
1. User wishlist item addition & A/B assignment (Phase 2)
2. Kafka event ingestion & Schema validation (Phase 1)
3. Fit Confidence ML Inference & Redis Caching (Phase 3)
4. Review & Quality Digest ABSA NLP & Media Classification (Phase 4)
5. Decision Trigger Layer, Anti-Fatigue Caps & Deep-Link Dispatch (Phase 5)
6. Native Mobile UI Component Rendering (Phase 3 & Phase 4)
7. Real-Time Flink Attribution Stream Summary (Phase 2)
"""

import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.ab_assignment_service import ABAssignmentService
from services.event_ingestion_service import EventIngestionService
from services.fit_confidence_service import FitConfidenceService
from services.quality_digest_service import QualityDigestService
from services.trigger_evaluation_service import TriggerEvaluationService
from services.experiment_analysis_service import ExperimentAnalysisService
from mobile_views.fit_confidence_views import NativeMobileFitViewRenderer
from mobile_views.quality_digest_views import NativeMobileQualityViewRenderer

def main():
    print("=" * 80)
    print("MYNTRA WISHLIST CONFIDENCE MVP - END-TO-END PIPELINE DEMONSTRATION")
    print("=" * 80)

    # 1. Initialize Services
    ab_service = ABAssignmentService()
    ingest_service = EventIngestionService()
    fit_service = FitConfidenceService()
    quality_service = QualityDigestService()
    trigger_service = TriggerEvaluationService()
    analysis_service = ExperimentAnalysisService()
    fit_renderer = NativeMobileFitViewRenderer()
    quality_renderer = NativeMobileQualityViewRenderer()

    test_user_id = "usr_98745210"
    test_product_id = "style_3948102"
    test_sku_id = "sku_991823"

    print("\n[STEP 1] A/B EXPERIMENT ASSIGNMENT (Phase 2)")
    assignment = ab_service.get_assignment(test_user_id)
    print(f"  • User ID          : {assignment['userId']}")
    print(f"  • Experiment Group : {assignment['experimentGroup']}")
    print(f"  • MurmurHash3 Bucket: {assignment['bucket']}")

    print("\n[STEP 2] KAFKA EVENT INGESTION (Phase 1 & Phase 2)")
    event_payload = {
        "eventId": "evt_demo_101",
        "eventName": "wishlist_item_added",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        "userId": test_user_id,
        "productId": test_product_id,
        "variantId": test_sku_id,
        "sourceSurface": "PDP",
        "experimentGroup": assignment["experimentGroup"]
    }
    success, msg = ingest_service.ingest_event(event_payload)
    print(f"  • Event Payload    : wishlist_item_added")
    print(f"  • Schema Validation: {msg}")

    print("\n[STEP 3] FIT CONFIDENCE ML INFERENCE & CACHING (Phase 3)")
    res_fit = fit_service.get_fit_confidence(test_product_id, test_user_id)
    print(f"  • Cold Call Latency: {res_fit['latencyMs']} ms (SLA Target < 45ms: {res_fit['slaMet']})")
    print(f"  • Confidence Level : {res_fit['personalization']['confidenceLevel']}")
    print(f"  • Recommended Size : {res_fit['personalization']['recommendedSize']} ({res_fit['personalization']['fitMatchPercentage']}% match)")
    print(f"  • Primary Rationale : {res_fit['personalization']['primaryReason']}")

    print("\n[STEP 4] REVIEW & QUALITY DIGEST NLP & MEDIA CLASSIFIER (Phase 4)")
    res_quality = quality_service.get_quality_digest(test_product_id)
    print(f"  • Quality API SLA  : {res_quality['latencyMs']} ms (SLA Target < 50ms: {res_quality['slaMet']})")
    print(f"  • Summary Preview  : {res_quality['data']['summaryPreview']}")
    print(f"  • Top Positive     : {res_quality['data']['topPositiveAspect']}")
    print(f"  • Aspect Clusters  : {len(res_quality['data']['aspectSummaries'])} verified aspects")
    print(f"  • Verified Media   : {len(res_quality['data']['verifiedCustomerMedia'])} CNN-approved customer photos")

    print("\n[STEP 5] DECISION TRIGGER EVALUATION & DEEP-LINK DISPATCH (Phase 5)")
    eval_res = trigger_service.evaluate_trigger_event({
        "productId": test_product_id,
        "triggerEventType": "NEW_FIT_EVIDENCE",
        "minNewReviews": 3
    })
    print(f"  • Trigger Evaluated : NEW_FIT_EVIDENCE")
    print(f"  • Candidates Assessed: {eval_res['usersEvaluated']}")
    print(f"  • Push Queued       : {eval_res['notificationsQueued']}")
    print(f"  • Suppressed Summary : {eval_res['suppressedSummary']}")

    print("\n[STEP 6] NATIVE MOBILE UI COMPONENT RENDER (Phase 3 & Phase 4)")
    chip_view = fit_renderer.render_surface1_wishlist_fit_chip(res_fit)
    quality_snippet = quality_renderer.render_surface1_quality_summary_snippet(res_quality)
    fit_sheet = fit_renderer.render_surface2_fit_detail_sheet(res_fit)
    quality_sheet = quality_renderer.render_surface3_quality_detail_sheet(res_quality)
    
    print(f"  • Surface 1 Wishlist Fit Chip    : {chip_view['chipText']} [{chip_view['badgeText']}]")
    print(f"  • Surface 1 Quality Snippet      : '{quality_snippet['displayText']}'")
    print(f"  • Surface 2 Fit Sheet Widgets    : {len(fit_sheet['widgets'])} native components")
    print(f"  • Surface 3 Quality Sheet Widgets: {len(quality_sheet['widgets'])} native components")

    print("\n[STEP 7] USER PURCHASE EVENT & FLINK REAL-TIME ATTRIBUTION (Phase 1 & Phase 2)")
    purchase_event = {
        "eventId": "evt_demo_102",
        "eventName": "wishlisted_item_purchased",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        "userId": test_user_id,
        "orderId": "ord_9901",
        "productId": test_product_id,
        "selectedSize": "M",
        "recommendedSize": "M",
        "daysSinceWishlistAdd": 1,
        "experimentGroup": assignment["experimentGroup"],
        "wasPurchasedWithin30Days": True
    }
    ingest_service.ingest_event(purchase_event)
    
    summary = ingest_service.get_attribution_summary()
    print("  • Real-Time Flink Attribution Summary:")
    print(f"      Treatment Group: Adders={summary['treatment']['wishlistAdders']}, Purchasers30d={summary['treatment']['purchasers30d']}, ConvRate={summary['treatment']['conversionRate']*100:.2f}%")
    print(f"      Control Group  : Adders={summary['control']['wishlistAdders']}, Purchasers30d={summary['control']['purchasers30d']}, ConvRate={summary['control']['conversionRate']*100:.2f}%")

    print("\n[STEP 8] PRODUCTION A/B EXPERIMENT STATISTICAL ANALYSIS & SHIP DECISION (Phase 7)")
    ship_report = analysis_service.execute_ship_decision()
    z_metrics = ship_report["zTestResult"]["statisticalMetrics"]
    post_mvp = ship_report["postMvpDecision"]
    print(f"  • 30-Day Conversion Lift : +{z_metrics['relativeLiftPct']}% (p = {z_metrics['pValue']})")
    print(f"  • Statistical Significance: {z_metrics['isStatisticallySignificant']} (Alpha = 0.05)")
    print(f"  • Operational Guardrails  : {ship_report['guardrailAudit']['overallStatus']}")
    print(f"  • Post-MVP Decision Matrix: {post_mvp['scenarioName']}")
    print(f"  • Executed Rollout Action : {post_mvp['actionTitle']}")
    print(f"  • Final Rollout Controller Stage: {ship_report['rolloutControllerState']['activeStage']}")

    print("\n" + "=" * 80)
    print("PIPELINE DEMONSTRATION COMPLETE - ALL PHASES 1 THROUGH 7 FUNCTIONAL")
    print("=" * 80)

if __name__ == "__main__":
    main()
