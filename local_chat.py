# pip install llama-cpp-python
# pip install cmake
# pip install ctransformers

# from ctransformers import AutoModelForCausalLM

# # --- CONFIGURATION ---
# # Replace this with the exact name of the file you downloaded
# MODEL_FILE = "./Phi-3-mini-4k-instruct-q4.gguf" 
# MODEL_TYPE = "phi3" # This tells the library to use Phi-3 logic

# print(f"Loading {MODEL_FILE}...")

# try:
#     # 1. Load the SLM
#     llm = AutoModelForCausalLM.from_pretrained(
#         MODEL_FILE, 
#         model_type=MODEL_TYPE,
#         context_length=2048,
#         threads=4 # Number of CPU cores to use
#     )
    
#     print("\n✅ Model Loaded Successfully!")
#     print("Type your message and press Enter. Type 'exit' to quit.\n")

#     # 2. Chat Loop
#     while True:
#         user_input = input("You: ")
        
#         if user_input.lower() in ["exit", "quit"]:
#             print("Closing chat...")
#             break
            
#         if not user_input.strip():
#             continue

#         # Phi-3 specific prompt format for best results
#         prompt = f"<|user|>\n{user_input}<|end|>\n<|assistant|>\n"

#         print("AI: ", end="", flush=True)
        
#         # 3. Stream the response word-by-word
#         for text in llm(prompt, stream=True):
#             print(text, end="", flush=True)
        
#         print("\n" + "-"*30)

# except Exception as e:
#     print(f"\n❌ Error: {e}")
#     print("Make sure the .gguf file is in the same folder as this script.")



import os
from ctransformers import AutoModelForCausalLM

# Use the exact name you have now
MODEL_FILE = "model.gguf"

print(f"🔄 Attempting to load: {MODEL_FILE}")

try:
    # We remove 'model_type' and let it auto-infer, 
    # or try 'gpt_bigcode' / 'llama' if 'phi3' fails.
    llm = AutoModelForCausalLM.from_pretrained(
        MODEL_FILE,
        model_type="phi3", # Try changing this to "llama" if it fails again
        context_length=2048,
        hf=True # This helps with some GGUF versions
    )
    
    print("✅ Success! Type your message:")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]: break
        
        # Simple prompt format
        prompt = f"User: {user_input}\nAssistant:"
        
        print("\nAI: ", end="", flush=True)
        for text in llm(prompt, stream=True):
            print(text, end="", flush=True)
        print("\n")

except Exception as e:
    print(f"❌ Failed again: {e}")
    print("\n--- QUICK FIX ---")
    print("If this fails, your GGUF file is likely a 'v3' format which ctransformers doesn't support.")