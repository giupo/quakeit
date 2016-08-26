'use strict';

import app from 'ampersand-app';
import Router from './router';
import { QuakeCollection } from './models/quake';
import _ from 'underscore';

window.app = app;

app.extend({
  init() {
    console.log('app starting');
   
    app.cities = ["Macerata", "Rieti", "Ascoli Piceno", "Perugia"];
    //app.cities = ["Ascoli Piceno"];
    app.quakes = new Object();

    _.each(app.cities, function(city) {
      app.quakes[city] = new QuakeCollection({
        zona: city
      });
      app.quakes[city].zona = city;
    });
    
    this.router = new Router();
    this.router.history.start({pushState: true});
    this.trigger('AppInit', 'ok');
  }
});

app.redrawing = false;

app.on('AppInit', (data)=> {
  console.log('App started ' + data);
});

require('domready')(function() {
  app.init();
  for (var zona0 in app.quakes) {
    var zona = zona0;
    if (app.quakes.hasOwnProperty(zona)) {
      app.chart.addSeries({
        id: zona,
        name: zona,
        data: []
      }, false);

      app.quakes[zona].fetch({
        success: function(collection, response, options) {
          collection.each(function(data) {
            app.chart.get(data.zona).addPoint({
              x: data.time,
              y: data.ml,
              info: {
                depth: data.depth,
                zona: data.zona,
                lat: data.lat,
                lon: data.lon
              }
            } , false); // non voglio ridisegnare il grafico ad ogni punto
          });
          if (! app.redawing) {
            app.redrawing = true;
            app.chart.redraw();
            app.redrawing = false;
          }
        }
      });
    }
  }
});
