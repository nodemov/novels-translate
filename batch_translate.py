# batch_translate.py - แปลทั้งโฟลเดอร์แบบ direct
from novel_translator import NovelTranslator

def batch_translate():
    # ตั้งค่า
    INPUT_FOLDER = r"C:\novels\english"     # โฟลเดอร์ไฟล์ต้นฉบับ
    OUTPUT_FOLDER = r"C:\novels\thai"       # โฟลเดอร์ไฟล์แปลแล้ว
    FILE_EXTENSIONS = ['.txt', '.md']       # นามสกุลไฟล์ที่จะแปล
    CHUNK_SIZE = 2000                       # ขนาด chunk
    DELAY = 1.0                            # หน่วงเวลาระหว่าง chunks (วินาที)
    
    # สร้าง translator
    translator = NovelTranslator()
    
    # เริ่มแปล
    print("🚀 เริ่มแปลทั้งโฟลเดอร์...")
    translator.translate_directory(
        input_dir=INPUT_FOLDER,
        output_dir=OUTPUT_FOLDER,
        file_extensions=FILE_EXTENSIONS,
        chunk_size=CHUNK_SIZE,
        delay_between_chunks=DELAY
    )
    print("✅ แปลเสร็จสิ้น!")

if __name__ == "__main__":
    batch_translate()