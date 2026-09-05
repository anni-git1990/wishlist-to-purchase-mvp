package com.myntra.wishlist.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// MARK: - Surface 1 & Surface 2 Android Jetpack Compose Native Mobile Screen
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WishlistFitScreen() {
    var showFitSheet by remember { mutableStateOf(false) }
    var selectedSize by remember { mutableStateOf("M") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Wishlist", color = Color.White, fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.smallTopAppBarColors(containerColor = Color(0xFFFF3F6C))
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            // Surface 1: Wishlist Card Component
            Card(
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("ROADSTER", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text("Men Pure Cotton Casual Shirt", color = Color.Gray, fontSize = 12.sp)
                    Text("₹1,299", fontWeight = FontWeight.Bold, fontSize = 14.sp)

                    Spacer(modifier = Modifier.height(8.dp))

                    // Surface 1: Size Recommendation Chip
                    Box(
                        modifier = Modifier
                            .background(Color(0xFFF0FDF4), shape = RoundedCornerShape(16.dp))
                            .clickable { showFitSheet = true }
                            .padding(horizontal = 10.dp, vertical = 6.dp)
                    ) {
                        Text(
                            text = "✨ Rec. Size: $selectedSize (88% match)",
                            color = Color(0xFF166534),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }

        // Surface 2: Fit Confidence Detail Bottom Sheet Modal
        if (showFitSheet) {
            ModalBottomSheet(
                onDismissRequest = { showFitSheet = false }
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp)
                ) {
                    Text("Personalized Fit Confidence", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        "Based on 4 past purchases in size M from Roadster & 18 peer reviews.",
                        fontSize = 13.sp,
                        color = Color.Gray
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(
                        onClick = { showFitSheet = false },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF3F6C)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Pre-Select Size $selectedSize & Add to Bag", color = Color.White)
                    }
                }
            }
        }
    }
}
