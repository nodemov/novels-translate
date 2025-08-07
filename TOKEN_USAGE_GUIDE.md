# Token Usage Guide for Novel Translator

## 📋 Summary of Your Model Capabilities

**Model**: `scb10x/typhoon-translate-4b`

- **Maximum Context**: 131,072 tokens
- **Recommended Context**: 16,384 tokens (for optimal performance)
- **Current Setting**: 8,192 tokens (your original setting)
- **Parameter Size**: 3.9B parameters
- **Quantization**: Q4_K_M

## 🔧 Optimized Settings Applied

I've updated your `novel_translator.py` with these optimized settings:

```python
"options": {
    "temperature": 0.2,      # Lower for more consistent translation
    "top_p": 0.85,           # Better focus on likely translations
    "max_tokens": 6000,      # Increased for longer Thai translations
    "num_ctx": 16384,        # Doubled context window for better coherence
    "repeat_penalty": 1.1,   # Prevent repetitive phrases
    "top_k": 40             # Limit vocabulary choices for quality
}
```

### Key Changes:

1. **Lower temperature** (0.2): More consistent, less creative translations
2. **Increased context** (16384): Better coherence across longer texts
3. **Higher max_tokens** (6000): Accommodates Thai text expansion
4. **Added repeat_penalty**: Reduces redundant phrases
5. **Added top_k**: Better vocabulary selection

## 🛠️ Tools Available

### 1. Quick Token Check

For fast analysis of text or files:

```bash
python3 quick_token_check.py english/chapter1.txt
```

### 2. Full Token Checker

For comprehensive analysis and optimization:

```bash
python3 token_checker.py
```

## 📊 Token Usage Guidelines

### Current Analysis (based on your chapter1.txt):

- **File size**: 8,620 characters
- **Input tokens**: ~2,403 tokens
- **Estimated output**: ~2,358 tokens
- **Total**: ~4,761 tokens
- **Status**: ✅ Well within limits

### Recommended Chunk Sizes:

- **Conservative**: 1,500-2,000 characters (safe for all content)
- **Optimal**: 3,000-4,000 characters (best balance)
- **Maximum**: 8,000-10,000 characters (for simple text)

## ⚡ Performance Optimization Tips

### 1. Chunk Size Strategy

```python
# For different text complexities:
- Simple narrative: up to 4000 characters
- Complex dialogue: 2000-3000 characters
- Dense descriptions: 1500-2500 characters
```

### 2. Context Window Usage

Your model can handle much larger contexts than originally set:

- **Original**: 8,192 tokens
- **Recommended**: 16,384 tokens (2x improvement)
- **Maximum**: 131,072 tokens (for very long contexts)

### 3. Quality vs Speed Trade-offs

```python
# For highest quality (slower):
temperature: 0.1, top_p: 0.8, top_k: 20

# For balanced quality/speed:
temperature: 0.2, top_p: 0.85, top_k: 40  # Current setting

# For faster processing:
temperature: 0.3, top_p: 0.9, top_k: 60
```

## 🎯 Best Practices

### 1. Monitor Token Usage

- Use `quick_token_check.py` before processing large files
- Check if your chunks exceed the context window
- Adjust chunk size based on content complexity

### 2. Optimize for Content Type

- **Dialogue-heavy**: Smaller chunks (better character consistency)
- **Narrative**: Larger chunks (better flow)
- **Technical terms**: Medium chunks (context for terminology)

### 3. Error Prevention

- Always check token count before processing
- Use delay between chunks (current: 1 second)
- Monitor for timeout errors with large contexts

## 🔍 How to Check Token Usage

### Method 1: Quick Check

```bash
# Check a specific file
python3 quick_token_check.py english/chapter1.txt

# Interactive mode
python3 quick_token_check.py
```

### Method 2: Comprehensive Analysis

```bash
python3 token_checker.py
# Choose option 1: Analyze text token usage
# Choose option 3: Get optimization recommendations
```

### Method 3: File-by-File Analysis

```bash
# Check all English files
for file in english/*.txt; do
    echo "Checking $file:"
    python3 quick_token_check.py "$file"
    echo "---"
done
```

## 📈 Expected Performance Improvements

With the optimized settings, you should see:

1. **Better Consistency**: Lower temperature reduces random variations
2. **Improved Context**: Larger context window maintains better coherence
3. **Fewer Errors**: Better token management prevents overflow
4. **Higher Quality**: Optimized parameters for translation tasks
5. **Faster Processing**: Better chunk sizing reduces API calls

## 🚨 Warning Signs to Watch For

1. **Token Overflow**: Total tokens > 16,384
   - Solution: Reduce chunk size
2. **Timeout Errors**: Requests taking too long
   - Solution: Reduce max_tokens or chunk size
3. **Poor Quality**: Inconsistent translations
   - Solution: Lower temperature, check chunk boundaries
4. **Memory Issues**: System running out of memory
   - Solution: Reduce num_ctx or process smaller batches

## 🔄 Testing Your Optimizations

1. **Test with sample text**:

   ```bash
   python3 token_checker.py
   # Choose option 2: Test current settings
   ```

2. **Benchmark different settings**:

   ```bash
   python3 token_checker.py
   # Choose option 4: Benchmark different settings
   ```

3. **Compare before/after**:
   - Process the same chapter with old and new settings
   - Compare quality, speed, and consistency

## 📝 Quick Reference Commands

```bash
# Check token usage for a file
python3 quick_token_check.py filename.txt

# Run full analysis tool
python3 token_checker.py

# Process with optimized translator
python3 novel_translator.py

# Check model status
curl http://localhost:11434/api/tags
```

The tools I've created will help you monitor and optimize your token usage for the best translation quality and performance!
