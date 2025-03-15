# filepath: f:\gemma and MT5\main.py
import streamlit as st
from news import get_news, summarize_articles
from alpha import get_symbol_data, plot_symbol_data

def main():
    st.set_page_config(page_title="News and Symbol Analysis", 
                       page_icon="📰",
                       layout="wide")
    
    st.title("🌍 Global News and Symbol Analysis")
    st.markdown("---")
    
    # Create two columns for the layout
    col1, col2 = st.columns([1, 1])
    
    # Left column for inputs and news
    with col1:
        symbol = st.selectbox("Select a symbol to analyze:", ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "BTCUSD"])
        search_button = st.button("Search News")
    
    # Right column for chart (loads immediately)
    with col2:
        with st.spinner('Loading charts...'):
            for timeframe in ['M5', 'H1', 'D1']:
                df = get_symbol_data(symbol, timeframe)
                if df is not None:
                    plot_symbol_data(df, symbol, timeframe)
                else:
                    st.error(f"Failed to load {symbol} data for {timeframe} timeframe.")
    
    # Handle news search when button is clicked
    if search_button:
        if symbol:
            try:
                with col1:
                    with st.spinner('Fetching news...'):
                        articles = get_news(symbol)
                        
                    if not articles:
                        st.warning("No news found for this topic.")
                    else:
                        st.success(f"Found {len(articles)} articles!")
                        
                        # Summarize all articles
                        with st.spinner('Analyzing news and generating AI decision...'):
                            summary = summarize_articles(articles, symbol)
                            st.markdown("### AI Summary and Trading Decision")
                            st.write(summary)
                        
                        st.markdown("### Recent News Articles")
                        for article in articles:
                            with st.expander(f"📰 {article['title']}"):
                                st.write(f"**Published:** {article.get('date', 'N/A')}")
                                st.write(f"**Source:** {article.get('source', 'N/A')}")
                                st.write(f"**Summary:** {article.get('body', 'No summary available')}")
                                st.markdown(f"[Read Full Article]({article.get('url', '#')})")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please select a symbol to search for.")

if __name__ == "__main__":
    main()