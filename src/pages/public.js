'use strict';

import app from 'ampersand-app';
import React from 'react';

export default React.createClass({
  displayName : 'PublicPage',

  onLoginClick (event) {
    event.preventDefault();
    console.log('cribbio');
    let x = app.router.history.navigate('/login');
    console.log(x);
  },

  onOtherPageClick (event) {
    event.preventDefault();
    console.log('ciola');
    app.router.history.navigate('/otherpage');
  },

  render () {
    console.log('PublicPage called');
    return  (
        /* jshint ignore:start */
        <div className='container'>
          <header role='banner'>
            <h1>Labelr</h1>
          </header>
          <div>
           <p>We label stuff for you, beacuse, we can &trade;</p>
              <a href='/login' onClick={this.onLoginClick} className='button button-large'>
                <span className='mega octicon octicon-mark-github'></span> Login with Github
              </a>
          </div>

          <div>
           <p>We label stuff for you, beacuse, we can &trade;</p>
              <a href='/otherPage' onClick={this.onOtherPageClick} className='button button-large'>
                <span className='mega octicon octicon-mark-github'></span> Login with Github
              </a>
          </div>
        </div>
          /* jshint ignore:end */
    );
  }
});
