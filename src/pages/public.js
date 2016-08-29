'use strict';

import app from 'ampersand-app';
import React from 'react';
//import ReactHighcharts from 'react-highcharts/ReactHighstock';
// import Highcharts from 'highcharts';
const ReactHighstock = require('react-highcharts/dist/ReactHighstock');
import $ from 'jquery';

const chartClassName = 'Puppu';

var config = {
  chart: {
    className: chartClassName
  },
  
  title: {
    text: 'Magnitudo #terremoto fonte: <a href="https://twitter.com/INGVterremoti">@INGVterremoti</a>'
  },

  xAxis: {
    type: 'datetime',
    title: {
      text: 'Date'
    }
  },

  yAxis: {        
  
  },

  tooltip: {
    formatter: function () {
      const info = this.points[0].point.info;
      var html = 'Orario:' + this.x +'<br/>' +
        'Magnitudo: <b>' + this.y + '</b><br/>' +
        'Profondita\': ' + info.depth + 'km<br/>' +
        'Zona: <b>' + info.zona + '</b> (Lat:' + info.lat +
        ', Lon:' + info.lon +')' ;
      return html;
    }
  } // tooltip
};


export default React.createClass({
  displayName : 'PublicPage',

  componentDidMount() {
    app.chart = this.refs.chart.getChart();
  },
  
  render () {
    return (
        <ReactHighstock config={config} ref="chart"></ReactHighstock>
    );
  }
});
