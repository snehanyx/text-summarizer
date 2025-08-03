from flask import Flask, request, jsonify, render_template
import re
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

def summarize_text(text, num_sentences=3):
    """Improved extractive summarization with basic importance scoring"""
    try:
        # Split into sentences while preserving punctuation
        sentences = re.findall(r'[^.!?]+[.!?]', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return "Could not identify sentences in the text."
        
        # Score sentences by word frequency
        word_freq = defaultdict(int)
        for sentence in sentences:
            for word in re.findall(r'\w+', sentence.lower()):
                word_freq[word] += 1
        
        # Score sentences (higher score = more important)
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = sum(word_freq[word] for word in re.findall(r'\w+', sentence.lower()))
            sentence_scores[i] = score / len(re.findall(r'\w+', sentence))
        
        # Get top sentences while preserving order
        top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
        top_indices.sort()  # Maintain original order
        
        return ' '.join([sentences[i] for i in top_indices])
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    start_time = datetime.now()
    
    try:
        text = request.form.get('text', '')
        length = request.form.get('length', 'medium')
        
        if not text.strip():
            return jsonify({"error": "Please enter some text to summarize"}), 400
            
        word_count = len(text.split())
        if word_count < 10:
            return jsonify({"error": "Text should be at least 10 words long"}), 400
        
        # Determine summary length
        num_sentences = {'short': 2, 'medium': 3, 'long': 5}.get(length, 3)
        
        # Generate summary
        summary = summarize_text(text, num_sentences)
        summary_word_count = len(summary.split())
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return jsonify({
            "summary": summary,
            "original_length": word_count,
            "summary_length": summary_word_count,
            "reduction": f"{round(100 - (summary_word_count/word_count)*100)}%",
            "processing_time": f"{processing_time:.2f} seconds"
        })
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)