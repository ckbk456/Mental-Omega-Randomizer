"""Reuse installed SHP frames for build/sell artwork missing from objectives.

SHP(TS) stores independent frames: an eight-byte file header, 24-byte frame
headers and absolute payload offsets. Preserve the compressed bytes; no pixel
decoding, palette conversion or game artwork is shipped with the launcher.
Format reference: OpenRA.Mods.Common/SpriteLoaders/ShpTSLoader.cs.
"""

import struct


STRUCTURE_ART_REVISION = 2


def shp_frame_count(data):
    """Validate an installed/staged SHP header and return its frame count."""
    if len(data) < 8:
        raise ValueError('Construction SHP has no complete header.')
    marker, width, height, count = struct.unpack_from('<4H', data)
    if marker != 0 or not width or not height or count < 2:
        raise ValueError('Construction SHP needs a canvas and body/shadow frames.')
    header_end = 8 + 24 * count
    if header_end > len(data):
        raise ValueError('Construction SHP frame headers are truncated.')
    for index in range(count):
        offset = 8 + 24 * index
        compression = data[offset + 8]
        payload = struct.unpack_from('<I', data, offset + 20)[0]
        if compression > 3 or (payload and not header_end <= payload < len(data)):
            raise ValueError('Construction SHP has an invalid frame payload.')
    return count


def static_structure_buildup(data):
    """Make one healthy construction step and its matching shadow.

    Native building sprites put shadows in their second half. A missing shadow
    uses a zero payload offset and stays empty. Each copied compressed frame is
    independent, so only its absolute offset changes in the two-frame container.
    """
    count = shp_frame_count(data)
    if count % 2:
        raise ValueError('Building SHP body/shadow frame count must be even.')
    offsets = sorted({
        struct.unpack_from('<I', data, 8 + 24 * index + 20)[0]
        for index in range(count)
    } - {0})
    ends = dict(zip(offsets, offsets[1:] + [len(data)]))
    headers = []
    payloads = []
    position = 8 + 2 * 24
    for index in (0, count // 2):
        start = 8 + index * 24
        header = bytearray(data[start:start + 24])
        source_offset = struct.unpack_from('<I', header, 20)[0]
        if source_offset:
            payload = data[source_offset:ends[source_offset]]
            struct.pack_into('<I', header, 20, position)
            payloads.append(payload)
            position += len(payload)
        headers.append(header)
    if not struct.unpack_from('<I', headers[0], 20)[0]:
        raise ValueError('Building SHP has no healthy body frame.')
    result = data[:6] + struct.pack('<H', 2) + b''.join(headers + payloads)
    shp_frame_count(result)
    return result
