from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature
import panel as pn
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class FeatureWordCloud(ParentGeovizFeature):
    def getOptionName(self):
        return "nlp_bertopics"

    def getRequiredColumns(self):
        return ["description_column"]

    def getHeaderText(self):
        return "Word Clouds for Bertopic Labels"

    def _generateComponent(self):
        model, topics = self.generated_data.data_dict["nlp_bertopics"]
        topics_df = model.get_topics()
        num_topics = len(topics_df)
        word_clouds = self.generate_word_clouds(
            self.df, "BERTopic_label", "bert_representation", num_topics
        )
        labels = sorted(self.df["BERTopic_label"].unique().tolist())
        dropdown = pn.widgets.Select(name="BERTopic Label", options=labels, value=-1)

        def display_word_cloud(label_index):
            return word_clouds[label_index]

        word_cloud_display = pn.bind(display_word_cloud, label_index=dropdown)

        component = pn.Column(dropdown, word_cloud_display)
        return component

    # Function to generate word clouds for each cluster
    def generate_word_clouds(self, df, cluster_column, text_column, num_clusters):
        # Initialize an empty dictionary to store cluster texts
        word_clouds = {}

        # Iterate over each cluster
        for cluster_id in range(-1, num_clusters - 1):
            # Filter the DataFrame to include only data points belonging to the current cluster
            cluster_df = df[df[cluster_column] == cluster_id]
            # Concatenate all descriptions within the cluster into a single string
            cluster_text = " ".join(cluster_df[text_column].values)
            # Generate word cloud
            wordcloud = WordCloud(
                width=400, height=200, background_color="white"
            ).generate(cluster_text)

            plt.figure(figsize=(6, 3))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.title(f"Cluster {cluster_id} Word Cloud")
            plt.axis("off")
            word_clouds[cluster_id] = pn.pane.Matplotlib(plt.gcf())
            plt.close()
        return word_clouds
