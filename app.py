"""
================================================================================
ShopEase Data Analysis - Streamlit App
Complete interactive dashboard with all 5 visualizations
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="ShopEase Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)

# ============================================================
# TITLE AND INTRODUCTION
# ============================================================
st.markdown("# 📊 ShopEase E-Commerce Data Analysis Dashboard")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("📈 **Sales Analysis Dashboard**")
with col2:
    st.info("📦 **Customer Insights**")
with col3:
    st.info("🎯 **Business Intelligence**")

st.markdown("---")

# ============================================================
# LOAD AND CACHE DATA
# ============================================================
@st.cache_data
def load_and_clean_data():
    """Load and clean the dataset"""
    try:
        df = pd.read_csv('shopease_raw_orders.csv')
        
        # Data cleaning
        df['Category'] = df['Category'].str.strip().str.title()
        df['City'] = df['City'].str.strip().str.title()
        df['PaymentMethod'] = df['PaymentMethod'].str.strip()
        df['OrderStatus'] = df['OrderStatus'].str.strip()
        
        # Convert dates
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], format='mixed', errors='coerce')
        
        # Clean discount
        df['Discount'] = pd.to_numeric(
            df['Discount'].astype(str).str.rstrip('%').str.strip(), 
            errors='coerce'
        ).fillna(0)
        
        # Remove invalid data
        df = df[df['Quantity'] > 0]
        
        # Create time columns
        df['YearMonth'] = df['OrderDate'].dt.to_period('M')
        df['Month'] = df['OrderDate'].dt.strftime('%B')
        df['Year'] = df['OrderDate'].dt.year
        
        return df
    except FileNotFoundError:
        st.error("❌ Error: 'shopease_raw_orders.csv' not found!")
        st.info("📁 Please make sure the CSV file is in the same directory as this script.")
        return None

# Load data
df = load_and_clean_data()

if df is not None:
    # ============================================================
    # SIDEBAR: FILTERS AND STATISTICS
    # ============================================================
    st.sidebar.markdown("## 🔧 Filters & Settings")
    st.sidebar.markdown("---")
    
    # Select which plots to show
    st.sidebar.markdown("### 📊 Select Visualizations")
    show_plot1 = st.sidebar.checkbox("Plot 1: Sales Trends by Category", value=True)
    show_plot2 = st.sidebar.checkbox("Plot 2: Rating Distribution", value=True)
    show_plot3 = st.sidebar.checkbox("Plot 3: Geographic Analysis", value=True)
    show_plot4 = st.sidebar.checkbox("Plot 4: Payment Methods", value=True)
    show_plot5 = st.sidebar.checkbox("Plot 5: Revenue Relationships", value=True)
    
    st.sidebar.markdown("---")
    
    # Category filter
    st.sidebar.markdown("### 🏷️ Category Filter")
    selected_categories = st.sidebar.multiselect(
        "Select Categories:",
        options=df['Category'].unique(),
        default=df['Category'].unique()
    )
    
    # Filter data by selected categories
    df_filtered = df[df['Category'].isin(selected_categories)]
    
    st.sidebar.markdown("---")
    
    # Summary statistics
    st.sidebar.markdown("### 📈 Summary Statistics")
    st.sidebar.metric("Total Orders", f"{len(df_filtered):,}")
    st.sidebar.metric("Total Revenue", f"${df_filtered['TotalAmount'].sum():,.0f}")
    st.sidebar.metric("Avg Order Value", f"${df_filtered['TotalAmount'].mean():,.2f}")
    
    if df_filtered['Rating'].notna().sum() > 0:
        st.sidebar.metric("Avg Rating", f"{df_filtered['Rating'].mean():.2f}/5.0")
    
    # ============================================================
    # KEY METRICS SECTION
    # ============================================================
    st.markdown("## 📊 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Orders",
            f"{len(df_filtered):,}",
            delta=f"{len(df_filtered) - len(df):,}" if len(df_filtered) != len(df) else None
        )
    
    with col2:
        st.metric(
            "Total Revenue",
            f"${df_filtered['TotalAmount'].sum()/1e6:.2f}M"
        )
    
    with col3:
        st.metric(
            "Avg Order Value",
            f"${df_filtered['TotalAmount'].mean():,.0f}"
        )
    
    with col4:
        delivered = (df_filtered['OrderStatus'] == 'Delivered').sum()
        delivery_rate = (delivered / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric(
            "Delivery Rate",
            f"{delivery_rate:.1f}%"
        )
    
    with col5:
        if df_filtered['Rating'].notna().sum() > 0:
            st.metric(
                "Avg Rating",
                f"{df_filtered['Rating'].mean():.2f}",
                delta=f"/ 5.0"
            )
    
    st.markdown("---")
    
    # ============================================================
    # PLOT 1: SALES TRENDS BY CATEGORY OVER TIME
    # ============================================================
    if show_plot1:
        st.markdown("## 📈 Plot 1: Sales Trends by Category Over Time")
        
        with st.spinner("Generating Plot 1..."):
            # Prepare data
            df_plot1 = df_filtered[
                (df_filtered['OrderDate'].notna()) & 
                (df_filtered['TotalAmount'].notna())
            ].copy()
            
            if len(df_plot1) > 0:
                sales_trend = df_plot1.groupby(['YearMonth', 'Category'])['TotalAmount'].sum().reset_index()
                sales_trend['YearMonth'] = sales_trend['YearMonth'].astype(str)
                
                # Create plot
                fig1, ax1 = plt.subplots(figsize=(14, 6))
                
                for category in sales_trend['Category'].unique():
                    category_data = sales_trend[sales_trend['Category'] == category]
                    ax1.plot(category_data['YearMonth'], category_data['TotalAmount'], 
                             marker='o', linewidth=2.5, markersize=8, label=category)
                
                ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
                ax1.set_ylabel('Total Sales (Amount)', fontsize=12, fontweight='bold')
                ax1.set_title('Sales Trends by Category Over Time (Jan-June 2026)', 
                              fontsize=14, fontweight='bold', pad=20)
                ax1.legend(loc='best', fontsize=10)
                ax1.tick_params(axis='x', rotation=45)
                ax1.grid(True, alpha=0.3)
                plt.tight_layout()
                
                st.pyplot(fig1)
                
                # Show insights
                with st.expander("📊 Insights"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info("""
                        **Key Findings:**
                        - Electronics dominates sales (~$8.4M)
                        - All categories show declining trend
                        - Seasonal pattern visible
                        """)
                    with col2:
                        top_category = df_plot1.groupby('Category')['TotalAmount'].sum().idxmax()
                        top_amount = df_plot1.groupby('Category')['TotalAmount'].sum().max()
                        st.success(f"""
                        **Top Performer:**
                        - Category: {top_category}
                        - Revenue: ${top_amount:,.0f}
                        """)
            else:
                st.warning("No data available for selected filters")
        
        st.markdown("---")
    
    # ============================================================
    # PLOT 2: RATING DISTRIBUTION BY CATEGORY
    # ============================================================
    if show_plot2:
        st.markdown("## ⭐ Plot 2: Customer Satisfaction by Category")
        
        with st.spinner("Generating Plot 2..."):
            df_ratings = df_filtered[df_filtered['Rating'].notna()].copy()
            
            if len(df_ratings) > 0:
                fig2, ax2 = plt.subplots(figsize=(14, 6))
                
                sns.boxplot(data=df_ratings, x='Category', y='Rating', palette='Set2', 
                            width=0.6, ax=ax2)
                sns.stripplot(data=df_ratings, x='Category', y='Rating', 
                             color='black', alpha=0.3, size=4, ax=ax2)
                
                ax2.set_xlabel('Category', fontsize=12, fontweight='bold')
                ax2.set_ylabel('Rating (out of 5)', fontsize=12, fontweight='bold')
                ax2.set_title('Customer Satisfaction: Rating Distribution by Category', 
                             fontsize=14, fontweight='bold', pad=20)
                ax2.set_ylim(0, 5.5)
                ax2.grid(axis='y', alpha=0.3)
                plt.tight_layout()
                
                st.pyplot(fig2)
                
                # Show statistics
                with st.expander("📊 Rating Statistics"):
                    rating_stats = df_ratings.groupby('Category')['Rating'].agg(
                        ['mean', 'median', 'std', 'count']
                    ).round(2)
                    st.dataframe(rating_stats)
            else:
                st.warning("No rating data available for selected filters")
        
        st.markdown("---")
    
    # ============================================================
    # PLOT 3: GEOGRAPHIC ANALYSIS
    # ============================================================
    if show_plot3:
        st.markdown("## 🗺️ Plot 3: Geographic Analysis")
        
        with st.spinner("Generating Plot 3..."):
            city_orders = df_filtered['City'].value_counts().head(10)
            city_revenue = df_filtered.groupby('City')['TotalAmount'].sum().sort_values(ascending=True).tail(10)
            
            if len(city_orders) > 0:
                fig3, axes = plt.subplots(1, 2, figsize=(16, 6))
                
                axes[0].barh(city_orders.index, city_orders.values, color='steelblue')
                axes[0].set_xlabel('Number of Orders', fontsize=11, fontweight='bold')
                axes[0].set_title('Top 10 Cities by Order Count', fontsize=12, fontweight='bold')
                axes[0].grid(axis='x', alpha=0.3)
                
                axes[1].barh(city_revenue.index, city_revenue.values, color='seagreen')
                axes[1].set_xlabel('Total Revenue (Amount)', fontsize=11, fontweight='bold')
                axes[1].set_title('Top 10 Cities by Total Revenue', fontsize=12, fontweight='bold')
                axes[1].grid(axis='x', alpha=0.3)
                
                plt.suptitle('Geographic Analysis: Orders and Revenue Distribution', 
                            fontsize=14, fontweight='bold', y=1.02)
                plt.tight_layout()
                
                st.pyplot(fig3)
                
                # Show city statistics
                with st.expander("📊 City Statistics"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Top 5 Cities by Orders:**")
                        st.dataframe(df_filtered['City'].value_counts().head(5))
                    with col2:
                        st.markdown("**Top 5 Cities by Revenue:**")
                        st.dataframe(df_filtered.groupby('City')['TotalAmount'].sum().sort_values(ascending=False).head(5))
            else:
                st.warning("No geographic data available")
        
        st.markdown("---")
    
    # ============================================================
    # PLOT 4: PAYMENT METHOD PREFERENCES
    # ============================================================
    if show_plot4:
        st.markdown("## 💳 Plot 4: Payment Method Preferences")
        
        with st.spinner("Generating Plot 4..."):
            payment_category = pd.crosstab(df_filtered['Category'], df_filtered['PaymentMethod'])
            
            if len(payment_category) > 0:
                fig4, ax4 = plt.subplots(figsize=(12, 6))
                
                sns.heatmap(payment_category, annot=True, fmt='d', cmap='YlOrRd', 
                           cbar_kws={'label': 'Number of Orders'}, linewidths=0.5, ax=ax4)
                ax4.set_xlabel('Payment Method', fontsize=12, fontweight='bold')
                ax4.set_ylabel('Category', fontsize=12, fontweight='bold')
                ax4.set_title('Payment Method Preferences by Product Category', 
                             fontsize=14, fontweight='bold', pad=20)
                plt.tight_layout()
                
                st.pyplot(fig4)
                
                # Show payment statistics
                with st.expander("📊 Payment Method Statistics"):
                    st.markdown("**Payment Method Distribution:**")
                    payment_dist = df_filtered['PaymentMethod'].value_counts()
                    payment_pct = (df_filtered['PaymentMethod'].value_counts() / len(df_filtered) * 100).round(1)
                    payment_table = pd.DataFrame({
                        'Count': payment_dist,
                        'Percentage': payment_pct.astype(str) + '%'
                    })
                    st.dataframe(payment_table)
            else:
                st.warning("No payment data available")
        
        st.markdown("---")
    
    # ============================================================
    # PLOT 5: REVENUE VS QUANTITY/DISCOUNT
    # ============================================================
    if show_plot5:
        st.markdown("## 📊 Plot 5: Revenue Relationships")
        
        with st.spinner("Generating Plot 5..."):
            df_plot5 = df_filtered[
                (df_filtered['Discount'].notna()) &
                (df_filtered['TotalAmount'].notna()) &
                (df_filtered['Quantity'].notna())
            ].copy()
            
            if len(df_plot5) > 0:
                categories = df_plot5['Category'].unique()
                colors = plt.cm.tab10(np.linspace(0, 1, len(categories)))
                
                fig5, axes = plt.subplots(1, 2, figsize=(16, 6))
                
                # Quantity vs Revenue
                for idx, category in enumerate(categories):
                    category_data = df_plot5[df_plot5['Category'] == category]
                    axes[0].scatter(category_data['Quantity'], category_data['TotalAmount'], 
                                   color=colors[idx], label=category, alpha=0.6, s=50)
                
                axes[0].set_xlabel('Quantity', fontsize=11, fontweight='bold')
                axes[0].set_ylabel('Total Amount (Revenue)', fontsize=11, fontweight='bold')
                axes[0].set_title('Quantity vs Revenue', fontsize=12, fontweight='bold')
                axes[0].legend(loc='upper left', fontsize=9)
                axes[0].grid(True, alpha=0.3)
                
                # Discount vs Revenue
                for idx, category in enumerate(categories):
                    category_data = df_plot5[df_plot5['Category'] == category]
                    axes[1].scatter(category_data['Discount'], category_data['TotalAmount'], 
                                   color=colors[idx], label=category, alpha=0.6, s=50)
                
                axes[1].set_xlabel('Discount (%)', fontsize=11, fontweight='bold')
                axes[1].set_ylabel('Total Amount (Revenue)', fontsize=11, fontweight='bold')
                axes[1].set_title('Discount vs Revenue', fontsize=12, fontweight='bold')
                axes[1].legend(loc='upper right', fontsize=9)
                axes[1].grid(True, alpha=0.3)
                
                plt.suptitle('Revenue Relationships: Quantity and Discount Impact', 
                            fontsize=14, fontweight='bold', y=1.00)
                plt.tight_layout()
                
                st.pyplot(fig5)
                
                # Show correlation
                with st.expander("📊 Correlation Analysis"):
                    corr_cols = ['Quantity', 'Discount', 'UnitPrice', 'Rating', 'TotalAmount']
                    corr_data = df_plot5[corr_cols].corr()['TotalAmount'].sort_values(ascending=False)
                    
                    fig_corr, ax = plt.subplots(figsize=(10, 5))
                    corr_data.plot(kind='barh', ax=ax, color='steelblue')
                    ax.set_xlabel('Correlation with Total Revenue', fontweight='bold')
                    ax.set_title('Feature Correlation with Revenue', fontweight='bold', fontsize=12, pad=15)
                    ax.grid(axis='x', alpha=0.3)
                    plt.tight_layout()
                    
                    st.pyplot(fig_corr)
            else:
                st.warning("No data available for revenue analysis")
        
        st.markdown("---")
    
    # ============================================================
    # DATA EXPORT SECTION
    # ============================================================
    st.markdown("## 📥 Data Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Filtered Data as CSV"):
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="Click to Download",
                data=csv,
                file_name=f"shopease_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Summary Report"):
            summary = f"""
SHOPEASE DATA ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== SUMMARY STATISTICS ===
Total Orders: {len(df_filtered):,}
Total Revenue: ${df_filtered['TotalAmount'].sum():,.2f}
Average Order Value: ${df_filtered['TotalAmount'].mean():,.2f}
Average Rating: {df_filtered['Rating'].mean():.2f}/5.0

=== ORDERS BY CATEGORY ===
{df_filtered['Category'].value_counts().to_string()}

=== ORDERS BY STATUS ===
{df_filtered['OrderStatus'].value_counts().to_string()}

=== TOP CITIES ===
{df_filtered['City'].value_counts().head(10).to_string()}

=== PAYMENT METHODS ===
{df_filtered['PaymentMethod'].value_counts().to_string()}
            """
            st.download_button(
                label="Click to Download",
                data=summary,
                file_name=f"shopease_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: gray; font-size: 12px;">
        ShopEase Data Analysis Dashboard | Built with Streamlit | 📊 Data-Driven Insights
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.error("❌ Unable to load data. Please check the CSV file path.")