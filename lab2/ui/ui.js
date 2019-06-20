"use strict";

// RPC wrapper
function invoke_rpc(method, args, timeout, on_done){
  $("#crash").hide();
  $("#timeout").hide();
  $("#rpc_spinner").show();
  //send RPC with whatever data is appropriate. Display an error message on crash or timeout
  var xhr = new XMLHttpRequest();
  xhr.open("POST", method, true);
  xhr.setRequestHeader('Content-Type','application/json; charset=UTF-8');
  xhr.timeout = timeout;
  xhr.send(JSON.stringify(args));
  xhr.ontimeout = function () {
    $("#timeout").show();
    $("#rpc_spinner").hide();
    $("#crash").hide();
  };
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      $("#rpc_spinner").hide();
      var result = JSON.parse(xhr.responseText)
      $("#timeout").hide();
      if (typeof(on_done) != "undefined"){
        on_done(result);
      }
    } else {
      $("#crash").show();
    }
  }
}

// Resource load wrapper
function load_resource(name, on_done) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", name, true);
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      var result = JSON.parse(xhr.responseText);
      on_done(result);
    }
  }
  xhr.send();
}

// Code that runs first
$(document).ready(function(){
    // race condition if init() does RPC on function not yet registered by restart()!
    //restart();
    //init();
    invoke_rpc( "/restart", {}, 0, function() { init(); } )
});

function restart(){
  invoke_rpc( "/restart", {} )
}

//  LAB CODE

// this is inlined into infra/ui/ui.js

function handle_better_together(){
  var betterOne = document.getElementById("betterOne").value;
  var betterTwo = document.getElementById("betterTwo").value;

  if (!(betterOne in name_mappings)){
    $("#message_out").text("\"" + betterOne + "\" isn't an actor we know about :(").addClass("bad");
    return;
  }

  if (!(betterTwo in name_mappings)){
    $("#message_out").text("\"" + betterTwo + "\" isn't an actor we know about :(").addClass("bad");
    return;
  }

  var betterTogether_handler = function( result ) {
    updateGraph([name_mappings[betterOne], name_mappings[betterTwo]], true);
    if (result) {
      $("#message_out").text("Yes, " + betterOne + " and " + betterTwo + " acted together!").removeClass("bad");
    } else {
      $("#message_out").text("No, " + betterOne + " and " + betterTwo + " did not act together :(").addClass("bad");
    }
  };

  var args = {  "actor_1": name_mappings[betterOne],
                "actor_2": name_mappings[betterTwo] };
  invoke_rpc( "/better_together", args, 1000, betterTogether_handler);
}

function handle_infinity(){
  // gracefully chooze 0 if n is not a number
  var n = parseInt(document.getElementById("n").value) || 0;

  var infinity_handler = function( result ){
    if (result){
      updateGraph(result, false);
      $("#message_out").text("Okay! We've marked them below:").removeClass("bad");
    } else {
      updateGraph(result, false);
      $("#message_out").text("We couldn't find anyone with that bacon number :(").addClass("bad");
    }
  };

  var args = {  "n": n };
  invoke_rpc( "/bacon_number", args, 1000, infinity_handler);
}

function handle_findingNemo(){
  var actor = document.getElementById("findingNemo").value;

  if (!(actor in name_mappings)){
    $("#message_out").text("\"" + actor + "\" isn't an actor we know about :(").addClass("bad");
    return;
  }

  var findingNemo_handler = function( result ) {
    if (result){
      updateGraph(result, true);
      $("#message_out").text("Okay! We've marked the path below:").removeClass("bad");
    } else {
      $("#message_out").text("We didn't find a path :()").addClass("bad");
    }
  };

  var args = {  "actor_name": name_mappings[actor] };
  invoke_rpc( "/bacon_path", args, 1000, findingNemo_handler);
}

var name_mappings = {};

function init(){
  // Fetch name bindings
  var names_callback = function( result ) {
    name_mappings = result;

    var actor_choices = [];
    for (var actor in name_mappings) {
      actor_choices.push({text: actor, value: name_mappings[actor]});
    }

    $("#betterOne").immybox({ choices: actor_choices });
    $("#betterTwo").immybox({ choices: actor_choices });
    $("#findingNemo").immybox({ choices: actor_choices });
  }
  var args = { "path": "resources/small_names.json"}
  invoke_rpc( "/load_json", args, 0, names_callback);

  d3.json("/resources/ui/ui_graph_data.json", function (error, graph) {
    if (error) throw error;
    window.graph = graph;
    drawForce(graph);
  });
}

// D3-related mess
function getColor(groupNumber){
  switch(groupNumber) {
    case 1:
      return "#aec7e8";
    case 2:
      return "#ff7f0e";
    case 3:
      return "#1f77b4";
    case 4:
      return "#2ca02c"
    default:
      return "#aec7e8";
  }
}

function getValuebyId(val){
  if (window.graph) {
    return window.graph.nodes[val].value;
  } else { return null; }
}

var force;

function handle_resize(){
  var width = document.getElementById('graph').offsetWidth;
  var height = document.getElementById('graph').offsetHeight;
  force.size([width, height]).resume();
}
window.onresize = handle_resize;

function drawForce(graph) {
  var svg = d3.select("#graph")
              .html('')
              .append("svg")
              .attr("width", "100%")
              .attr("height", "80ex");

  force = d3.layout.force()
                    .charge(-120)
                    .linkDistance(50);

  handle_resize();

  force.nodes(graph.nodes)
       .links(graph.links)
       .start();

  var link = svg.selectAll(".link")
                .data(graph.links)
                .enter().append("line")
                .attr("class", "link")
                .attr('stroke', function (d) {
                  return d.edge_color;
                })
                .style("stroke-width", function (d) {
                  return Math.sqrt(d.value);
                });

  var node = svg.selectAll(".node")
                .data(graph.nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", 8)
                .style("fill", function (d) {
                  return getColor(d.group);//color(d.group);
                })
                .call(force.drag);

  node.append("title") .text(function (d) { return d.name; });

  force.on("tick", function () {
          link.attr("x1", function (d) {
              return d.source.x;
          })
       .attr("y1", function (d) {
          return d.source.y;
       })
       .attr("x2", function (d) {
          return d.target.x;
       })
       .attr("y2", function (d) {
          return d.target.y;
       });

       node.attr("cx", function (d) { return d.x; })
           .attr("cy", function (d) { return d.y; });
  });
}

function updateGraph(values, mark_edges) {
  if (window.graph) {
    var bacon = 4724;
    var graph = window.graph;

    // reset the graph
    // clear selected nodes
    for (var i = 0; i < graph.nodes.length; i++) {
      if (graph.nodes[i].value == bacon) {
        graph.nodes[i].group = 2;
      } else {
        graph.nodes[i].group = 1;
      }
    }
    // clear selected edges
    for (var i = 0; i < graph.links.length; i++) {
      graph.links[i].edge_color = "#999999";
      graph.links[i].value = 1;
    }

    // Select all nodes in values
    for (var i = 0; i < graph.nodes.length; i++) {
      // if node is in values but isn't bacon, select it
      var g_val = graph.nodes[i].value;
      if ((g_val != bacon) && (values.indexOf(g_val) >= 0)){
        graph.nodes[i].group = 4;
      }
    }

    // select all edges between values
    if (mark_edges) {
      for (var i = 0; i < graph.links.length; i++) {
        // figure out what this edge connects
        var x, y;
        if (typeof graph.links[i].source == "object"){
          x = graph.links[i].source.value;
          y = graph.links[i].target.value;
        } else {
          x = getValuebyId(graph.links[i].source);
          y = getValuebyId(graph.links[i].target);
        }

        // is this edge connecting consecutive in values?
        var ix, iy;
        ix = values.indexOf(x);
        iy = values.indexOf(y);
        if ((ix>=0) && (iy>=0) && (Math.abs(ix-iy) == 1)){
          graph.links[i].edge_color = "#F44336";
          graph.links[i].value = 16;
        }
      }
    }

    drawForce(graph);
  }
}

