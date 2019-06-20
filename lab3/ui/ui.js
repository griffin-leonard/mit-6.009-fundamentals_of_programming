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
      var board = JSON.parse(xhr.responseText)
      hide($("#timeout"));
      if (typeof (on_done) != "undefined") {
        on_done(board);
      }
    } else {
      show($("#crash"));
    }
  }
}

// Resource load wrapper
function load_resource(name, on_done) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", name, true);
  xhr.onloadend = function () {
    if (xhr.status === 200) {
      var board = JSON.parse(xhr.responseText);
      on_done(board);
    }
  }
  xhr.send();
}

// Code that runs first
$(document).ready(function () {
  invoke_rpc("/restart", {}, 0, function () { init(); })
});

function restart() {
  invoke_rpc("/restart", {})
}

//  LAB CODE

// this is inlined into infra/ui/ui.js

var canvas;
var ctx;

var chosen_dim_x = 0;
var chosen_dim_y = 0;
var chosen_slice;
var dimensions;
var xray_state;

var render_board;

var canvas = null;
var context = null;

var SQUARE_SIZE = 30;
var DEFAULT_DIMENSIONS = "[10, 10]";

// --------------------- init functions ------------------------//

function init_board() {
  var error = false;
  var new_dimensions = get_size(function(err, msg) {
    signal_input_error(msg);
    error = true;
  });

  if (error) {
    return;
  }
  
  change_xray_state("XRAY OFF");
  xray_state = false;

  change_board_state("NEW GAME!");

  // to prevent error from overwriting the previous valid game
  dimensions = new_dimensions;

  chosen_dim_y = 0;
  if (dimensions.length > 1) {
    chosen_dim_x = 1;
  } else {
    chosen_dim_x = 0;
  }

  setup_selectors();

  chosen_slice = dimensions.map(function() {
    return 0;
  });

  var board_rows = dimensions[chosen_dim_y];
  var board_cols = dimensions[chosen_dim_x];

  var width = board_cols * SQUARE_SIZE;
  var height = board_rows * SQUARE_SIZE;

  var num_bombs = get_num_bombs();
  var bomb_list = new_random_game(num_bombs);

  invoke_rpc("/ui_new_game", get_args({bombs: bomb_list}), 0, function () {
    render_rpc();
  });
}

function init() {
  init_board();
  init_gui();
}

function get_num_bombs() {
  var num_dims = dimensions.length;
  var av = dimensions.reduce(function(a,b) {return a+b})/num_dims;
  return Math.floor(Math.pow(av, num_dims/2));
}

// -------------------- interaction logic ----------------------//

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

function init_gui() {
  canvas = document.getElementById('myCanvas');
  context = canvas.getContext('2d');

  canvas.addEventListener('click', function (evt) {
    var mousePos = get_square(canvas, evt);
    if (!xray_state) {
      dig_square(mousePos.y, mousePos.x);
    }
  }, false);

  $("#dimensions").on('keyup', function (e) {
    if (e.keyCode == 13) {
      handle_new_game();
    }
  });

  show($('#rpc_status'));
}

function get_square(canvas, evt) {
  var rect = canvas.getBoundingClientRect();
  return {
    x: Math.floor((evt.clientX - rect.left) / SQUARE_SIZE),
    y: Math.floor((evt.clientY - rect.top) / SQUARE_SIZE)
  };
}

function change_board_state(text, type) {
  var elt = $('#gameStateText');
  elt.removeClass();
  if (type === 'victory') {
    elt.addClass('win');
  } else if (type === 'defeat') {
    elt.addClass('lose');
  }
  elt.text(text);
}

function change_xray_state(text) {
  document.getElementById('xray_button').innerHTML = text;
}

function get_size(onerr) {
  var size_string = document.getElementById('dimensions').value;
  size_string = size_string.replace("[", "").replace("]", "");
  var size;
  try {
    size = parse_size("[" + size_string + "]");
  }
  catch(err) {
    onerr(err, "input incorrectly formatted");
    return;
  }

  if (size.length === 0) {
    onerr(null, "empty array is not valid");
    return;
  }

  size = size.map(function(dim) {
    return Math.max(parseInt(dim), 0); 
  });

  size.forEach(function(dim) {
    if (dim === 0) {
      onerr(null, "zero is not a valid dimension");
      return;
    }
  });

  document.getElementById('dimensions').value = JSON.stringify(size);

  return size;
}

function handle_new_game() {
  hide($('#input-error'));
  init_board();
}

function disable_radio() {
  $('#choose-coord input[type="number"]').attr('disabled', false);

  var selected_x = $('input[type="radio"][name="selector_x"]:checked').val();
  var selected_y = $('input[type="radio"][name="selector_y"]:checked').val();
  
  $($('#choose-coord input[type="number"]')[selected_x]).attr('disabled', true);

  $($('#choose-coord input[type="number"]')[selected_y]).attr('disabled', true);
}

function setup_selectors() {
  var selector_dim = $('#selector>#dim-name>.content');
  var selector_x = $('#selector>#choose-x>.content');
  var selector_y = $('#selector>#choose-y>.content');
  var selector_coord = $('#selector>#choose-coord>.content');

  selector_dim.html('');
  selector_x.html('');
  selector_y.html('');
  selector_coord.html('');

  dimensions.forEach(function(dim, i) {
    var dim_name = $('<div>'+i+'</div>');
    selector_dim.append(dim_name);

    var x_sel = $('<div><input class="mdl-radio__button" type="radio" name="selector_x" value="'+i+'"></div>');
    
    var y_sel = $('<div><input  class="mdl-radio__button" type="radio" name="selector_y" value="'+i+'"></div>');

    x_sel.on('change', function() {
      disable_radio();
      render_selected();
    });
    
    y_sel.on('change', function() {
      disable_radio();
      render_selected();
    });

    selector_x.append(x_sel);
    selector_y.append(y_sel);

    var coord_sel = $('<div><input class="coord-sel" type="number" min="0" max="'+(dim-1)+'" value="0"></div>');
    coord_sel.on('input', function() {
      var input = $($('#choose-coord input[type="number"]')[i]);
      var val = input.val();
      val = parseInt(val);
      val = val? val: 0;
      val = Math.max(Math.min(val, dim-1), 0);
      input.val(val);
      render_selected();
    });
    selector_coord.append(coord_sel);
  });

  $('input[type="radio"][name="selector_x"][value="'+chosen_dim_x+'"]').prop("checked", true);
  $('input[type="radio"][name="selector_y"][value="'+chosen_dim_y+'"]').prop("checked", true);

  disable_radio();
};

function render_selected() {
  chosen_dim_x = parseInt($('input[type="radio"][name="selector_x"]:checked').val());
  chosen_dim_y = parseInt($('input[type="radio"][name="selector_y"]:checked').val());

  dimensions.forEach(function(dim, i) {
    var val = parseInt($($('#choose-coord input[type="number"]')[i]).val()); 
    chosen_slice[i] = val;
  });

  render(render_board);
}

function signal_input_error(msg) {
  $('#input-error #message').text(msg);
  show($('#input-error'));
}

// ------------------- Render logic -------------------------------------//

function render(render_board) {
  // calculate unit for lattice cell 
  var board_rows = dimensions[chosen_dim_y];
  var board_cols = dimensions[chosen_dim_x];

  // if it's actually a 1D slice they want
  if (chosen_dim_x === chosen_dim_y) {
    board_rows = 1;
  }

  var width = board_cols * SQUARE_SIZE;
  var height = board_rows * SQUARE_SIZE;

  canvas.height = height;
  canvas.width = width;  
  context.clearRect(0, 0, width, height);

  // draw lines for each column
  for (var x = 0; x <= board_cols; x += 1) {
    context.beginPath();
    context.moveTo(x * SQUARE_SIZE, 0);
    context.lineTo(x * SQUARE_SIZE, height);
    context.strokeStyle = "#000";
    context.lineWidth = 1;
    context.stroke();
    context.closePath();
  }

  // draw lines for each row
  for (var y = 0; y <= board_rows; y += 1) {
    context.beginPath();
    context.moveTo(0, y * SQUARE_SIZE);
    context.lineTo(width, y * SQUARE_SIZE);
    context.strokeStyle = "#000";
    context.lineWidth = 1;
    context.stroke();
    context.closePath();
  }

  // color each square
  // get_value

  // using the recursive getter here
  for (var row = 0; row < board_rows; row++) {
    for (var col = 0; col < board_cols; col++) {
      var coord = chosen_slice.slice();
      coord[chosen_dim_y] = row;
      coord[chosen_dim_x] = col;

      var value = get_value(coord, render_board);

      if (value == '_') {
        square_style_fill(col, row);
      }
      else if (value == '.') {
        square_style_bomb(col, row);
      }
      else if (value == ' ') {
        //empty cell, pass
      }
      else {
        square_style_text(col, row, value);
      }
    }
  }
}

// ---------------------------- game helper logic ---------------------------//

function parse_size(size_string) {
  return JSON.parse(size_string);
}

function new_random_game(num_bombs) {
  var bomb_list = [];

  var bomb_set = new Set();

  var board_rows = dimensions[chosen_dim_y];
  var board_cols = dimensions[chosen_dim_x];

  for (var i = 0; i < num_bombs; i++) {
    
    var bomb = dimensions.map(function(dim) {
      return Math.floor(Math.random() * (dim));
    });
    bomb_set.add(JSON.stringify(bomb));
  }

  for (var value of bomb_set) {
    bomb_list.push(JSON.parse(value));
  }
  return bomb_list
}

function get_value(coord, board){
  var this_coord = coord[0];
  
  // Base case
  if (coord.length === 1){
    return board[this_coord]
  }
  
  // Recursive case
  return get_value(coord.slice(1), board[this_coord])
}

// ----------------------- RPC -----------------------------------------//

function get_args(optional) {
  return {
    "xray": xray_state,
    "bombs": optional && optional.bombs,
    "dimensions": dimensions,
    "coordinates": optional && optional.coordinates,
  };
}

function render_rpc() {
  invoke_rpc("/ui_render", get_args(), 0, function(result) {
    render_board = result;
    render(render_board);
  });
}

function handle_xray_button() {
  xray_state = !xray_state;
  var board_text = xray_state? "XRAY ON (GAME PAUSED)" : "XRAY OFF";
    
  change_xray_state(board_text);
  
  render_rpc();
}

function dig_square(row, col) {
  var coord = chosen_slice.slice();
  coord[chosen_dim_y] = row;
  coord[chosen_dim_x] = col;

  invoke_rpc("/ui_dig", get_args({coordinates: coord}), 0, function (result) {
    var state = result[0];
    var dug = result[1];
    var board_text = '';
    if (state == "victory") {
      board_text = "YOU WIN - YOU CLEARED THE BOARD!";
    }
    else if (state == "defeat") {
      board_text = "YOU LOSE - YOU DUG A BOMB!";
    }
    else if (state == "ongoing") {
      board_text = "GOOD MOVE - YOU DUG " + dug + " SQUARES!";
    }
    else {
      board_text = "ERROR - CHECK YOUR GAME STATUS!";
    }
    change_board_state(board_text, state);
  
    render_rpc();
  });
}


// ----------------- Canvas drawing functions -------------------- //

function square_style_fill(x, y) {
  context.beginPath();
  context.fillStyle = "gray"
  context.fillRect(
    (x * SQUARE_SIZE) + 2, 
    (y * SQUARE_SIZE) + 2, 
    SQUARE_SIZE - 4, 
    SQUARE_SIZE - 4
  );
  context.closePath();
}

function square_style_bomb(x, y) {
  context.beginPath();
  context.fillStyle = "#FF4081"
  context.arc(
    (x + .5) * SQUARE_SIZE, 
    (y + .5) * SQUARE_SIZE, 
    SQUARE_SIZE / 2 - 4, 0, 
    Math.PI * 2, 
    true
  );
  context.fill()
  context.closePath();
}

function square_style_text(x, y, text) {
  context.beginPath();
  context.fillStyle = "#389ce2";
  
  context.font = "15px Arial";
  context.fillText(
    text, 
    (x + .5) * SQUARE_SIZE - 5, 
    (y + .5) * SQUARE_SIZE + 5
  );
  context.fill()
  context.closePath();
}
