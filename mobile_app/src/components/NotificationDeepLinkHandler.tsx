import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface NotificationPayload {
  itemId: string;
  sheet: 'fit' | 'quality';
  message: string;
}

interface NotificationDeepLinkHandlerProps {
  onDeepLinkTriggered: (itemId: string, sheet: 'fit' | 'quality') => void;
}

export const NotificationDeepLinkHandler: React.FC<NotificationDeepLinkHandlerProps> = ({
  onDeepLinkTriggered,
}) => {
  const simulatedNotification: NotificationPayload = {
    itemId: 'style_3948102',
    sheet: 'fit',
    message: '🔔 3 new similar-height fit reviews added for Roadster Shirt',
  };

  const handlePushPress = () => {
    // Simulates opening deep-link scheme: myntra://wishlist/detail?itemId=style_3948102&sheet=fit
    onDeepLinkTriggered(simulatedNotification.itemId, simulatedNotification.sheet);
  };

  return (
    <TouchableOpacity style={styles.banner} onPress={handlePushPress} activeOpacity={0.9}>
      <View style={styles.textWrapper}>
        <Text style={styles.bannerTitle}>Contextual Re-Engagement Push</Text>
        <Text style={styles.bannerMsg}>{simulatedNotification.message}</Text>
      </View>
      <Text style={styles.arrow}>➔</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#1E293B',
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginHorizontal: 12,
    marginTop: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  textWrapper: {
    flex: 1,
    marginRight: 8,
  },
  bannerTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#FF3F6C',
  },
  bannerMsg: {
    fontSize: 12,
    color: '#F8FAFC',
    marginTop: 2,
  },
  arrow: {
    fontSize: 16,
    color: '#FF3F6C',
    fontWeight: 'bold',
  },
});
