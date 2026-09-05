import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Image,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { WishlistFitChip } from '../components/WishlistFitChip';
import { FitConfidenceDetailSheet } from '../components/FitConfidenceDetailSheet';
import { QualityDigestSheet } from '../components/QualityDigestSheet';

export const WishlistScreen: React.FC = () => {
  const [isFitSheetVisible, setIsFitSheetVisible] = useState(false);
  const [isQualitySheetVisible, setIsQualitySheetVisible] = useState(false);

  // Mock Wishlist Item Data from Backend Microservices
  const item = {
    productId: 'style_3948102',
    brand: 'ROADSTER',
    title: 'Men Pure Cotton Casual Shirt',
    price: 1299,
    imageUrl: 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400',
    fitConfidence: {
      recommendedSize: 'M',
      fitMatchPercentage: 88,
      confidenceLevel: 'HIGH' as const,
      primaryReason: 'Based on 4 successful past purchases in size M from Roadster & 18 peer reviews.',
      trueToSizePct: 92,
      shrinkageRisk: 'Low (2%)',
      peerReviews: [
        {
          reviewId: 'rev_101',
          userHeightCm: 175,
          userWeightKg: 72,
          sizePurchased: 'M',
          comment: 'Fits perfectly across chest and shoulders. Length is ideal for untucked wear.',
        },
        {
          reviewId: 'rev_102',
          userHeightCm: 178,
          userWeightKg: 74,
          sizePurchased: 'M',
          comment: 'Fabric has good stretch. No tightness around armholes.',
        },
      ],
    },
    qualityDigest: {
      summaryPreview: '100% combed cotton, soft feel, highly breathable for summer wear.',
      aspects: [
        { aspect: 'Fabric & Material', sentiment: 'POSITIVE' as const, summaryText: 'Soft feel', positivePct: 98 },
        { aspect: 'Color Permanence', sentiment: 'POSITIVE' as const, summaryText: 'No bleeding', positivePct: 95 },
        { aspect: 'Stitching & Durability', sentiment: 'POSITIVE' as const, summaryText: 'Reinforced seams', positivePct: 92 },
      ],
      verifiedMedia: [
        { mediaId: 'm1', photoUrl: 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=200', variant: 'Size M - Navy' },
        { mediaId: 'm2', photoUrl: 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=200', variant: 'Size M - Navy' },
      ],
    },
  };

  const handleAddToBag = (size: string) => {
    Alert.alert('Success', `Added ${item.title} (Size ${size}) to Bag!`);
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header Bar */}
      <View style={styles.navBar}>
        <Text style={styles.navTitle}>WISHLIST (1 Item)</Text>
      </View>

      <ScrollView style={styles.content}>
        {/* Wishlist Card Item (Surface 1) */}
        <View style={styles.card}>
          <View style={styles.itemRow}>
            <Image source={{ uri: item.imageUrl }} style={styles.itemImage} />
            
            <View style={styles.itemDetails}>
              <Text style={styles.brand}>{item.brand}</Text>
              <Text style={styles.title} numberOfLines={1}>{item.title}</Text>
              <Text style={styles.price}>₹{item.price}</Text>

              {/* Surface 1 Fit Recommendation Chip */}
              <WishlistFitChip
                recommendedSize={item.fitConfidence.recommendedSize}
                matchPercentage={item.fitConfidence.fitMatchPercentage}
                confidenceLevel={item.fitConfidence.confidenceLevel}
                onPress={() => setIsFitSheetVisible(true)}
              />
            </View>
          </View>

          {/* Surface 1 Quality Digest Preview Snippet */}
          <TouchableOpacity
            style={styles.snippetCard}
            onPress={() => setIsQualitySheetVisible(true)}
          >
            <Text style={styles.snippetTitle}>Quality Digest:</Text>
            <Text style={styles.snippetText}>{item.qualityDigest.summaryPreview}</Text>
            <Text style={styles.snippetCta}>View Full Digest ➔</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Surface 2 Native Fit Confidence Detail Bottom Sheet Modal */}
      <FitConfidenceDetailSheet
        visible={isFitSheetVisible}
        onClose={() => setIsFitSheetVisible(false)}
        recommendedSize={item.fitConfidence.recommendedSize}
        matchPercentage={item.fitConfidence.fitMatchPercentage}
        confidenceLevel={item.fitConfidence.confidenceLevel}
        primaryReason={item.fitConfidence.primaryReason}
        trueToSizePct={item.fitConfidence.trueToSizePct}
        shrinkageRisk={item.fitConfidence.shrinkageRisk}
        peerReviews={item.fitConfidence.peerReviews}
        onAddToBag={handleAddToBag}
      />

      {/* Surface 3 Native Review & Quality Digest Detail Bottom Sheet Modal */}
      <QualityDigestSheet
        visible={isQualitySheetVisible}
        onClose={() => setIsQualitySheetVisible(false)}
        summaryPreview={item.qualityDigest.summaryPreview}
        aspects={item.qualityDigest.aspects}
        verifiedMedia={item.qualityDigest.verifiedMedia}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F4F6',
  },
  navBar: {
    height: 50,
    backgroundColor: '#FF3F6C',
    justifyContent: 'center',
    paddingHorizontal: 16,
  },
  navTitle: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  content: {
    padding: 12,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  itemRow: {
    flexDirection: 'row',
  },
  itemImage: {
    width: 90,
    height: 110,
    borderRadius: 8,
    backgroundColor: '#E2E8F0',
  },
  itemDetails: {
    flex: 1,
    marginLeft: 12,
  },
  brand: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#282C3F',
  },
  title: {
    fontSize: 13,
    color: '#535766',
    marginTop: 2,
  },
  price: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#282C3F',
    marginTop: 4,
  },
  snippetCard: {
    backgroundColor: '#F8FAFC',
    borderLeftWidth: 3,
    borderLeftColor: '#FF3F6C',
    borderRadius: 6,
    padding: 8,
    marginTop: 12,
  },
  snippetTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#0F172A',
  },
  snippetText: {
    fontSize: 11,
    color: '#475569',
    marginTop: 2,
  },
  snippetCta: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#FF3F6C',
    marginTop: 4,
  },
});
