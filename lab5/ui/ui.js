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

var selected_corpus;
var trie_mode;
var prefix;
var autocorrect;
var max_results;

// Code that runs first
$(document).ready(function(){
    // race condition if init() does RPC on function not yet registered by restart()!
    //restart();
    //init();
    invoke_rpc( "/restart", {}, 0, function() { init(); } );
    set_max_results(10);
    $('#max-results-slider').on('input', function(){
      set_max_results(this.value);
    });

    switch_mode("words");
    $('.mode-select-button').click(handle_mode_select);
    autocorrect = false;
    $('#autocorrect-switch').on('input', function() { autocorrect = this.checked; });

    // Setup autocomplete functionality
    $('#prefixbox').on('input', handle_complete);
    $('#prefixbox').keydown(navigate_completions);

    // Close autocomplete list when user clicks elsewhere on the page
    $(document).click(clearCompletions);
});

function restart(){
  invoke_rpc( "/restart", {} )
}

var corpora = {};
var selected_corpus = null;

function switch_mode(mode) {
  var mode_button = $('#' + mode + '-selector');
  mode_button.removeClass("mdl-button--colored");
  mode_button.addClass("mdl-button--accent");
  trie_mode = mode;
}

function set_max_results(val) {
  if (val > 0) {
    $('#max-results-label').html(val);    
  }
  else {
    $('#max-results-label').html('<strong>&infin;</strong>');
  }
  max_results = parseInt(val);
  if ($('#max-results-slider').val() != val) {
    $('#max-results-slider').val(val);
  }
}

// UI button handlers
function handle_mode_select(e) {
  if (trie_mode) {
    var selectedButton = $('#' + trie_mode + '-selector');
    selectedButton.removeClass("mdl-button--accent");
    selectedButton.addClass("mdl-button--colored");
  }
  switch_mode(e.target.id.split("-")[0]);
}

function handle_corpus_select(corpus_name) {
  // corpus is already loaded in memory, simply switch to it!
  $("#selected_corpus").html(corpus_name);
  selected_corpus = corpora[corpus_name];
  $("#lab_message").html("");
  //render(current_test_case, null);
}

function handle_complete() {
  prefix = $('#prefixbox').val().toLowerCase();
  if (prefix.length === 0) {
    clearCompletions();
    return;
  }
  // RPC to server.py to
  var complete_callback = function( solution ) {
    if (solution[0] != 'ok') {
      $("#lab_message").html("Your code raised an exception.");
      return;
    }/* else if (solution[1] == null) {
      $("#lab_message").html("Your code found no solution.");
    }*/
    else {
      $("#lab_message").html("Your code gave " + solution[1].length + " completion(s).");
    }

    // Show the completions
    fillCompletions(solution[1]);
  };
  invoke_rpc("/complete", {"corpus": selected_corpus,
    "prefix": prefix, "max_results": max_results,
    "trie_mode": trie_mode, "autocorrect": autocorrect},
    5000, complete_callback);
}

// Clear the list of autocompletions
function clearCompletions(e) {
  if (e != null) {
    if (e.target != null && e.target.classList && e.target.classList.contains("completion")) {
      return null;
    }
  }
  $('#completions').empty();
}

// De-highlight all completions from list
function deactivateCompletions(e) {
  $('.active-completion').removeClass('active-completion');
}

// Highlight a completion in the list
function activateCompletion(completion) {
  // If completion is an integer, get the appropriate completion element
  if (completion === parseInt(completion, 10)) {
    completion = $('#completion-' + completion);
  }
  // Else it is a mouseover event
  else {
    completion = $(completion.currentTarget);
  }
  if (completion != null) {
    deactivateCompletions();
    completion.addClass('active-completion');
  }
}

// Fill in the prefix box with a selected autocompletion
function selectCompletion(completion) {
  var completion_text = $(completion).find('span').html();
  $('#prefixbox').val(completion_text);
  clearCompletions();
}

// Allow for the completions to be navigated using arrow keys
function navigate_completions(e) {
  var active_completion = $('.active-completion');
  var num_completions = $('.completion').length;
  var active_num;
  if (active_completion.length > 0) {
    active_completion = active_completion[0];
    active_num = active_completion.id.split("-");
    active_num = parseInt(active_num[active_num.length - 1]);
  }
  switch(e.which) {
    case 40:
      // Down arrow key
      e.preventDefault();
      if (active_completion == null || active_completion.length == 0) {
        deactivateCompletions();
        activateCompletion(1);
      }
      else if (active_num < num_completions) {
        deactivateCompletions();
        activateCompletion(active_num + 1);
      }
      break;
    case 38:
      // Up arrow key
      e.preventDefault();
      if (active_completion == null || active_completion.length == 0) {
        deactivateCompletions();
        activateCompletion(num_completions);
      }
      else if (active_num > 1) {
        deactivateCompletions();
        activateCompletion(active_num - 1);
      }
      break;
    case 13:
      // Enter key
      e.preventDefault();
      if (active_completion != null) {
        // Select the active completion
        selectCompletion(active_completion);
      }
      break;
    default:
      break;
  }
}

function fillCompletions(completions) {
  // clear previous completions
  clearCompletions();
  var container = $('#completions');
  completions.forEach(function(completion, i) {
    // Add the completion to the list
    container.append("<li></li>");
    var list = container.children().last();
    list.addClass("mdl-list__item completion");
    list.attr('id', 'completion-' + (i+1));
    list.html("<span class='mdl-list__item-primary-content'>" + completion + "</span>");
    list.click(function(e) { selectCompletion(e.currentTarget); } );
    list.mouseover(activateCompletion);
    list.mouseout(deactivateCompletions);
  });
}

// Initialization code (called when the UI is loaded)
var initialized = false;
function init() {
  if (initialized) return;
  initialized = true;

  // Load list of corpora
  var corpus_names_callback = function( corpus_names ) {
    for (var i in corpus_names) {
      var filename = corpus_names[i];
      if (!(filename.match(/.*?[.]txt/i))) continue;

      var corpus_callback = function( corpus ) {
        var first = Object.keys(corpora).length == 0;
        corpora[corpus] = corpus;

        $("#corpora").append(
          "<li class=\"mdl-menu__item\" onclick=\"handle_corpus_select('" +
          corpus +
          "')\">" +
          corpus +
          "</li>");

        // is it first? select it!
        if (first) handle_corpus_select(corpus);
      };
      invoke_rpc("/load_corpus", { "path": "resources/corpora/"+filename }, 0, corpus_callback);
    };
  };
  invoke_rpc("/ls", { "path": "resources/corpora/" }, 0, corpus_names_callback);
}