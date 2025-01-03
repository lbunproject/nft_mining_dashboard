import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="LBUN NFT Mining Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    nft_details = pd.read_csv('nft_details.csv')
    winner_list = pd.read_csv('winner_list.csv')
    return nft_details, winner_list

def shorten_address(address):
    return f"{address[:6]}...{address[-5:]}" if isinstance(address, str) else address

def format_rewards(value):
    return f"{value:,.3f}"

# Load data
nft_details, winner_list = load_data()

# Assign a unique_id to each NFT based on row number (starting from 1)
nft_details = nft_details.reset_index(drop=True)
nft_details['unique_id'] = nft_details.index + 1  # unique_id starts at 1

# Shorten owner addresses for display
nft_details['short_owner'] = nft_details['owner'].apply(shorten_address)

# Parse 'minted' to datetime
nft_details['minted_date'] = pd.to_datetime(nft_details['minted'], format='%m/%d/%Y')

# Define today's date
today_date = pd.to_datetime('2025-01-02')

# Calculate 'life_left'
nft_details['life_left'] = 365 - (today_date - nft_details['minted_date']).dt.days
# Convert 'life_left' to string, replace negatives with 'Expired', and cap at 365
nft_details['life_left'] = nft_details['life_left'].apply(lambda x: str(min(x, 365)) if x >= 0 else 'Expired')

# Ensure consistent data types for merging
nft_details['unique_id'] = nft_details['unique_id'].astype(str)
winner_list['Winner (Row)'] = winner_list['Winner (Row)'].astype(str)

# Debugging: Check if all Winner (Row) entries have corresponding unique_id
unmatched_winners = winner_list[~winner_list['Winner (Row)'].isin(nft_details['unique_id'])]
if not unmatched_winners.empty:
    st.warning("There are unmatched Winner (Row) entries in winner_list.csv:")
    st.dataframe(unmatched_winners)
else:
    #st.success("All Winner (Row) entries successfully matched with nft_details.csv.")
    pass

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "Leaderboard"])

if page == "Dashboard":
    st.title('LBUN NFT Mining Dashboard')
    st.write("Explore the mining results over the year, including NFT performance, rewards, and more.")

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        equipment_types = ['All'] + sorted(nft_details['equipment'].unique())
        selected_equipment = st.selectbox('Select Equipment', options=equipment_types)
        wallet_addresses = ['All'] + sorted(nft_details['short_owner'].unique())
        selected_wallet = st.selectbox('Select Wallet Address', options=wallet_addresses)

    # Apply filters
    filtered_nft_details = nft_details.copy()
    if selected_equipment != 'All':
        filtered_nft_details = filtered_nft_details[filtered_nft_details['equipment'] == selected_equipment]
    if selected_wallet != 'All':
        filtered_nft_details = filtered_nft_details[filtered_nft_details['short_owner'] == selected_wallet]

    # Display filtered NFTs
    if selected_wallet != 'All':
        st.write(f"NFTs owned by {selected_wallet}:")
    else:
        st.write("All NFTs:")

    # Select columns to display (excluding 'unique_id')
    display_columns = ['token_id', 'market', 'equipment', 'boost', 'short_owner', 'minted', 'life_left']
    st.dataframe(
        filtered_nft_details[display_columns],
        use_container_width=False,
        hide_index=True
    )

    # Merge winner_list with filtered_nft_details for rewards and wins
    filtered_winner_list = winner_list.merge(
        filtered_nft_details[['unique_id', 'equipment', 'boost']],
        left_on='Winner (Row)',
        right_on='unique_id',
        how='inner'
    )

    # Ensure unique virtual blocks and calculate totals
    unique_blocks = filtered_winner_list.drop_duplicates(subset=['Virtual Block'])
    total_wins = unique_blocks['Virtual Block'].nunique()
    total_rewards = unique_blocks['Reward (BASE)'].sum()

    # Display totals
    st.write(f"### Total Wins: {total_wins}")
    st.write(f"### Total Rewards Earned: {format_rewards(total_rewards)} BASE")

    # Reward distribution
    if selected_equipment == 'All':
        # Pie chart for reward distribution by equipment
        reward_by_equipment = filtered_winner_list.groupby('equipment').agg(
            total_reward=('Reward (BASE)', 'sum')
        ).reset_index()

        # Calculate percentage for each slice
        total = reward_by_equipment['total_reward'].sum()
        reward_by_equipment['percent'] = 100 * reward_by_equipment['total_reward'] / total

        # Add a column to determine if the label should be shown
        reward_by_equipment['show_label'] = reward_by_equipment['percent'] > 5

        # Create the pie chart
        fig_pie = px.pie(
            reward_by_equipment,
            values='total_reward',
            names='equipment',
            title='Reward Distribution by Equipment',
            color_discrete_sequence=px.colors.sequential.Plasma
        )

        # Use `texttemplate` to conditionally show labels for slices with percentages > 5%
        fig_pie.update_traces(
            textinfo='none',  # Hide all labels initially
            texttemplate=reward_by_equipment.apply(
                lambda row: f"{row['percent']:.2f}%" if row['show_label'] else '',
                axis=1
            ),
            hovertemplate='<b>%{label}</b><br>Reward: %{value}<br>Percentage: %{percent}',
        )
    else:
        # Pie chart for reward distribution by boost levels for the selected equipment
        reward_by_boost = filtered_winner_list.groupby('boost').agg(
            total_reward=('Reward (BASE)', 'sum')
        ).reset_index()

        # Calculate percentage for each slice
        total = reward_by_boost['total_reward'].sum()
        reward_by_boost['percent'] = 100 * reward_by_boost['total_reward'] / total
        
        # Add a column to determine if the label should be shown
        reward_by_boost['show_label'] = reward_by_boost['percent'] > 3

        fig_pie = px.pie(
            reward_by_boost,
            values='total_reward',
            names='boost',
            title=f'Reward Distribution by Boost ({selected_equipment})',
            color_discrete_sequence=px.colors.sequential.Plasma
        )

        # Use `texttemplate` to conditionally show labels for slices with percentages > 5%
        fig_pie.update_traces(
            textinfo='none',  # Hide all labels initially
            texttemplate=reward_by_boost.apply(
                lambda row: f"{row['percent']:.2f}%" if row['show_label'] else '',
                axis=1
            ),
            hovertemplate='<b>%{label}</b><br>Reward: %{value}<br>Percentage: %{percent}',
        )

    st.plotly_chart(fig_pie, use_container_width=True)

    # NFT ownership distribution
    ownership_distribution = filtered_nft_details.groupby('short_owner').size().reset_index(name='nfts_owned')

    # Calculate percentage for each slice
    total = ownership_distribution['nfts_owned'].sum()
    ownership_distribution['percent'] = 100 * ownership_distribution['nfts_owned'] / total

    # Add a column to determine if the label should be shown
    ownership_distribution['show_label'] = ownership_distribution['percent'] > 3

    fig_ownership = px.pie(
        ownership_distribution,
        values='nfts_owned',
        names='short_owner',
        title=f'NFT Ownership Distribution ({selected_equipment if selected_equipment != "All" else "All Equipment"})',
        color_discrete_sequence=px.colors.sequential.RdBu
    )

    # Use `texttemplate` to conditionally show labels for slices with percentages > 5%
    fig_ownership.update_traces(
        textinfo='none',  # Hide all labels initially
        texttemplate=ownership_distribution.apply(
            lambda row: f"{row['percent']:.2f}%" if row['show_label'] else '',
            axis=1
        ),
        hovertemplate='<b>%{label}</b><br>Owned: %{value}<br>Percentage: %{percent}',
    )

    st.plotly_chart(fig_ownership, use_container_width=True)


elif page == "Leaderboard":
    st.title("Leaderboard Stats")

    # Calculate leaderboard stats
    # Merge winner_list with nft_details on unique_id
    rewards_by_owner = winner_list.merge(
        nft_details[['unique_id', 'owner']],
        left_on='Winner (Row)',
        right_on='unique_id',
        how='inner'
    )

    # Group by owner to calculate total rewards and total wins
    rewards_by_owner = rewards_by_owner.groupby('owner').agg(
        total_rewards=('Reward (BASE)', 'sum'),
        total_wins=('Virtual Block', 'nunique')  # Assuming each Virtual Block is a unique win
    ).reset_index()

    # Shorten owner addresses for display
    rewards_by_owner['short_owner'] = rewards_by_owner['owner'].apply(shorten_address)

    # NFTs owned by each owner
    nfts_owned = nft_details.groupby('owner').size().reset_index(name='nfts_owned')
    nfts_owned['short_owner'] = nfts_owned['owner'].apply(shorten_address)

    # Top ten owners by rewards
    st.subheader("Top Ten Owners by Rewards Won")
    top_rewards = rewards_by_owner.nlargest(10, 'total_rewards').copy()
    top_rewards['total_rewards'] = top_rewards['total_rewards'].apply(format_rewards)
    top_rewards = top_rewards.reset_index(drop=True).reset_index()
    top_rewards['Rank'] = top_rewards['index'] + 1  # Start numbering at 1
    st.dataframe(top_rewards[['Rank', 'short_owner', 'total_rewards']], use_container_width=False, hide_index=True)

    # **New Table: Top Ten Owners by Wins**
    st.subheader("Top Ten Owners by Wins")  # Added subheader
    top_wins = rewards_by_owner.nlargest(10, 'total_wins').copy()
    top_wins = top_wins.reset_index(drop=True).reset_index()
    top_wins['Rank'] = top_wins['index'] + 1  # Start numbering at 1
    st.dataframe(top_wins[['Rank', 'short_owner', 'total_wins']], use_container_width=False, hide_index=True)

    # Top ten owners by NFTs owned
    st.subheader("Top Ten Owners by NFTs Owned")
    top_nfts_owned = nfts_owned.nlargest(10, 'nfts_owned').copy()
    top_nfts_owned = top_nfts_owned.reset_index(drop=True).reset_index()
    top_nfts_owned['Rank'] = top_nfts_owned['index'] + 1  # Start numbering at 1
    st.dataframe(top_nfts_owned[['Rank', 'short_owner', 'nfts_owned']], use_container_width=False, hide_index=True)

    # Top ten equipment/boost combinations by rewards
    st.subheader("Top Ten Equipment/Boost by Rewards Won")
    rewards_by_boost = winner_list.merge(
        nft_details[['unique_id', 'equipment', 'boost']],
        left_on='Winner (Row)',
        right_on='unique_id',
        how='inner'
    )
    rewards_by_boost = rewards_by_boost.groupby(['equipment', 'boost']).agg(
        total_rewards=('Reward (BASE)', 'sum')
    ).reset_index()
    top_boost_rewards = rewards_by_boost.nlargest(10, 'total_rewards').copy()
    top_boost_rewards['total_rewards'] = top_boost_rewards['total_rewards'].apply(format_rewards)
    top_boost_rewards = top_boost_rewards.reset_index(drop=True).reset_index()
    top_boost_rewards['Rank'] = top_boost_rewards['index'] + 1  # Start numbering at 1
    st.dataframe(top_boost_rewards[['Rank', 'equipment', 'boost', 'total_rewards']], use_container_width=False, hide_index=True)

    # Bottom ten owners by rewards
    st.subheader("Bottom Ten Owners by Rewards Won")
    bottom_rewards = rewards_by_owner.nsmallest(10, 'total_rewards').sort_values(by='total_rewards', ascending=False).copy()
    bottom_rewards['total_rewards'] = bottom_rewards['total_rewards'].apply(format_rewards)
    bottom_rewards = bottom_rewards.reset_index(drop=True).reset_index()
    bottom_rewards['Rank'] = bottom_rewards['index'] + 1  # Start numbering at 1
    st.dataframe(bottom_rewards[['Rank', 'short_owner', 'total_rewards']], use_container_width=False, hide_index=True)

    # Bottom ten owners by wins
    st.subheader("Bottom Ten Owners by Wins")
    bottom_wins = rewards_by_owner.nsmallest(10, 'total_wins').sort_values(by='total_wins', ascending=False).copy()
    bottom_wins = bottom_wins.reset_index(drop=True).reset_index()
    bottom_wins['Rank'] = bottom_wins['index'] + 1  # Start numbering at 1
    st.dataframe(bottom_wins[['Rank', 'short_owner', 'total_wins']], use_container_width=False, hide_index=True)
