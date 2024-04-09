from rrcgeoviz.datagenerators.ParentDataGenerator import ParentDataGenerator
from bertopic import BERTopic
import re
import nltk
from nltk.corpus import stopwords
import pycountry


class GeneratorBertopic(ParentDataGenerator):
    def getOptionName(self):
        return "nlp_bertopics"

    def generateData(self):
        print("Generating Bertopic Model...")
        model = self.createModelInstance()
        return model

    def cleanData(self):
        # Get a list of country names and abbreviations
        country_names = [country.name.lower() for country in pycountry.countries]
        country_codes = [country.alpha_2.lower() for country in pycountry.countries]

        # Text cleaning and preprocessing
        self.data["description"] = self.data[
            "description"
        ].str.lower()  # Convert to lowercase

        # Define a function to preprocess each description
        def preprocess_description(text):
            if isinstance(text, str):  # Check if the value is a string
                # Remove months of the year
                text = re.sub(
                    r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b",
                    "",
                    text,
                )
                # Remove countries
                country_patterns = "|".join(country_names + country_codes)
                text = re.sub(r"\b(?:" + country_patterns + r")\b", "", text)
                # Remove "local time"
                text = re.sub(r"local time", "", text)
                # Remove special characters and punctuation
                text = re.sub(r"[^a-zA-Z\s]", "", text)
                # Remove stopwords
                stop_words = set(stopwords.words("english"))
                return " ".join(
                    [word for word in text.split() if word not in stop_words]
                )
            else:
                return ""  # Return an empty string for NaN values

        self.data["description"] = self.data["description"].apply(
            preprocess_description
        )

        # Drop rows with missing descriptions
        self.data = self.data.dropna(subset=["description"])

        # Reset the index after dropping rows
        self.data = self.data.reset_index(drop=True)

    def createModelInstance(self):
        self.cleanData()

        model = BERTopic(nr_topics="auto")
        # Fit BERTopic on the data
        topics, _ = model.fit_transform(self.data["description"])

        # Add the topic labels as a new column in the dataset
        self.data["BERTopic_label"] = topics
        return model, topics
