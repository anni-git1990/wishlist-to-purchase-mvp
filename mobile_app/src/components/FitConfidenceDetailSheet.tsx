import React, { useState } from 'react';
import {
  View,
  Text,
  Modal,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
} from 'react-native';

interface PeerReview {
  reviewId: string;
  userHeightCm: number;
  userWeightKg: number;
  sizePurchased: string;
  comment: string;
}

interface FitConfidenceDetailSheetProps {
  visible: boolean;
  onClose: () => void;
  recommendedSize: string;
  matchPercentage: number;
  confidenceLevel: string;
  primaryReason: string;
  trueToSizePct: number;
  shrinkageRisk: string;
  peerReviews: PeerReview[];
  onAddToBag: (selectedSize: string) => void;
}

export const FitConfidenceDetailSheet: React.FC<FitConfidenceDetailSheetProps> = ({
  visible,
  onClose,
  recommendedSize,
  matchPercentage,
  confidenceLevel,
  primaryReason,
  trueToSizePct,
  shrinkageRisk,
  peerReviews,
  onAddToBag,
}) => {
  const [selectedSize, setSelectedSize] = useState<string>(recommendedSize);

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <TouchableOpacity style={styles.backdrop} onPress={onClose} />
        
        <View style={styles.sheetContainer}>
          <View style={styles.dragHandle} />
          
          <View style={styles.headerRow}>
            <Text style={styles.title}>Personalized Fit Confidence</Text>
            <View style={styles.confidenceBadge}>
              <Text style={styles.confidenceText}>{confidenceLevel} MATCH</Text>
            </View>
          </View>

          <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
            {/* Rationale Section */}
            <Text style={styles.reasonText}>{primaryReason}</Text>

            {/* Fit Attribute Progress Bars */}
            <View style={styles.metricCard}>
              <View style={styles.barHeader}>
                <Text style={styles.barLabel}>True to Size Match</Text>
                <Text style={styles.barVal}>{trueToSizePct}%</Text>
              </View>
              <View style={styles.barBg}>
                <View style={[styles.barFill, { width: `${trueToSizePct}%` }]} />
              </View>

              <View style={[styles.barHeader, { marginTop: 12 }]}>
                <Text style={styles.barLabel}>Post-Wash Shrinkage Risk</Text>
                <Text style={styles.barVal}>{shrinkageRisk}</Text>
              </View>
              <View style={styles.barBg}>
                <View style={[styles.barFill, { width: '15%', backgroundColor: '#22C55E' }]} />
              </View>
            </View>

            {/* Peer Feedback Section */}
            <Text style={styles.sectionHeader}>Verified Similar-Body Peer Evidence</Text>
            {peerReviews.map((peer) => (
              <View key={peer.reviewId} style={styles.peerCard}>
                <Text style={styles.peerMeta}>
                  Height: {Math.floor(peer.userHeightCm / 30.48)}'{Math.round((peer.userHeightCm % 30.48) / 2.54)}" • Weight: {peer.userWeightKg}kg • Size: {peer.sizePurchased}
                </Text>
                <Text style={styles.peerComment}>"{peer.comment}"</Text>
              </View>
            ))}

            {/* Size Selector */}
            <Text style={styles.sectionHeader}>Select Variant Size</Text>
            <View style={styles.sizeRow}>
              {['S', 'M', 'L', 'XL'].map((size) => (
                <TouchableOpacity
                  key={size}
                  style={[
                    styles.sizeChip,
                    selectedSize === size && styles.selectedSizeChip,
                  ]}
                  onPress={() => setSelectedSize(size)}
                >
                  <Text
                    style={[
                      styles.sizeChipText,
                      selectedSize === size && styles.selectedSizeText,
                    ]}
                  >
                    {size} {size === recommendedSize ? '(Rec)' : ''}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </ScrollView>

          {/* Add to Bag CTA */}
          <TouchableOpacity
            style={styles.addBagBtn}
            onPress={() => {
              onAddToBag(selectedSize);
              onClose();
            }}
          >
            <Text style={styles.addBagText}>
              Pre-Select Size {selectedSize} & Add to Bag
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  backdrop: {
    flex: 1,
  },
  sheetContainer: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    maxHeight: '80%',
  },
  dragHandle: {
    width: 40,
    height: 4,
    backgroundColor: '#CBD5E1',
    borderRadius: 2,
    alignSelf: 'center',
    marginBottom: 16,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0F172A',
  },
  confidenceBadge: {
    backgroundColor: '#DCFCE7',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  confidenceText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#166534',
  },
  scrollContent: {
    marginBottom: 16,
  },
  reasonText: {
    fontSize: 13,
    color: '#475569',
    marginBottom: 16,
    lineHeight: 18,
  },
  metricCard: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
  },
  barHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  barLabel: {
    fontSize: 12,
    color: '#64748B',
  },
  barVal: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#0F172A',
  },
  barBg: {
    height: 8,
    backgroundColor: '#E2E8F0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    backgroundColor: '#FF3F6C',
    borderRadius: 4,
  },
  sectionHeader: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1E293B',
    marginTop: 12,
    marginBottom: 8,
  },
  peerCard: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    padding: 10,
    marginBottom: 8,
  },
  peerMeta: {
    fontSize: 11,
    color: '#64748B',
    marginBottom: 2,
  },
  peerComment: {
    fontSize: 12,
    color: '#334155',
    fontStyle: 'italic',
  },
  sizeRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 4,
  },
  sizeChip: {
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  selectedSizeChip: {
    borderColor: '#FF3F6C',
    backgroundColor: '#FFF1F2',
  },
  sizeChipText: {
    fontSize: 12,
    color: '#475569',
  },
  selectedSizeText: {
    color: '#FF3F6C',
    fontWeight: 'bold',
  },
  addBagBtn: {
    backgroundColor: '#FF3F6C',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  addBagText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: 'bold',
  },
});
