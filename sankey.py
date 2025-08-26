import pandas as pd
import plotly.graph_objects as go
import os

# Label mappings
FAMESWAP_LABELS = {
    'Tech & Science': 'Technology',
    'Educational & QA': 'Education',
    'Quotes & Sayings': 'Quotes',
    'Pets & Animals': 'Pets',
    'Food & Nutrition': 'Food',
    'Outdoor & Travel': 'Travel',
    'Art & Creativity': 'Creativity',
    'Cars & Bikes': 'Cars',
    'Crypto & NFT': 'Crypto',
    'Beauty & Makeup': 'Beauty',
    'Fitness & Sports': 'Sports',
    'Reviews & How-to': 'How-to',
    'Models & Celebrities': 'Celebrities',
    'Humor & Memes': 'Memes',
    'Luxury & Motivation': 'Motivation',
    'Gaming & Entertainment': 'Gaming',
    'Fashion & Style': 'Fashion',
    'Movies TV & Fanpages': 'Fanpages'
}

TOPIC_LABELS = {
    'cryptocurrency_content': 'Cryptocurrency',
    'financial_content': 'Money',
    'gambling_content': 'Gambling',
    'hateful_extremist_content': 'Extremist',
    'manosphere_redpill_content': 'Manosphere',
    'medical_health_content': 'Medical',
    'news_content': 'News',
    'political_content': 'Political',
    'religious_content': 'Religious',
    'unclassified': 'Not at-risk'
}

# Category ordering
FAMESWAP_ORDER = [
    'Humor & Memes', 'Gaming & Entertainment', 'Tech & Science', 'Educational & QA',
    'Reviews & How-to', 'Models & Celebrities', 'Luxury & Motivation', 'Movies TV & Fanpages',
    'Fitness & Sports', 'Fashion & Style', 'Quotes & Sayings', 'Crypto & NFT',
    'Food & Nutrition', 'Art & Creativity', 'Cars & Bikes', 'Outdoor & Travel',
    'Pets & Animals', 'Beauty & Makeup',
]

BROAD_CATEGORY_ORDER = ['Other', 'Ideological', 'Financial']

SPECIFIC_TOPIC_ORDER = [
    'Not at-risk', 'Political', 'News', 'Religious', 'Medical', 'Manosphere',
    'Extremist', 'Cryptocurrency', 'Money', 'Gambling'
]

def load_sankey_data(parquet_file="./data/sankey_data.parquet"):
    """
    Load sankey data from parquet file
    
    Parameters:
    -----------
    parquet_file : str
        Path to the parquet file
        
    Returns:
    --------
    df : DataFrame
        The loaded sankey data
    """
    if not os.path.exists(parquet_file):
        raise FileNotFoundError(f"Parquet file {parquet_file} not found.")
    
    print(f"Loading data from {parquet_file}...")
    df = pd.read_parquet(parquet_file)
    print(f"Loaded {len(df)} records")
    
    return df

def hex_to_rgba(hex_color, alpha=0.5):
    """Convert hex color to rgba with transparency"""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})'

def create_sankey_diagram(df, proportional=False):
    """
    Create a two-level sankey diagram:
    FameSwap categories → Broad categories → Specific topic categories
    
    Args:
        df: DataFrame with the data
        proportional: If True, use proportional flows based on topic values
    """
    # Process ALL topics (including unclassified) but we'll filter flows later
    topic_columns = [
        'cryptocurrency_content', 'financial_content', 'gambling_content',
        'hateful_extremist_content',
        'manosphere_redpill_content', 'medical_health_content', 'news_content',
        'political_content', 
        'religious_content',
        'unclassified'  # Include this for processing
    ]
    
    # Keep all broad category groupings
    broad_categories = {
        'Ideological': ['Political', 'Religious', 'News', 'Medical', 'Manosphere', 'Extremist'],
        'Financial': ['Cryptocurrency', 'Money', 'Gambling'],
        'Other': ['Not at-risk']  # Keep this
    }
    
    # Keep all colors
    broad_colors = {
        'Ideological': '#FF6B6B',
        'Financial': '#4ECDC4',
        'Other': '#BDC3C7'  # Keep this
    }
    
    topic_colors = {
        'Cryptocurrency': '#45B7D1',
        'Money': '#85C1E9',
        'Gambling': '#5DADE2',
        'Extremist': '#F8C471',
        'Manosphere': '#BB8FCE',
        'Medical': '#F7DC6F',
        'News': '#D7BDE2',
        'Political': '#EC7063',
        'Religious': '#F9E79F',
        'Not at-risk': '#BDC3C7'  # Keep this
    }
    
    # Filter out Beauty & Makeup from the data processing
    df_filtered = df[df['fameswap_category'] != 'Beauty & Makeup'].copy()
    
    # Create flow data using filtered dataframe
    topic_flows = []
    
    if proportional:
        # For proportional flows, normalize each row so total = 1
        df_normalized = df_filtered.copy()
        
        # Calculate the sum of topic values for each row (only for topics = 1)
        topic_sums = df_normalized[topic_columns].sum(axis=1)
        
        # Normalize each topic column by the row sum (avoid division by zero)
        for topic_col in topic_columns:
            # Only normalize rows where the topic is 1 and there are other topics
            mask = (df_normalized[topic_col] == 1) & (topic_sums > 0)
            df_normalized.loc[mask, topic_col] = 1.0 / topic_sums[mask]
            df_normalized.loc[~mask, topic_col] = 0
        
        # Now create flows using the normalized values
        for topic_col in topic_columns:
            topic_channels = df_normalized[df_normalized[topic_col] > 0].copy()
            if len(topic_channels) > 0:
                flows = topic_channels.groupby('fameswap_category')[topic_col].sum().reset_index()
                flows.columns = ['fameswap_category', 'count']
                flows['specific_topic'] = TOPIC_LABELS[topic_col]
                topic_flows.append(flows)
    else:
        # Use binary flows (original behavior) with filtered data
        for topic_col in topic_columns:
            topic_channels = df_filtered[df_filtered[topic_col] == 1]
            if len(topic_channels) > 0:
                flows = topic_channels.groupby('fameswap_category').size().reset_index(name='count')
                flows['specific_topic'] = TOPIC_LABELS[topic_col]
                topic_flows.append(flows)
    
    if not topic_flows:
        print("No flows found!")
        return None
    
    all_flows = pd.concat(topic_flows, ignore_index=True)
    
    # Add broad category mapping
    topic_to_broad = {}
    for broad_cat, topics in broad_categories.items():
        for topic in topics:
            topic_to_broad[topic] = broad_cat
    
    all_flows['broad_category'] = all_flows['specific_topic'].map(topic_to_broad)
    
    # Calculate flows from FameSwap categories to broad categories
    broad_flows = all_flows.groupby(['fameswap_category', 'broad_category'])['count'].sum().reset_index()
    
    # Calculate flows from broad categories to specific topics
    specific_flows = all_flows.groupby(['broad_category', 'specific_topic'])['count'].sum().reset_index()
    
    # Get ordered categories based on our predefined orders
    def get_ordered_list(available_items, order_list):
        """Get items in specified order, with unmapped ones at the end"""
        ordered = []
        remaining = set(available_items)
        
        # Add items in specified order
        for item in order_list:
            if item in remaining:
                ordered.append(item)
                remaining.remove(item)
        
        # Add any remaining items
        ordered.extend(sorted(remaining))
        return ordered
    
    # Get unique categories and apply ordering
    available_fameswap = df['fameswap_category'].unique()
    fameswap_categories = get_ordered_list(available_fameswap, FAMESWAP_ORDER)
    
    # Remove "Beauty & Makeup" from the categories
    fameswap_categories = [cat for cat in fameswap_categories if cat != 'Beauty & Makeup']
    
    available_broad = broad_flows['broad_category'].unique()
    broad_category_list = get_ordered_list(available_broad, BROAD_CATEGORY_ORDER)
    
    available_specific = specific_flows['specific_topic'].unique()
    specific_topics = get_ordered_list(available_specific, SPECIFIC_TOPIC_ORDER)
    
    # Create node labels, colors, and positions
    all_labels = []
    all_colors = []
    all_x_positions = []
    all_y_positions = []
    
    # Define invisible nodes
    invisible_nodes = {'Other', 'Not at-risk'}
    
    # FameSwap categories (left column) - with darker colors and explicit positioning
    fameswap_spacing = 0.9 / len(fameswap_categories)  # Distribute evenly in 90% of space
    for i, cat in enumerate(fameswap_categories):
        all_labels.append(FAMESWAP_LABELS.get(cat, cat))
        all_colors.append('#A1B2B9')  # Darker blue color
        all_x_positions.append(0.01)  # Left column
        all_y_positions.append(0.05 + i * fameswap_spacing)  # Even spacing
    
    # Broad categories (middle column) - add more spacing between visible categories
    visible_broad_categories = [cat for cat in broad_category_list if cat not in invisible_nodes]
    
    visible_idx = 0
    for cat in broad_category_list:
        if cat in invisible_nodes:
            all_labels.append("")  # Empty label for invisible nodes
            all_colors.append("rgba(0,0,0,0)")  # Transparent color
            all_x_positions.append(0.3)  # Middle column
            all_y_positions.append(0.001)  # Put invisible nodes at top
        else:
            all_labels.append("")  # Empty string for visible broad categories too
            all_colors.append(broad_colors.get(cat, '#BDC3C7'))
            all_x_positions.append(0.5)  # Middle column
            if cat in ['Ideological']:
                all_y_positions.append(0.3)  # Start at 30% and add spacing
                visible_idx += 1
            else:
                all_y_positions.append(0.7)  # Start at 70% and add spacing
                visible_idx += 1
    
    # Specific topics (right column) - explicit positioning for each category
    specific_y_positions = {
        'Political': 0.1,
        'News': 0.2,
        'Religious': 0.3,
        'Medical': 0.4,
        'Manosphere': 0.45,
        'Extremist': 0.5,
        'Cryptocurrency': 0.6,
        'Money': 0.68,
        'Gambling': 0.75,
        'Not at-risk': 0.0001  # Invisible node at top
    }
    
    for cat in specific_topics:
        if cat in invisible_nodes:
            all_labels.append("")  # Empty label for invisible nodes
            all_colors.append("rgba(0,0,0,0)")  # Transparent color
            all_x_positions.append(2)  # Right column
            all_y_positions.append(0.0001)  # Push invisible nodes to very top
        else:
            all_labels.append(cat)
            all_colors.append(topic_colors.get(cat, '#BDC3C7'))
            all_x_positions.append(0.8)  # Right column
            all_y_positions.append(specific_y_positions.get(cat, 0.5))  # Use explicit position or default
    
    # Create mapping from category names to node indices
    node_mapping = {}
    idx = 0
    for cat in fameswap_categories:
        node_mapping[cat] = idx
        idx += 1
    for cat in broad_category_list:
        node_mapping[cat] = idx
        idx += 1
    for cat in specific_topics:
        node_mapping[cat] = idx
        idx += 1
    
    # Sort flows for consistent ordering
    broad_flows_sorted = broad_flows.copy()
    broad_flows_sorted['source_cat'] = pd.Categorical(
        broad_flows_sorted['fameswap_category'], 
        categories=fameswap_categories, 
        ordered=True
    )
    broad_flows_sorted['target_cat'] = pd.Categorical(
        broad_flows_sorted['broad_category'], 
        categories=broad_category_list, 
        ordered=True
    )
    broad_flows_sorted = broad_flows_sorted.sort_values(['source_cat', 'target_cat'])
    
    specific_flows_sorted = specific_flows.copy()
    specific_flows_sorted['source_cat'] = pd.Categorical(
        specific_flows_sorted['broad_category'], 
        categories=broad_category_list, 
        ordered=True
    )
    specific_flows_sorted['target_cat'] = pd.Categorical(
        specific_flows_sorted['specific_topic'], 
        categories=specific_topics, 
        ordered=True
    )
    specific_flows_sorted = specific_flows_sorted.sort_values(['source_cat', 'target_cat'])
    
    # Prepare data for sankey
    source = []
    target = []
    value = []
    link_colors = []
    
    # Add flows from FameSwap to broad categories - include ALL flows but make invisible ones transparent
    for _, row in broad_flows_sorted.iterrows():
        source.append(node_mapping[row['fameswap_category']])
        target.append(node_mapping[row['broad_category']])
        value.append(row['count'])
        
        if row['broad_category'] in invisible_nodes:
            # Make links to invisible nodes transparent
            link_colors.append("rgba(0,0,0,0)")
        else:
            broad_color = broad_colors.get(row['broad_category'], '#BDC3C7')
            link_colors.append(hex_to_rgba(broad_color, alpha=0.6))
    
    # Add flows from broad categories to specific topics - include ALL flows but make invisible ones transparent
    for _, row in specific_flows_sorted.iterrows():
        source.append(node_mapping[row['broad_category']])
        target.append(node_mapping[row['specific_topic']])
        value.append(row['count'])
        
        if row['specific_topic'] in invisible_nodes or row['broad_category'] in invisible_nodes:
            # Make links to/from invisible nodes transparent
            link_colors.append("rgba(0,0,0,0)")
        else:
            topic_color = topic_colors.get(row['specific_topic'], '#BDC3C7')
            link_colors.append(hex_to_rgba(topic_color, alpha=0.6))
    
    # Create the sankey diagram with explicit positioning
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0),  # Remove borders entirely
            label=all_labels,
            color=all_colors,
            x=all_x_positions,  # Explicit x positions
            y=all_y_positions   # Explicit y positions
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors
        )
    )])
    
    fig.update_layout(
        title_text="",
        font_size=20,
        width=600,
        height=1000
    )
    
    return fig

def create_sankey_plot(parquet_file="./data/sankey_data.parquet", proportional=True, 
                      save_html=None, save_png=None, save_pdf=None, show_plot=True):
    """
    Load data and create sankey diagram - all-in-one function
    
    Parameters:
    -----------
    parquet_file : str
        Path to the parquet file
    proportional : bool
        Whether to use proportional flows
    save_html : str or None
        Path to save HTML file
    save_png : str or None
        Path to save PNG file  
    save_pdf : str or None
        Path to save PDF file
    show_plot : bool
        Whether to display the plot
        
    Returns:
    --------
    df : DataFrame
        The loaded data
    fig : Plotly figure object
    """
    # Load the data
    df = load_sankey_data(parquet_file)
    
    # Create the plot
    print("Creating sankey diagram...")
    fig = create_sankey_diagram(df, proportional=proportional)
    
    if fig is None:
        print("Failed to create sankey diagram")
        return df, None
    
    # Save files if requested
    if save_html:
        fig.write_html(save_html)
        print(f"Saved HTML to {save_html}")
    
    if save_png:
        fig.write_image(save_png, width=600, height=1000, scale=2)
        print(f"Saved PNG to {save_png}")
    
    if save_pdf:
        fig.write_image(save_pdf, width=600, height=1000)
        print(f"Saved PDF to {save_pdf}")
    
    # Show plot if requested
    #if show_plot:
    #    fig.show()
    
    return df, fig

# Main execution
if __name__ == "__main__":
    # Simple usage - load data and create plot
    df, fig = create_sankey_plot(parquet_file='./data/sankey_data.parquet', save_html="./output/sankey.html")

    # Define the content categories
ideological_columns = ['political_content', 'news_content', 'manosphere_redpill_content', 'medical_health_content']
financial_columns = ['financial_content', 'gambling_content', 'cryptocurrency_content']

# Find accounts with ANY ideological content
has_ideological = df[ideological_columns].any(axis=1)

# Find accounts with ANY financial content  
has_financial = df[financial_columns].any(axis=1)

# Find accounts with EITHER ideological OR financial content
has_either = has_ideological | has_financial

# Find accounts with NEITHER ideological NOR financial content
has_neither = ~has_either

# Get the count and percentage
neither_count = has_neither.sum()
neither_percentage = has_neither.mean() * 100

print(f"Accounts with ideological content: {has_ideological.sum()}")
print(f"Accounts with financial content: {has_financial.sum()}")
print(f"Accounts with neither ideological nor financial content: {neither_count}")
print(f"Percentage: {neither_percentage:.1f}%")
print(f"Total accounts: {len(df)}")

# Of the 541 channels that have either ideological or financial content:
channels_with_either = has_ideological | has_financial  # This gives you your 541
subset_df = df[channels_with_either]

# Within this subset:
ideological_pct_within = subset_df[ideological_columns].any(axis=1).mean() * 100
financial_pct_within = subset_df[financial_columns].any(axis=1).mean() * 100

print(f"Of the 541 channels with ideological/financial content:")
print(f"  {ideological_pct_within:.1f}% have ideological content")
print(f"  {financial_pct_within:.1f}% have financial content")