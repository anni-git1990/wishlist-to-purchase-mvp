import React from 'react';
import {
  View,
  Text,
  Modal,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
} from 'react-native';

interface AspectSummary {
  aspect: string;
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'MIXED';
  summaryText: string;
  positivePct: number;
}

interface CustomerMedia {
  mediaId: string;
  photoUrl: string;
  variant: string;
}

interface QualityDigestSheetProps {
  visible: boolean;
  onClose: () => void;
  summaryPreview: string;
  aspects: AspectSummary[];
  verifiedMedia: CustomerMedia[];
}

export const QualityDigestSheet: React.FC<QualityDigestSheetProps> = ({
  visible,
  onClose,
  summaryPreview,
  aspects,
  verifiedMedia,
}) => {
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
          
          <Text style={styles.title}>Verified Review & Quality Digest</Text>

          <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
            {/* Traceable Summary Card */}
            <View style={styles.summaryCard}>
              <Text style={styles.summaryTitle}>LLM Traceable Summary</Text>
              <Text style={styles.summaryText}>{summaryPreview}</Text>
            </View>

            {/* Aspect Sentiment Badges */}
            <Text style={styles.sectionHeader}>Verified Quality Aspects</Text>
            <View style={styles.aspectGrid}>
              {aspects.map((aspect) => (
                <View key={aspect.aspect} style={styles.aspectBadge}>
                  <Text style={styles.aspectTitle}>{aspect.aspect}</Text>
                  <Text style={styles.aspectPct}>{aspect.positivePct}% Positive</Text>
                </View>
              ))}
            </View>

            {/* Verified Customer Photos Carousel */}
            <Text style={styles.sectionHeader}>Verified Customer Photos (CNN Approved)</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.photoCarousel}>
              {verifiedMedia.map((media) => (
                <View key={media.mediaId} style={styles.photoWrapper}>
                  <Image source={{ uri: media.photoUrl }} style={styles.photoImg} />
                  <Text style={styles.variantTag}>{media.variant}</Text>
                </View>
              ))}
            </ScrollView>
          </ScrollView>

          {/* Close Button */}
          <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
            <Text style={styles.closeText}>Close Quality Digest</Text>
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
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: 14,
  },
  scrollContent: {
    marginBottom: 16,
  },
  summaryCard: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
  },
  summaryTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FF3F6C',
    marginBottom: 4,
  },
  summaryText: {
    fontSize: 13,
    color: '#334155',
    lineHeight: 18,
  },
  sectionHeader: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 8,
  },
  aspectGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16,
  },
  aspectBadge: {
    backgroundColor: '#F0FDF4',
    borderWidth: 1,
    borderColor: '#BBF7D0',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  aspectTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#166534',
  },
  aspectPct: {
    fontSize: 10,
    color: '#15803D',
  },
  photoCarousel: {
    flexDirection: 'row',
  },
  photoWrapper: {
    marginRight: 10,
  },
  photoImg: {
    width: 100,
    height: 100,
    borderRadius: 8,
    backgroundColor: '#E2E8F0',
  },
  variantTag: {
    fontSize: 10,
    color: '#64748B',
    marginTop: 4,
    textAlign: 'center',
  },
  closeBtn: {
    backgroundColor: '#0F172A',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  closeText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: 'bold',
  },
});
