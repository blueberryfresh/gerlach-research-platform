import json

with open('personality_validation_20251228_084335.json', encoding='utf-8') as f:
    data = json.load(f)

self_tests = [r for r in data['detailed_results'] if r['personality_type'] == 'self_centred']

print("Self-Centred Responses with Negative Markers:")
print("=" * 80)

for idx, test in enumerate(self_tests, 1):
    if test['analysis']['negative_count'] > 0:
        print(f"\nTest {idx}: {test['prompt'][:70]}")
        print(f"Response: {test['response'][:250]}...")
        print(f"Negative markers found: {test['analysis']['negative_markers_found']}")
        print(f"Positive markers found: {test['analysis']['positive_markers_found'][:8]}")
        print(f"Score: {test['analysis']['authenticity_score']:.3f}")
        print("-" * 80)
