'use strict';

import app from 'ampersand-app';
import Router from './router';
import { QuakeCollection } from './models/quake';
import _ from 'underscore';
import ReactGA from 'react-ga';

window.app = app;

app.extend({

  redrawing: false,

  cities: ["Rieti", "Perugia", "Macerata", "Norcia", "Ascoli Piceno"],

  init() {
    console.log('app starting');
    console.log('registering GA');
    ReactGA.initialize('UA-47705605-2', {
      debug: false
    });
    console.log('GA registered');
    this.router = new Router();
    this.router.history.start({pushState: true});
    this.trigger('AppInit', 'ok');
  },
  
  reloadData() {
    app.quakes = new Object();
    
    _.each(app.cities, function(city) {
      app.quakes[city] = new QuakeCollection({
        zona: city
      });
      app.quakes[city].zona = city;
    });

    for(var i=0;i < app.chart.series.length; i++) {
      app.chart.series[i].remove();
    }
    
    app.chart.redraw();
    
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
              ReactGA.pageview("/data/" + data.zona);
              console.log(data.zona);
              app.chart.get(data.zona).addPoint({
                x: data.time,
                y: data.ml,
                info: {
                  depth: data.depth,
                  zona: data.zona,
                  lat: data.lat,
                  lon: data.lon
                }
              }, false); // non voglio ridisegnare il grafico ad ogni punto
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
  }
});

require('domready')(function() {
  app.init();
});

app.on('AppInit', (data) => {
  console.log('App started ' + data);
  ReactGA.pageview("/");
  app.reloadData();
});
