CHUNK_SIZE = 1024 * 1024
VALID_DOWNLOAD_FILES = ["fields", "time_series", "results"]


def download_write_chunks(filename, res):
    file = open(filename, "wb")
    file_size = float(res.headers["Content-Length"])
    downloaded = 0
    for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            file.write(chunk)
            downloaded += len(chunk)
            print(
                "Downloaded {:>5.1%}\r".format(downloaded / file_size),
                end="",
                flush=True,
            )
    file.close()
