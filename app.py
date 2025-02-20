from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import ast
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO

app = Flask(__name__)

# Load Data
dp = pd.read_csv(r"data\Detailed_Property.csv")   # Property details
pbp = pd.read_csv(r"data\property_by_place.csv")  # Location insights
pr = pd.read_csv(r"data\property_reviews.csv")    # Reviews

@app.route('/')
def index():
    # Guest Satisfaction Histogram
    fig1 = px.histogram(dp, x="guestSatisfactionOverall", nbins=20, 
                        title="📊 Guest Satisfaction Distribution", 
                        color_discrete_sequence=["#FAD02E"])
    graph1 = fig1.to_html(full_html=False)

    # Room Type Distribution
    fig2 = px.pie(dp, names="roomType", title="🏠 Distribution of Room Types", hole=0.4)
    graph2 = fig2.to_html(full_html=False)

    # Price vs Ratings Scatter Plot
    pbp["numeric_price"] = pbp["price"].str.replace(r"[^\d.]", "", regex=True).astype(float)
    fig3 = px.scatter(pbp, x="numeric_price", y="avgRating", title="💰 Price vs Ratings",
                      trendline="ols", color="avgRating", color_continuous_scale="Viridis",
                      hover_data={"price": True, "title": True, "city": True, "numeric_price": False})
    graph3 = fig3.to_html(full_html=False)

    # Number of Listings by City
    fig4 = px.bar(pbp["city"].value_counts().reset_index(), 
                  x="index", y="city", title="🏙️ Number of Listings by City",
                  labels={"index": "City", "city": "Number of Listings"},
                  color_discrete_sequence=["#636EFA"])
    graph4 = fig4.to_html(full_html=False)

    # Correlation Heatmap
    rating_cols = ["guestSatisfactionOverall", "cleanlinessRating", "communicationRating",
                   "locationRating", "accuracyRating", "valueRating"]
    corr_matrix = dp[rating_cols].corr()
    fig5 = ff.create_annotated_heatmap(z=np.round(corr_matrix.values, 2), x=rating_cols, y=rating_cols,
                                       colorscale="Viridis", showscale=True)
    fig5.update_layout(title="🔍 Factors Affecting Guest Satisfaction")
    graph5 = fig5.to_html(full_html=False)

    # Bedroom Count vs Ratings
    fig6 = px.box(pbp, x="bedrooms", y="avgRating", title="🛏️ How Bedroom Count Affects Ratings", color="bedrooms")
    fig6.update_layout(xaxis_title="Number of Bedrooms", yaxis_title="Average Rating")
    graph6 = fig6.to_html(full_html=False)

    # Superhost vs Ratings
    fig7 = px.box(pbp, x="isSuperhost", y="avgRating", title="⭐ Do Superhosts Get Better Ratings?",
                  color="isSuperhost", labels={"isSuperhost": "Superhost Status", "avgRating": "Average Rating"})
    graph7 = fig7.to_html(full_html=False)

    # Word Cloud for Amenities
    amenities_list = []
    for groups in dp["sections.amenities.seeAllAmenitiesGroups"].dropna():
        try:
            if isinstance(groups, str):
                groups = ast.literal_eval(groups)
            if isinstance(groups, list):
                for group in groups:
                    if isinstance(group, dict) and "amenities" in group:
                        for amenity in group["amenities"]:
                            if isinstance(amenity, dict) and "title" in amenity and amenity.get("available", True):
                                amenities_list.append(amenity["title"])
        except (ValueError, SyntaxError):
            continue

    wordcloud_img = None
    if amenities_list:
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(amenities_list))
        img = BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        wordcloud_img = base64.b64encode(img.getvalue()).decode()

    return render_template('index.html', graph1=graph1, graph2=graph2, graph3=graph3, 
                           graph4=graph4, graph5=graph5, graph6=graph6, graph7=graph7,
                           wordcloud_img=wordcloud_img)

if __name__ == '__main__':
    app.run(debug=True)
