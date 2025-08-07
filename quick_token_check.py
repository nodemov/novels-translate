#!/usr/bin/env python3
"""
Quick Token Check Script
A simple way to check token usage for your novel translation chunks
"""

import tiktoken
import sys
import os

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken"""
    try:
        tokenizer = tiktoken.get_encoding("cl100k_base")
        return len(tokenizer.encode(text))
    except:
        # Fallback: approximate count
        return len(text) // 4

def analyze_chunk(text: str) -> dict:
    """Analyze a text chunk for translation"""
    # Your prompt template
    prompt_template = """คุณคือนักแปลมืออาชีพที่มีความเชี่ยวชาญในการแปลนิยาย Wuxia/Xianxia จีนจากภาษาอังกฤษเป็นภาษาไทย

กรุณาแปลเนื้อหาต่อไปนี้จากภาษาอังกฤษเป็นภาษาไทย:

{text}

หลักการแปล:
1. รักษาความหมายและบรรยากาศของนิยาย Wuxia/Xianxia ไว้
2. ใช้ภาษาไทยที่อ่านง่ายและไหลลื่น
3. แปลศัพท์เฉพาะ: Cultivation→การเพาะพิถี, Qi→ชี่, Dantian→ต้านเถียน, Breakthrough→ก้าวกระโดด, Elder→ผู้อาวุโส, Young Master→คุณชายหนุ่ม
4. คงชื่อตัวละครและสถานที่เฉพาะไว้
5. ปรับการใช้ภาษาให้เหมาะสมกับผู้อ่านไทย
6. รักษาบุคลิกและสไตล์การพูดของตัวละครไว้

การแปล:"""
    
    full_prompt = prompt_template.format(text=text)
    
    # Token counts
    system_tokens = count_tokens(prompt_template.replace("{text}", ""))
    input_tokens = count_tokens(text)
    total_input_tokens = count_tokens(full_prompt)
    estimated_output_tokens = int(input_tokens * 1.2)  # Thai output is usually longer
    total_tokens = total_input_tokens + estimated_output_tokens
    
    return {
        "text_length": len(text),
        "system_tokens": system_tokens,
        "input_tokens": input_tokens,
        "total_input_tokens": total_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "total_estimated_tokens": total_tokens
    }

def main():
    if len(sys.argv) > 1:
        # File provided as argument
        filename = sys.argv[1]
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Analyzing file: {filename}")
        else:
            print(f"File not found: {filename}")
            return
    else:
        # Interactive mode
        print("Quick Token Checker")
        print("==================")
        text = input("Enter text to analyze (or filename): ").strip()
        
        if os.path.exists(text):
            with open(text, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Analyzing file content...")
    
    analysis = analyze_chunk(text)
    
    print(f"\n📊 Token Analysis:")
    print(f"Text length: {analysis['text_length']:,} characters")
    print(f"System prompt: {analysis['system_tokens']} tokens")
    print(f"Input text: {analysis['input_tokens']} tokens")
    print(f"Total input: {analysis['total_input_tokens']} tokens")
    print(f"Estimated output: {analysis['estimated_output_tokens']} tokens")
    print(f"Total estimated: {analysis['total_estimated_tokens']} tokens")
    
    # Context limits
    current_limit = 16384  # Updated limit
    max_limit = 131072     # Model maximum
    
    print(f"\n🎯 Context Analysis:")
    print(f"Current context limit: {current_limit:,} tokens")
    print(f"Model maximum: {max_limit:,} tokens")
    
    if analysis['total_estimated_tokens'] <= current_limit:
        print("✅ Within current context limit")
    elif analysis['total_estimated_tokens'] <= max_limit:
        print("⚠️  Exceeds current limit but within model maximum")
        print(f"   Consider increasing num_ctx to {analysis['total_estimated_tokens'] + 1000}")
    else:
        print("❌ Exceeds model maximum!")
        reduction_factor = max_limit / analysis['total_estimated_tokens']
        suggested_size = int(analysis['text_length'] * reduction_factor * 0.8)
        print(f"   Reduce chunk size to approximately {suggested_size} characters")
    
    # Chunk size recommendations
    if analysis['text_length'] > 2000:
        optimal_chunks = analysis['total_estimated_tokens'] // current_limit + 1
        chunk_size = analysis['text_length'] // optimal_chunks
        print(f"\n💡 Recommendation:")
        print(f"Split into {optimal_chunks} chunks of ~{chunk_size} characters each")

if __name__ == "__main__":
    main()
