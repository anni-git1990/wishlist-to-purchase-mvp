import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface WishlistFitChipProps {
  recommendedSize: string;
  matchPercentage: number;
  confidenceLevel: 'HIGH' | 'MEDIUM' | 'LIMITED_EVIDENCE';
  onPress: () => void;
}

export const WishlistFitChip: React.FC<WishlistFitChipProps> = ({
  recommendedSize,
  matchPercentage,
  confidenceLevel,
  onPress,
}) => {
  const isHighConfidence = confidenceLevel === 'HIGH';

  return (
    <TouchableOpacity
      style={[
        styles.chipContainer,
        isHighConfidence ? styles.highBg : styles.mediumBg,
      ]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <Text style={styles.sparkleIcon}>✨</Text>
      <Text style={styles.chipText}>
        Rec. Size: <Text style={styles.sizeText}>{recommendedSize}</Text>
      </Text>
      <View style={styles.badge}>
        <Text style={styles.badgeText}>{matchPercentage}% match</Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  chipContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 20,
    marginTop: 8,
    alignSelf: 'flex-start',
    borderWidth: 1,
  },
  highBg: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  mediumBg: {
    backgroundColor: '#FEFCE8',
    borderColor: '#FEF08A',
  },
  sparkleIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  chipText: {
    fontSize: 12,
    color: '#166534',
    fontWeight: '500',
  },
  sizeText: {
    fontWeight: 'bold',
    color: '#15803D',
  },
  badge: {
    backgroundColor: '#BBF7D0',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
    marginLeft: 6,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#166534',
  },
});
