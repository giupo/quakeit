'use strict';

import app from 'ampersand-app';
import AmpersandModel from 'ampersand-model';
import Collection from 'ampersand-collection';
import restMixin from 'ampersand-collection-rest-mixin';
import underscoreMixin from 'ampersand-collection-underscore-mixin';

var Quake = AmpersandModel.extend({
  urlRoot: '/data',
  props: {
    id: 'number',
    text: 'string',
    zona: 'string',
    lat: 'number',
    lon: 'number',
    ml: 'number',
    depth : 'number',
    time: 'date'
  }
})

module.exports.Quake = Quake;

module.exports.QuakeCollection = Collection.extend(underscoreMixin, restMixin, {
  url: function() {
    if (this.zona !== undefined) {
      return '/data/' + this.zona;
    } else {
      return '/data'
    }
  },
  model: Quake
});
