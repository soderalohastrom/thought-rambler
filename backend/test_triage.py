#!/usr/bin/env python3
"""
Test script for the Intelligent Text Triage System
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from triage import TextTriageSystem, URLInferenceEngine, GibberishDetector

async def test_triage_system():
    """Test the complete triage system with various input types"""
    
    print("=" * 60)
    print("INTELLIGENT TEXT TRIAGE SYSTEM - TEST SUITE")
    print("=" * 60)
    
    # Initialize system
    triage_system = TextTriageSystem()
    
    # Test data simulating an SMS dump
    test_text = """
    need milk and eggs from store

    https://amazon.com/dp/B08XYZ123

    that hammock site we looked at yesterday where they had the cool colors

    asdflkjasdf

    meeting at 3pm conf room 2 with Sarah about Q4 projections

    reddit.com/r/woodworking/comments/abc123

    don't forget to call mom about thanksgiving plans

    blue bird social media thing has breaking news about the election

    Remember to pay electric bill by Friday!!! URGENT

    kelleherinternational.com careers page might have that job

    jjjjjjjjjjjjj

    I should really update my resume this weekend and apply for new positions

    Check out github.com/awesome-python for learning resources
    
    !!!???....,,,

    The weather's been really strange lately like yesterday it was sunny

    That meditation app with the British voice

    😊😊😊😊😊😊

    Need to schedule dentist appointment - tooth still hurts

    """
    
    print("\nProcessing text dump...")
    print("-" * 40)
    
    # Process the text
    results = await triage_system.process_text_dump(test_text)
    
    # Display results
    print(f"\n📊 PROCESSING SUMMARY")
    print("-" * 40)
    print(f"Total chunks processed: {results['summary']['total_chunks']}")
    print(f"\nBreakdown:")
    for category, count in results['summary']['breakdown'].items():
        icon = {
            'thoughts': '🧠',
            'urls': '🔗',
            'todos': '✅',
            'quarantined': '🗑️',
            'salvaged': '♻️'
        }.get(category, '📝')
        print(f"  {icon} {category}: {count}")
    
    print(f"\n📈 QUALITY METRICS")
    print("-" * 40)
    metrics = results['summary']['quality_metrics']
    print(f"  Clean ratio: {metrics['clean_ratio']*100:.1f}%")
    print(f"  Salvage ratio: {metrics['salvage_ratio']*100:.1f}%")
    print(f"  URL inference ratio: {metrics['url_inference_ratio']*100:.1f}%")
    
    # Show detailed results
    print(f"\n🧠 THOUGHTS ({len(results['thoughts'])})")
    print("-" * 40)
    for thought in results['thoughts'][:3]:  # Show first 3
        print(f"  • {thought.get('original_text', '')[:60]}...")
    
    print(f"\n🔗 URLS ({len(results['urls'])})")
    print("-" * 40)
    for url in results['urls']:
        url_text = url.get('urls', [{}])[0].get('url', '') if 'urls' in url else url.get('url', '')
        confidence = url.get('confidence', 'unknown')
        url_type = url.get('type', 'unknown')
        print(f"  • [{url_type}] {url_text} (confidence: {confidence})")
        if url_type == 'inferred':
            print(f"    Original: '{url.get('original_text', '')}'")
    
    print(f"\n✅ TODOS ({len(results['todos'])})")
    print("-" * 40)
    for todo in results['todos']:
        urgency = todo.get('urgency', 'medium')
        urgency_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(urgency, '⚪')
        print(f"  {urgency_icon} {todo.get('action', '')[:60]}...")
    
    if results['salvaged']:
        print(f"\n♻️ SALVAGED ({len(results['salvaged'])})")
        print("-" * 40)
        for item in results['salvaged']:
            parts = item.get('salvaged_parts', [])
            print(f"  • Recovered {len(parts)} parts from: {item.get('original_text', '')[:30]}...")
    
    if results['quarantine']:
        print(f"\n🗑️ QUARANTINE ({len(results['quarantine'])})")
        print("-" * 40)
        for item in results['quarantine'][:3]:  # Show first 3
            text = item.get('original_text', '')[:20]
            issues = ', '.join(item.get('issues', []))[:40]
            print(f"  • '{text}...' - Issues: {issues}")
    
    # Recommendations
    if results['summary']['recommendations']:
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 40)
        for rec in results['summary']['recommendations']:
            print(f"  • {rec}")
    
    # Test individual components
    print(f"\n🔬 COMPONENT TESTS")
    print("-" * 40)
    
    # Test gibberish detection
    detector = GibberishDetector()
    test_cases = [
        "This is a normal sentence.",
        "asdflkjasdf",
        "meeting at 3pm",
        "!!!!????....",
        "Need to buy milk"
    ]
    
    print("\nGibberish Detection:")
    for text in test_cases:
        result = detector.analyze(text)
        status = "✅" if result['classification'] == 'high_quality' else "❌"
        print(f"  {status} '{text[:30]}' -> {result['classification']} ({result['quality_score']:.2f})")
    
    # Test URL inference
    url_engine = URLInferenceEngine()
    url_tests = [
        "that hammock site",
        "blue bird social media",
        "github python resources",
        "meditation app british voice"
    ]
    
    print("\nURL Inference:")
    for desc in url_tests:
        result = await url_engine.infer_url(desc)
        if result['url']:
            print(f"  🔗 '{desc}' -> {result['url']} ({result['confidence']})")
        else:
            print(f"  ❓ '{desc}' -> Could not infer")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_triage_system())
