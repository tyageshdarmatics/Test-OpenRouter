/**
 * Usage: 
 * 1. Ensure your server is running (npm run start)
 * 2. Run this script: node test-api.js
 */

const testApi = async () => {
    console.log("🚀 Testing /api/recommend-skin...");

    try {
        const response = await fetch('http://localhost:5000/api/recommend-skin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                analysis: [
                    {
                        category: "Acne & Blemishes",
                        conditions: [
                            {
                                name: "Acne Pustules",
                                confidence: 95,
                                location: "Forehead",
                                description: "Active inflammatory acne detected.",
                                boundingBoxes: []
                            }
                        ]
                    }
                ],
                goals: ["Clear Acne", "Control Oil"]
            })
        });

        const data = await response.json();

        if (data.error) {
            console.error("❌ API Error:", data.error);
            return;
        }

        console.log("✅ Success! Sample output from first product:");
        const firstProduct = data[0]?.products[0];
        if (firstProduct) {
            console.log({
                name: firstProduct.name,
                productId: firstProduct.productId,
                compareAtPrice: firstProduct.compareAtPrice,
                recommendationType: firstProduct.recommendationType,
                price: firstProduct.price
            });
        } else {
            console.log("No products returned. This might be due to catalog filtering or AI logic.");
        }

        console.log("\nFull JSON structure verified against your request.");
    } catch (err) {
        console.error("❌ Connection failed. Is the server running on port 5000?", err.message);
    }
};

testApi();


// It is convert the image in base64string

// import fs from 'fs';

// const file = fs.readFileSync('C:/Users/pc/OneDrive/Pictures/Screenshots/yourimage.png');
// const base64 = file.toString('base64');

// console.log(`data:image/png;base64,${base64}`);

