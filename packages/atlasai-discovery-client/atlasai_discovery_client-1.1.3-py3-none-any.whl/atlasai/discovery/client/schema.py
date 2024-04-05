import sgqlc.types


schema = sgqlc.types.Schema()



########################################################################
# Scalars and Enumerations
########################################################################
class Action(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Add', 'Delete', 'Replace')


class AssetType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Other', 'Raster', 'Unknown', 'Vector')


Boolean = sgqlc.types.Boolean

class DataType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Float', 'Int', 'IsoDateTime', 'String')


class EntityContext(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Instance', 'Product', 'Release', 'Search')


class FtsMethod(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('TsQuery', 'WebSearch')


class GeoJson(sgqlc.types.Scalar):
    __schema__ = schema


class HttpMethod(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('GET', 'PATCH', 'POST', 'PUT')


ID = sgqlc.types.ID

Int = sgqlc.types.Int

class IsoDateTime(sgqlc.types.Scalar):
    __schema__ = schema


class Json(sgqlc.types.Scalar):
    __schema__ = schema


class ModelName(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Instance', 'Product', 'Release')


class OrderDirection(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('asc', 'desc')


class PublicationStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('InReview', 'NotPublished', 'Published', 'Rejected', 'Retired', 'ToPublish', 'ToReview')


String = sgqlc.types.String


########################################################################
# Input Objects
########################################################################
class AssetInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('path', 'save_to_storage', 'tags', 'scan_config', 'type', 'metadata', 'crs', 'extent')
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='path')
    save_to_storage = sgqlc.types.Field(Boolean, graphql_name='saveToStorage')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('TagInput')), graphql_name='tags')
    scan_config = sgqlc.types.Field(Json, graphql_name='scanConfig')
    type = sgqlc.types.Field(AssetType, graphql_name='type')
    metadata = sgqlc.types.Field(Json, graphql_name='metadata')
    crs = sgqlc.types.Field(String, graphql_name='crs')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')


class BasicSearchInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('odata', 'limit', 'offset', 'order_by', 'filter_children')
    odata = sgqlc.types.Field(String, graphql_name='odata')
    limit = sgqlc.types.Field(Int, graphql_name='limit')
    offset = sgqlc.types.Field(Int, graphql_name='offset')
    order_by = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('OrderByInput')), graphql_name='orderBy')
    filter_children = sgqlc.types.Field(Boolean, graphql_name='filterChildren')


class CreateInstanceInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('product_id_or_name', 'effective_date_range', 'ignore_timezone', 'tags', 'reference', 'assets', 'parents', 'extent')
    product_id_or_name = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='productIdOrName')
    effective_date_range = sgqlc.types.Field('DateRangeInput', graphql_name='effectiveDateRange')
    ignore_timezone = sgqlc.types.Field(Boolean, graphql_name='ignoreTimezone')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('TagInput')), graphql_name='tags')
    reference = sgqlc.types.Field(Json, graphql_name='reference')
    assets = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AssetInput))), graphql_name='assets')
    parents = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='parents')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')


class CreateProductInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('internal_name', 'display_name', 'description', 'license', 'reference', 'data_steward', 'tags')
    internal_name = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='internalName')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    description = sgqlc.types.Field(String, graphql_name='description')
    license = sgqlc.types.Field(String, graphql_name='license')
    reference = sgqlc.types.Field(Json, graphql_name='reference')
    data_steward = sgqlc.types.Field(Json, graphql_name='dataSteward')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('TagInput')), graphql_name='tags')


class CreateReleaseInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('product_id_or_name', 'instance_ids', 'version', 'name', 'description', 'publish_status', 'license', 'tags', 'audience', 'extent')
    product_id_or_name = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='productIdOrName')
    instance_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='instanceIds')
    version = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='version')
    name = sgqlc.types.Field(String, graphql_name='name')
    description = sgqlc.types.Field(String, graphql_name='description')
    publish_status = sgqlc.types.Field(PublicationStatus, graphql_name='publishStatus')
    license = sgqlc.types.Field(String, graphql_name='license')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('TagInput')), graphql_name='tags')
    audience = sgqlc.types.Field(Json, graphql_name='audience')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')


class DateRangeInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('lower', 'upper', 'include_lower', 'include_upper', 'empty')
    lower = sgqlc.types.Field(IsoDateTime, graphql_name='lower')
    upper = sgqlc.types.Field(IsoDateTime, graphql_name='upper')
    include_lower = sgqlc.types.Field(Boolean, graphql_name='includeLower')
    include_upper = sgqlc.types.Field(Boolean, graphql_name='includeUpper')
    empty = sgqlc.types.Field(Boolean, graphql_name='empty')


class DistinctInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('entity', 'odata')
    entity = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='entity')
    odata = sgqlc.types.Field(String, graphql_name='odata')


class EmailSubscriptionConfigInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('to', 'cc', 'bcc')
    to = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='to')
    cc = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='cc')
    bcc = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='bcc')


class OrderByInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('field', 'direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='field')
    direction = sgqlc.types.Field(OrderDirection, graphql_name='direction')


class SearchInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('odata', 'limit', 'offset', 'order_by', 'complete_products')
    odata = sgqlc.types.Field(String, graphql_name='odata')
    limit = sgqlc.types.Field(Int, graphql_name='limit')
    offset = sgqlc.types.Field(Int, graphql_name='offset')
    order_by = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(OrderByInput)), graphql_name='orderBy')
    complete_products = sgqlc.types.Field(Boolean, graphql_name='completeProducts')


class SlackSubscriptionConfigInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('webhook_url',)
    webhook_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='webhookUrl')


class SubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('model_name', 'odata')
    model_name = sgqlc.types.Field(sgqlc.types.non_null(ModelName), graphql_name='modelName')
    odata = sgqlc.types.Field(String, graphql_name='odata')


class TagInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('name', 'value')
    name = sgqlc.types.Field(String, graphql_name='name')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class UpdateInstanceInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('effective_date_range', 'ignore_timezone', 'tags', 'reference', 'assets', 'parents', 'parents_action', 'extent')
    effective_date_range = sgqlc.types.Field(DateRangeInput, graphql_name='effectiveDateRange')
    ignore_timezone = sgqlc.types.Field(Boolean, graphql_name='ignoreTimezone')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TagInput)), graphql_name='tags')
    reference = sgqlc.types.Field(Json, graphql_name='reference')
    assets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AssetInput)), graphql_name='assets')
    parents = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='parents')
    parents_action = sgqlc.types.Field(Action, graphql_name='parentsAction')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')


class UpdateInstanceInputWithId(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'effective_date_range', 'ignore_timezone', 'tags', 'reference', 'assets', 'parents', 'parents_action', 'extent')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    effective_date_range = sgqlc.types.Field(DateRangeInput, graphql_name='effectiveDateRange')
    ignore_timezone = sgqlc.types.Field(Boolean, graphql_name='ignoreTimezone')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TagInput)), graphql_name='tags')
    reference = sgqlc.types.Field(Json, graphql_name='reference')
    assets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AssetInput)), graphql_name='assets')
    parents = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='parents')
    parents_action = sgqlc.types.Field(Action, graphql_name='parentsAction')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')


class UpdateProductInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('internal_name', 'display_name', 'description', 'license', 'reference', 'data_steward', 'tags')
    internal_name = sgqlc.types.Field(ID, graphql_name='internalName')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    description = sgqlc.types.Field(String, graphql_name='description')
    license = sgqlc.types.Field(String, graphql_name='license')
    reference = sgqlc.types.Field(Json, graphql_name='reference')
    data_steward = sgqlc.types.Field(Json, graphql_name='dataSteward')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TagInput)), graphql_name='tags')


class UpdateProductInputWithId(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'internal_name', 'display_name', 'description', 'license', 'reference', 'data_steward', 'tags')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    internal_name = sgqlc.types.Field(ID, graphql_name='internalName')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    description = sgqlc.types.Field(String, graphql_name='description')
    license = sgqlc.types.Field(String, graphql_name='license')
    reference = sgqlc.types.Field(Json, graphql_name='reference')
    data_steward = sgqlc.types.Field(Json, graphql_name='dataSteward')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TagInput)), graphql_name='tags')


class UpdateReleaseInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('version', 'name', 'description', 'publish_status', 'license', 'tags', 'audience', 'instance_ids', 'instance_ids_action', 'extent')
    version = sgqlc.types.Field(String, graphql_name='version')
    name = sgqlc.types.Field(String, graphql_name='name')
    description = sgqlc.types.Field(String, graphql_name='description')
    publish_status = sgqlc.types.Field(PublicationStatus, graphql_name='publishStatus')
    license = sgqlc.types.Field(String, graphql_name='license')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TagInput)), graphql_name='tags')
    audience = sgqlc.types.Field(Json, graphql_name='audience')
    instance_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='instanceIds')
    instance_ids_action = sgqlc.types.Field(Action, graphql_name='instanceIdsAction')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')


class UpdateReleaseInputWithId(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'version', 'name', 'description', 'publish_status', 'license', 'tags', 'audience', 'instance_ids', 'instance_ids_action', 'extent')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    version = sgqlc.types.Field(String, graphql_name='version')
    name = sgqlc.types.Field(String, graphql_name='name')
    description = sgqlc.types.Field(String, graphql_name='description')
    publish_status = sgqlc.types.Field(PublicationStatus, graphql_name='publishStatus')
    license = sgqlc.types.Field(String, graphql_name='license')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TagInput)), graphql_name='tags')
    audience = sgqlc.types.Field(Json, graphql_name='audience')
    instance_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='instanceIds')
    instance_ids_action = sgqlc.types.Field(Action, graphql_name='instanceIdsAction')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')


class WebhookSubscriptionConfigInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('url', 'method', 'audience')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')
    method = sgqlc.types.Field(sgqlc.types.non_null(HttpMethod), graphql_name='method')
    audience = sgqlc.types.Field(String, graphql_name='audience')



########################################################################
# Output Objects and Interfaces
########################################################################
class Asset(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id', 'uris', 'instance_id', 'type', 'path', 'save_to_storage', 'storage_path', 'metadata', 'crs', 'extent', 'tags', 'scan_config', 'create_date', 'modify_date')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    uris = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='uris')
    instance_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='instanceId')
    type = sgqlc.types.Field(sgqlc.types.non_null(AssetType), graphql_name='type')
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='path')
    save_to_storage = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='saveToStorage')
    storage_path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='storagePath')
    metadata = sgqlc.types.Field(Json, graphql_name='metadata')
    crs = sgqlc.types.Field(String, graphql_name='crs')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Tag')), graphql_name='tags')
    scan_config = sgqlc.types.Field(sgqlc.types.non_null(Json), graphql_name='scanConfig')
    create_date = sgqlc.types.Field(sgqlc.types.non_null(IsoDateTime), graphql_name='createDate')
    modify_date = sgqlc.types.Field(sgqlc.types.non_null(IsoDateTime), graphql_name='modifyDate')


class DateRange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('lower', 'upper', 'include_lower', 'include_upper', 'empty')
    lower = sgqlc.types.Field(IsoDateTime, graphql_name='lower')
    upper = sgqlc.types.Field(IsoDateTime, graphql_name='upper')
    include_lower = sgqlc.types.Field(Boolean, graphql_name='includeLower')
    include_upper = sgqlc.types.Field(Boolean, graphql_name='includeUpper')
    empty = sgqlc.types.Field(Boolean, graphql_name='empty')


class DistinctValues(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('entity', 'values')
    entity = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='entity')
    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TypedValue'))), graphql_name='values')


class EmailSubscriptionConfig(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('to', 'cc', 'bcc')
    to = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='to')
    cc = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='cc')
    bcc = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='bcc')


class FullSearchResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('product', 'instances')
    product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='product')
    instances = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Instance')), graphql_name='instances')


class Instance(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id', 'uris', 'product_id', 'product_name', 'effective_date_range', 'ignore_timezone', 'tags', 'reference', 'extent', 'assets', 'parents', 'parent_ids', 'create_date', 'modify_date')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    uris = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='uris')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='productId')
    product_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productName')
    effective_date_range = sgqlc.types.Field(DateRange, graphql_name='effectiveDateRange')
    ignore_timezone = sgqlc.types.Field(Boolean, graphql_name='ignoreTimezone')
    tags = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Tag'))), graphql_name='tags')
    reference = sgqlc.types.Field(Json, graphql_name='reference')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')
    assets = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Asset))), graphql_name='assets')
    parents = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Instance')), graphql_name='parents')
    parent_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='parentIds')
    create_date = sgqlc.types.Field(sgqlc.types.non_null(IsoDateTime), graphql_name='createDate')
    modify_date = sgqlc.types.Field(sgqlc.types.non_null(IsoDateTime), graphql_name='modifyDate')


class Mutation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('create_product', 'update_product', 'delete_product', 'create_products', 'update_products', 'delete_products', 'create_instance', 'update_instance', 'delete_instance', 'create_instances', 'update_instances', 'delete_instances', 'create_release', 'update_release', 'delete_release', 'create_releases', 'update_releases', 'delete_releases', 'create_subscription', 'update_subscription', 'delete_subscription')
    create_product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='createProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateProductInput), graphql_name='input', default=None)),
))
    )
    update_product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='updateProduct', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateProductInput), graphql_name='input', default=None)),
))
    )
    delete_product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='deleteProduct', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    create_products = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Product')), graphql_name='createProducts', args=sgqlc.types.ArgDict((
        ('inputs', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CreateProductInput))), graphql_name='inputs', default=None)),
))
    )
    update_products = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Product')), graphql_name='updateProducts', args=sgqlc.types.ArgDict((
        ('inputs', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UpdateProductInputWithId))), graphql_name='inputs', default=None)),
))
    )
    delete_products = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Product')), graphql_name='deleteProducts', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    create_instance = sgqlc.types.Field(sgqlc.types.non_null(Instance), graphql_name='createInstance', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateInstanceInput), graphql_name='input', default=None)),
))
    )
    update_instance = sgqlc.types.Field(sgqlc.types.non_null(Instance), graphql_name='updateInstance', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateInstanceInput), graphql_name='input', default=None)),
))
    )
    delete_instance = sgqlc.types.Field(sgqlc.types.non_null(Instance), graphql_name='deleteInstance', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    create_instances = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Instance)), graphql_name='createInstances', args=sgqlc.types.ArgDict((
        ('inputs', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CreateInstanceInput))), graphql_name='inputs', default=None)),
))
    )
    update_instances = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Instance)), graphql_name='updateInstances', args=sgqlc.types.ArgDict((
        ('inputs', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UpdateInstanceInputWithId))), graphql_name='inputs', default=None)),
))
    )
    delete_instances = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Instance)), graphql_name='deleteInstances', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    create_release = sgqlc.types.Field(sgqlc.types.non_null('Release'), graphql_name='createRelease', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateReleaseInput), graphql_name='input', default=None)),
))
    )
    update_release = sgqlc.types.Field(sgqlc.types.non_null('Release'), graphql_name='updateRelease', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateReleaseInput), graphql_name='input', default=None)),
))
    )
    delete_release = sgqlc.types.Field(sgqlc.types.non_null('Release'), graphql_name='deleteRelease', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    create_releases = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Release')), graphql_name='createReleases', args=sgqlc.types.ArgDict((
        ('inputs', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CreateReleaseInput))), graphql_name='inputs', default=None)),
))
    )
    update_releases = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Release')), graphql_name='updateReleases', args=sgqlc.types.ArgDict((
        ('inputs', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UpdateReleaseInputWithId))), graphql_name='inputs', default=None)),
))
    )
    delete_releases = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Release')), graphql_name='deleteReleases', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ids', default=None)),
))
    )
    create_subscription = sgqlc.types.Field(sgqlc.types.non_null('Subscription'), graphql_name='createSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SubscriptionInput), graphql_name='input', default=None)),
        ('email', sgqlc.types.Arg(EmailSubscriptionConfigInput, graphql_name='email', default=None)),
        ('slack', sgqlc.types.Arg(SlackSubscriptionConfigInput, graphql_name='slack', default=None)),
        ('webhook', sgqlc.types.Arg(WebhookSubscriptionConfigInput, graphql_name='webhook', default=None)),
))
    )
    update_subscription = sgqlc.types.Field(sgqlc.types.non_null('Subscription'), graphql_name='updateSubscription', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SubscriptionInput), graphql_name='input', default=None)),
        ('email', sgqlc.types.Arg(EmailSubscriptionConfigInput, graphql_name='email', default=None)),
        ('slack', sgqlc.types.Arg(SlackSubscriptionConfigInput, graphql_name='slack', default=None)),
        ('webhook', sgqlc.types.Arg(WebhookSubscriptionConfigInput, graphql_name='webhook', default=None)),
))
    )
    delete_subscription = sgqlc.types.Field(sgqlc.types.non_null('Subscription'), graphql_name='deleteSubscription', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )


class Product(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id', 'uris', 'internal_name', 'display_name', 'description', 'license', 'reference', 'data_steward', 'tags', 'releases', 'create_date', 'modify_date')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    uris = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='uris')
    internal_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='internalName')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    description = sgqlc.types.Field(String, graphql_name='description')
    license = sgqlc.types.Field(String, graphql_name='license')
    reference = sgqlc.types.Field(Json, graphql_name='reference')
    data_steward = sgqlc.types.Field(Json, graphql_name='dataSteward')
    tags = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Tag'))), graphql_name='tags')
    releases = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Release')), graphql_name='releases')
    create_date = sgqlc.types.Field(sgqlc.types.non_null(IsoDateTime), graphql_name='createDate')
    modify_date = sgqlc.types.Field(sgqlc.types.non_null(IsoDateTime), graphql_name='modifyDate')


class Query(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('product', 'products', 'instance', 'instances', 'release', 'releases', 'subscription', 'subscriptions', 'entities', 'distinct', 'search', 'download')
    product = sgqlc.types.Field(sgqlc.types.non_null(Product), graphql_name='product', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    products = sgqlc.types.Field(sgqlc.types.non_null('SearchResults'), graphql_name='products', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(BasicSearchInput, graphql_name='input', default=None)),
))
    )
    instance = sgqlc.types.Field(sgqlc.types.non_null(Instance), graphql_name='instance', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    instances = sgqlc.types.Field(sgqlc.types.non_null('SearchResults'), graphql_name='instances', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(BasicSearchInput, graphql_name='input', default=None)),
))
    )
    release = sgqlc.types.Field(sgqlc.types.non_null('Release'), graphql_name='release', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    releases = sgqlc.types.Field(sgqlc.types.non_null('SearchResults'), graphql_name='releases', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(BasicSearchInput, graphql_name='input', default=None)),
))
    )
    subscription = sgqlc.types.Field(sgqlc.types.non_null('Subscription'), graphql_name='subscription', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null('SearchResults'), graphql_name='subscriptions', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(BasicSearchInput), graphql_name='input', default=None)),
))
    )
    entities = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='entities', args=sgqlc.types.ArgDict((
        ('context', sgqlc.types.Arg(EntityContext, graphql_name='context', default=None)),
))
    )
    distinct = sgqlc.types.Field(sgqlc.types.non_null(DistinctValues), graphql_name='distinct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DistinctInput), graphql_name='input', default=None)),
))
    )
    search = sgqlc.types.Field(sgqlc.types.non_null('SearchResults'), graphql_name='search', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(SearchInput, graphql_name='input', default=None)),
))
    )
    download = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='download', args=sgqlc.types.ArgDict((
        ('reference', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='reference', default=None)),
))
    )


class Release(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id', 'uris', 'product_id', 'product_name', 'instance_ids', 'version', 'name', 'description', 'publish_status', 'license', 'tags', 'extent', 'audience', 'create_date', 'modify_date')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    uris = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='uris')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='productId')
    product_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productName')
    instance_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='instanceIds')
    version = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='version')
    name = sgqlc.types.Field(String, graphql_name='name')
    description = sgqlc.types.Field(String, graphql_name='description')
    publish_status = sgqlc.types.Field(sgqlc.types.non_null(PublicationStatus), graphql_name='publishStatus')
    license = sgqlc.types.Field(String, graphql_name='license')
    tags = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Tag'))), graphql_name='tags')
    extent = sgqlc.types.Field(GeoJson, graphql_name='extent')
    audience = sgqlc.types.Field(Json, graphql_name='audience')
    create_date = sgqlc.types.Field(sgqlc.types.non_null(IsoDateTime), graphql_name='createDate')
    modify_date = sgqlc.types.Field(sgqlc.types.non_null(IsoDateTime), graphql_name='modifyDate')


class SearchResults(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('results', 'more', 'next_limit', 'next_offset')
    results = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SearchResult'))), graphql_name='results')
    more = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='more')
    next_limit = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='nextLimit')
    next_offset = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='nextOffset')


class SlackSubscriptionConfig(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('webhook_url',)
    webhook_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='webhookUrl')


class Subscription(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id', 'user_id', 'model_name', 'odata', 'config')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    user_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='userId')
    model_name = sgqlc.types.Field(sgqlc.types.non_null(ModelName), graphql_name='modelName')
    odata = sgqlc.types.Field(String, graphql_name='odata')
    config = sgqlc.types.Field('SubscriptionConfig', graphql_name='config')


class Tag(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'value')
    name = sgqlc.types.Field(String, graphql_name='name')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class TypedValue(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('value', 'type')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')
    type = sgqlc.types.Field(sgqlc.types.non_null(DataType), graphql_name='type')


class WebhookSubscriptionConfig(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('url', 'method', 'audience')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')
    method = sgqlc.types.Field(sgqlc.types.non_null(HttpMethod), graphql_name='method')
    audience = sgqlc.types.Field(String, graphql_name='audience')



########################################################################
# Unions
########################################################################
class SearchResult(sgqlc.types.Union):
    __schema__ = schema
    __types__ = (FullSearchResult, Product, Instance, Release, Subscription)


class SubscriptionConfig(sgqlc.types.Union):
    __schema__ = schema
    __types__ = (EmailSubscriptionConfig, SlackSubscriptionConfig, WebhookSubscriptionConfig)



########################################################################
# Schema Entry Points
########################################################################
schema.query_type = Query
schema.mutation_type = Mutation
schema.subscription_type = None

