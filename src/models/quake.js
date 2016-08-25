'use strict';

import app from 'ampersand-app';
import AmpersandModel from 'ampersand-model';
import Collection from 'ampersand-collection';
import restMixin from 'ampersand-collection-rest-mixin';
import underscoreMixin from 'ampersand-collection-underscore-mixin';

var Switch = AmpersandModel.extend({
  urlRoot: 'https://localhost:8443/api/v1/switch',
  props: {
    pin: 'integer',
    description: 'string'
  }
});

var SwitchCollection = Collection.extend(underscoreMixin, restMixin, {
    url: '/api/v1/quake',
    model: Switch
});

app.switches = new SwitchCollection();
app.switches.fetch();
