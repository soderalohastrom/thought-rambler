import requests
import json
from sample_data import get_sample_ramble, get_all_samples

def test_api_endpoint(base_url="http://localhost:8000"):
    """Test the thought parsing API endpoint"""
    print(f"Testing API at {base_url}")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test with sample data
    test_cases = [
        {"size": "small", "text": get_sample_ramble("small")},
        {"size": "medium", "text": get_sample_ramble("medium")},
        {"size": "large", "text": get_sample_ramble("large")[:500]}  # Truncate for testing
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['size'].upper()} ramble ---")
        print(f"Input length: {len(test_case['text'])} characters")
        print(f"Input preview: {test_case['text'][:100]}...")
        
        payload = {
            "text": test_case['text'],
            "provider": "openai",
            "model": "gpt-3.5-turbo"
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/parse-thoughts",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['total_chunks']} chunks detected")
                print(f"Processing time: {result['processing_time']:.3f} seconds")
                
                for i, chunk in enumerate(result['chunks'][:3], 1):  # Show first 3 chunks
                    print(f"  Chunk {i}: {chunk['text'][:80]}...")
                    print(f"    Keywords: {chunk['topic_keywords']}")
                    print(f"    Sentiment: {chunk['sentiment']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_endpoint()
