import json
from pathlib import Path
import time

def pandas_vs_json_assessment():
    """Quick assessment of pandas vs current JSON approach"""
    
    print("📊 PANDAS VS JSON PERFORMANCE ASSESSMENT")
    print("=" * 50)
    
    # Test current JSON approach speed
    zaak_files = list(Path('bronmateriaal-onbewerkt/zaak').glob('*.json'))
    vote_files = list(Path('bronmateriaal-onbewerkt/stemming').glob('*.json'))
    
    print(f"🧪 TEST 1: JSON Loading Speed")
    
    start_time = time.time()
    total_moties = 0
    total_votes = 0
    
    # Load all motion files
    for file in zaak_files:
        data = json.load(open(file, encoding='utf-8'))
        total_moties += len(data)
    
    # Load 5 vote files  
    for file in vote_files[:5]:
        data = json.load(open(file, encoding='utf-8'))
        total_votes += len(data)
    
    json_load_time = time.time() - start_time
    
    print(f"   ⏱️ JSON approach: {json_load_time:.3f}s")
    print(f"   📊 Loaded {total_moties} moties + {total_votes} votes")
    
    print(f"\n🎯 PANDAS ASSESSMENT:")
    print(f"   Current data size: 22.9 MB")
    print(f"   Records: ~10,000 total")
    print(f"   JSON speed: {json_load_time:.3f}s for partial load")
    
    print(f"\n✅ RECOMMENDATION:")
    if json_load_time < 1.0:
        print(f"   🏃‍♂️ KEEP JSON: Current approach is fast enough")
        print(f"   📋 Benefits: Simple, flexible, no dependencies")
        print(f"   ⚡ Performance: {json_load_time:.3f}s loading is excellent")
        
        print(f"\n🔄 CONSIDER PANDAS LATER FOR:")
        print(f"   🔗 Cross-dataset joins (motie + stemming)")
        print(f"   📈 Complex aggregations (party voting patterns)")
        print(f"   🏗️ Data transformation for web API")
        print(f"   📊 Analytics and reporting features")
        
    else:
        print(f"   🐼 CONSIDER PANDAS: Loading is slow")
        
    return json_load_time

def estimate_full_dataset_size():
    """Estimate full dataset size with all entity types"""
    
    print(f"\n📏 FULL DATASET SIZE ESTIMATION")
    print("=" * 40)
    
    current_size = 22.9  # MB
    
    estimates = {
        "Zaak (all types)": current_size * 2,  # Assume 2x more than just moties
        "Document entities": current_size * 1.5,  # Rich text content
        "Activiteit entities": current_size * 0.8,  # Activity logs
        "Complete dataset": current_size * 4.5  # Total estimate
    }
    
    for entity_type, size_mb in estimates.items():
        pandas_threshold = 100  # MB where pandas becomes useful
        recommendation = "JSON OK" if size_mb < pandas_threshold else "Consider Pandas"
        print(f"   {entity_type:20}: {size_mb:5.1f} MB - {recommendation}")
    
    print(f"\n🎯 CONCLUSION:")
    total_estimated = estimates["Complete dataset"]
    if total_estimated < 100:
        print(f"   ✅ Stick with JSON approach")
        print(f"   📊 Estimated full dataset: {total_estimated:.1f} MB")
        print(f"   🚀 JSON will remain fast and flexible")
    else:
        print(f"   🐼 Pandas recommended for full dataset")
        print(f"   📊 Estimated {total_estimated:.1f} MB may benefit from DataFrame operations")

if __name__ == "__main__":
    load_time = pandas_vs_json_assessment()
    estimate_full_dataset_size()
    
    print(f"\n💡 FINAL VERDICT:")
    print(f"   🎯 Current phase: Continue with JSON")  
    print(f"   🔄 Next phase: Evaluate pandas for data transformation")
    print(f"   🌐 Web API phase: Consider pandas for complex queries")