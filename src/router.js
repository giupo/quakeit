import app from 'ampersand-app';
import Router from 'ampersand-router';
import React from 'react';
import ReactDom from 'react-dom';

import PublicPage from './pages/public';

export default Router.extend({
  routes: {
    '': 'public'
  },

  public () {
    app.trigger('hello', {data:'ciccio'});
    /* jshint ignore:start */
    ReactDom.render(<PublicPage/>, document.body);
  }
});
