import os
import glob
import json
import time
import re
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='en', target='zh-CN')

def has_chinese(text):
    """Check if text already contains Chinese characters."""
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def is_translatable(text):
    """Check if text contains meaningful English to translate."""
    stripped = text.strip()
    if not stripped:
        return False
    # Skip if already contains Chinese
    if has_chinese(stripped):
        return False
    # Skip if it's only whitespace, punctuation, or special chars
    if not any(c.isascii() and c.isalpha() for c in stripped):
        return False
    # Skip very short text (like "---" or single chars)
    alpha_count = sum(1 for c in stripped if c.isalpha())
    if alpha_count < 3:
        return False
    return True

def strip_markdown_formatting(text):
    """Remove markdown formatting for translation, return (prefix, clean_text, suffix)."""
    # Handle headings
    heading_match = re.match(r'^(#{1,6}\s+)', text)
    prefix = heading_match.group(1) if heading_match else ''
    clean = text[len(prefix):] if prefix else text
    
    # Remove trailing newlines
    suffix = ''
    while clean.endswith('\n'):
        suffix += '\n'
        clean = clean[:-1]
    
    return prefix, clean, suffix

def translate_with_retry(text, retries=5, base_delay=3):
    """Translate with exponential backoff."""
    for i in range(retries):
        try:
            result = translator.translate(text)
            return result
        except Exception as e:
            delay = base_delay * (2 ** i)
            print(f"  Error: {type(e).__name__}. Retry {i+1}/{retries} in {delay}s...")
            time.sleep(delay)
    print(f"  FAILED after {retries} retries. Skipping.")
    return None

def translate_line(line):
    """Translate a single line, preserving markdown formatting."""
    prefix, clean_text, suffix = strip_markdown_formatting(line)
    
    if not is_translatable(clean_text):
        return None
    
    # Remove HTML tags for translation, but keep them
    # Check if line is mostly HTML
    html_stripped = re.sub(r'<[^>]+>', '', clean_text).strip()
    if not html_stripped or not any(c.isalpha() for c in html_stripped):
        return None
    
    translated = translate_with_retry(clean_text)
    if translated and translated.strip() != clean_text.strip():
        return translated
    return None

def process_notebook(filepath):
    """Process a single notebook file."""
    print(f"\nProcessing: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modified = False
    for cell_idx, cell in enumerate(data.get('cells', [])):
        if cell.get('cell_type') != 'markdown':
            continue
        
        source = cell.get('source', [])
        # Skip if cell already has Chinese (already translated)
        cell_text = ''.join(source)
        if has_chinese(cell_text):
            continue
        
        # Collect all lines and translate them
        # Strategy: combine all lines into one text block, translate, then insert below
        translatable_lines = []
        line_indices = []
        
        for i, line in enumerate(source):
            if is_translatable(line):
                translatable_lines.append(line)
                line_indices.append(i)
        
        if not translatable_lines:
            continue
        
        # Batch translate: combine lines with a separator
        # Use "|||" as separator so we can split them back
        separator = " ||| "
        combined = separator.join(l.strip().replace('\n', ' ') for l in translatable_lines)
        
        # Limit to 5000 chars per batch (Google Translate limit)
        if len(combined) > 4500:
            # Split into smaller batches
            batches = []
            current_batch = []
            current_len = 0
            batch_indices = []
            current_indices = []
            
            for j, (line, idx) in enumerate(zip(translatable_lines, line_indices)):
                line_clean = line.strip().replace('\n', ' ')
                if current_len + len(line_clean) + len(separator) > 4500 and current_batch:
                    batches.append(current_batch)
                    batch_indices.append(current_indices)
                    current_batch = [line_clean]
                    current_indices = [idx]
                    current_len = len(line_clean)
                else:
                    current_batch.append(line_clean)
                    current_indices.append(idx)
                    current_len += len(line_clean) + len(separator)
            
            if current_batch:
                batches.append(current_batch)
                batch_indices.append(current_indices)
        else:
            batches = [[l.strip().replace('\n', ' ') for l in translatable_lines]]
            batch_indices = [line_indices]
        
        # Translate each batch
        translations = {}  # idx -> translated_text
        for batch, indices in zip(batches, batch_indices):
            combined_text = separator.join(batch)
            translated = translate_with_retry(combined_text)
            time.sleep(1.5)  # Rate limit delay
            
            if translated:
                parts = translated.split("|||")
                parts = [p.strip() for p in parts]
                
                # If split count matches, assign individually
                if len(parts) == len(indices):
                    for idx, trans in zip(indices, parts):
                        translations[idx] = trans
                else:
                    # Fallback: translate line by line
                    print(f"  Batch split mismatch ({len(parts)} vs {len(indices)}), falling back to individual translation")
                    for idx, line_text in zip(indices, batch):
                        trans = translate_with_retry(line_text)
                        time.sleep(1.5)
                        if trans:
                            translations[idx] = trans
        
        if not translations:
            continue
        
        # Build new source with translations inserted after each line
        new_source = []
        for i, line in enumerate(source):
            new_source.append(line)
            if i in translations:
                trans = translations[i]
                # Add proper line breaks
                if line.endswith('\n'):
                    new_source.append('\n')
                    new_source.append(trans + '\n')
                else:
                    new_source.append('\n\n')
                    new_source.append(trans)
                modified = True

        cell['source'] = new_source

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        print(f"  ✅ Saved!")
    else:
        print(f"  ⏭️  Skipped (already translated or no translatable content)")

if __name__ == "__main__":
    search_dir = "/Users/a1-6/Desktop/AIAgent/00-python/1-AI Python for Beginners/AiPython代码"
    ipynb_files = sorted(glob.glob(os.path.join(search_dir, "**", "*.ipynb"), recursive=True))
    
    print(f"Found {len(ipynb_files)} notebook files")
    for f in ipynb_files:
        process_notebook(f)
    print("\n✅ All done!")
