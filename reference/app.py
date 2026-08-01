import streamlit as st 
import json
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

print("running")


st.title("Business Location Explorer")
st.write("IAT 459")

# load data function
@st.cache_data
def load_data(path="business_locations.geojson"):
    with open(path) as f:
        geojson = json.load(f)
    rows = [] #rows in the geojson
    #this function can read geojson files that have only points (other type of features will throw error)
    for feat in geojson["features"]:
        props = feat["properties"]
        lon, lat = feat["geometry"]["coordinates"]
        rows.append({**props, "lon":lon, "lat":lat})
    return pd.DataFrame(rows)

#call function and load dataframe
df = load_data()

#--------SCALING THE DATA--------#
#quickly grab column names (this gets displayed)
# st.write(df.columns)
# ID
# Neighborhood
# Category
# Subcategory
# Floor_Area_sqm
# Daily_Foot_Traffic
# Community_Impact_Score
# Annual_Revenue_k
# lon
# lat

#-------- HOT-CODING NUMERIC COLUMNS/FEATURES --------
#Put everything in sidebar
st.sidebar.header("1. Select Features")
NUMERIC_COLS = ["Floor_Area_sqm","Daily_Foot_Traffic","Community_Impact_Score","Annual_Revenue_k"]
X = df[NUMERIC_COLS].to_numpy()
X_scaled = StandardScaler().fit_transform(X)
# to preview: st.write(X_scaled)

#selected features becomes an interactive array
selected_features = st.sidebar.multiselect("Features to be used in models", options=NUMERIC_COLS, default=NUMERIC_COLS)
# st.write(selected_features)

# have to have at least 2 features to run algorithims on, so create rule
# if < 2 features, stop all code
if len(selected_features) < 2:
    st.warning('Pick at least two features to continue')
    st.stop()

#-------- MODELS / ALGORITHIM SIDE BAR --------#
#Put everything in sidebar
st.sidebar.header("2. Clustering")
#Select model type
algo = st.sidebar.selectbox('Algorithim',["Kmeans", "DBSCAN"])
#Conditional rendering based on algorithim
#--------K-MEANS CLUSTERING / DBSCAN --------#
# Paramater tuning
if algo == "Kmeans":
    K = st.sidebar.slider("Number of Clusters", 2,10)
elif algo == "DBSCAN":
    #epsilon slider (radius)
    eps = st.sidebar.slider("Epsilon (eps)", min_value=0.1, max_value=5.0, value=0.5, step=0.1)
    # samples, min points to form cluster
    min_samples = st.sidebar.slider("Min Samples", min_value=2, max_value=15, step=1, value=5)
    # st.write("ADD DBSCAN PARAMETERS")

#create labels as empty array
labels = None

# OUTPUT
if algo == "Kmeans":
    model = KMeans(n_clusters=K)
    labels = model.fit_predict(X_scaled)
elif algo == "DBSCAN":
    # st.write("ADD DBSCAN HERE")
    min_samples_int = int(min_samples)
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X_scaled)

# Catch error if no labels do not continue
if labels is None or len(labels) == 0: 
    st.warning("there is no clustering labels")
    st.stop()

#to preview cluster labels: st.write(labels)
#add to dataframe, type cast into categorical labels
df["cluster"] = pd.Categorical(labels.astype(str))
# to check: st.dataframe(df.head())
n_clusters_found = df["cluster"].nunique()
st.metric("Number of clusters", n_clusters_found)

#--------UI & DISPLAY--------#
#display with expander
with st.expander("Look at Dataset"):
    st.dataframe(df.head(20))
    st.write('''
        Our business locations in the geojson.
    ''')
    f"{len(df)} locations, {df["Neighborhood"].nunique()} neighborhoods"

#pass list to tabs
map_tab, dr_tab = st.tabs(["Map", "Dimensionality Reduction"])

with map_tab:
    #create scattermap with plotly
    fig = px.scatter_map(
    df, lat="lat", lon="lon", zoom=10, height=550, map_style="carto-darkmatter", color="cluster"
    )
    #display map
    st.plotly_chart(fig, width="stretch")

with dr_tab:
    reducer = PCA(n_components=2,random_state=42)
    embedding = reducer.fit_transform(X_scaled)
    df["dim_1"] = embedding[:,0]
    df["dim_2"] = embedding[:,1]

    fig_dr  = px.scatter(
        df, 
        x="dim_1",
        y="dim_2",
        color="cluster",
        height = 550
    )
    st.plotly_chart(fig_dr,width="stretch")