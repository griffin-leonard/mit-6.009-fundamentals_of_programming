"use strict";

// RPC wrapper
function invoke_rpc(method, args, timeout, on_done) {
  hide($("#crash"));
  hide($("#timeout"));
  show($("#rpc_spinner"));
  //send RPC with whatever data is appropriate. Display an error message on crash or timeout
  var xhr = new XMLHttpRequest();
  xhr.open("POST", method, true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.timeout = timeout;
  xhr.send(JSON.stringify(args));
  xhr.ontimeout = function () {
    show($("#timeout"));
    hide($("#rpc_spinner"));
    hide($("#crash"));
  };
  xhr.onloadend = function () {
    if (xhr.status === 200) {
      hide($("#rpc_spinner"));
      var result = JSON.parse(xhr.responseText);
      hide($("#timeout"));
      if (typeof (on_done) != "undefined") {
        on_done(result);
      }
    } else {
      show($("#crash"));
    }
  };
}

// Resource load wrapper
function load_resource(name, on_done) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", name, true);
  xhr.onloadend = function () {
    if (xhr.status === 200) {
      var result = JSON.parse(xhr.responseText);
      on_done(result);
    }
  };
  xhr.send();
}


function hide($object) {
  $object.css({
    display: 'none'
  });
}

function show($object) {
  $object.css({
    display: 'inline-block'
  });
}

// Code that runs first
$(document).ready(function(){
    invoke_rpc( "/restart", {}, 0, function() { init(); } );
});

function restart(){
  invoke_rpc( "/restart", {} );
}

//  LAB CODE

var step = 50;

var ghosting = false;
var debug = false;

var busy = false;
var emoji;
var path;
var mouse_action = null;
var svg_width;
var svg_height;
var scale_x;
var scale_y;
var last_data;

var tile_size = 1;
var window_size;

var intervalId = null;

var DIRECTION_BUTTONS = [37,38,39,40];
var BUTTON_ON = "mdl-button--colored button-on";
var PATH_DIM = 30;

// Towers are hardcoded for now.
var TOWER_INFO = {
    'ThriftyZookeeper': {'price': 100, 'texture': '1f46e'},
    'OverreachingZookeeper': {'price': 150, 'texture': '1f477'},
    'SpeedyZookeeper': {'price': 250, 'texture': '1f472'}
}

// convert game data into svg
function display(data) {
    // Initialize the background svg.
    init_svg();
    var states = data[0];
    var formations = data[1];
    var money = data[2];
    path = data[3];
    var targets_remaining = data[4];
    var step_num = data[5] + 1;
    
    // Update balance.
    $('#game-stats').text('Overall Money: $' + money + ' - Remaining Lives: ' + targets_remaining);

    // Create the state and reference state.
    var state = states[0];
    var ref_state = states[1];
    $('#game-state').text(state).removeClass("warning");
    $('#game-frame').text('');
    enable_forward_buttons();

    if (ghosting) {  
      if (ref_state) { 
        $('#game-frame').text('; Ref Frame: '+ step_num);
        if (state != ref_state) {
          $('#game-state').text("should be " + ref_state + ", but is " + state + "!").addClass("warning");
        }
      } else {
        // ghost mode must be over
        disable_forward_buttons();
        if (intervalId) { // if it's running, pause it
          handle_pause_button();
        }
      }
    } 

    var showGhosts = $('#show-ghosts').prop('checked');
    var showMain = $('#show-main').prop('checked');
    formations = formations.filter(function(formation) {
      // if it's a ghost and we're showing ghosts or
      // if it's not a ghost and we're showing normals
      return (!!formation.ghost && showGhosts) || (!formation.ghost && showMain);
    });

    // build list of svg for emoji
    var flist = [];
    formations.forEach(function(formation) {
        // formation attributes: texture, rect
        var svg = emoji[formation.texture];
        if (svg === undefined) {
            console.log('no emoji for '+JSON.stringify(formation));
        } else {
            var x = (formation.rect[0]-(formation.rect[2]-1)/2).toString();
            var y = (formation.rect[1]-(formation.rect[3]-1)/2).toString();
            var g = '<g transform="translate('+x+' '+y+')';
            
            var scalex = scale_x * ((formation.rect[2]-1) / 60);
            var scaley = scale_y * ((formation.rect[3]-1) / 60);
            
            if (scalex != 1 || scaley != 1) {
                g += 'scale('+scalex.toString()+' '+scaley.toString()+')';
            }
            g += '"';
            if (formation.ghost) {
                g += ' opacity="0.5"';
            }
            g += '>';
            g += svg;
            if (debug) {
                g += '<rect x="0" y="0" width="64" height="64" stroke="red" stroke-width="2" fill="none"/>';
                g += '<text x="-5" y="-5" text-anchor="end" stroke="red" fill="red">'+x.toString()+","+y.toString()+'</text>';
            }
            g += '</g>';
            flist.push(g);
        }
    });

    // Update the SVG.
    var bigger_svg = document.getElementById("game-grid");
    bigger_svg.innerHTML = create_path(path) + flist.join('');
}

function init_svg() {
    var w = $('#wrapper');
    svg_width = w.width();
    svg_height = 3*svg_width/4;   // 4:3 aspect ratio
    
    // Initialize the global scale.
    scale_x = svg_width / window_size[0];
    scale_y = svg_height / window_size[1];
}

function create_path(path) {
    var plist = [];
    for (var i = 0; i < path.length-1; i++) {
        // Extract meaningful information from the points.
        var start_x = path[i][0], start_y = path[i][1];
        var end_x = path[i+1][0], end_y = path[i+1][1];
        
        // Depending on what direction is being traversed, construct the rectangle.
        var x, y, width, height;
        if (start_x == end_x) {
            width = PATH_DIM;
            height = Math.abs(end_y-start_y)+PATH_DIM;
            
            // Going down.
            if (end_y > start_y) {
                x = (start_x-PATH_DIM/2).toString();
                y = (start_y-PATH_DIM/2).toString();
            } else {
                x = (end_x-PATH_DIM/2).toString();
                y = (end_y-PATH_DIM/2).toString();
            }
        } else {
            width = Math.abs(end_x-start_x)+PATH_DIM;
            height = PATH_DIM;
            
            // Going right.
            if (start_x < end_x) {
                x = (start_x-PATH_DIM/2).toString();
                y = (start_y-PATH_DIM/2).toString();
            } else {
                x = (end_x-PATH_DIM/2).toString();
                y = (end_y-PATH_DIM/2).toString();
            }
        }
        
        // Construct the rectangle.
        var g = '<rect x="' + x + '" y="' + y + '" width="' + width + '" height="' + height + '" stroke="#e4e4a1" stroke-width="1" fill="#e4e4a1"/>';
        plist.push(g);
    }
    return plist.join('');
}

function debug_render() {
  if (last_data) {
    display(last_data);
  }
}

function disable_ghost_button(){
  $("#ghost").prop('disabled', true).css('visibility', 'hidden');
}

function enable_ghost_button(){
  $("#ghost").prop('disabled', false).css('visibility', 'visible');
}

function disable_forward_buttons(){
  $("#step_simulation").prop('disabled', true);
  $("#run_simulation").prop('disabled', true);
}

function enable_forward_buttons(){
  $("#step_simulation").prop('disabled', false);
  $("#run_simulation").prop('disabled', false);
}

function hide_all_simulate_buttons() {
  $("#step_simulation").css('display','none');
  $("#run_simulation").css('display','none');
  $("#pause_simulation").css('display','none');
}

function show_forward_buttons() {
  $("#pause_simulation").css('display','none');
  $("#run_simulation").css('display','inline-block');
  if (ghosting) {
    $("#step_simulation").css('display','inline-block');
  }
}

function show_pause_button() {
  $("#pause_simulation").css('display','inline-block');
  $("#run_simulation").css('display','none');
  $("#step_simulation").css('display','none');
}

function timestep(actions) {
    busy = true;

    init_svg();

    invoke_rpc('/timestep', [mouse_action, ghosting], 500, function (data) {
        last_data = data;
        if (emoji) display(data);
        busy = false;
        mouse_action = null;
    });
}

// like timestep, but don't advance game state
function render() {
    busy = true;
    init_svg();

    invoke_rpc('/render', [ghosting], 500, function (data) {
        last_data = data;
        if (emoji) display(data);
        busy = false;
    });
}

function init_gui() {
    // add mouse listener to game board
    mouse_action = null;
    
    $("#wrapper").on('click', function(event) {
        var posX = $(this).offset().left, posY = $(this).offset().top;
        mouse_action = [(event.pageX - posX), (event.pageY - posY)];
    });
    
    $('#show-main').on('change', debug_render);
    $('#show-ghosts').on('change', debug_render);
    
    // load SVG for all the emoji
    load_resource('/resources/emoji.json',function (data) {
        emoji = {};
        var re = new RegExp('\<svg.*?\>(.*)\</svg\>');
        $.each(data,function(codepoint,svg) {
            svg = svg.replace(re,'$1');
            emoji[codepoint] = svg;
        });
        $(document).ready(function(){
            init_tower_carousel();
            $(".owl-carousel").owlCarousel({
                loop: false,
                margin: 10,
                nav: true,
                navText: ["<img src='left-arrow.png' class='nav-arrow'>","<img src='right-arrow.png' class='nav-arrow'>"],
                mouseDrag: false
            });
        });  
        if (last_data) display(last_data);
    });

    // hide controls until we have a map
    hide_all_simulate_buttons();
    
    // getting around a material bug where the menu doesn't close on click?
    $('#map_list').click(function () {
      $('.is-visible').removeClass('is-visible');
    });

    // set up map selection
    invoke_rpc("/ls", {"path":"resources/maps/"}, 0, function(loaded) {
        loaded.sort();
        for (var i in loaded) {
            if (loaded[i] != "zoo1-tiny.json") { // do not display zoo1-tiny on UI
                $("#map_list").append(
                    "<li class=\"mdl-menu__item\" onclick=\"handle_map_select('" +
                        loaded[i] +
                        "')\">" +
                        loaded[i] +
                        "</li>");
            }
        }
        // start by selecting a map
        // if a valid one is stored, us it
        var map = sessionStorage.getItem('map');
        if (!map || loaded.indexOf(map)<0) {
          map = loaded[0];
        }
        handle_map_select(map);
    });
}

function init_tower_carousel() {
    // Fetch the carousel.
    var tower_carousel = document.getElementById("tower-carousel");
    
    // Create divs for each item.
    for (let key in TOWER_INFO) {
        // Create the containing div and store attributes.
        let div = document.createElement('div');
        div.classList.add("tower");
        div.classList.add("item");
        let new_emoji = emoji[TOWER_INFO[key]['texture']];
        if (new_emoji === undefined) {
            console.log('no emoji for '+JSON.stringify(key));
        }
        let tower_cost = TOWER_INFO[key]['price'];
        
        // Create the SVG (icon) of the tower.
        let body = '<svg width="' + 
            "60" +
            '" height="' +
            "60"+
            '" viewbox="0 0 ' +
            "60"+
            ' ' +
            "60"+
            '">';
        body += '<g>' + new_emoji + '</g>'
        body += "</svg>";
        
        // Add text.
        body += '<p>' + key.toString() + '</p>'
        body += '<p>$' + tower_cost.toString() + '</p>'
        
        // Add all information to the tower. the tower.
        div.innerHTML = body;
        
        // Add listeners.
        div.addEventListener('click', function(event) {
            mouse_action = key;
        });
        
        tower_carousel.appendChild(div);
    }
}

function handle_map_select(value){
    pause();
    ghosting = false;
    update_ghost_button_display();

    hide_all_simulate_buttons();

    invoke_rpc('/init_game',value,500,function (args) {
        $('#current_map').text(value);
        show_forward_buttons();
        sessionStorage.setItem('map', value);
        if (args[0]) {
          enable_ghost_button();
        } else {
          disable_ghost_button();
        }
        window_size = args[1];
        
        render();
    });
}

function handle_reset_button() {
    pause();
    handle_map_select($('#current_map').text());
}

function handle_simulate_button(){
  // start simulation
  if(!intervalId){
    // show / hide GUI elements
    show_pause_button();
    mouse_action = null;
    start();
  }
}

function handle_step_button(){
  timestep();
}

function handle_ghost_button(){
    ghosting = !ghosting;
    update_ghost_button_display();
    render();
}

function update_ghost_button_display() {
    var button = $('#ghost');
    var toggles = $('.view-toggle');
    var step_button = $('#step_simulation');
    if (ghosting) {
        button.addClass(BUTTON_ON);
        toggles.css('visibility', 'visible');
        step_button.css('display','inline-block');
    } else {
        button.removeClass(BUTTON_ON);
        toggles.css('visibility', 'hidden');
        step_button.css('display','none');
    }
  
}

function handle_pause_button(){
  if(intervalId){
    // show / hide GUI elements
    show_forward_buttons();
    pause();
  }
}

function handle_debug_button() {
    debug = !debug;
    var button = $('#debug');
    if (debug) {
        button.addClass(BUTTON_ON);
    } else {
        button.removeClass(BUTTON_ON)
    }

    if (last_data) display(last_data);
}

function start() {
    timestep();
    intervalId = setInterval(function() {
      if (!busy) timestep()
    }, step);
}

function pause() {
    clearInterval(intervalId);
    intervalId = null;
}

function init(){
    init_gui();
}


