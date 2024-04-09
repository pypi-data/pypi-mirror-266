from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature
from nltk.corpus import stopwords
import panel as pn
import panel as pn


class FeatureBertopic(ParentGeovizFeature):
    def getOptionName(self):
        return "nlp_bertopics"

    def getRequiredColumns(self):
        return ["description_column"]

    def getHeaderText(self):
        return "Bertopics Intertopic Map"

    def _generateComponent(self):
        model, topics = self.generated_data.data_dict["nlp_bertopics"]
        self.df["BERTopic_label"] = topics

        topics_info = model.get_topic_info()

        mapping = {}
        for i, representation in enumerate(topics_info["Representation"]):
            mapping[i - 1] = representation  # Since "BERTopic_label" starts from -1

        # Map the values from topics_info["Representation"] to "BERTopic_label" in df
        self.df["bert_representation"] = self.df["BERTopic_label"].map(mapping)
        self.df["bert_representation"] = self.df["bert_representation"].apply(
            lambda x: ", ".join(x)
        )

        topics_df = model.get_topics()
        num_topics = len(topics_df)
        display_num_topics = pn.Column(
            f"The number of topics found by BERTopic is: {num_topics}"
        )
        top_ten_topics_info = pn.Column(
            model.get_topic_info()
            .head(10)
            .set_index("Topic")[["Count", "Name", "Representation"]]
        )

        bert = pn.Column(
            display_num_topics, model.visualize_topics(), top_ten_topics_info
        )
        return bert
