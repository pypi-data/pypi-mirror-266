import cv2
from .helpers import danger
from .classes.Repository import Repository


def path(directory: str) -> None:
    Repository.directory = directory


def write(key: str, filename: str) -> None:
    cv2.imwrite(
        filename=filename,
        img=Repository.images[key]
    )


def save(*args, **kwargs) -> None:
    write(args, kwargs)


def image(filename: str, key: str | None = None, color: bool = True) -> None:
    # TODO: add no extension in the file
    if key is None:
        key = filename.split(".")[0]

    Repository.images[key] = cv2.imread(filename, int(color))
    return Repository.images[key]


def wait(delay=0):
    cv2.waitKey(delay)


def showWait(*args, **kwargs):
    kwargs["wait"] = True
    show(*args, **kwargs)


def show(key: any = None, wait: bool = False, window: str = "Homa Window") -> None:
    # TODO: add functionality to distinguish between camera and images

    if key is not None and not isinstance(key, str):
        Repository.imshow(window, key)

    elif key is None:
        for key, image in Repository.images.items():
            Repository.imshow(key, image)

    elif key is not None:
        if key in Repository.images:
            Repository.imshow(key, Repository.images[key])
        else:
            danger(f"No image found with key {key}")

    if wait:
        cv2.waitKey(0)
