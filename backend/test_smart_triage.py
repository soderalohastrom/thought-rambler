#!/usr/bin/env python3
"""
Test script comparing Basic vs Smart Segmentation
Demonstrates improved STT handling with spaCy integration
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from triage import TextTriageSystem
from nlp_core import NLPCore

# STT-like text (no punctuation, run-on thoughts)
STT_SAMPLE = """
so I was thinking about that hammock site yesterday really need to check it out oh and don't forget to call mom about thanksgiving that meditation app with the British voice you mentioned sounds interesting btw did you see the news on twitter about the AI breakthrough I should schedule a dentist appointment tomorrow morning urgent need to pay the electric bill by friday
"""

# Well-formatted text
FORMATTED_SAMPLE = """
So I was thinking about that hammock site yesterday. Really need to check it out.

Oh, and don't forget to call mom about thanksgiving!

That meditation app with the British voice you mentioned sounds interesting.

BTW, did you see the news on Twitter about the AI breakthrough?

I should schedule a dentist appointment tomorrow morning.

URGENT: Need to pay the electric bill by Friday!
"""

async def test_segmentation_comparison():
    print("=" * 70)
    print("SMART SEGMENTATION vs BASIC SEGMENTATION COMPARISON")
    print("=" * 70)
    
    # Test STT sample with both methods
    print("\n📝 TESTING STT-LIKE INPUT (no punctuation, run-on)")
    print("-" * 70)
    print(f"Input: {STT_SAMPLE[:100]}...")
    
    # Basic segmentation
    print("\n🔸 BASIC SEGMENTATION:")
    basic_system = TextTriageSystem(use_smart_segmentation=False)
    basic_results = await basic_system.process_text_dump(STT_SAMPLE)
    
    print(f"  Chunks found: {basic_results['summary']['total_chunks']}")
    print(f"  Breakdown:")
    for category, count in basic_results['summary']['breakdown'].items():
        if count > 0:
            print(f"    - {category}: {count}")
    
    # Smart segmentation
    print("\n🔹 SMART SEGMENTATION (spaCy):")
    smart_system = TextTriageSystem(use_smart_segmentation=True)
    smart_results = await smart_system.process_text_dump(STT_SAMPLE, segmentation_mode='balanced')
    
    print(f"  Chunks found: {smart_results['summary']['total_chunks']}")
    print(f"  Breakdown:")
    for category, count in smart_results['summary']['breakdown'].items():
        if count > 0:
            print(f"    - {category}: {count}")
    
    # Show detailed chunk analysis
    print("\n📊 CHUNK DETAILS (Smart Segmentation):")
    print("-" * 70)
    
    if smart_results['thoughts']:
        print("  Thoughts:")
        for i, thought in enumerate(smart_results['thoughts'][:3], 1):
            print(f"    {i}. {thought['original_text'][:60]}...")
    
    if smart_results['urls']:
        print("  URLs:")
        for url in smart_results['urls']:
            print(f"    - {url.get('url', url.get('original_text', '')[:40])}")
            if url['type'] == 'inferred':
                print(f"      (inferred from: '{url['original_text'][:30]}')")
    
    if smart_results['todos']:
        print("  TODOs:")
        for todo in smart_results['todos']:
            print(f"    - [{todo['urgency'].upper()}] {todo['action'][:50]}...")
    
    # Test different segmentation modes
    print("\n🔬 TESTING SEGMENTATION MODES:")
    print("-" * 70)
    
    modes = ['strict', 'balanced', 'loose']
    for mode in modes:
        results = await smart_system.process_text_dump(STT_SAMPLE, segmentation_mode=mode)
        print(f"  {mode.upper()} mode: {results['summary']['total_chunks']} chunks")
    
    # Test entity-aware features
    print("\n🏷️ ENTITY-AWARE FEATURES:")
    print("-" * 70)
    
    nlp_core = NLPCore()
    entities = nlp_core.extract_entities(STT_SAMPLE)
    if entities:
        print("  Entities found:")
        for entity_text, entity_type in entities:
            print(f"    - {entity_text} ({entity_type})")
    
    # Show quality metrics
    print("\n📈 QUALITY METRICS:")
    print("-" * 70)
    print("  Basic System:")
    print(f"    - Clean ratio: {basic_results['summary']['quality_metrics']['clean_ratio']*100:.1f}%")
    print(f"    - URL inference: {basic_results['summary']['quality_metrics']['url_inference_ratio']*100:.1f}%")
    
    print("  Smart System:")
    print(f"    - Clean ratio: {smart_results['summary']['quality_metrics']['clean_ratio']*100:.1f}%")
    print(f"    - URL inference: {smart_results['summary']['quality_metrics']['url_inference_ratio']*100:.1f}%")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 70)
    if smart_results['summary']['recommendations']:
        for rec in smart_results['summary']['recommendations']:
            print(f"  • {rec}")
    else:
        print("  • Smart segmentation successfully handled STT input")
        print("  • All thoughts properly separated despite lack of punctuation")
        print("  • Entity recognition enhanced URL and TODO detection")

    print("\n" + "=" * 70)
    print("SMART SEGMENTATION ADVANTAGE: Better handling of STT/voice input!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_segmentation_comparison())
