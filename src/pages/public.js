'use strict';

import app from 'ampersand-app';
import React from 'react';
import ReactHighcharts from 'react-highcharts';
import Highcharts from 'highcharts';
import $ from 'jquery';

const chartClassName = 'Puppu';

var getChartReferenceByClassName = function (className) {
  var cssClassName = className;
  var foundChart = null;

  $(Highcharts.charts).each(function(i, chart){    
    if(chart.container.classList.contains(cssClassName)){
      foundChart = chart;
      return chart;
    }
    return null;
  });

  return foundChart;
};

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

  //series: [{
  //  data: []
  //}],

  tooltip: {
    formatter: function () {
      var html = 'Orario:' + this.x +'<br/>' +
        'Magnitudo: <b>' + this.y + '</b><br/>' +
        'Profondita\': ' + this.point.info.depth + 'km<br/>' +
        'Zona: <b>' + this.point.info.zona + '</b> (Lat:' + this.point.info.lat +
        ', Lon:' + this.point.info.lon +' )' ;
      return html;
    }
  },
};


export default React.createClass({
  displayName : 'PublicPage',

  componentDidMount() {
    var chart = getChartReferenceByClassName(chartClassName);
    app.chart = chart;
  },
  
  render () {
    return (
      <ReactHighcharts config={config}></ReactHighcharts>
    );
  }
});
