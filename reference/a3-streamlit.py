import json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# PAGE CONFIG
st.set_page_config(page_title="Vancouver Neighborhood Clustering", layout="wide")

st.title("Neighborhood Similarity Explorer")
st.write("IAT 459 — Part B: Area-Level Business Composition Analysis")

# load data function
@st.cache_data
def load_data(path="vancouver_business_licences_clean.csv"):
    df_raw = pd.read_csv(path)
    return df_raw

#call function and load dataframe
df_active = load_data()


#-------- AREA FILTERING --------
AREA_COL = "localarea"
# remove rows with missing localarea values
df_clean = df_active.dropna(subset=[AREA_COL]).copy()
# how many total businesses are in each neighborhood
area_counts = df_clean[AREA_COL].value_counts()

# keep only neighborhoods above the cutoff threshold
# justification: Smaller areas are more likely to create huge skews in data for business distrubution.
# 25 was chosen because it keeps at least one business for each neighborhood
MIN_BUSINESS_CUTOFF = 25
valid_areas = area_counts[area_counts >= MIN_BUSINESS_CUTOFF].index
df_filtered = df_clean[df_clean[AREA_COL].isin(valid_areas)]

if len(df_filtered) == 0:
    st.warning("No neighborhoods meet the current cutoff threshold!")
    st.stop()

#-------- CROSSTABS / FEATURES --------

# - Rows = Neighborhoods (Areas)
# - Columns = Business Categories
X_area_pct = pd.crosstab(
    df_filtered[AREA_COL], 
    df_filtered["business_category"], 
    normalize="index"
) * 100

# centroid coordinates (lat/lon) for each neighborhood
area_coords = (
    df_filtered.groupby(AREA_COL)[["latitude", "longitude"]]
    .mean()
    .reset_index()
    .rename(columns={"longitude": "lon", "latitude": "lat"})
)

# merge centroids with business count
area_df = area_coords.merge(
    area_counts.rename("business_count").reset_index(), 
    left_on=AREA_COL, 
    right_on=AREA_COL
)

#-------- SIDEBAR: BUSINESS CATEGORIES --------

all_categories = list(X_area_pct.columns)
selected_categories = st.sidebar.multiselect(
    "Select Business Categories for Clustering", 
    options=all_categories, 
    default=all_categories
)
if len(selected_categories) < 2:
    st.warning("Select at least two business categories!")
    st.stop()

X_matrix = X_area_pct[selected_categories].values

#-------- SIDEBAR: K-MEANS CLUSTERING MODEL --------
st.sidebar.header("Clustering Model")

# interactive slider for K
K = st.sidebar.slider("Number of Clusters (K)", min_value=2, max_value=10, value=4, step=1)
# Extract feature matrix array
X_matrix = X_area_pct.values
#Fit to K-means model
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
area_labels = kmeans.fit_predict(X_matrix)

#small summary
st.sidebar.write(f"**Total Neighborhoods:** {len(valid_areas)}")
st.sidebar.write(f"**Business Cutoff:** $\ge$ {MIN_BUSINESS_CUTOFF} businesses")

#-------- EXPANDER: DATASET --------
area_df["cluster"] = pd.Categorical(area_labels.astype(str))
st.metric("Analyzed Neighborhoods", len(area_df))
with st.expander("Area/Neighborhood Matrix (Business by share %)"):
    st.dataframe(X_area_pct.round(2))
    st.caption(f"{len(X_area_pct)} neighborhoods x {X_area_pct.shape[1]} business types.")

#--------UI & DISPLAY--------#
#pass list to tabs
map_tab, dr_tab, membership_tab = st.tabs([
    "Cluster Map", 
    "Dimensionality Reduction (PCA)", 
    "Cluster breakdown"
])

# --- TAB 1: MAP CLUSTER ---

with map_tab:
    st.subheader("Neighborhood Centroids Map")
    
    fig_map = px.scatter_map(
        area_df, 
        lat="lat", 
        lon="lon", 
        color="cluster",
        size="business_count",
        hover_name=AREA_COL,
        hover_data={"business_count": True, "lat": False, "lon": False},
        zoom=10, 
        height=550, 
        map_style="carto-darkmatter",
        title=f"Neighborhood Centroid Clusters (K = {K})"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# --- TAB 2: PCA DIMENSIONALITY REDUCTION ---
with dr_tab:
    st.subheader("2D PCA Composition Feature Space")
    
    # 2D PCA reduction
    pca = PCA(n_components=2, random_state=42)
    embedding = pca.fit_transform(X_matrix)
    
    area_df["dim_1"] = embedding[:, 0]
    area_df["dim_2"] = embedding[:, 1]
    var = pca.explained_variance_ratio_
    
    fig_dr = px.scatter(
        area_df, 
        x="dim_1", 
        y="dim_2", 
        color="cluster",
        hover_name=AREA_COL,
        labels={
            "dim_1": f"PCA Component 1 ({var[0]*100:.1f}% Variance)",
            "dim_2": f"PCA Component 2 ({var[1]*100:.1f}% Variance)"
        },
        height=550,
        title="PCA Projection of Area Business Mix"
    )
    st.plotly_chart(fig_dr, use_container_width=True)

# --- TAB 3: CLUSTER MEMBERSHIP & INTERPRETATION ---
with membership_tab:
    st.subheader("Cluster Membership & Dominant Business Profiles")
    
    # Select cluster
    cluster_list = sorted(area_df["cluster"].unique())
    selected_cluster = st.selectbox("Select Cluster to Inspect:", cluster_list)
    
    # Get members
    members = area_df[area_df["cluster"] == selected_cluster][AREA_COL].tolist()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"### Neighborhoods in Cluster `{selected_cluster}` ({len(members)})")
        for m in members:
            st.markdown(f"- **{m}**")
            
    with col2:
        st.markdown(f"### Average Business % Mix for Cluster `{selected_cluster}`")
        cluster_crosstab = X_area_pct.loc[X_area_pct.index.isin(members)]
        avg_mix = cluster_crosstab.mean().sort_values(ascending=False).head(8).reset_index()
        avg_mix.columns = ["Business Category", "Avg %"]
        
        fig_bar = px.bar(
            avg_mix, 
            x="Avg %", 
            y="Business Category", 
            orientation='h',
            title=f"Top Defining Categories for Cluster {selected_cluster}",
            height=400
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)


st.subheader("Markdown")

st.markdown("""
1. **Does the grouping seem meaningful given what you know (or can look up) about these areas? Any surprising groupings? Explain using the actual cluster membership, not just the general shape of the plot.**

Neighborhoods with similar business environments naturally pair up. For example, commercial and office hubs like **Downtown** and **Fairview** group together because they are full of corporate offices, shops, and restaurants. They are touristy destinations.

Quieter residential areas like **Dunbar-Southlands** and **Kerrisdale** form their own group, 
made up mostly of local health clinics, personal services, and small home businesses.
""")
