class GeminiService {
    static API_KEY = 'AIzaSyD2hXQOicNPJfWl_6lzgWNrMYusCGgVcuY';
    static API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';
    
    /**
     * Generate explanation for seed size prediction based on input parameters
     * @param {Object} params - The input parameters used for prediction
     * @param {Object} results - The prediction results
     * @returns {Promise<string>} - A promise that resolves to the explanation text
     */
    static async explainPrediction(params, results) {
        try {
            const promptText = this._buildExplanationPrompt(params, results);
            const response = await this._callGeminiAPI(promptText);
            return this._formatExplanation(response);
        } catch (error) {
            console.error('Error calling Gemini API:', error);
            return this._getFallbackExplanation(params, results);
        }
    }
    
    /**
     * Get recommended crops based on soil type and environmental conditions
     * @param {Object} params - The input parameters used for prediction
     * @returns {Promise<Array>} - A promise that resolves to an array of recommended crops
     */
    static async getRecommendedCrops(params) {
        try {
            const promptText = this._buildCropRecommendationPrompt(params);
            const response = await this._callGeminiAPI(promptText);
            return this._parseCropRecommendations(response);
        } catch (error) {
            console.error('Error getting crop recommendations:', error);
            return this._getFallbackCropRecommendations(params);
        }
    }
    
    /**
     * Build a prompt for the Gemini model to get crop recommendations
     * @private
     */
    static _buildCropRecommendationPrompt(params) {
        // Add humidity to params if available
        const humidity = params.humidity || '60';

        // Get soil type information
        const soilTypeInfo = this._getSoilTypeInfo(params.soil_type);
        
        // Get regional growing info
        const regionalInfo = this._getRegionalInfo(params.region);
        
        // Get seasonal info
        const seasonalInfo = this._getSeasonalInfo(params.season);
        
        // Create a more specific prompt that discourages generic responses
        return `
You are an agricultural specialist for Maharashtra, India. Provide VERY SPECIFIC and DIVERSE crop recommendations for this EXACT set of growing conditions.

DETAILED CONDITIONS:
- Region: ${params.region} (${regionalInfo})
- Season: ${params.season} (${seasonalInfo})
- Soil Type: ${params.soil_type} (${soilTypeInfo})
- Current Temperature: ${params.temperature}°C
- Soil Moisture: ${params.moisture}%
- Humidity: ${humidity}%
- Soil pH: ${params.soil_ph}

YOUR TASK:
Recommend 5-7 UNIQUE crops well-suited to THESE EXACT conditions.

IMPORTANT REQUIREMENTS:
1. DO NOT include the standard set of "Sunflower, Green Gram, Vegetables, Mustard, Groundnut"
2. DO NOT suggest common default crops like "Wheat, Rice, Cotton, Jowar, Bajra"
3. TEMPERATURE CONSIDERATION: Select crops that thrive at ${params.temperature}°C
4. MOISTURE CONSIDERATION: Choose crops adapted to ${params.moisture}% soil moisture
5. pH CONSIDERATION: Include crops suited for soil pH ${params.soil_ph}
6. Include at least 2-3 specialty/niche crops specific to these exact conditions
7. Include at least 1-2 high-value cash crops suited for these conditions
8. Strongly consider crops that are known to grow well in ${params.region} specifically during ${params.season}
9. DIVERSITY: Ensure your recommendations span different crop categories (pulses, vegetables, cereals, etc.)

FORMAT:
Respond ONLY with a JSON array of crop names:
["Crop1", "Crop2", "Crop3", "Crop4", "Crop5"]

Do not include explanations or other text.`;
    }
    
    /**
     * Get detailed soil type information
     * @private
     */
    static _getSoilTypeInfo(soilType) {
        const soilInfo = {
            'Black Soil': 'high clay content with excellent water retention, rich in carbonates, calcium, magnesium, and potash, alkaline with pH 7.5-8.5',
            'Red Soil': 'porous with good drainage, poor in nitrogen and organic matter, rich in potash, slightly acidic with pH 6.0-6.8',
            'Laterite Soil': 'acidic with pH 5.0-6.0, poor in nitrogen and calcium, rich in iron and aluminum oxides, requires fertilization',
            'Medium Black Soil': 'moderate clay content with balanced drainage and water retention, pH 7.0-8.0, more versatile than heavy black soil',
            'Alluvial Soil': 'highly fertile with potash, phosphoric acid, and lime, variable texture, pH 6.5-7.5, excellent for intensive agriculture',
            'Sandy Soil': 'large particles with excellent drainage but poor water and nutrient retention, acidic with pH 5.5-6.5, warms quickly'
        };
        
        return soilInfo[soilType] || 'specific soil properties that influence crop selection';
    }
    
    /**
     * Get regional growing information
     * @private
     */
    static _getRegionalInfo(region) {
        const regionInfo = {
            'Vidarbha': 'hot and dry climate, moderate rainfall of 700-900mm annually, known for cotton, soybean, and citrus cultivation',
            'Marathwada': 'semi-arid climate, low rainfall (600-800mm), prone to drought, traditional jowar and bajra growing area',
            'Western Maharashtra': 'moderate rainfall (700-1200mm), diverse climate zones, known for sugarcane, grapes, and onions',
            'Konkan': 'high rainfall region (2500-3500mm), coastal climate, humid, suitable for rice, coconut, and mango cultivation',
            'North Maharashtra': 'varied climate with moderate rainfall (600-900mm), known for banana, cotton, and wheat cultivation'
        };
        
        return regionInfo[region] || 'specific regional climate and growing conditions';
    }
    
    /**
     * Get seasonal growing information
     * @private
     */
    static _getSeasonalInfo(season) {
        const seasonInfo = {
            'Kharif': 'monsoon season from June to October, warm and humid with plenty of rainfall',
            'Rabi': 'winter season from October to March, cooler temperatures with limited rainfall',
            'Summer': 'hot dry season from March to June, high temperatures with very limited rainfall'
        };
        
        return seasonInfo[season] || 'specific growing season with its characteristic climate';
    }
    
    /**
     * Parse crop recommendations from Gemini API response
     * @private
     */
    static _parseCropRecommendations(response) {
        try {
            if (response?.candidates?.[0]?.content?.parts?.[0]?.text) {
                const text = response.candidates[0].content.parts[0].text.trim();
                // Extract JSON array from the response
                const match = text.match(/\[.*\]/s);
                if (match) {
                    const jsonStr = match[0];
                    return JSON.parse(jsonStr);
                }
            }
            throw new Error('Failed to parse crop recommendations');
        } catch (error) {
            console.error('Error parsing crop recommendations:', error);
            throw error;
        }
    }
    
    /**
     * Get fallback crop recommendations when API call fails
     * @private
     */
    static _getFallbackCropRecommendations(params) {
        // Try multiple different prompts to get varied recommendations
        const prompts = [
            // First attempt - very specific
            `I need 5-7 UNCOMMON crops that grow specifically in ${params.soil_type} in ${params.region} during ${params.season} with temperature ${params.temperature}°C, moisture ${params.moisture}%, and pH ${params.soil_ph}. DO NOT include wheat, rice, cotton, jowar, bajra, sunflower, green gram, vegetables, mustard, or groundnut in your list. Format as JSON array only: ["Crop1", "Crop2", "Crop3", "Crop4", "Crop5"]`,
            
            // Second attempt - focus on specialty crops
            `Provide 5-7 UNIQUE specialty or niche crops suited for ${params.soil_type} in ${params.region} during ${params.season}. Prioritize uncommon, high-value crops that local farmers might not typically grow but would succeed in these conditions (temp: ${params.temperature}°C, moisture: ${params.moisture}%, pH: ${params.soil_ph}). Provide ONLY a JSON array: ["Crop1", "Crop2", "Crop3", "Crop4", "Crop5"]`,
            
            // Third attempt - focus on cash crops
            `List 5-7 profitable cash crops for ${params.region} with ${params.soil_type} during ${params.season}. Temperature: ${params.temperature}°C. Exclude common crops (wheat, rice, cotton, jowar, bajra, sunflower, green gram). Return ONLY a JSON array.`,
            
            // Fourth attempt - focus on crop diversity
            `List 5-7 diverse crops from different categories (at least one pulse, one vegetable, one spice, one oilseed, etc.) suited for ${params.soil_type} in ${params.season} season in ${params.region}. DO NOT include sunflower, green gram, mustard, groundnut. Return ONLY as JSON array.`
        ];
        
        // Try each prompt in sequence until one succeeds - use higher temperature for more creativity
        return this._tryMultiplePromptsWithHighTemperature(prompts)
            .then(crops => {
                if (crops && crops.length > 0) {
                    return crops;
                }
                // If all API calls fail, use region/soil/season-specific fallbacks
                return this._getRegionSoilSeasonSpecificCrops(params);
            })
            .catch(() => {
                // If all API calls fail, use region/soil/season-specific fallbacks
                return this._getRegionSoilSeasonSpecificCrops(params);
            });
    }
    
    /**
     * Try multiple prompts with higher temperature setting for more variety
     * @private
     */
    static async _tryMultiplePromptsWithHighTemperature(prompts) {
        for (const prompt of prompts) {
            try {
                const response = await fetch(
                    `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${this.API_KEY}`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            contents: [{
                                parts: [{
                                    text: prompt
                                }]
                            }],
                            generationConfig: {
                                temperature: 0.9, // Higher temperature for more varied results
                                maxOutputTokens: 1024
                            }
                        })
                    }
                );
                
                if (!response.ok) {
                    continue; // Try next prompt if this one fails
                }
                
                const result = await response.json();
                const text = result?.candidates?.[0]?.content?.parts?.[0]?.text;
                
                if (text) {
                    // Extract JSON array from the response
                    const match = text.match(/\[.*\]/s);
                    if (match) {
                        const jsonStr = match[0];
                        try {
                            const crops = JSON.parse(jsonStr);
                            if (Array.isArray(crops) && crops.length > 0) {
                                return crops;
                            }
                        } catch (e) {
                            console.error('Error parsing JSON:', e);
                        }
                    }
                }
            } catch (error) {
                console.error('Error calling API with prompt:', error);
            }
        }
        throw new Error('All prompts failed');
    }
    
    /**
     * Get crops specific to region, soil type and season
     * @private
     */
    static _getRegionSoilSeasonSpecificCrops(params) {
        // Create a combination key to get specific crops
        const soil = params.soil_type.replace(/\s+/g, '');
        const region = params.region.replace(/\s+/g, '');
        const season = params.season;
        
        // Determine temperature range
        let tempRange = 'Normal';
        if (parseFloat(params.temperature) < 20) {
            tempRange = 'Cool';
        } else if (parseFloat(params.temperature) > 30) {
            tempRange = 'Hot';
        }
        
        // Determine moisture range
        let moistureRange = 'Medium';
        if (parseFloat(params.moisture) < 40) {
            moistureRange = 'Dry';
        } else if (parseFloat(params.moisture) > 70) {
            moistureRange = 'Wet';
        }
        
        // Create detailed key with all parameters
        const detailedKey = `${soil}_${region}_${season}_${tempRange}_${moistureRange}`;
        
        // Create basic key with just soil, region, and season
        const key = `${soil}_${region}_${season}`;
        
        // Define crop combinations for different soil, region, season, temp, and moisture
        const cropCombinations = {
            // Black Soil combinations with temperature and moisture variations
            'BlackSoil_Vidarbha_Kharif_Hot_Dry': ['Moth Bean', 'Cluster Bean', 'Horse Gram', 'Castor', 'Sesame', 'Pigeon Pea'],
            'BlackSoil_Vidarbha_Kharif_Hot_Medium': ['Cotton', 'Pigeon Pea', 'Soybean', 'Black Gram', 'Sesame'],
            'BlackSoil_Vidarbha_Kharif_Normal_Medium': ['Cotton', 'Soybean', 'Pigeon Pea', 'Green Gram', 'Sorghum'],
            
            'BlackSoil_Vidarbha_Rabi_Cool_Medium': ['Wheat', 'Chickpea', 'Safflower', 'Linseed', 'Coriander'],
            'BlackSoil_Vidarbha_Rabi_Normal_Medium': ['Chickpea', 'Safflower', 'Sorghum', 'Linseed', 'Mustard'],
            
            'BlackSoil_Vidarbha_Summer_Hot_Dry': ['Sesame', 'Cluster Bean', 'Watermelon', 'Bottle Gourd', 'Snake Gourd'],
            'BlackSoil_Vidarbha_Summer_Hot_Medium': ['Mung Bean', 'Watermelon', 'Muskmelon', 'Bottle Gourd', 'Bitter Gourd'],
            
            // Red Soil combinations with variations
            'RedSoil_WesternMaharashtra_Kharif_Normal_Medium': ['Pearl Millet', 'Pigeon Pea', 'Green Gram', 'Black Gram', 'Cowpea'],
            'RedSoil_WesternMaharashtra_Kharif_Hot_Dry': ['Pearl Millet', 'Moth Bean', 'Cluster Bean', 'Sesame', 'Horse Gram'],
            
            'RedSoil_WesternMaharashtra_Rabi_Normal_Dry': ['Chickpea', 'Coriander', 'Fenugreek', 'Cumin', 'Mustard'],
            
            'RedSoil_WesternMaharashtra_Summer_Hot_Dry': ['Cluster Bean', 'Cowpea', 'Bottle Gourd', 'Sesame', 'Guar'],
            'RedSoil_WesternMaharashtra_Summer_Hot_Medium': ['Groundnut', 'Sesame', 'Okra', 'Bitter Gourd', 'Ridge Gourd'],
            
            // Laterite Soil combinations with variations
            'LateriteSoil_Konkan_Kharif_Normal_Wet': ['Rice', 'Finger Millet', 'Cowpea', 'Horse Gram', 'Sesame'],
            'LateriteSoil_Konkan_Kharif_Hot_Wet': ['Rice', 'Black Gram', 'Green Gram', 'Cowpea', 'Bitter Gourd'],
            
            'LateriteSoil_Konkan_Rabi_Cool_Medium': ['Finger Millet', 'Horse Gram', 'Sweet Potato', 'Colocasia', 'Turmeric'],
            'LateriteSoil_Konkan_Rabi_Normal_Medium': ['Finger Millet', 'Horse Gram', 'Vegetables', 'Pulses', 'Sweet Potato'],
            
            'LateriteSoil_Konkan_Summer_Hot_Medium': ['Okra', 'Bitter Gourd', 'Ridge Gourd', 'Sweet Potato', 'Chillies'],
            'LateriteSoil_Konkan_Summer_Hot_Wet': ['Vegetables', 'Watermelon', 'Cucumber', 'Gourds', 'Chillies'],
            
            // Medium Black Soil with variations
            'MediumBlackSoil_NorthMaharashtra_Kharif_Normal_Medium': ['Cotton', 'Soybean', 'Pearl Millet', 'Sorghum', 'Pigeon Pea'],
            'MediumBlackSoil_NorthMaharashtra_Kharif_Hot_Dry': ['Pearl Millet', 'Moth Bean', 'Cluster Bean', 'Sesame', 'Castor'],
            
            'MediumBlackSoil_NorthMaharashtra_Rabi_Cool_Medium': ['Wheat', 'Chickpea', 'Sunflower', 'Mustard', 'Fenugreek'],
            'MediumBlackSoil_NorthMaharashtra_Rabi_Normal_Medium': ['Wheat', 'Chickpea', 'Sunflower', 'Mustard', 'Vegetables'],
            
            // Alluvial Soil with variations
            'AlluvialSoil_WesternMaharashtra_Kharif_Normal_Wet': ['Rice', 'Sugarcane', 'Turmeric', 'Ginger', 'Elephant Foot Yam'],
            'AlluvialSoil_WesternMaharashtra_Kharif_Hot_Wet': ['Rice', 'Sugarcane', 'Taro', 'Water Chestnut', 'Lotus Root'],
            
            'AlluvialSoil_WesternMaharashtra_Rabi_Cool_Medium': ['Wheat', 'Potato', 'Onion', 'Garlic', 'Tomato'],
            'AlluvialSoil_WesternMaharashtra_Rabi_Normal_Medium': ['Wheat', 'Vegetables', 'Potato', 'Onion', 'Ginger'],
            
            'AlluvialSoil_WesternMaharashtra_Summer_Hot_Medium': ['Muskmelon', 'Watermelon', 'Cucumber', 'Bitter Gourd', 'Okra'],
            'AlluvialSoil_WesternMaharashtra_Summer_Hot_Wet': ['Sugarcane', 'Vegetables', 'Melons', 'Cucumber', 'Pointed Gourd'],
            
            // More soil and region combinations
            'BlackSoil_Marathwada_Kharif': ['Cotton', 'Pigeon Pea', 'Green Gram', 'Black Gram', 'Soybean'],
            'BlackSoil_Marathwada_Rabi': ['Sorghum', 'Wheat', 'Chickpea', 'Safflower', 'Sunflower'],
            'BlackSoil_Marathwada_Summer': ['Sesame', 'Bitter Gourd', 'Bottle Gourd', 'Ridge Gourd', 'Cucumber'],
            
            'RedSoil_NorthMaharashtra_Kharif': ['Pearl Millet', 'Green Gram', 'Black Gram', 'Sesame', 'Cluster Bean'],
            'RedSoil_NorthMaharashtra_Rabi': ['Wheat', 'Chickpea', 'Sunflower', 'Mustard', 'Fenugreek'],
            'RedSoil_NorthMaharashtra_Summer': ['Sesame', 'Bitter Gourd', 'Ridge Gourd', 'Bottle Gourd', 'Snake Gourd'],
            
            'AlluvialSoil_Konkan_Kharif': ['Rice', 'Sweet Potato', 'Turmeric', 'Ginger', 'Elephant Foot Yam'],
            'AlluvialSoil_Konkan_Rabi': ['Pulses', 'Sweet Potato', 'Elephant Foot Yam', 'Onion', 'Chillies'],
            'AlluvialSoil_Konkan_Summer': ['Bitter Gourd', 'Ridge Gourd', 'Cucumber', 'Snake Gourd', 'Chillies'],
            
            // Additional combinations for variety
            'BlackSoil_WesternMaharashtra_Kharif': ['Cotton', 'Pigeon Pea', 'Soybean', 'Green Gram', 'Black Eyed Peas'],
            'BlackSoil_Konkan_Rabi': ['Groundnut', 'Cowpea', 'Field Beans', 'Hyacinth Beans', 'Black Gram'],
            'RedSoil_Marathwada_Summer': ['Sesame', 'Guar', 'Cluster Bean', 'Bitter Gourd', 'Bottle Gourd'],
            'LateriteSoil_NorthMaharashtra_Kharif': ['Rice', 'Finger Millet', 'Cowpea', 'Pigeon Pea', 'Sesame'],
            'MediumBlackSoil_Konkan_Summer': ['Bitter Gourd', 'Ridge Gourd', 'Snake Gourd', 'Pointed Gourd', 'Cucumber'],
            'AlluvialSoil_Vidarbha_Rabi': ['Wheat', 'Potato', 'Onion', 'Tomato', 'Fenugreek']
        };
        
        // First try the detailed key with temperature and moisture
        if (cropCombinations[detailedKey]) {
            return cropCombinations[detailedKey];
        }
        
        // Then try the basic key without temperature and moisture
        if (cropCombinations[key]) {
            return cropCombinations[key];
        }
        
        // Try using just the soil type and season if region-specific data isn't available
        const soilSeasonKey = `${soil}_${season}`;
        
        const soilSeasonCombinations = {
            'BlackSoil_Kharif': ['Cotton', 'Soybean', 'Pigeon Pea', 'Green Gram', 'Black Gram', 'Sesame'],
            'BlackSoil_Rabi': ['Wheat', 'Chickpea', 'Safflower', 'Linseed', 'Mustard', 'Coriander'],
            'BlackSoil_Summer': ['Sesame', 'Cluster Bean', 'Mung Bean', 'Bottle Gourd', 'Watermelon', 'Bitter Gourd'],
            
            'RedSoil_Kharif': ['Pearl Millet', 'Cluster Bean', 'Moth Bean', 'Horse Gram', 'Sesame', 'Cowpea'],
            'RedSoil_Rabi': ['Chickpea', 'Coriander', 'Fenugreek', 'Cumin', 'Mustard', 'Safflower'],
            'RedSoil_Summer': ['Sesame', 'Guar', 'Cluster Bean', 'Watermelon', 'Muskmelon', 'Bitter Gourd'],
            
            'LateriteSoil_Kharif': ['Rice', 'Finger Millet', 'Cowpea', 'Horse Gram', 'Sesame', 'Little Millet'],
            'LateriteSoil_Rabi': ['Finger Millet', 'Horse Gram', 'Sweet Potato', 'Black Gram', 'Field Beans', 'Amaranth'],
            'LateriteSoil_Summer': ['Bitter Gourd', 'Ridge Gourd', 'Cucumber', 'Snake Gourd', 'Chillies', 'Pointed Gourd'],
            
            'MediumBlackSoil_Kharif': ['Cotton', 'Pearl Millet', 'Sorghum', 'Pigeon Pea', 'Green Gram', 'Black Gram'],
            'MediumBlackSoil_Rabi': ['Wheat', 'Chickpea', 'Safflower', 'Mustard', 'Fenugreek', 'Linseed'],
            'MediumBlackSoil_Summer': ['Sesame', 'Cluster Bean', 'Bitter Gourd', 'Ridge Gourd', 'Snake Gourd', 'Bottle Gourd'],
            
            'AlluvialSoil_Kharif': ['Rice', 'Sugarcane', 'Turmeric', 'Ginger', 'Taro', 'Elephant Foot Yam'],
            'AlluvialSoil_Rabi': ['Wheat', 'Potato', 'Onion', 'Garlic', 'Tomato', 'Leafy Vegetables'],
            'AlluvialSoil_Summer': ['Muskmelon', 'Watermelon', 'Cucumber', 'Bitter Gourd', 'Okra', 'Snake Gourd'],
            
            'SandySoil_Kharif': ['Pearl Millet', 'Cluster Bean', 'Moth Bean', 'Cowpea', 'Sesame', 'Horse Gram'],
            'SandySoil_Rabi': ['Cumin', 'Mustard', 'Chickpea', 'Coriander', 'Fenugreek', 'Isabgol'],
            'SandySoil_Summer': ['Watermelon', 'Muskmelon', 'Cluster Bean', 'Cucumber', 'Ridge Gourd', 'Snake Gourd']
        };
        
        if (soilSeasonCombinations[soilSeasonKey]) {
            return soilSeasonCombinations[soilSeasonKey];
        }
        
        // Last resort fallbacks for each soil type - with variation to avoid the same defaults
        const soilTypeFallbacks = {
            'Black Soil': ['Cotton', 'Soybean', 'Pigeon Pea', 'Chickpea', 'Linseed', 'Safflower'],
            'Red Soil': ['Pearl Millet', 'Groundnut', 'Sorghum', 'Chickpea', 'Cluster Bean', 'Horse Gram'],
            'Laterite Soil': ['Rice', 'Finger Millet', 'Sweet Potato', 'Black Gram', 'Horse Gram', 'Little Millet'],
            'Medium Black Soil': ['Cotton', 'Wheat', 'Pearl Millet', 'Pigeon Pea', 'Chickpea', 'Safflower'],
            'Alluvial Soil': ['Rice', 'Wheat', 'Potato', 'Sugarcane', 'Elephant Foot Yam', 'Taro'],
            'Sandy Soil': ['Pearl Millet', 'Cluster Bean', 'Watermelon', 'Muskmelon', 'Moth Bean', 'Sesame']
        };
        
        // Get a random number to add some variety to recommendations
        const randomNum = Math.floor(Date.now() / 1000) % 3;
        
        // Seasonal variations for absolute fallback - different options based on season
        const seasonalFallbacks = {
            'Kharif': [
                ['Cowpea', 'Black Gram', 'Horse Gram', 'Pearl Millet', 'Finger Millet', 'Sorghum'],
                ['Pigeon Pea', 'Green Gram', 'Sesame', 'Little Millet', 'Cluster Bean', 'Moth Bean'],
                ['Cotton', 'Soybean', 'Rice', 'Turmeric', 'Ginger', 'Elephant Foot Yam']
            ],
            'Rabi': [
                ['Chickpea', 'Mustard', 'Linseed', 'Safflower', 'Coriander', 'Cumin'],
                ['Wheat', 'Potato', 'Onion', 'Garlic', 'Fenugreek', 'Fennel'],
                ['Field Beans', 'Garden Pea', 'Lentil', 'Barley', 'Oats', 'Spinach']
            ],
            'Summer': [
                ['Watermelon', 'Muskmelon', 'Cucumber', 'Ridge Gourd', 'Bottle Gourd', 'Snake Gourd'],
                ['Bitter Gourd', 'Pointed Gourd', 'Okra', 'Cluster Bean', 'Cowpea', 'Guar'],
                ['Sesame', 'Mung Bean', 'Amaranth', 'Roselle', 'Sword Bean', 'Winged Bean']
            ]
        };
        
        if (soilTypeFallbacks[params.soil_type]) {
            return soilTypeFallbacks[params.soil_type];
        }
        
        // Absolute fallback if nothing else works - use seasonal variations with randomization
        if (seasonalFallbacks[params.season]) {
            return seasonalFallbacks[params.season][randomNum];
        }
        
        // Final default that should be different from generic "Sunflower, Green Gram, Vegetables, Mustard, Groundnut"
        return ['Sesame', 'Black Gram', 'Cowpea', 'Finger Millet', 'Bitter Gourd', 'Cluster Bean'];
    }
    
    /**
     * Build a prompt for the Gemini model to explain the prediction
     * @private
     */
    static _buildExplanationPrompt(params, results) {
        return `
As an agricultural expert, provide a practical and straightforward explanation of why these seed recommendations make sense for a farmer.

INPUTS:
- Crop: ${params.crop_name}
- Region: ${params.region}
- Season: ${params.season}
- Soil Type: ${params.soil_type}
- Temperature: ${params.temperature}°C
- Soil Moisture: ${params.moisture}%
- Soil pH: ${params.soil_ph}

PREDICTION RESULTS:
- Recommended Seed Size: ${results.seed_size}
- Sowing Depth: ${results.sowing_depth} cm
- Plant Spacing: ${results.spacing} cm

Format your response in simple, farmer-friendly language (about 100 words) that explains:
1. Why this seed size works well for these growing conditions
2. How the recommended sowing depth helps the seeds grow properly
3. Why this plant spacing is good for the crop
4. Include some practical benefits the farmer will see

Avoid complicated scientific terms, percentages, or research-oriented language. Just provide useful, factual information that a farmer can understand and use. Make it conversational and helpful, not technical.`;
    }
    
    /**
     * Call the Gemini API with the given prompt
     * @private
     */
    static async _callGeminiAPI(promptText) {
        const response = await fetch(`${this.API_URL}?key=${this.API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: promptText
                    }]
                }],
                generationConfig: {
                    temperature: 0.9,
                    maxOutputTokens: 1024
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    }
    
    /**
     * Format the explanation from Gemini API response
     * @private
     */
    static _formatExplanation(response) {
        try {
            // Extract the text from the response
            if (response && 
                response.candidates && 
                response.candidates[0] && 
                response.candidates[0].content && 
                response.candidates[0].content.parts && 
                response.candidates[0].content.parts[0] && 
                response.candidates[0].content.parts[0].text) {
                
                const text = response.candidates[0].content.parts[0].text.trim();
                return text;
            }
            throw new Error('Unexpected API response format');
        } catch (error) {
            console.error('Error parsing AI response:', error);
            throw error;
        }
    }
    
    /**
     * Generate a fallback explanation when API call fails
     * @private
     */
    static _getFallbackExplanation(params, results) {
        return `For growing ${params.crop_name} in ${params.region} during ${params.season}, ${results.seed_size} seeds work best with your ${params.soil_type}. Planting at ${results.sowing_depth} cm deep protects seeds while allowing them to emerge properly in these conditions. Spacing plants ${results.spacing} cm apart gives them enough room to grow without competing for water and nutrients. This approach helps your plants develop strong roots and produce a good harvest, even considering your soil's pH of ${params.soil_ph} and the local temperature of ${params.temperature}°C. These recommendations are based on what has worked well for farmers in similar conditions.`;
    }
}

// Export for use in other scripts
window.GeminiService = GeminiService; 