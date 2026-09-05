import SwiftUI

// MARK: - Surface 1 & Surface 2 SwiftUI Native iOS Mobile Screen
struct WishlistFitView: View {
    @State private var isFitSheetPresented = false
    @State private var isQualitySheetPresented = false
    @State private var selectedSize = "M"
    
    var body: some View {
        NavigationView {
            VStack {
                // Surface 1: Wishlist Item Card
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: "tshirt.fill")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 80, height: 100)
                        .background(Color.gray.opacity(0.2))
                        .cornerRadius(8)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ROADSTER")
                            .font(.subheadline)
                            .bold()
                        Text("Men Pure Cotton Casual Shirt")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("₹1,299")
                            .font(.subheadline)
                            .bold()
                        
                        // Surface 1: Size Recommendation Chip
                        Button(action: { isFitSheetPresented = true }) {
                            HStack(spacing: 4) {
                                Text("✨ Rec. Size: **\(selectedSize)**")
                                Text("88% match")
                                    .font(.caption2)
                                    .bold()
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color.green.opacity(0.2))
                                    .cornerRadius(8)
                            }
                            .font(.caption)
                            .foregroundColor(.green)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(Color.green.opacity(0.1))
                            .cornerRadius(16)
                        }
                    }
                }
                .padding()
                .background(Color.white)
                .cornerRadius(12)
                .shadow(radius: 2)
                .padding()
                
                Spacer()
            }
            .navigationTitle("Wishlist")
            .sheet(isPresented: $isFitSheetPresented) {
                // Surface 2: Fit Confidence Detail Bottom Sheet Drawer
                FitConfidenceSheetView(selectedSize: $selectedSize)
            }
        }
    }
}

struct FitConfidenceSheetView: View {
    @Binding var selectedSize: String
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Personalized Fit Confidence")
                .font(.headline)
            
            Text("Based on 4 past purchases in size M from Roadster & 18 peer reviews.")
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            VStack(alignment: .leading) {
                Text("True to Size Match: 92%")
                ProgressView(value: 0.92)
                    .accentColor(.pink)
            }
            
            Button(action: {
                presentationMode.wrappedValue.dismiss()
            }) {
                Text("Pre-Select Size \(selectedSize) & Add to Bag")
                    .bold()
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.pink)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}
