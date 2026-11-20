Vanisha’s Summary:
For this milestone, I focused on inspecting and cleaning the Employment in Agrifood System (AFS.csv) from World Bank Data360. The original dataset contained 4287 observations from across 172 countries covering the years 2000-2024. I filtered the dataset to only contain US observations, since our project is focusing specifically on the United States.

During the inspection and exploration process, I saw that the dataset contained 25 annual observations for the US and that the available employment indicator, Off-Farm Employment Share, was measured as a percentage. There were no missing values or duplicate records in the US subsection, while the original dataset contained 74 missing employment values for global observations.

I created a Python notebook to document this process, including examining column names and data types, checking for missing values and duplicates, filtering the data to suit our project’s needs, and standardizing data types and syntax. I exported the cleaned dataset as a CSV file to prepare it for integration with the other datasets.

One challenge I ran into was that the dataset only indicates employment through Off-Farm Employment Share percentage, not a separate On-Farm percentage, which we’ll have to consider when forming a conclusion.
