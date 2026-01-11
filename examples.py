"""
Example news snippets for testing the Fake News Detection system.
Contains both real and fake news examples across different categories.
"""

FAKE_NEWS_EXAMPLES = {
    "Health Misinformation": "BREAKING: Doctors HATE this one simple trick! Miracle cure for all diseases discovered by local grandmother. Big Pharma doesn't want you to know about this natural remedy that cures cancer, diabetes, and heart disease in just 3 days!",
    
    "Political Conspiracy": "SHOCKING REVELATION: Secret documents prove government is hiding aliens in underground facility. Whistleblower reveals truth about Area 51 that mainstream media refuses to report. Share before this gets deleted!",
    
    "Celebrity Hoax": "UNBELIEVABLE: Famous actor found living on deserted island after faking death 10 years ago. Exclusive photos reveal the truth Hollywood tried to hide. You won't believe what happened next!",
    
    "Technology Scam": "WARNING: Your phone is being hacked RIGHT NOW! Delete these 10 apps immediately or lose all your data. Tech companies are secretly stealing your information. Forward this to everyone you know!",
    
    "Financial Fraud": "URGENT: Banks are collapsing tomorrow! Withdraw all your money NOW before it's too late. Secret insider reveals the truth about the coming financial apocalypse. Act fast!"
}

REAL_NEWS_EXAMPLES = {
    "Politics": "The Federal Reserve announced today that it will maintain current interest rates following its monthly policy meeting. The decision comes after reviewing recent economic indicators including employment data and inflation metrics.",
    
    "Technology": "Apple Inc. released its quarterly earnings report showing revenue growth of 8 percent year-over-year. The company attributed the increase to strong iPhone sales in international markets, particularly in Asia.",
    
    "Health": "According to a new study published in the Journal of Medicine, researchers at Stanford University have identified a potential biomarker for early detection of Alzheimer's disease. The findings are based on a five-year clinical trial involving 2,000 participants.",
    
    "Business": "Amazon announced plans to open three new distribution centers in the Midwest, creating approximately 5,000 jobs over the next two years. The expansion is part of the company's strategy to improve delivery times in rural areas.",
    
    "Science": "NASA's James Webb Space Telescope has captured detailed images of a distant galaxy formed approximately 13 billion years ago. The observations provide new insights into the early universe and star formation processes."
}

def get_all_examples():
    """Returns all examples as a dictionary with category labels."""
    examples = {}
    
    for category, text in FAKE_NEWS_EXAMPLES.items():
        examples[f"❌ FAKE: {category}"] = text
    
    for category, text in REAL_NEWS_EXAMPLES.items():
        examples[f"✅ REAL: {category}"] = text
    
    return examples

def get_fake_examples():
    """Returns only fake news examples."""
    return {f"❌ {k}": v for k, v in FAKE_NEWS_EXAMPLES.items()}

def get_real_examples():
    """Returns only real news examples."""
    return {f"✅ {k}": v for k, v in REAL_NEWS_EXAMPLES.items()}
