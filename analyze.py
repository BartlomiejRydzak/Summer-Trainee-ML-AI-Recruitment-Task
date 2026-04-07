import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

def load_data(path="dblp_sample.csv"):
    df = pd.read_csv(path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year", "title"])
    df["authors"] = df["authors"].apply(
        lambda x: x.split(";") if isinstance(x, str) else []
    )
    return df

def plot_publications_per_year(df):
    pubs_per_year = df.groupby("year").size()
    plt.figure()
    pubs_per_year.plot()
    plt.title("Publications per Year")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

def top_venues(df, n=10):
    print("\n=== TOP VENUES ===")
    print(df["booktitle"].value_counts().head(n))

def top_authors(df, n=10):
    print("\n=== TOP AUTHORS ===")
    df_exploded = df.explode("authors")
    print(df_exploded["authors"].value_counts().head(n))

def build_collaboration_graph(df, limit=50000):
    G = nx.Graph()
    for _, row in df.head(limit).iterrows():
        authors = row["authors"]
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                if G.has_edge(authors[i], authors[j]):
                    G[authors[i]][authors[j]]["weight"] += 1
                else:
                    G.add_edge(authors[i], authors[j], weight=1)
    return G

def analyze_graph(G):
    print("\n=== GRAPH STATS ===")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    degree = dict(G.degree())
    top = sorted(degree.items(), key=lambda x: -x[1])[:10]
    print("\nTop collaborators:")
    for name, deg in top:
        print(f"  {name}: {deg}")

def keyword_trends(df, keywords):
    plt.figure()
    for kw in keywords:
        trend = (
            df[df["title"].str.contains(kw, case=False, na=False)]
            .groupby("year")
            .size()
        )
        trend.plot(label=kw)
    plt.legend()
    plt.title("Keyword Trends Over Time")
    plt.xlabel("Year")
    plt.ylabel("Publications")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df = load_data("dblp_sample.csv")

    plot_publications_per_year(df)
    top_venues(df)
    top_authors(df)

    G = build_collaboration_graph(df)
    analyze_graph(G)

    keyword_trends(df, ["machine learning", "deep learning", "neural network", "database"])