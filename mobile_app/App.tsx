import React from 'react';
import { SafeAreaView, StatusBar, StyleSheet, View } from 'react-native';
import { WishlistScreen } from './src/screens/WishlistScreen';
import { NotificationDeepLinkHandler } from './src/components/NotificationDeepLinkHandler';

export default function App() {
  const handleDeepLink = (itemId: string, sheet: 'fit' | 'quality') => {
    console.log(`Deep Link Triggered: myntra://wishlist/detail?itemId=${itemId}&sheet=${sheet}`);
  };

  return (
    <SafeAreaView style={styles.appContainer}>
      <StatusBar barStyle="light-content" backgroundColor="#FF3F6C" />
      <NotificationDeepLinkHandler onDeepLinkTriggered={handleDeepLink} />
      <WishlistScreen />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  appContainer: {
    flex: 1,
    backgroundColor: '#F4F4F6',
  },
});
