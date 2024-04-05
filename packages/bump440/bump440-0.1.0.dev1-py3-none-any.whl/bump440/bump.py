# src/bump440/bump.py

from .versions import CurrentVersion, Epoch, Release, Pre, Post, Dev, Part


def bump(part: Part):
    if part == Part.CURRENT:
        print(CurrentVersion().get())
    elif part == Part.EPOCH:
        Epoch().bump()
    elif part == Part.RELEASE:
        Release().bump()
    elif part == Part.PRE:
        Pre().bump()
    elif part == Part.POST:
        Post().bump()
    elif part == Part.DEV:
        Dev().bump()
    else:
        raise ValueError(f"Invalid argument: {part}. Expected one of {list(Part)}.")


if __name__ == "__main__":
    bump()
