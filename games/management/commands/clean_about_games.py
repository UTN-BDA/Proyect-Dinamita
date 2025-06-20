import pandas as pd

base_path = (
    r"C:\Users\franb\OneDrive\Documents\GitHub\Proyect-Dinamita\dataset\tables\\"
)
games = pd.read_csv(base_path + "games.csv", usecols=["app_id"])
about = pd.read_csv(base_path + "about_game.csv")

about = about[about["app_id"].isin(games["app_id"])]

about.to_csv(base_path + "about_game.csv", index=False)
print("Solo se dejaron los app_id válidos.")
