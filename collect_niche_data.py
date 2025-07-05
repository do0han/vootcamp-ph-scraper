#!/usr/bin/env python3
"""
Comprehensive Niche Category Data Collection Script
니치 카테고리 데이터 수집 및 분석 스크립트
"""

import json
import sys
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project path
sys.path.append(str(Path(__file__).parent / "vootcamp_ph_scraper"))

from vootcamp_ph_scraper.scrapers.niche_category_scraper import NicheCategoryScraper
from vootcamp_ph_scraper.utils.product_tagger import ProductTagger

def collect_niche_category_data(products_per_category: int = 10, save_to_db: bool = False):
    """Collect data from all niche categories"""
    
    print("🎯 Starting Comprehensive Niche Category Data Collection")
    print("=" * 70)
    print(f"📊 Products per category: {products_per_category}")
    print(f"💾 Save to database: {save_to_db}")
    print()
    
    # Initialize scraper
    scraper = NicheCategoryScraper(use_undetected=True)
    
    collection_results = {}
    start_time = datetime.now()
    
    try:
        # Collect data for each category
        for i, category_key in enumerate(scraper.TARGET_CATEGORIES, 1):
            print(f"📂 [{i}/{len(scraper.TARGET_CATEGORIES)}] Processing: {category_key}")
            print("-" * 50)
            
            category_start = datetime.now()
            
            try:
                # Scrape category data
                products = scraper.scrape_lazada_niche_category(
                    category_key, 
                    limit=products_per_category
                )
                
                collection_results[category_key] = products
                
                # Category summary
                if products:
                    avg_relevance = sum(p.get('niche_relevance_score', 0) for p in products) / len(products)
                    high_relevance_count = sum(1 for p in products if p.get('niche_relevance_score', 0) > 50)
                    
                    print(f"✅ Collected {len(products)} products")
                    print(f"📊 Average relevance: {avg_relevance:.1f}/100")
                    print(f"🎯 High relevance products: {high_relevance_count}")
                    
                    # Show top 3 products
                    print("🏆 Top 3 products:")
                    for j, product in enumerate(products[:3], 1):
                        name = product.get('product_name', 'Unknown')[:40]
                        price = product.get('price_numeric', 0)
                        relevance = product.get('niche_relevance_score', 0)
                        print(f"   {j}. {name}... (₱{price:,} | Score: {relevance:.1f})")
                    
                    # Save to database if requested
                    if save_to_db:
                        success = scraper.save_to_database(products, category_key)
                        if success:
                            print("💾 Successfully saved to database")
                        else:
                            print("⚠️ Database save failed")
                else:
                    print("❌ No products collected")
                
                category_time = (datetime.now() - category_start).total_seconds()
                print(f"⏱️ Category completed in {category_time:.1f} seconds")
                print()
                
                # Wait between categories to avoid rate limiting
                if i < len(scraper.TARGET_CATEGORIES):
                    wait_time = 10
                    print(f"⏳ Waiting {wait_time} seconds before next category...")
                    time.sleep(wait_time)
                    print()
                
            except Exception as e:
                print(f"❌ Error processing {category_key}: {e}")
                collection_results[category_key] = []
                continue
        
        # Generate comprehensive report
        total_time = (datetime.now() - start_time).total_seconds()
        report = scraper.generate_collection_report(collection_results)
        
        print("🎉 Data Collection Completed!")
        print("=" * 50)
        print(f"⏱️ Total time: {total_time:.1f} seconds")
        print(f"📦 Total products: {report['total_products']}")
        print(f"📂 Categories processed: {report['categories_processed']}")
        print()
        
        return collection_results, report
        
    except Exception as e:
        print(f"❌ Critical error in data collection: {e}")
        return {}, {}
    
    finally:
        scraper.close()

def analyze_niche_data_coverage(collection_results: Dict[str, List[Dict[str, Any]]]):
    """Analyze the quality and coverage of collected niche data"""
    
    print("🔍 Analyzing Niche Data Coverage")
    print("=" * 50)
    
    tagger = ProductTagger()
    
    coverage_analysis = {
        'timestamp': datetime.now().isoformat(),
        'categories': {},
        'overall_metrics': {},
        'coverage_gaps': {},
        'quality_assessment': {}
    }
    
    total_products = 0
    total_high_relevance = 0
    category_performance = {}
    
    for category_key, products in collection_results.items():
        if not products:
            continue
        
        print(f"\n📂 Analyzing {category_key}:")
        
        # Basic metrics
        num_products = len(products)
        total_products += num_products
        
        # Relevance analysis
        relevance_scores = [p.get('niche_relevance_score', 0) for p in products]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        high_relevance_products = sum(1 for score in relevance_scores if score > 50)
        total_high_relevance += high_relevance_products
        
        # Confidence analysis
        confidence_counts = {}
        for product in products:
            confidence = product.get('tag_confidence', 'none')
            confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
        
        # Price analysis
        prices = [p.get('price_numeric') for p in products if p.get('price_numeric')]
        avg_price = sum(prices) / len(prices) if prices else 0
        
        # Keyword diversity analysis
        all_keywords = []
        for product in products:
            tags = product.get('hierarchical_tags', [])
            for tag in tags:
                if tag.get('category') == category_key:
                    all_keywords.extend(tag.get('matched_keywords', []))
        
        unique_keywords = len(set(all_keywords))
        
        category_analysis = {
            'products_found': num_products,
            'average_relevance_score': round(avg_relevance, 2),
            'high_relevance_products': high_relevance_products,
            'high_relevance_percentage': round((high_relevance_products / num_products) * 100, 2),
            'confidence_distribution': confidence_counts,
            'average_price': round(avg_price, 2),
            'keyword_diversity': unique_keywords,
            'top_products': [
                {
                    'name': p.get('product_name', 'Unknown')[:50],
                    'price': p.get('price_numeric'),
                    'relevance_score': p.get('niche_relevance_score', 0),
                    'confidence': p.get('tag_confidence', 'none')
                }
                for p in sorted(products, key=lambda x: x.get('niche_relevance_score', 0), reverse=True)[:3]
            ]
        }
        
        coverage_analysis['categories'][category_key] = category_analysis
        category_performance[category_key] = avg_relevance
        
        print(f"   📦 Products: {num_products}")
        print(f"   🎯 Avg Relevance: {avg_relevance:.1f}/100")
        print(f"   🏆 High Relevance: {high_relevance_products}/{num_products} ({(high_relevance_products/num_products)*100:.1f}%)")
        print(f"   💰 Avg Price: ₱{avg_price:,.0f}")
        print(f"   🏷️ Keyword Diversity: {unique_keywords} unique keywords")
    
    # Overall metrics
    overall_high_relevance_rate = (total_high_relevance / total_products) * 100 if total_products else 0
    best_category = max(category_performance.items(), key=lambda x: x[1]) if category_performance else (None, 0)
    worst_category = min(category_performance.items(), key=lambda x: x[1]) if category_performance else (None, 0)
    
    coverage_analysis['overall_metrics'] = {
        'total_products_collected': total_products,
        'total_high_relevance_products': total_high_relevance,
        'overall_high_relevance_rate': round(overall_high_relevance_rate, 2),
        'best_performing_category': best_category[0] if best_category[0] else None,
        'best_category_score': round(best_category[1], 2) if best_category[0] else 0,
        'worst_performing_category': worst_category[0] if worst_category[0] else None,
        'worst_category_score': round(worst_category[1], 2) if worst_category[0] else 0,
        'average_products_per_category': round(total_products / len(collection_results), 2) if collection_results else 0
    }
    
    print(f"\n📊 OVERALL ANALYSIS:")
    print(f"   🎯 Total Products: {total_products}")
    print(f"   🏆 High Relevance Rate: {overall_high_relevance_rate:.1f}%")
    print(f"   🥇 Best Category: {best_category[0]} ({best_category[1]:.1f})")
    print(f"   📉 Worst Category: {worst_category[0]} ({worst_category[1]:.1f})")
    
    # Coverage gaps analysis
    print(f"\n🔍 Coverage Gap Analysis:")
    
    coverage_gaps = {}
    for category_key in collection_results.keys():
        category_info = tagger.get_category_info(category_key)
        if not category_info:
            continue
        
        expected_keywords = set(
            category_info.get('primary_keywords', []) +
            category_info.get('product_keywords', [])[:10]  # Top 10 product keywords
        )
        
        products = collection_results[category_key]
        found_keywords = set()
        for product in products:
            tags = product.get('hierarchical_tags', [])
            for tag in tags:
                if tag.get('category') == category_key:
                    found_keywords.update(tag.get('matched_keywords', []))
        
        missing_keywords = expected_keywords - found_keywords
        coverage_rate = ((len(expected_keywords) - len(missing_keywords)) / len(expected_keywords)) * 100 if expected_keywords else 0
        
        coverage_gaps[category_key] = {
            'expected_keywords_count': len(expected_keywords),
            'found_keywords_count': len(found_keywords),
            'missing_keywords_count': len(missing_keywords),
            'coverage_rate': round(coverage_rate, 2),
            'missing_keywords': list(missing_keywords)[:5]  # Top 5 missing
        }
        
        print(f"   📂 {category_key}: {coverage_rate:.1f}% keyword coverage")
        if missing_keywords:
            print(f"      Missing: {', '.join(list(missing_keywords)[:3])}...")
    
    coverage_analysis['coverage_gaps'] = coverage_gaps
    
    # Quality assessment
    quality_score = 0
    if overall_high_relevance_rate > 60:
        quality_score += 40
    elif overall_high_relevance_rate > 40:
        quality_score += 25
    elif overall_high_relevance_rate > 20:
        quality_score += 10
    
    if total_products >= 50:
        quality_score += 30
    elif total_products >= 30:
        quality_score += 20
    elif total_products >= 15:
        quality_score += 10
    
    avg_coverage_rate = sum(gap['coverage_rate'] for gap in coverage_gaps.values()) / len(coverage_gaps) if coverage_gaps else 0
    if avg_coverage_rate > 70:
        quality_score += 30
    elif avg_coverage_rate > 50:
        quality_score += 20
    elif avg_coverage_rate > 30:
        quality_score += 10
    
    quality_assessment = {
        'overall_quality_score': min(100, quality_score),
        'data_completeness': 'excellent' if total_products >= 50 else 'good' if total_products >= 30 else 'fair' if total_products >= 15 else 'poor',
        'relevance_quality': 'excellent' if overall_high_relevance_rate > 60 else 'good' if overall_high_relevance_rate > 40 else 'fair' if overall_high_relevance_rate > 20 else 'poor',
        'keyword_coverage': 'excellent' if avg_coverage_rate > 70 else 'good' if avg_coverage_rate > 50 else 'fair' if avg_coverage_rate > 30 else 'poor'
    }
    
    coverage_analysis['quality_assessment'] = quality_assessment
    
    print(f"\n🏆 QUALITY ASSESSMENT:")
    print(f"   📊 Overall Quality Score: {quality_score}/100")
    print(f"   📦 Data Completeness: {quality_assessment['data_completeness']}")
    print(f"   🎯 Relevance Quality: {quality_assessment['relevance_quality']}")
    print(f"   🏷️ Keyword Coverage: {quality_assessment['keyword_coverage']}")
    
    return coverage_analysis

def generate_final_report(collection_results: Dict[str, List[Dict[str, Any]]], 
                         collection_report: Dict[str, Any],
                         coverage_analysis: Dict[str, Any]):
    """Generate comprehensive final report"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create detailed report
    final_report = {
        'metadata': {
            'report_type': 'niche_category_data_collection',
            'timestamp': datetime.now().isoformat(),
            'collection_date': timestamp,
            'version': '1.0'
        },
        'executive_summary': {
            'total_categories_targeted': len(NicheCategoryScraper.TARGET_CATEGORIES),
            'total_products_collected': sum(len(products) for products in collection_results.values()),
            'successful_categories': len([cat for cat, products in collection_results.items() if products]),
            'average_products_per_category': round(sum(len(products) for products in collection_results.values()) / len(collection_results), 2) if collection_results else 0,
            'data_quality_score': coverage_analysis.get('quality_assessment', {}).get('overall_quality_score', 0)
        },
        'collection_results': collection_results,
        'collection_report': collection_report,
        'coverage_analysis': coverage_analysis,
        'recommendations': []
    }
    
    # Generate recommendations
    recommendations = []
    
    total_products = final_report['executive_summary']['total_products_collected']
    quality_score = final_report['executive_summary']['data_quality_score']
    
    if total_products < 30:
        recommendations.append({
            'priority': 'high',
            'category': 'data_collection',
            'issue': 'Low product count',
            'recommendation': 'Increase scraping frequency or expand search terms',
            'target': 'Collect at least 50 products total across all categories'
        })
    
    if quality_score < 70:
        recommendations.append({
            'priority': 'medium',
            'category': 'data_quality',
            'issue': 'Low quality score',
            'recommendation': 'Improve keyword matching and relevance scoring',
            'target': 'Achieve quality score above 80'
        })
    
    # Category-specific recommendations
    for category_key, analysis in coverage_analysis.get('categories', {}).items():
        if analysis['high_relevance_percentage'] < 50:
            recommendations.append({
                'priority': 'medium',
                'category': 'category_improvement',
                'issue': f'Low relevance in {category_key}',
                'recommendation': 'Refine search terms and improve keyword matching',
                'target': f'Achieve >60% high relevance for {category_key}'
            })
    
    final_report['recommendations'] = recommendations
    
    # Save report files
    reports_dir = Path('niche_data_reports')
    reports_dir.mkdir(exist_ok=True)
    
    # JSON report
    json_file = reports_dir / f'niche_collection_report_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    # Markdown summary report
    md_file = reports_dir / f'niche_collection_summary_{timestamp}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Niche Category Data Collection Report
## {datetime.now().strftime("%B %d, %Y")}

### Executive Summary
- **Total Products Collected**: {final_report['executive_summary']['total_products_collected']}
- **Categories Processed**: {final_report['executive_summary']['successful_categories']}/{final_report['executive_summary']['total_categories_targeted']}
- **Data Quality Score**: {final_report['executive_summary']['data_quality_score']}/100
- **Average Products per Category**: {final_report['executive_summary']['average_products_per_category']}

### Category Breakdown
""")
        
        for category_key, analysis in coverage_analysis.get('categories', {}).items():
            f.write(f"""
#### {category_key.replace('_', ' ').title()}
- **Products Found**: {analysis['products_found']}
- **Average Relevance**: {analysis['average_relevance_score']}/100
- **High Relevance Products**: {analysis['high_relevance_products']} ({analysis['high_relevance_percentage']}%)
- **Average Price**: ₱{analysis['average_price']:,.0f}
- **Keyword Diversity**: {analysis['keyword_diversity']} unique keywords

**Top Products:**
""")
            for i, product in enumerate(analysis['top_products'], 1):
                f.write(f"{i}. {product['name']} - ₱{product['price']:,} (Score: {product['relevance_score']})\n")
            f.write("\n")
        
        f.write(f"""
### Sample Products (Top 5 from each category)
""")
        
        for category_key, products in collection_results.items():
            if not products:
                continue
            
            f.write(f"\n#### {category_key.replace('_', ' ').title()}\n")
            
            # Sort by relevance score and take top 5
            top_products = sorted(products, key=lambda x: x.get('niche_relevance_score', 0), reverse=True)[:5]
            
            for i, product in enumerate(top_products, 1):
                name = product.get('product_name', 'Unknown')
                price = product.get('price_numeric', 0)
                relevance = product.get('niche_relevance_score', 0)
                confidence = product.get('tag_confidence', 'none')
                
                # Get hierarchical tags
                tags = []
                for tag in product.get('hierarchical_tags', []):
                    if tag.get('category') == category_key:
                        tags.append(tag.get('full_path', ''))
                        break
                
                f.write(f"""
**{i}. {name}**
- Price: ₱{price:,}
- Relevance Score: {relevance}/100
- Tag Confidence: {confidence}
- Category Path: {tags[0] if tags else 'Not tagged'}
- Keywords: {', '.join(product.get('hierarchical_tags', [{}])[0].get('matched_keywords', [])[:3]) if product.get('hierarchical_tags') else 'None'}
""")
        
        f.write(f"""
### Recommendations
""")
        for rec in recommendations:
            f.write(f"- **{rec['priority'].upper()}**: {rec['recommendation']} (Target: {rec['target']})\n")
    
    print(f"\n📋 Final Report Generated:")
    print(f"   📄 Detailed JSON: {json_file}")
    print(f"   📝 Summary Markdown: {md_file}")
    
    return final_report

def main():
    """Main execution function"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting Niche Category Data Pipeline")
    print("=" * 60)
    
    # Configuration
    PRODUCTS_PER_CATEGORY = 8  # Reduced for faster testing
    SAVE_TO_DATABASE = False  # Set to True to save to Supabase
    
    try:
        # Step 1: Collect data
        print("📊 Phase 1: Data Collection")
        collection_results, collection_report = collect_niche_category_data(
            products_per_category=PRODUCTS_PER_CATEGORY,
            save_to_db=SAVE_TO_DATABASE
        )
        
        if not collection_results:
            print("❌ No data collected. Exiting.")
            return
        
        # Step 2: Analyze coverage
        print("\n🔍 Phase 2: Coverage Analysis")
        coverage_analysis = analyze_niche_data_coverage(collection_results)
        
        # Step 3: Generate final report
        print("\n📋 Phase 3: Report Generation")
        final_report = generate_final_report(
            collection_results, 
            collection_report, 
            coverage_analysis
        )
        
        # Summary
        print(f"\n🎉 NICHE DATA PIPELINE COMPLETED!")
        print("=" * 50)
        print(f"📦 Total Products: {final_report['executive_summary']['total_products_collected']}")
        print(f"🏆 Quality Score: {final_report['executive_summary']['data_quality_score']}/100")
        print(f"📂 Categories: {final_report['executive_summary']['successful_categories']}/{final_report['executive_summary']['total_categories_targeted']}")
        print(f"📋 Recommendations: {len(final_report['recommendations'])}")
        
        return final_report
        
    except Exception as e:
        print(f"❌ Critical error in main execution: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()