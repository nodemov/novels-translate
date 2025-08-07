#!/usr/bin/env python3
"""
Token Checker and Optimizer for Novel Translator
This utility helps you check token usage and optimize settings for your Ollama translation model.
"""

import requests
import json
import tiktoken
import time
from typing import Dict, List, Tuple, Optional
import os

class TokenChecker:
    def __init__(self, model_name="scb10x/typhoon-translate-4b", ollama_url="http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        
        # Model specifications from ollama show
        self.model_specs = {
            "context_length": 131072,  # Maximum context length
            "current_num_ctx": 8192,   # Current setting from model
            "parameter_size": "3.9B",
            "quantization": "Q4_K_M"
        }
        
        # Initialize tokenizer (approximate - using GPT tokenizer as estimation)
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            print("Warning: Could not load tiktoken, using approximate token counting")
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters for Thai/English mixed text
            return len(text) // 4
    
    def get_model_info(self) -> Dict:
        """Get detailed model information from Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/show",
                json={"name": self.model_name},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting model info: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return {}
    
    def analyze_prompt_tokens(self, text: str) -> Dict:
        """Analyze token usage for a translation prompt"""
        # Your current prompt template
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
        
        # Count tokens for different parts
        system_tokens = self.count_tokens(prompt_template.replace("{text}", ""))
        input_tokens = self.count_tokens(text)
        total_input_tokens = self.count_tokens(full_prompt)
        
        return {
            "system_prompt_tokens": system_tokens,
            "input_text_tokens": input_tokens,
            "total_input_tokens": total_input_tokens,
            "estimated_output_tokens": input_tokens * 1.2,  # Thai tends to be slightly longer
            "total_estimated_tokens": total_input_tokens + (input_tokens * 1.2)
        }
    
    def test_token_limits(self, test_text: str) -> Dict:
        """Test actual token usage with the model"""
        print("Testing token usage with actual model...")
        
        prompt = f"""คุณคือนักแปลมืออาชีพที่มีความเชี่ยวชาญในการแปลนิยาย Wuxia/Xianxia จีนจากภาษาอังกฤษเป็นภาษาไทย

กรุณาแปลเนื้อหาต่อไปนี้จากภาษาอังกฤษเป็นภาษาไทย:

{test_text}

หลักการแปล:
1. รักษาความหมายและบรรยากาศของนิยาย Wuxia/Xianxia ไว้
2. ใช้ภาษาไทยที่อ่านง่ายและไหลลื่น
3. แปลศัพท์เฉพาะ: Cultivation→การเพาะพิถี, Qi→ชี่, Dantian→ต้านเถียน, Breakthrough→ก้าวกระโดด, Elder→ผู้อาวุโส, Young Master→คุณชายหนุ่ม
4. คงชื่อตัวละครและสถานที่เฉพาะไว้
5. ปรับการใช้ภาษาให้เหมาะสมกับผู้อ่านไทย
6. รักษาบุคลิกและสไตล์การพูดของตัวละครไว้

การแปล:"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 2000,
                "num_ctx": 8192  # Current setting
            }
        }
        
        start_time = time.time()
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response_time": end_time - start_time,
                    "input_length": len(test_text),
                    "output_length": len(result.get('response', '')),
                    "estimated_input_tokens": self.count_tokens(prompt),
                    "estimated_output_tokens": self.count_tokens(result.get('response', '')),
                    "response": result.get('response', '')[:200] + "..." if len(result.get('response', '')) > 200 else result.get('response', '')
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def optimize_settings(self, target_chunk_size: int = 2000) -> Dict:
        """Suggest optimal settings based on model capabilities"""
        analysis = self.analyze_prompt_tokens("x" * target_chunk_size)
        
        recommendations = {
            "current_settings": {
                "chunk_size": target_chunk_size,
                "max_tokens": 4000,
                "temperature": 0.3,
                "top_p": 0.9,
                "num_ctx": self.model_specs["current_num_ctx"]
            },
            "recommended_settings": {},
            "warnings": [],
            "optimizations": []
        }
        
        total_tokens = analysis["total_estimated_tokens"]
        
        # Check if we're exceeding context length
        if total_tokens > self.model_specs["current_num_ctx"]:
            recommendations["warnings"].append(
                f"Estimated total tokens ({total_tokens}) exceeds current context length ({self.model_specs['current_num_ctx']})"
            )
            
            # Suggest smaller chunk size
            safe_chunk_size = int(target_chunk_size * (self.model_specs["current_num_ctx"] / total_tokens) * 0.8)
            recommendations["recommended_settings"]["chunk_size"] = safe_chunk_size
            recommendations["optimizations"].append(f"Reduce chunk size to {safe_chunk_size} for safe processing")
        
        # Suggest optimal max_tokens
        estimated_output = analysis["estimated_output_tokens"]
        if estimated_output > 4000:
            recommendations["warnings"].append(f"Estimated output tokens ({estimated_output}) may exceed max_tokens (4000)")
            recommendations["recommended_settings"]["max_tokens"] = int(estimated_output * 1.2)
        
        # Suggest optimal num_ctx if we can use more
        max_possible_ctx = min(self.model_specs["context_length"], 32768)  # Practical limit
        if total_tokens * 2 < max_possible_ctx:
            recommendations["recommended_settings"]["num_ctx"] = max_possible_ctx
            recommendations["optimizations"].append(f"Increase num_ctx to {max_possible_ctx} for better context handling")
        
        # Temperature and top_p recommendations
        recommendations["recommended_settings"]["temperature"] = 0.2  # Lower for more consistent translation
        recommendations["recommended_settings"]["top_p"] = 0.85      # Slightly lower for better quality
        
        return recommendations
    
    def benchmark_settings(self, test_cases: List[str], settings_list: List[Dict]) -> Dict:
        """Benchmark different settings with test cases"""
        results = {}
        
        for i, settings in enumerate(settings_list):
            setting_name = f"Setting_{i+1}"
            results[setting_name] = {
                "settings": settings,
                "test_results": []
            }
            
            print(f"\nTesting {setting_name}: {settings}")
            
            for j, test_text in enumerate(test_cases):
                print(f"  Test case {j+1}...")
                result = self.test_with_settings(test_text, settings)
                results[setting_name]["test_results"].append(result)
                time.sleep(1)  # Avoid overwhelming the model
        
        return results
    
    def test_with_settings(self, text: str, settings: Dict) -> Dict:
        """Test translation with specific settings"""
        prompt = f"""คุณคือนักแปลมืออาชีพที่มีความเชี่ยวชาญในการแปลนิยาย Wuxia/Xianxia จีนจากภาษาอังกฤษเป็นภาษาไทย

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

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": settings
        }
        
        start_time = time.time()
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response_time": end_time - start_time,
                    "input_tokens": self.count_tokens(prompt),
                    "output_tokens": self.count_tokens(result.get('response', '')),
                    "quality_score": self.estimate_quality(result.get('response', ''), text)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": end_time - start_time
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    def estimate_quality(self, translation: str, original: str) -> float:
        """Simple quality estimation based on length ratio and content"""
        if not translation:
            return 0.0
        
        # Basic checks
        length_ratio = len(translation) / len(original)
        
        # Ideal ratio for English->Thai is around 0.8-1.2
        if 0.8 <= length_ratio <= 1.2:
            length_score = 1.0
        else:
            length_score = max(0.0, 1.0 - abs(length_ratio - 1.0))
        
        # Check for Thai characters
        thai_chars = sum(1 for c in translation if '\u0E00' <= c <= '\u0E7F')
        thai_ratio = thai_chars / len(translation) if translation else 0
        thai_score = min(1.0, thai_ratio * 2)  # Expect at least 50% Thai characters
        
        return (length_score + thai_score) / 2

def main():
    checker = TokenChecker()
    
    print("🔍 Token Checker and Optimizer for Novel Translator")
    print("=" * 60)
    
    # Get model info
    model_info = checker.get_model_info()
    if model_info:
        print(f"Model: {checker.model_name}")
        print(f"Context Length: {checker.model_specs['context_length']:,} tokens")
        print(f"Current num_ctx: {checker.model_specs['current_num_ctx']:,} tokens")
        print(f"Parameter Size: {checker.model_specs['parameter_size']}")
        print(f"Quantization: {checker.model_specs['quantization']}")
    
    while True:
        print("\n" + "=" * 60)
        print("Choose an option:")
        print("1. Analyze text token usage")
        print("2. Test current settings")
        print("3. Get optimization recommendations")
        print("4. Benchmark different settings")
        print("5. Check specific file")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            text = input("\nEnter text to analyze (or 'sample' for sample text): ").strip()
            if text.lower() == 'sample':
                text = "The young cultivator sat in meditation, circulating his qi through his dantian. After years of practice, he was finally ready for his breakthrough to the next realm."
            
            analysis = checker.analyze_prompt_tokens(text)
            print(f"\n📊 Token Analysis:")
            print(f"System prompt tokens: {analysis['system_prompt_tokens']}")
            print(f"Input text tokens: {analysis['input_text_tokens']}")
            print(f"Total input tokens: {analysis['total_input_tokens']}")
            print(f"Estimated output tokens: {analysis['estimated_output_tokens']:.0f}")
            print(f"Total estimated tokens: {analysis['total_estimated_tokens']:.0f}")
            print(f"Current context limit: {checker.model_specs['current_num_ctx']}")
            
            if analysis['total_estimated_tokens'] > checker.model_specs['current_num_ctx']:
                print("⚠️  WARNING: Estimated tokens exceed current context limit!")
            else:
                print("✅ Token usage within limits")
        
        elif choice == "2":
            test_text = input("\nEnter test text (or 'sample' for sample): ").strip()
            if test_text.lower() == 'sample':
                test_text = "The sect master looked at his disciple with approval. 'Your cultivation has progressed well,' he said."
            
            result = checker.test_token_limits(test_text)
            if result['success']:
                print(f"\n✅ Test successful!")
                print(f"Response time: {result['response_time']:.2f} seconds")
                print(f"Input tokens: {result['estimated_input_tokens']}")
                print(f"Output tokens: {result['estimated_output_tokens']}")
                print(f"Sample response: {result['response']}")
            else:
                print(f"\n❌ Test failed: {result['error']}")
        
        elif choice == "3":
            chunk_size = input("\nEnter target chunk size (default 2000): ").strip()
            chunk_size = int(chunk_size) if chunk_size.isdigit() else 2000
            
            recommendations = checker.optimize_settings(chunk_size)
            print(f"\n🎯 Optimization Recommendations:")
            print(f"\nCurrent settings:")
            for key, value in recommendations['current_settings'].items():
                print(f"  {key}: {value}")
            
            if recommendations['warnings']:
                print(f"\n⚠️  Warnings:")
                for warning in recommendations['warnings']:
                    print(f"  • {warning}")
            
            if recommendations['recommended_settings']:
                print(f"\n✨ Recommended settings:")
                for key, value in recommendations['recommended_settings'].items():
                    print(f"  {key}: {value}")
            
            if recommendations['optimizations']:
                print(f"\n🔧 Optimizations:")
                for opt in recommendations['optimizations']:
                    print(f"  • {opt}")
        
        elif choice == "4":
            print("\n🏁 Benchmarking different settings...")
            test_cases = [
                "The young master's face turned red with anger.",
                "The ancient formation began to glow with spiritual energy.",
                "Elder Zhang stroked his beard thoughtfully."
            ]
            
            settings_list = [
                {"temperature": 0.2, "top_p": 0.85, "max_tokens": 2000, "num_ctx": 8192},
                {"temperature": 0.3, "top_p": 0.9, "max_tokens": 4000, "num_ctx": 8192},
                {"temperature": 0.1, "top_p": 0.8, "max_tokens": 3000, "num_ctx": 16384},
            ]
            
            results = checker.benchmark_settings(test_cases, settings_list)
            
            print(f"\n📈 Benchmark Results:")
            for setting_name, data in results.items():
                print(f"\n{setting_name}:")
                print(f"Settings: {data['settings']}")
                
                successful_tests = [r for r in data['test_results'] if r.get('success')]
                if successful_tests:
                    avg_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
                    avg_quality = sum(r['quality_score'] for r in successful_tests) / len(successful_tests)
                    print(f"Average response time: {avg_time:.2f}s")
                    print(f"Average quality score: {avg_quality:.2f}")
                    print(f"Success rate: {len(successful_tests)}/{len(data['test_results'])}")
                else:
                    print("All tests failed")
        
        elif choice == "5":
            filename = input("\nEnter filename to check: ").strip()
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    analysis = checker.analyze_prompt_tokens(content)
                    print(f"\n📁 File Analysis: {filename}")
                    print(f"File size: {len(content)} characters")
                    print(f"Estimated tokens needed: {analysis['total_estimated_tokens']:.0f}")
                    print(f"Recommended chunk size: {len(content) * checker.model_specs['current_num_ctx'] // analysis['total_estimated_tokens'] if analysis['total_estimated_tokens'] > checker.model_specs['current_num_ctx'] else len(content)}")
                except Exception as e:
                    print(f"Error reading file: {e}")
            else:
                print("File not found")
        
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
