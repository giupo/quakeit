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
    this.trigger('AppInit', 'ciula');
  }
});

app.on('AppInit', (data)=> {
  console.log('App started ' + data);
});

app.init();
app.quakes.fetch();
