'use strict';

import app from 'ampersand-app';
import React from 'react';
import ReactHighcharts from 'react-highcharts';

var config = {
  title: {
    text: 'Intensita\' #terremoto da inizio evento fonte: @INGVterremoti'
  },
  
  xAxis: {
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  },
  series: [{
    data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 295.6, 454.4]
  }]
};


export default React.createClass({
  displayName : 'PublicPage',

  render () {
    return (
      <ReactHighcharts config={config}></ReactHighcharts>
    );
  }
});
