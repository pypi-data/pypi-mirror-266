import pooch


file_path = pooch.retrieve(
    # URL to one of Pooch's test files
    url="https://github.com/fatiando/pooch/raw/v1.0.0/data/tiny-data.txt",
    #known_hash="md5:70e2afd3fd7e336ae478b1e740a5f08e",
    known_hash=None,
)


print(file_path)

