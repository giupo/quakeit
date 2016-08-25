'use strict';

import app from 'ampersand-app';
import Router from './router';
import { QuakeCollection } from './models/quake';

window.app = app;

app.extend({
  init() {
    console.log('app starting');
    this.router = new Router();
    this.router.history.start({pushState: true});
    app.quakes = new QuakeCollection();
    this.trigger('AppInit', 'ok');
  }
});

app.on('AppInit', (data)=> {
  console.log('App started ' + data);
});

require('domready')(function() {
  app.init();
  app.quakes.fetch({
    success: function(collection, response, options) {
      collection.each(function(data) {
        app.chart.series[0].addPoint({
          x: data.time,
          y: data.ml
        }, false);
      });

      app.chart.redraw();
    }
  });
});
