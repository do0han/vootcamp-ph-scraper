"""
Report Type Dispatcher

Central dispatcher function that routes report generation requests to 
specific report generators based on report_type.
"""

import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_specialized_report(user_profile, report_type):
    """
    Main dispatcher function for generating specialized reports.
    
    Args:
        user_profile (dict): User profile information including persona, interests, etc.
        report_type (str): Type of report to generate
        
    Returns:
        str: Generated report content
    """
    
    # Normalize report_type to handle different formats
    report_type = report_type.lower().strip()
    
    # Dispatcher logic using if/elif/else structure
    if report_type == "content_strategy" or report_type == "content-strategy":
        return generate_content_strategy_report(user_profile)
    elif report_type == "monetization" or report_type == "monetization_plan":
        return generate_monetization_plan_report(user_profile)
    elif report_type == "performance_optimization" or report_type == "performance-optimization":
        return generate_performance_optimization_report(user_profile)
    elif report_type == "content_ideas" or report_type == "content-ideas":
        return generate_content_ideas_report(user_profile)
    elif report_type == "trend_analysis" or report_type == "trend-analysis":
        return generate_trend_analysis_report(user_profile)
    elif report_type == "competitor_analysis" or report_type == "competitor-analysis":
        return generate_competitor_analysis_report(user_profile)
    else:
        return f"Error: Unknown report type '{report_type}'. Available types: content_strategy, monetization, performance_optimization, content_ideas, trend_analysis, competitor_analysis"


def get_user_profile(persona_id):
    # This function is a placeholder.
    # In a real application, you would fetch this from a database
    # or a user management service.
    # For this UAT, we will receive the full profile directly.
    # This function will not be used by the test script.
    return None

def generate_content_strategy_report(user_profile):
    """
    Generates a personalized Content Strategy Report based on a persona profile.
    This version now calls the OpenAI API.
    """
    if not user_profile:
        return "Error: user_profile cannot be None."

    persona = user_profile.get('persona', {})
    persona_name = persona.get('name', 'Content Creator')
    channel_category = user_profile.get('channel_category', 'General')
    mbti_type = user_profile.get('mbti', 'Not specified')
    mbti_details = persona.get('mbti_details', 'Not specified')

    prompt = f"""You are an expert Content Strategist for Filipino creators. Your task is to generate a Content Strategy Report that is deeply personalized based on the provided [Persona Profile].

Persona Profile:
- Channel Category: {channel_category}
- MBTI: {mbti_type} ({mbti_details})

Your output MUST strictly follow these rules:

1.  **Section 1 & 2 (Hot Topics & Seasonal Keywords):** All topics and keywords must be filtered and adapted to be directly relevant to the '{channel_category}' category. For example, if the category is "Beauty," you must suggest topics like "Glass Skin Trend" or "GRWM (Get Ready With Me)," NOT "DIY Home Projects."

2.  **Section 3 (Top 5 Concrete Content Ideas):** This is the most important section. Every single idea must be a direct reflection of both the Channel Category and the MBTI type.
    -   **For the Channel Category:** The idea must be undeniably about this topic. (e.g., for "Beauty," it must be about makeup, skincare, etc.).
    -   **For the MBTI type:** The angle and format of the idea must align with the personality traits of the {mbti_type}. For an "ESFP (Entertainer)," suggest social, engaging, and trend-focused formats like challenges or live streams. For an "INTP (Logician)," suggest analytical, deep-dive, or experimental formats.

3.  **Strict Exclusion:** DO NOT include any advice on monetization or performance optimization. Focus 100% on personalized content strategy.
"""

    try:
        # --- OpenAI API Call ---
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert Content Strategist for Filipino creators."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        report_content = response.choices[0].message.content
        return report_content.strip()

    except Exception as e:
        print(f"An error occurred while calling OpenAI API: {e}")
        return f"Error: Failed to generate report due to an API error. Please check API key and service status. Details: {e}"


def generate_monetization_plan_report(user_profile):
    """
    Generate a comprehensive Monetization Plan Report using AI.
    
    Args:
        user_profile (dict): User profile information including persona, interests, etc.
        
    Returns:
        str: AI-generated monetization plan report
    """
    
    # Extract user information
    persona = user_profile.get('persona', {})
    persona_name = persona.get('name', 'Content Creator')
    persona_id = persona.get('id', 'general')
    interests = user_profile.get('interests', [])
    budget = user_profile.get('budget', 'Not specified')
    
    # Create detailed prompt for Monetization Plan
    prompt = f"""You are a BUSINESS DEVELOPMENT CONSULTANT specializing in Filipino content creator monetization. Your ONLY job is to provide monetization strategies and revenue opportunities.

STRICT EXCLUSION RULE: DO NOT include any content ideas, creative strategies, performance tips, or analytics advice. Focus EXCLUSIVELY on monetization and revenue generation.

USER PROFILE:
- Persona: {persona_name} ({persona_id})
- Interests: {', '.join(interests) if interests else 'General content'}
- Budget Context: {budget}
- Target Market: Philippines

Generate a comprehensive Monetization Plan Report with the following EXACT structure:

# 💰 Monetization Plan Report: {persona_name}

## 💵 Section 1: Immediate Revenue Opportunities (0-3 months)
List 4-5 monetization strategies that can be implemented immediately with the {persona_name} niche. Include:
- Revenue stream name and description
- Expected monthly income range (in Philippine Peso)
- Required setup time and effort level
- Specific Filipino platforms and partnerships to target

## 🚀 Section 2: Long-term Revenue Strategies (6-12 months)
Provide advanced monetization approaches for sustained growth, considering:
- Scalable business models for Filipino market
- Premium offerings and subscription models
- Local partnership opportunities
- Digital product development strategies

## 💼 Section 3: Top 5 Monetization Tactics

For each monetization tactic, provide:

### [Number]. "[Revenue Stream Name]"
- **Revenue Type**: [One-time, recurring, commission-based, etc.]
- **Income Potential**: [Monthly range in PHP]
- **Setup Requirements**: [Time, tools, initial investment needed]
- **Filipino Market Fit**: [Why this works specifically in Philippines]
- **Implementation Steps**: [3-4 concrete action steps]
- **Success Metrics**: [How to measure revenue performance]
- **Risk Level**: [Low/Medium/High with brief explanation]

MONETIZATION GUIDELINES:
- Focus on Filipino market opportunities and purchasing power
- Consider local payment methods (GCash, PayMaya, bank transfers)
- Include both digital and physical product opportunities
- Consider Filipino business culture and relationship-building
- Factor in local tax implications and business registration
- Emphasize sustainable, ethical monetization practices

IMPORTANT CONSTRAINTS:
- DO NOT mention content creation strategies
- DO NOT include performance optimization advice
- DO NOT suggest creative ideas or content topics
- FOCUS ONLY on revenue generation and business development
- Keep tone professional and business-focused

Generate the report now, following this structure exactly."""

    # For now, return the sample report (in actual implementation, this would call an AI service)
    # TODO: Replace with actual AI API call (OpenAI, Anthropic, etc.)
    return f"""# 💰 Monetization Plan Report: {persona_name}

## 💵 Section 1: Immediate Revenue Opportunities (0-3 months)

### 1. "Affiliate Marketing sa Filipino Brands"
Partner with local brands relevant to {persona_id} niche. Filipino audiences trust recommendations from creators they follow. Expected monthly income: ₱5,000-15,000 depending on audience size and engagement rates.

### 2. "Sponsored Content Partnerships"
Collaborate with Filipino brands for sponsored posts and product features. Local businesses are increasingly investing in influencer marketing. Setup time: 1-2 weeks for initial partnerships.

### 3. "Digital Consultation Services"
Offer 1-on-1 consultations related to your {persona_id} expertise. Filipinos value personal advice and are willing to pay for specialized knowledge. Income potential: ₱1,500-3,000 per session.

### 4. "Online Workshop Hosting"
Create paid workshops teaching skills related to your niche. Use platforms like Zoom or Facebook Live with paid access. Expected income: ₱8,000-25,000 per workshop batch.

### 5. "Local Brand Ambassador Programs"
Become a brand ambassador for Filipino companies in your niche. Long-term partnerships provide stable monthly income. Expected range: ₱3,000-12,000 monthly retainer.

## 🚀 Section 2: Long-term Revenue Strategies (6-12 months)

### Digital Product Development
- **E-courses and Masterclasses**: Comprehensive online courses selling for ₱2,999-₱9,999
- **Digital Templates/Resources**: Downloadable resources priced ₱299-₱1,499
- **Exclusive Membership Communities**: Monthly subscription model ₱199-₱999/month
- **Personal Branding Packages**: Complete service offerings ₱15,000-₱50,000

### Strategic Partnerships
- **Local Business Collaborations**: Joint ventures with complementary Filipino businesses
- **Cross-Creator Partnerships**: Revenue-sharing collaborations with other Filipino creators
- **Corporate Training Contracts**: B2B services for Filipino companies ₱25,000-₱100,000 per contract

### Physical Product Lines
- **Branded Merchandise**: T-shirts, accessories with Filipino-inspired designs
- **Local Product Curation**: Curated boxes of Filipino products with monthly subscription model
- **Book Publishing**: Physical books distributed through local bookstores and online

## 💼 Section 3: Top 5 Monetization Tactics

### 1. "Filipino Brand Affiliate Network"
- **Revenue Type**: Commission-based (5-20% per sale)
- **Income Potential**: ₱8,000-₱30,000 monthly
- **Setup Requirements**: 2-3 weeks, media kit creation, audience analytics
- **Filipino Market Fit**: Local brands offer higher commissions than international ones
- **Implementation Steps**: 1) Create professional media kit, 2) Research Filipino brands in niche, 3) Send partnership proposals, 4) Set up tracking systems
- **Success Metrics**: Click-through rates, conversion rates, monthly commission earnings
- **Risk Level**: Low - no upfront costs, performance-based income

### 2. "Premium Consultation Services"
- **Revenue Type**: One-time service fees
- **Income Potential**: ₱15,000-₱45,000 monthly
- **Setup Requirements**: 1 week, booking system, service packages definition
- **Filipino Market Fit**: Filipinos prefer personalized service and expert guidance
- **Implementation Steps**: 1) Define service packages, 2) Set up booking calendar, 3) Create service agreements, 4) Market to existing audience
- **Success Metrics**: Booking rate, client satisfaction scores, repeat bookings
- **Risk Level**: Low - leverages existing expertise, flexible scheduling

### 3. "Subscription-Based Exclusive Content"
- **Revenue Type**: Recurring monthly subscription
- **Income Potential**: ₱12,000-₱60,000 monthly (depending on subscriber count)
- **Setup Requirements**: 3-4 weeks, platform setup, exclusive content creation
- **Filipino Market Fit**: Growing acceptance of subscription models, lower price points work well
- **Implementation Steps**: 1) Choose platform (Patreon, local alternatives), 2) Define tier structure, 3) Create exclusive content calendar, 4) Launch with early bird pricing
- **Success Metrics**: Subscriber growth rate, retention rate, monthly recurring revenue
- **Risk Level**: Medium - requires consistent content creation, subscriber retention challenges

### 4. "Corporate Workshop Facilitation"
- **Revenue Type**: Project-based contracts
- **Income Potential**: ₱25,000-₱100,000 per project
- **Setup Requirements**: 4-6 weeks, workshop curriculum development, corporate outreach
- **Filipino Market Fit**: Companies investing in employee development, preference for local facilitators
- **Implementation Steps**: 1) Develop workshop curriculum, 2) Create corporate proposal template, 3) Network with HR professionals, 4) Pilot with small companies
- **Success Metrics**: Contract value, client satisfaction, repeat bookings
- **Risk Level**: Medium - longer sales cycles, requires business development skills

### 5. "E-commerce Product Line"
- **Revenue Type**: Product sales with profit margins
- **Income Potential**: ₱20,000-₱80,000 monthly
- **Setup Requirements**: 2-3 months, product development, inventory management
- **Filipino Market Fit**: Strong e-commerce growth, preference for locally-made products
- **Implementation Steps**: 1) Identify product opportunities, 2) Source suppliers or manufacturers, 3) Set up Shopee/Lazada stores, 4) Integrate with content strategy
- **Success Metrics**: Sales volume, profit margins, customer acquisition cost
- **Risk Level**: High - inventory risk, upfront investment, logistics complexity

---

*💰 This monetization plan focuses on sustainable revenue generation tailored for the Filipino content creator market.*"""


def generate_performance_optimization_report(user_profile):
    """
    Generate a comprehensive Performance Optimization Report using AI.
    
    Args:
        user_profile (dict): User profile information including persona, interests, etc.
        
    Returns:
        str: AI-generated performance optimization report
    """
    
    # Extract user information
    persona = user_profile.get('persona', {})
    persona_name = persona.get('name', 'Content Creator')
    persona_id = persona.get('id', 'general')
    interests = user_profile.get('interests', [])
    budget = user_profile.get('budget', 'Not specified')
    
    # Create detailed prompt for Performance Optimization
    prompt = f"""You are a CHANNEL GROWTH HACKER specializing in Filipino content creator performance optimization. Your ONLY job is to provide performance metrics improvement strategies.

STRICT EXCLUSION RULE: DO NOT include any content ideas, creative strategies, or monetization advice. Focus EXCLUSIVELY on performance metrics, analytics, and growth optimization.

USER PROFILE:
- Persona: {persona_name} ({persona_id})
- Interests: {', '.join(interests) if interests else 'General content'}
- Budget Context: {budget}
- Target Market: Philippines

Generate a comprehensive Performance Optimization Report with the following EXACT structure:

# 📈 Performance Optimization Report: {persona_name}

## 🎯 Section 1: Thumbnail & Visual Optimization
List 5-6 data-driven thumbnail and visual strategies specifically for Filipino audiences. Include:
- Specific visual elements that perform well in Philippines
- Color psychology for Filipino viewers
- Text overlay strategies for Tagalog/English mix
- Face vs. non-face thumbnail performance metrics
- Platform-specific thumbnail optimization

## ⏰ Section 2: Upload Timing & Scheduling Strategy
Provide optimal posting schedules based on Filipino audience behavior, considering:
- Peak engagement hours for Filipino time zones
- Day-of-week performance patterns
- Seasonal timing considerations (holidays, school calendar)
- Platform-specific optimal timing
- Cross-platform scheduling coordination

## 📊 Section 3: Top 5 Performance Optimization Tactics

For each optimization tactic, provide:

### [Number]. "[Optimization Strategy Name]"
- **Metric Focus**: [CTR, Watch Time, Engagement Rate, etc.]
- **Expected Improvement**: [Percentage increase range]
- **Implementation Time**: [How long to see results]
- **Filipino Market Specifics**: [Cultural/behavioral considerations]
- **Testing Method**: [How to A/B test this optimization]
- **Success Measurement**: [Specific KPIs to track]
- **Platform Priority**: [Which platforms benefit most]

OPTIMIZATION GUIDELINES:
- Focus on Filipino audience behavior patterns and preferences
- Consider Filipino internet usage patterns and device preferences
- Include mobile-first optimization strategies
- Factor in local internet speeds and data costs
- Consider Filipino social media engagement behaviors
- Emphasize sustainable, ethical growth practices

IMPORTANT CONSTRAINTS:
- DO NOT mention content creation ideas or topics
- DO NOT include monetization strategies or revenue advice
- DO NOT suggest creative concepts or storylines
- FOCUS ONLY on metrics, analytics, and performance improvement
- Keep tone technical and data-focused

Generate the report now, following this structure exactly."""

    # For now, return the sample report (in actual implementation, this would call an AI service)
    # TODO: Replace with actual AI API call (OpenAI, Anthropic, etc.)
    return f"""# 📈 Performance Optimization Report: {persona_name}

## 🎯 Section 1: Thumbnail & Visual Optimization

### 1. "Filipino Face Recognition Advantage"
Thumbnails featuring Filipino faces perform 35% better than non-face thumbnails in the local market. Filipino audiences prefer seeing relatable faces and expressions. Use clear, well-lit facial shots with emotional expressions.

### 2. "Bright Color Psychology"
Vibrant colors (orange, yellow, red) increase click-through rates by 28% among Filipino viewers. These colors stand out in mobile feeds and align with Filipino aesthetic preferences for lively, energetic visuals.

### 3. "Taglish Text Overlay Strategy"
Mix Filipino and English text in thumbnails for maximum appeal. Use Filipino words for emotional hooks ("Grabe!", "Hindi ko inaasahan!") and English for clarity. Optimal text size: 60-80px for mobile viewing.

### 4. "Mobile-First Thumbnail Design"
89% of Filipino users access content via mobile. Design thumbnails that are legible on 5-6 inch screens. Use high contrast ratios (4.5:1 minimum) and limit text to 3-4 words maximum.

### 5. "Cultural Context Visual Cues"
Include recognizable Filipino visual elements (jeepney, local food, familiar backgrounds) to increase relatability. These elements can improve CTR by 22% compared to generic visuals.

### 6. "Emotion-Driven Expression Optimization"
Surprised expressions (wide eyes, open mouth) perform 40% better than neutral faces. Filipino audiences respond strongly to dramatic, expressive thumbnails that convey excitement or shock.

## ⏰ Section 2: Upload Timing & Scheduling Strategy

### Peak Engagement Windows for Filipino Audiences:
- **Weekday Prime Time**: 7:00 PM - 10:00 PM (Philippine Time) - highest engagement period
- **Weekend Morning**: 9:00 AM - 12:00 PM (Saturday/Sunday) - strong family viewing time
- **Lunch Break Surge**: 12:00 PM - 1:00 PM (Monday-Friday) - mobile viewing spike
- **Late Night Scroll**: 10:30 PM - 12:00 AM - secondary peak for younger demographics

### Platform-Specific Optimal Timing:
- **YouTube**: Tuesday-Thursday, 8:00 PM upload for maximum 24-hour performance
- **TikTok**: Wednesday-Friday, 6:00 PM for peak evening engagement
- **Instagram**: Saturday-Sunday, 10:00 AM for weekend leisure browsing
- **Facebook**: Monday, Wednesday, Friday, 7:30 PM for highest reach

### Seasonal Considerations:
- **School Calendar Impact**: June-March (school year) vs April-May (summer break) show 45% variance in teen engagement
- **Payday Patterns**: 15th and 30th of month show 30% higher engagement on lifestyle content
- **Holiday Seasons**: December shows 60% increase in family-oriented content consumption

## 📊 Section 3: Top 5 Performance Optimization Tactics

### 1. "Filipino Algorithm Engagement Pattern Optimization"
- **Metric Focus**: First 24-hour engagement rate and watch time retention
- **Expected Improvement**: 25-40% increase in initial performance metrics
- **Implementation Time**: 2-3 upload cycles to see consistent results
- **Filipino Market Specifics**: Filipino audiences engage heavily in first 6 hours after upload, then taper off faster than Western audiences
- **Testing Method**: A/B test upload times in 2-hour windows, track 24-hour performance
- **Success Measurement**: Compare 24-hour view velocity, engagement rate, and share rate
- **Platform Priority**: YouTube and TikTok show strongest patterns, Instagram secondary

### 2. "Mobile Data-Conscious Video Optimization"
- **Metric Focus**: Watch time completion rates and bounce rate reduction
- **Expected Improvement**: 15-30% improvement in average view duration
- **Implementation Time**: Immediate impact with proper video compression
- **Filipino Market Specifics**: Many users on limited data plans, prefer videos that load quickly and don't consume excessive data
- **Testing Method**: Compare performance of different video quality settings (720p vs 1080p)
- **Success Measurement**: Track completion rates, buffer rates, and user retention graphs
- **Platform Priority**: All platforms benefit, but mobile-focused platforms (TikTok, Instagram) see biggest gains

### 3. "Taglish Keyword Optimization Strategy"
- **Metric Focus**: Search discovery and suggested video placement
- **Expected Improvement**: 20-35% increase in organic discovery
- **Implementation Time**: 4-6 weeks for search algorithm adaptation
- **Filipino Market Specifics**: Mix of Filipino and English keywords captures broader search behavior
- **Testing Method**: Use different keyword combinations in titles/descriptions, track search traffic
- **Success Measurement**: Monitor search impressions, discovery source analytics, and suggested video clicks
- **Platform Priority**: YouTube primary, with secondary benefits on Instagram and TikTok hashtags

### 4. "Filipino Engagement Timing Micro-Optimization"
- **Metric Focus**: Comment response rates and community engagement
- **Expected Improvement**: 40-60% increase in community interaction
- **Implementation Time**: 2-4 weeks to establish pattern recognition
- **Filipino Market Specifics**: Filipino audiences expect creator interaction, especially within first 2-3 hours of upload
- **Testing Method**: Vary creator response timing, measure subsequent engagement patterns
- **Success Measurement**: Track comment-to-view ratios, response rates, and returning viewer percentages
- **Platform Priority**: All platforms benefit, but community-focused platforms (YouTube, Facebook) show strongest results

### 5. "Cross-Platform Performance Syndication"
- **Metric Focus**: Overall reach amplification and audience growth rate
- **Expected Improvement**: 30-50% increase in total audience growth
- **Implementation Time**: 6-8 weeks for full ecosystem optimization
- **Filipino Market Specifics**: Filipino users are highly active across multiple platforms, cross-promotion drives significant traffic
- **Testing Method**: Create platform-specific adaptations, track cross-referral analytics
- **Success Measurement**: Monitor subscriber/follower growth rates across all platforms, track referral sources
- **Platform Priority**: YouTube as hub, TikTok for discovery, Instagram for community, Facebook for sharing

---

*📈 This performance optimization plan focuses on data-driven growth strategies tailored for Filipino audience behavior patterns.*"""


def generate_content_ideas_report(user_profile):
    """
    Placeholder function for Content Ideas Report generation.
    
    Args:
        user_profile (dict): User profile information
        
    Returns:
        str: Placeholder report content
    """
    return "Placeholder for Content Ideas Report"


def generate_trend_analysis_report(user_profile):
    """
    Placeholder function for Trend Analysis Report generation.
    
    Args:
        user_profile (dict): User profile information
        
    Returns:
        str: Placeholder report content
    """
    return "Placeholder for Trend Analysis Report"


def generate_competitor_analysis_report(user_profile):
    """
    Placeholder function for Competitor Analysis Report generation.
    
    Args:
        user_profile (dict): User profile information
        
    Returns:
        str: Placeholder report content
    """
    return "Placeholder for Competitor Analysis Report"


# Example usage and testing
if __name__ == "__main__":
    # Test user profile
    test_user_profile = {
        "persona": {"id": "tech", "name": "테크 크리에이터", "emoji": "💻"},
        "interests": ["mechanical keyboards", "coding", "gadgets"],
        "budget": "₱5,000-15,000"
    }
    
    # Test all report types
    report_types = [
        "content_strategy",
        "monetization", 
        "performance_optimization",
        "content_ideas",
        "trend_analysis",
        "competitor_analysis",
        "unknown_type"
    ]
    
    print("=== Report Dispatcher Test ===")
    for report_type in report_types:
        print(f"\n📊 Testing report_type: '{report_type}'")
        result = generate_specialized_report(test_user_profile, report_type)
        print(f"✅ Result: {result}")