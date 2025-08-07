import requests
import json
import time
import os
from typing import List
import re

class NovelTranslator:
    def __init__(self, model_name="scb10x/typhoon-translate-4b", ollama_url="http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.api_url = f"{ollama_url}/api/generate"
        
    def chunk_text(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        """แบ่งข้อความเป็น chunks โดยพยายามตัดที่จุดสิ้นสุดประโยค"""
        # แยกตามย่อหน้า
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # ถ้าย่อหน้านี้ + chunk ปัจจุบันยังไม่เกินขีดจำกัด
            if len(current_chunk + paragraph) < max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                # บันทึก chunk ปัจจุบันและเริ่ม chunk ใหม่
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        # เพิ่ม chunk สุดท้าย
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def translate_chunk(self, text: str) -> str:
        """แปลข้อความ chunk เดียว"""
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
            "options": {
                "temperature": 0.2,      # Lower for more consistent translation
                "top_p": 0.85,           # Better focus on likely translations
                "max_tokens": 6000,      # Increased for longer Thai translations
                "num_ctx": 16384,        # Increased context window for better coherence
                "repeat_penalty": 1.1,   # Prevent repetitive phrases
                "top_k": 40             # Limit vocabulary choices for quality
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            
            if 'response' in result:
                return result['response'].strip()
            else:
                print(f"ข้อผิดพลาด: ไม่พบ response ใน result")
                return text
                
        except requests.exceptions.Timeout:
            print("หมดเวลารอ - ลองใหม่...")
            time.sleep(5)
            return self.translate_chunk(text)  # ลองใหม่
        except requests.exceptions.RequestException as e:
            print(f"ข้อผิดพลาดในการเชื่อมต่อ: {e}")
            return text
        except Exception as e:
            print(f"ข้อผิดพลาด: {e}")
            return text
    
    def translate_file(self, input_file: str, output_file: str, chunk_size: int = 2000, 
                      delay_between_chunks: float = 1.0) -> None:
        """แปลไฟล์ทั้งหมด"""
        print(f"กำลังอ่านไฟล์: {input_file}")
        
        # อ่านไฟล์ต้นฉบับ
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"ไม่พบไฟล์: {input_file}")
            return
        except UnicodeDecodeError:
            # ลองอ่านด้วย encoding อื่น
            encodings = ['utf-8', 'cp1252', 'iso-8859-1']
            content = None
            for encoding in encodings:
                try:
                    with open(input_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    print(f"อ่านไฟล์สำเร็จด้วย encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                print("ไม่สามารถอ่านไฟล์ได้")
                return
        
        # แบ่งเป็น chunks
        chunks = self.chunk_text(content, chunk_size)
        total_chunks = len(chunks)
        
        print(f"แบ่งข้อความเป็น {total_chunks} ส่วน")
        print("เริ่มการแปล...")
        
        translated_chunks = []
        
        # แปลทีละ chunk
        for i, chunk in enumerate(chunks, 1):
            print(f"กำลังแปลส่วนที่ {i}/{total_chunks}")
            
            translated = self.translate_chunk(chunk)
            translated_chunks.append(translated)
            
            # แสดงความคืบหน้า
            progress = (i / total_chunks) * 100
            print(f"ความคืบหน้า: {progress:.1f}%")
            
            # รอระหว่าง chunks เพื่อไม่ให้ระบบทำงานหนักเกินไป
            if i < total_chunks:
                time.sleep(delay_between_chunks)
        
        # รวมผลการแปล
        translated_content = "\n\n".join(translated_chunks)
        
        # บันทึกผลลัพธ์
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            print(f"\nการแปลเสร็จสิ้น! บันทึกที่: {output_file}")
        except Exception as e:
            print(f"ข้อผิดพลาดในการบันทึก: {e}")
    
    def translate_directory(self, input_dir: str, output_dir: str, 
                           file_extensions: List[str] = ['.txt'], **kwargs) -> None:
        """แปลไฟล์ทั้งหมดในโฟลเดอร์"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for filename in os.listdir(input_dir):
            if any(filename.lower().endswith(ext) for ext in file_extensions):
                input_path = os.path.join(input_dir, filename)
                output_filename = f"translated_{filename}"
                output_path = os.path.join(output_dir, output_filename)
                
                print(f"\n{'='*50}")
                print(f"กำลังแปล: {filename}")
                print(f"{'='*50}")
                
                self.translate_file(input_path, output_path, **kwargs)

def main():
    # สร้าง translator instance
    translator = NovelTranslator()
    
    print("🔄 Novel Translator for Ollama")
    print("=" * 40)
    
    while True:
        print("\nเลือกโหมด:")
        print("1. แปลไฟล์เดียว")
        print("2. แปลทุกไฟล์ในโฟลเดอร์") 
        print("3. ออกจากโปรแกรม")
        
        choice = input("\nเลือก (1-3): ").strip()
        
        if choice == "1":
            # แปลไฟล์เดียว
            input_file = input("ระบุไฟล์ต้นฉบับ: ").strip()
            if not input_file:
                continue
                
            if not os.path.exists(input_file):
                print("ไม่พบไฟล์ที่ระบุ")
                continue
            
            # สร้างชื่อไฟล์ผลลัพธ์
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_translated.txt"
            
            # ตัวเลือกเพิ่มเติม
            chunk_size = input("ขนาด chunk (ค่าเริ่มต้น 2000): ").strip()
            chunk_size = int(chunk_size) if chunk_size.isdigit() else 2000
            
            delay = input("หน่วงเวลาระหว่าง chunks วินาที (ค่าเริ่มต้น 1): ").strip()
            delay = float(delay) if delay.replace('.','').isdigit() else 1.0
            
            translator.translate_file(input_file, output_file, chunk_size, delay)
            
        elif choice == "2":
            # แปลทั้งโฟลเดอร์
            input_dir = input("ระบุโฟลเดอร์ต้นฉบับ: ").strip()
            if not input_dir or not os.path.exists(input_dir):
                print("ไม่พบโฟลเดอร์ที่ระบุ")
                continue
            
            output_dir = input("ระบุโฟลเดอร์ปลายทาง (ค่าเริ่มต้น translated_novels): ").strip()
            output_dir = output_dir if output_dir else "translated_novels"
            
            # ตัวเลือกเพิ่มเติม
            extensions_input = input("ระบุนามสกุลไฟล์ (.txt,.md หรือ enter สำหรับค่าเริ่มต้น): ").strip()
            extensions = [ext.strip() for ext in extensions_input.split(',')] if extensions_input else ['.txt']
            
            chunk_size = input("ขนาด chunk (ค่าเริ่มต้น 2000): ").strip()
            chunk_size = int(chunk_size) if chunk_size.isdigit() else 2000
            
            delay = input("หน่วงเวลาระหว่าง chunks วินาที (ค่าเริ่มต้น 1): ").strip()
            delay = float(delay) if delay.replace('.','').isdigit() else 1.0
            
            translator.translate_directory(input_dir, output_dir, extensions, 
                                         chunk_size=chunk_size, delay_between_chunks=delay)
            
        elif choice == "3":
            print("ขอบคุณที่ใช้งาน!")
            break
        else:
            print("กรุณาเลือก 1-3")

if __name__ == "__main__":
    main()