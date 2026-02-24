"""
Quick test to see if response generation is working
"""
from composite_big5_llms import CompositeBig5LLMManager

print("Initializing manager...")
manager = CompositeBig5LLMManager()

print("\nTesting single response...")
question = "How do you handle conflicts?"
print(f"Question: {question}")

print("\nGetting response from Collaborator...")
response = manager.get_response("collaborator", question)
print(f"Response type: {type(response)}")
print(f"Response length: {len(response)}")
print(f"Response content: '{response}'")
print(f"Response repr: {repr(response)}")

print("\n" + "="*70)
print("Testing get_all_responses...")
responses = manager.get_all_responses(question)
print(f"Number of responses: {len(responses)}")

for key, resp in responses.items():
    print(f"\n{key}:")
    print(f"  Type: {type(resp)}")
    print(f"  Length: {len(resp)}")
    print(f"  Content: '{resp}'")
    print(f"  Repr: {repr(resp)}")
