def inclusion(data: str, super_string: str) -> bool:
    return data in super_string


def min_length(data: str, min_length: int) -> bool:
    return len(data) >= min_length


def get_filter_mask(data: list[str], *fns):
    mask = [True] * len(data)
    for fn in fns:
        mask = [x and fn(data[i]) for i, x in enumerate(mask)]
      
    return mask

def apply_filter_pipeline(data: list[str], *fns):
    mask = get_filter_mask(data, *fns)
    return [data[i] for i, x in enumerate(mask) if x]