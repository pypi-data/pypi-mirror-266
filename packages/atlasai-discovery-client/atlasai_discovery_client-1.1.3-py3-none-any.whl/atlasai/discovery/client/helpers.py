from collections import namedtuple
import json

import arrow
from shapely import geometry, wkb, wkt
import semver

from . import schema
from .misc import build_input_builder

ENCODED_PATH = 'encoded:'

BigQueryPath = namedtuple(
    'BigQueryPath',
    ['project_id', 'table_id', 'query'],
    defaults=[None, None],
)

CloudSQLPath = namedtuple(
    'CloudSQLPath',
    ['connection_name', 'database', 'table', 'query'],
    defaults=[None, None],
)

def encode_json(value, default_fn=lambda: dict()):
    value = value or default_fn()
    return json.dumps(value)

def encode_tags(tags):
    tags = tags or []
    if isinstance(tags, str):
        tags = dict([
            [
                x.strip()
                for x in tag.strip().split(':')
            ]
            for tag in tags.split(',')
        ])

    if isinstance(tags, dict):
        tags = [
            {
                'name': k,
                'value': v
            }
            for k, v in tags.items()
        ]

    for tag in tags:
        if not isinstance(tag, (dict, schema.TagInput)):
            raise ValueError('Every tag must be a dictionary: {"name": TAG_NAME, "value": TAG_VALUE}')
        elif 'name' not in tag:
            raise ValueError('Every tag must have the following keys: name, value')
        elif 'value' not in tag:
            raise ValueError('Every tag must have the following keys: name, value')

    return [
        (
            schema.TagInput(**tag)
            if isinstance(tag, dict)
            else tag
        )
        for tag in tags
    ]

def encode_assets(assets):
    # if string, treat as path
    if isinstance(assets, str):
        assets = [assets]

    # if dict, treat as key, value dictionary: {"path": "tags"}
    if isinstance(assets, dict):
        assets = [
            {
                'path': path,
                'tags': encode_tags(tags),
            }
            for path, tags in assets.items()
        ]

    for idx in range(len(assets)):
        asset = assets[idx]

        # if string, treat as path
        if isinstance(asset, str):
            asset = assets[idx] = {
                'path': asset
            }
        elif isinstance(asset, dict):
            if 'tags' in asset:
                asset['tags'] = encode_tags(asset['tags'])
            if 'scan_config' in asset:
                asset['scan_config'] = encode_json(asset['scan_config'])
            if 'metadata' in asset:
                asset['metadata'] = encode_json(asset['metadata'])
            if 'extent' in asset:
                asset['extent'] = encode_json(asset['extent'])

    # resolve encoded paths
    for asset in assets:
        if isinstance(asset['path'], (BigQueryPath, CloudSQLPath)):
            asset['path'] = ENCODED_PATH + json.dumps(asset['path']._asdict())

    return [
        schema.AssetInput(**asset)
        for asset in assets
    ]

def encode_str_list(str_list):
    if isinstance(str_list, str):
        str_list = [str_list]

    deduped = []
    for id_ in str_list:
        if not isinstance(id_, str):
            id_ = str(id_)
        if id_ not in deduped:
            deduped.append(id_)

    return deduped

def encode_date_range(date_range):
    if not date_range:
        return schema.DateRangeInput(empty=True)

    val = schema.DateRangeInput(
        include_lower=True,
        include_upper=False,
        empty=False,
    )
    # [YYYY-MM-DDTHH::II::SSZ, YYYY-MM-DDTHH::II::SSZ)
    if isinstance(date_range, str):
        date_range = list(date_range.strip())
        if date_range[0] in ('(', '['):
            char = date_range.pop(0)
            if char == '(':
                val.include_lower = False
        if date_range[-1] in (')', ']'):
            char = date_range.pop(-1)
            if char == ']':
                val.include_upper = True

        parts = [
            x.strip()
            for x in ''.join(date_range).split(',')
        ]
        for idx, part in enumerate(parts):
            if not part:
                continue
            elif idx > 1:
                break

            part = arrow.get(part).isoformat()
            if idx == 0:
                val.lower = part
            elif idx == 1:
                val.upper = part
    elif isinstance(date_range, dict):
        if date_range.get('empty') is True:
            return schema.DateRangeInput(empty=True)

        for k in ('lower', 'upper', 'include_lower', 'include_upper'):
            v = date_range.get(k)
            if v is None:
                continue
            if k in ('lower', 'upper'):
                setattr(val, k, arrow.get(v).isoformat())
            elif k in ('include_lower', 'include_upper'):
                setattr(val, k, bool(v))

    return val

def encode_semver(value):
    return str(semver.VersionInfo.parse(value))

def in_(possibilities):
    def wrapper(value):
        if value not in possibilities:
            raise ValueError(f'Unknown value: {value}. Permitted values: {list(possibilities)}')

        return value

    return wrapper

def encode_geojson(value):
    if isinstance(value, str):
        # geojson?
        try:
            shape = geometry.shape(json.loads(value))
        except Exception:
            pass
        else:
            return geometry.mapping(shape)

        # wkt?
        try:
            shape = wkt.loads(value)
        except Exception:
            pass
        else:
            return geometry.mapping(shape)

        # wkb
        try:
            shape = wkb.loads(value)
        except Exception:
            pass
        else:
            return geometry.mapping(shape)
    elif isinstance(value, dict):
        try:
            value = geometry.shape(value)
        except Exception:
            pass
        else:
            return value
    elif isinstance(value, geometry.base.BaseGeometry):
        return geometry.mapping(shape)

    raise ValueError(f'Unknown geometry provided: {value}')

def encode_order_by(value):
    #
    # "ENTITY [desc|asc][,ENTITY [desc|asc][,ENTITY [desc|asc]]]"
    #
    if not value:
        return []

    clauses = [
        v.strip()
        for v in value.split(',')
    ]
    clauses = [
        [
            part.strip()
            for part in clause.rsplit(' ', 1)
        ]
        for clause in clauses
    ]
    clauses = [
        schema.OrderByInput(
            field=clause[0],
            direction=(
                clause[-1]
                if len(clause) > 1
                else 'asc'
            )
        )
        for clause in clauses
    ]

    return clauses

search_build_input = build_input_builder({
    'order_by': encode_order_by,
})

def decode_geometry(geom):
    if isinstance(geom, str):
        return geometry.shape(json.loads(geom))
    elif isinstance(geom, dict):
        return geometry.shape(geom)

    if not all([
        hasattr(geom, k)
        for k in (
            'type',
            'coordinates',
        )
    ]):
        raise ValueError('Expected keywords not found: `type`, `coordinates`')

    return geometry.shape(geom.__dict__)
