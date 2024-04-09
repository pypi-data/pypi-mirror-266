import itertools

def build_from_scratch(_list_of_conversion_for_metadata_pair, _metadata_values, _edge_factories_clusters):
    _create_edges_from_manual_annotation(_list_of_conversion_for_metadata_pair)
    _create_edges_using_factories_clusters(_metadata_values, _edge_factories_clusters)


def _create_edges_using_factories_clusters(metadata_values,
                                           factories_clusters):
    # one property change policy.
    attributes = list(metadata_values.keys())
    attributes_values_lists = list(metadata_values.values())
    for attribute_values in itertools.product(*attributes_values_lists):
        source = dict(zip(attributes, attribute_values))
        for attribute in metadata_values.keys():
            for new_attribute_v in exclude_key_from_list(metadata_values[attribute], source[attribute]):
                target = source.copy()
                target[source] = new_attribute_v
                for factory_cluster in factories_clusters:
                    can_use_factories_in_cluster, factories = factory_cluster
                    if not can_use_factories_in_cluster(source, target):
                        continue
                    for factory in factories:
                        function = factory(source, target)
                        if function is not None:
                            self._add_edge(source, target, function, factory)
