from .type import Metadata


def find_closest_metadata(source_metadata, candidates):
    if len(candidates) == 0:
        return None
    if len(candidates) == 1:
        return candidates[0]

    targets = candidates
    targets = [
        candidate for candidate in targets
        if candidate["data_representation"] == source_metadata["data_representation"]
    ]
    if len(targets) == 0:
        targets = candidates

    color_matched_targets = [
        candidate for candidate in targets
        if candidate["color_channel"] == source_metadata["color_channel"]
    ]
    if len(color_matched_targets) == 0:
        if source_metadata["color_channel"] in ["rgb", "bgr"]:
            for metadata in targets:
                if metadata["color_channel"] in ["rgb", "bgr"]:
                    return metadata
    return targets[0]


def decode_separator():
    return '_'


def encode_metadata(metadata: dict) -> str:
    return decode_separator().join([str(metadata[key]) for key in Metadata.__annotations__.keys()])


def decode_metadata(metadata_str: str) -> dict:
    metadata_list = metadata_str.split(decode_separator())
    metadata = {k: v for k, v in zip(list(Metadata.__annotations__.keys()), metadata_list)}
    metadata['minibatch_input'] = True if metadata['minibatch_input'] == 'True' else False
    return metadata
