import streamlit as st
import joblib
import re
import string
import io
import requests
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import quote
from examples import get_all_examples

# --- Config & Assets ---
st.set_page_config(
    page_title="Fake News Detection Using Python",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
    }
    
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    
    .result-card {
        padding: 2rem;
        border-radius: 16px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .real-news {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 5px solid #10b981;
    }
    
    .fake-news {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 5px solid #ef4444;
    }

    /* Social Buttons */
    .share-btn {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 8px;
        text-decoration: none;
        color: white !important;
        font-size: 14px;
        font-weight: 500;
        margin-right: 10px;
        transition: opacity 0.2s;
    }
    .share-whatsapp { background-color: #25D366; }
    .share-twitter { background-color: #1DA1F2; }
    .share-telegram { background-color: #0088cc; }
</style>
""", unsafe_allow_html=True)

# --- Logic Layer ---

def wordopt(text):
    text = str(text).lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W"," ",text) 
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub(r'\breuters\b', '', text)
    text = re.sub(r'\bwashington\b', '', text)
    return text

@st.cache_resource
def load_model():
    """Load the trained model and vectorizer with better error handling."""
    try:
        v = joblib.load("vectorizer.jb")
        m = joblib.load("lr_model.jb")
        return v, m, None
    except FileNotFoundError:
        error_msg = "⚠️ Model files not found. Please ensure 'lr_model.jb' and 'vectorizer.jb' are in the same directory."
        return None, None, error_msg
    except Exception as e:
        error_msg = f"⚠️ Error loading models: {str(e)}"
        return None, None, error_msg

def fetch_url_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        return f"Error: {str(e)}"

def get_share_links(prediction, text):
    base_msg = "🚨 This news looks FAKE! Be careful." if prediction == 0 else "✅ This news seems REAL."
    short_text = (text[:100] + '...') if len(text) > 100 else text
    msg = quote(f"{base_msg}\n\nContent: {short_text}\n\nVerified by AI Sentinel")
    
    links = {
        "WhatsApp": f"https://api.whatsapp.com/send?text={msg}",
        "Twitter": f"https://twitter.com/intent/tweet?text={msg}",
        "Telegram": f"https://t.me/share/url?url=https://fake-news-detector.streamlit.app&text={msg}"
    }
    return links

# --- UI Layout ---

vectorizer, model, load_error = load_model()

# Display model loading error if exists
if load_error:
    st.error(load_error)
    st.info("💡 **Tip:** If you're running this locally, make sure the model files are in the project directory. If deploying, ensure the files are included in your repository.")
    st.stop()

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1041/1041916.png", width=100)
    st.title("Fake News App")
    st.markdown("### Python Powered Analysis")
    st.info("Ensuring truth across WhatsApp, Twitter, and the Web.")
    
    st.divider()
    
    # Statistics Dashboard
    st.subheader("📊 System Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Accuracy", "98%", delta="High")
    with col2:
        st.metric("Training Data", "44K+", delta="Articles")
    
    with st.expander("ℹ️ How It Works"):
        st.markdown("""
        **Our AI analyzes news using:**
        
        1. **Text Preprocessing** - Cleans and normalizes text
        2. **TF-IDF Vectorization** - Converts text to numerical features
        3. **Logistic Regression** - Predicts fake vs real
        
        **Trained on 44,000+ articles** from verified sources.
        
        **Note:** This is a tool to assist verification, not replace critical thinking.
        """)
    
    with st.expander("❓ Tips for Spotting Fake News"):
        st.markdown("""
        - ✅ Check the source credibility
        - ✅ Look for author information
        - ✅ Verify with multiple sources
        - ✅ Check the publication date
        - ✅ Be skeptical of sensational headlines
        - ✅ Look for evidence and citations
        """)
    
    st.divider()
    
    st.subheader("🌐 Global Access")
    st.info("Accessible from any device with an internet connection once deployed.")
    st.caption("Works on WiFi and Mobile Data")

# Main Interface
st.markdown("# 🛡️ Fake News Detection Using Python")
st.markdown("#### Verify news instantly using Machine Learning (Logistic Regression).")
st.markdown("---")

# Quick stats banner
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**🎯 98% Accurate**")
with col2:
    st.markdown("**⚡ Instant Results**")
with col3:
    st.markdown("**🌐 URL Scanning**")
with col4:
    st.markdown("**📱 Mobile Ready**")

st.markdown("---")

tab1, tab2 = st.tabs(["📝 Manual Analysis", "🔗 URL Link Scan"])

with tab1:
    # Example selector
    st.markdown("### Try an Example or Enter Your Own")
    
    examples_dict = get_all_examples()
    example_options = ["-- Select an example --"] + list(examples_dict.keys())
    
    selected_example = st.selectbox(
        "Choose a sample news snippet:",
        example_options,
        help="Select a pre-loaded example to see how the system works"
    )
    
    # Pre-fill text area if example selected
    default_text = ""
    if selected_example != "-- Select an example --":
        default_text = examples_dict[selected_example]
    
    input_text = st.text_area(
        "Or paste your own news headline or article content:",
        value=default_text,
        height=200,
        placeholder="Example: Scientists discover breakthrough in renewable energy technology...",
        help="Paste any news text you want to verify"
    )
    
    if st.button("🚀 Run AI Analysis", key="btn_manual", use_container_width=True):
        if input_text.strip():
            # Input validation
            if len(input_text.strip()) < 10:
                st.warning("⚠️ Please enter at least 10 characters for accurate analysis.")
            else:
                with st.spinner("🔍 Analyzing text patterns..."):
                    if vectorizer and model:
                        clean = wordopt(input_text)
                        vec = vectorizer.transform([clean])
                        pred = model.predict(vec)[0]
                        proba = model.predict_proba(vec)[0]
                        
                        # Get confidence score
                        confidence = max(proba) * 100
                        
                        if pred == 1:
                            st.markdown(f'<div class="result-card real-news"><h3>✅ Verdict: REAL NEWS</h3><p>Our AI model indicates this information is likely <strong>authentic</strong>.</p></div>', unsafe_allow_html=True)
                            st.success(f"**Confidence Score:** {confidence:.1f}%")
                            st.info("💡 **Recommendation:** While our AI suggests this is real news, always verify with multiple trusted sources.")
                        else:
                            st.markdown(f'<div class="result-card fake-news"><h3>🚨 Verdict: FAKE NEWS</h3><p>High probability of <strong>misinformation</strong> detected! Please verify your sources.</p></div>', unsafe_allow_html=True)
                            st.error(f"**Confidence Score:** {confidence:.1f}%")
                            st.warning("⚠️ **Warning:** This content shows patterns commonly found in fake news. Cross-check with reputable news sources before sharing.")
                    
                        # Sharing Options
                        st.markdown("---")
                        st.markdown("### 📣 Share Verification Result")
                        st.caption("Help others avoid misinformation by sharing this verification")
                        links = get_share_links(pred, input_text)
                        cols = st.columns(3)
                        cols[0].markdown(f'<a href="{links["WhatsApp"]}" target="_blank" class="share-btn share-whatsapp">📱 WhatsApp</a>', unsafe_allow_html=True)
                        cols[1].markdown(f'<a href="{links["Twitter"]}" target="_blank" class="share-btn share-twitter">🐦 Twitter / X</a>', unsafe_allow_html=True)
                        cols[2].markdown(f'<a href="{links["Telegram"]}" target="_blank" class="share-btn share-telegram">✈️ Telegram</a>', unsafe_allow_html=True)
                    else:
                        st.error("❌ Model files are not loaded. Please ensure the model files are available.")
        else:
            st.warning("⚠️ Please enter some text to analyze!")

with tab2:
    st.markdown("### Analyze News from Any Website")
    st.caption("Enter a URL and we'll scrape and analyze the content for you")
    
    input_url = st.text_input(
        "Enter News Article URL:",
        placeholder="https://www.example-news-site.com/article-title",
        help="Paste the full URL of a news article"
    )
    
    if st.button("🌐 Connect & Analyze", key="btn_url", use_container_width=True):
        if input_url.strip():
            # Basic URL validation
            if not input_url.startswith(('http://', 'https://')):
                st.error("⚠️ Please enter a valid URL starting with http:// or https://")
            else:
                with st.spinner("🌐 Fetching content from URL..."):
                    scraped_text = fetch_url_content(input_url)
                    if scraped_text.startswith("Error"):
                        st.error(f"❌ {scraped_text}")
                        st.info("💡 **Troubleshooting Tips:**\n- Check if the URL is accessible\n- Some websites block automated scraping\n- Try copying the article text manually instead")
                    else:
                        st.success(f"✅ Successfully fetched {len(scraped_text)} characters from the article")
                        with st.expander("📄 View Scraped Content (Preview)"):
                            st.text_area("Article Text:", scraped_text[:1000] + "..." if len(scraped_text) > 1000 else scraped_text, height=200)
                        
                        with st.spinner("🔍 Analyzing content..."):
                            if vectorizer and model:
                                clean = wordopt(scraped_text)
                                vec = vectorizer.transform([clean])
                                pred = model.predict(vec)[0]
                                proba = model.predict_proba(vec)[0]
                                confidence = max(proba) * 100
                                
                                if pred == 1:
                                    st.markdown(f'<div class="result-card real-news"><h3>✅ Verdict: REAL NEWS</h3><p>The content from this URL appears <strong>trustworthy</strong>.</p></div>', unsafe_allow_html=True)
                                    st.success(f"**Confidence Score:** {confidence:.1f}%")
                                    st.info("💡 **Recommendation:** This article shows characteristics of real news, but always verify with multiple sources.")
                                else:
                                    st.markdown(f'<div class="result-card fake-news"><h3>🚨 Verdict: FAKE NEWS</h3><p>This URL may lead to <strong>misinformation</strong>!</p></div>', unsafe_allow_html=True)
                                    st.error(f"**Confidence Score:** {confidence:.1f}%")
                                    st.warning("⚠️ **Warning:** Be cautious! This content shows patterns typical of fake news.")
                        
                                # Sharing
                                st.markdown("---")
                                st.markdown("### 📣 Share Verification Result")
                                st.caption("Warn others about this content")
                                links = get_share_links(pred, scraped_text)
                                cols = st.columns(3)
                                cols[0].markdown(f'<a href="{links["WhatsApp"]}" target="_blank" class="share-btn share-whatsapp">📱 WhatsApp</a>', unsafe_allow_html=True)
                                cols[1].markdown(f'<a href="{links["Twitter"]}" target="_blank" class="share-btn share-twitter">🐦 Twitter / X</a>', unsafe_allow_html=True)
                                cols[2].markdown(f'<a href="{links["Telegram"]}" target="_blank" class="share-btn share-telegram">✈️ Telegram</a>', unsafe_allow_html=True)
                            else:
                                st.error("❌ Model files are not loaded.")
        else:
            st.warning("⚠️ Please enter a URL to analyze!")

st.divider()

# Footer with additional info
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🎯 Accuracy**")
    st.caption("98% on test data")
with col2:
    st.markdown("**📚 Training**")
    st.caption("44,000+ articles")
with col3:
    st.markdown("**🤖 Model**")
    st.caption("Logistic Regression + TF-IDF")

st.divider()
st.caption("© 2026 Fake News Detection Using Python - Developed for General Public, Students, and Journalists")
st.caption("⚠️ **Disclaimer:** This tool assists in identifying potential misinformation but should not be the sole source for fact-checking. Always use critical thinking and verify with multiple trusted sources.")
