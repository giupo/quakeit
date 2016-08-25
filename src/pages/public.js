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
    text: 'Intensita\' #terremoto da inizio evento fonte: @INGVterremoti'
  },


  xAxis: {
    type: 'datetime',
    title: {
      text: 'Date'
    }
  },

  yAxis: {        
  
  },

  series: [{
    data: []
  }],

  tooltip: {
  }
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
