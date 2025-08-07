# � Novel Translator - Chinese to Thai Translation Tool

A powerful tool for translating Chinese novels (Wuxia/Xianxia) from English to Thai using Ollama and the Typhoon-translate model.

## 🚀 Quick Start Guide

### Prerequisites

- macOS with Homebrew installed
- Python 3.8 or higher
- At least 8GB of RAM (16GB recommended)

## 📥 Step 1: Install Ollama

```bash
# Install Ollama using Homebrew
brew install ollama

# Start Ollama service
ollama serve
```

## 🤖 Step 2: Install the Translation Model

Open a new terminal window and run:

```bash
# Download and install the Typhoon translate model (4GB download)
ollama pull scb10x/typhoon-translate-4b

# Verify installation
ollama list
```

## 🐍 Step 3: Install Python Dependencies

```bash
# Install required Python packages
pip3 install requests tiktoken

# Alternative: if you have pip instead of pip3
pip install requests tiktoken
```

## 📁 Step 4: Download and Setup Project

```bash
# Clone or download this project to your local machine
# Navigate to the project directory
cd /path/to/novels-translate

# Make scripts executable
chmod +x quick_token_check.py
chmod +x token_checker.py
```

## ✅ Step 5: Verify Installation

Test if everything is working:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test token checker (should work without errors)
python3 quick_token_check.py

# Test with sample text
echo "The young cultivator meditated quietly." | python3 quick_token_check.py
```

## 🔧 How to Use

### Option 1: Quick Token Check (Recommended for beginners)

```bash
# Check token usage for a specific file
python3 quick_token_check.py english/chapter1.txt

# Interactive mode - enter text directly
python3 quick_token_check.py
```

### Option 2: Comprehensive Token Analysis

```bash
# Full analysis and optimization tool
python3 token_checker.py

# Follow the menu options:
# 1. Analyze text token usage
# 2. Test current settings
# 3. Get optimization recommendations
# 4. Benchmark different settings
# 5. Check specific file
```

### Option 3: Translate Files

```bash
# Start the translation tool
python3 novel_translator.py

# Choose your option:
# 1. Translate single file
# 2. Translate entire folder
```

## 📊 Understanding Token Usage

### What are tokens?

Tokens are pieces of text that the AI model processes. For English/Thai text:

- 1 token ≈ 3-4 characters
- Your model can handle up to 131,072 tokens maximum
- Recommended: 16,384 tokens for optimal performance

### Token Limits by Content:

- **Simple text**: Up to 4,000 characters per chunk
- **Complex dialogue**: 2,000-3,000 characters per chunk
- **Dense descriptions**: 1,500-2,500 characters per chunk

## 🎯 Step-by-Step Translation Process

### 1. Check Your Text First

```bash
# Always check token usage before translating
python3 quick_token_check.py your_file.txt
```

### 2. Prepare Your Files

```
novels-translate/
├── english/           # Put your English files here
│   ├── chapter1.txt
│   ├── chapter2.txt
│   └── chapter3.txt
└── thai/             # Translated files will go here
```

### 3. Run Translation

```bash
# Start the translator
python3 novel_translator.py

# Select option 1 for single file:
# - Input file: english/chapter1.txt
# - Chunk size: 2000 (recommended)
# - Delay: 1 second (recommended)

# Select option 2 for batch translation:
# - Input folder: english
# - Output folder: thai
# - File extensions: .txt
```

### 4. Monitor Progress

The translator will:

- ✅ Split your text into optimal chunks
- ✅ Translate each chunk with context preservation
- ✅ Show progress percentage
- ✅ Save results with "translated\_" prefix

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. "Connection refused" error

```bash
# Make sure Ollama is running
ollama serve

# Check if model is loaded
ollama list
```

#### 2. "Token limit exceeded" error

```bash
# Check your file size
python3 quick_token_check.py problematic_file.txt

# Reduce chunk size in translator
# Use 1500-2000 characters instead of default
```

#### 3. "Model not found" error

```bash
# Reinstall the model
ollama pull scb10x/typhoon-translate-4b
```

#### 4. Slow translation speed

```bash
# Check system resources
top

# Reduce chunk size or increase delay between chunks
# Use token_checker.py to optimize settings
```

#### 5. Poor translation quality

```bash
# Use token_checker.py to optimize settings
python3 token_checker.py

# Choose option 3: Get optimization recommendations
# Apply recommended temperature and top_p values
```

## 📈 Optimization Tips

### 1. Check Before You Translate

Always run token check first:

```bash
python3 quick_token_check.py english/chapter1.txt
```

### 2. Optimal Settings for Different Content

```python
# For consistent quality (recommended):
chunk_size = 2000
temperature = 0.2
delay = 1.0

# For faster processing:
chunk_size = 1500
temperature = 0.3
delay = 0.5

# For highest quality (slower):
chunk_size = 1000
temperature = 0.1
delay = 2.0
```

### 3. Monitor Your System

```bash
# Check CPU/Memory usage during translation
top

# If system is struggling, reduce chunk size or add delays
```

## 📋 File Structure After Setup

```
novels-translate/
├── README.md                    # This file
├── TOKEN_USAGE_GUIDE.md        # Detailed token information
├── novel_translator.py         # Main translation tool
├── quick_token_check.py        # Fast token checking
├── token_checker.py           # Comprehensive analysis
├── batch_translate.py          # Batch processing tool
├── english/                    # Input folder
│   ├── chapter1.txt
│   ├── chapter2.txt
│   └── chapter3.txt
└── thai/                      # Output folder
    ├── translated_chapter1.txt
    ├── translated_chapter2.txt
    └── translated_chapter3.txt
```

## 🎉 Success Indicators

You'll know everything is working when:

✅ `ollama list` shows your model  
✅ `python3 quick_token_check.py` runs without errors  
✅ Token checker shows "✅ Within current context limit"  
✅ Translation produces Thai text output  
✅ No timeout or connection errors

## 💡 Pro Tips

1. **Always check tokens first** - Use `quick_token_check.py` before translating large files
2. **Start small** - Test with a small chapter before processing entire novels
3. **Monitor system resources** - Translation is CPU/memory intensive
4. **Use appropriate chunk sizes** - Larger chunks = better context, but higher token usage
5. **Save your work** - Translated files are automatically saved with "translated\_" prefix
6. **Backup important files** - Keep copies of your original English texts

## 🆘 Getting Help

If you encounter issues:

1. **Check the TOKEN_USAGE_GUIDE.md** for detailed optimization information
2. **Run the token checker** with option 3 for recommendations
3. **Verify Ollama is running** with `curl http://localhost:11434/api/tags`
4. **Check system resources** with `top` command
5. **Test with small samples** before processing large files

## 📚 Additional Resources

- **Ollama Documentation**: https://ollama.ai/docs
- **Typhoon Model Info**: Available via `ollama show scb10x/typhoon-translate-4b`
- **Token Usage Guide**: See `TOKEN_USAGE_GUIDE.md` in this project
