// Thin helpers around Chart.js used by the dashboard and analytics pages.
const COLORS = {teal:"#2a7f86", saffron:"#e8a93a", rose:"#c4455a", slate:"#b9c7c9", ink:"#14323b"};
Chart.defaults.font.family = '"Instrument Sans", system-ui, sans-serif';
Chart.defaults.color = "#5d6f73";

function _mount(id, config){
  const el = document.getElementById(id);
  if(!el) return null;
  config.options = Object.assign({responsive:true, maintainAspectRatio:false}, config.options || {});
  return new Chart(el, config);
}
function barChart(id, labels, datasets, opts = {}){
  return _mount(id, {type:"bar", data:{labels, datasets}, options:Object.assign(
    {scales:{y:{beginAtZero:true, ticks:{precision:0}}}, plugins:{legend:{display:datasets.length>1}}}, opts)});
}
function hBarChart(id, labels, datasets, opts = {}){
  return barChart(id, labels, datasets, Object.assign({indexAxis:"y",
    scales:{x:{beginAtZero:true, ticks:{precision:0}}}}, opts));
}
function lineChart(id, labels, datasets, opts = {}){
  return _mount(id, {type:"line", data:{labels, datasets}, options:Object.assign(
    {scales:{y:{beginAtZero:true}}, interaction:{mode:"index", intersect:false}}, opts)});
}
function doughnutChart(id, labels, data, colors){
  return _mount(id, {type:"doughnut", data:{labels, datasets:[{data, backgroundColor:colors, borderWidth:0}]},
    options:{cutout:"62%", plugins:{legend:{position:"bottom"}}}});
}
