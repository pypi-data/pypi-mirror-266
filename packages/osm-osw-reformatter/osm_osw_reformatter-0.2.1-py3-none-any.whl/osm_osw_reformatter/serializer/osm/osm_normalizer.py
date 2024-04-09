import ogr2osm

class OSMNormalizer(ogr2osm.TranslationBase):

    OSM_IMPLIED_FOOTWAYS = (
        "footway",
        "pedestrian",
        "steps",
        "living_street"
    )

    def filter_tags(self, tags):
        '''
        Override this method if you want to modify or add tags to the xml output
        '''

        # Handle zones
        if 'highway' in tags and tags['highway'] == 'pedestrian' and '_w_id' in tags and tags['_w_id']:
            tags['area'] = 'yes'

        # OSW derived fields
        tags.pop('_u_id', '')
        tags.pop('_v_id', '')
        tags.pop('_w_id', '')
        tags.pop('incline', '')
        tags.pop('length', '')
        if 'foot' in tags and tags['foot'] == 'yes' and 'highway' in tags and tags['highway'] in self.OSM_IMPLIED_FOOTWAYS:
            tags.pop('foot', '')

        # OSW fields with similar OSM field names
        tags['incline'] = tags.pop('climb', '')

        return tags

    def process_feature_post(self, osmgeometry, ogrfeature, ogrgeometry):
        '''
        This method is called after the creation of an OsmGeometry object. The
        ogr feature and ogr geometry used to create the object are passed as
        well. Note that any return values will be discarded by ogr2osm.
        '''
        if osmgeometry.tags['_id'][0]:
            osmgeometry.id = int(osmgeometry.tags.pop('_id')[0])