"""
Classes to sample an existing object catalog, assigning random sky
positions for CCD-level simulations.
"""
from skycatalogs.objects import BaseObject, ObjectCollection
from skycatalogs.utils import Disk
from .utils import RandomSkyPositions


__all__ = ["RandomizedObject", "RandomizedCollection"]


class RandomizedObject(BaseObject):

    def __init__(self, sampled_object, ra, dec, parent_collection, index):
        self.sampled_object = sampled_object
        obj_id = sampled_object.id + "_randomized"
        super().__init__(ra, dec, obj_id, parent_collection._object_type,
                         parent_collection, index)

    @property
    def subcomponents(self):
        return self.sampled_object.subcomponents

    def get_gsobject_components(self, gsparams=None, rng=None):
        return self.sampled_object.get_gsobject_components(
            gsparams=gsparams, rng=rng)

    def get_observer_sed_component(self, component, mjd=None):
        return self.sampled_object.get_observer_sed_component(
            component, mjd=mjd)


class RandomizedCollection(ObjectCollection):

    def __init__(self, region, random_seed, object_list, sky_catalog, object_type):
        self.sky_pos = RandomSkyPositions.make_generator(region, seed=random_seed)
        self.object_list = object_list
        self._sky_catalog = sky_catalog
        self._object_type = object_type
        self._object_type_unique = object_type
        self._object_class = RandomizedObject
        self._uniform_object_type = True

    @property
    def native_columns(self):
        return ()

    def __getitem__(self, key):
        sampled_object = self.object_list[key]
        ra, dec = next(self.sky_pos)
        return RandomizedObject(sampled_object, ra, dec, self, key)

    def __len__(self):
        return len(self.object_list)

    @staticmethod
    def register(sky_catalog, object_type):
        sky_catalog.cat_cxt.register_source_type(
            object_type,
            object_class=RandomizedObject,
            collection_class=RandomizedCollection,
            custom_load=True
        )

    @staticmethod
    def load_collection(region, sky_catalog, mjd=None, exposure=None,
                        object_type=None):
        config = dict(sky_catalog.raw_config["object_types"][object_type])
        sampled_region = Disk(config['ra'], config['dec'], config['radius']*3600.0)
        object_list = sky_catalog.get_object_type_by_region(
            sampled_region, config["sampled_object_type"])
        return RandomizedCollection(region,
                                    config['random_seed'],
                                    object_list,
                                    sky_catalog,
                                    object_type)
