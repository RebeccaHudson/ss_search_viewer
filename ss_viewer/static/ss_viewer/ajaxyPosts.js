function pull_search_type(form_data){
  console.log(form_data); //form_data is now a form_element
  var action = $(form_data).attr('action').split("/")[1];
  return action;
}

function setup_shared_search_controls_dict(){
  var shared_controls_element = document.querySelector('#shared_controls');
  var shared_controls_inputs = $(shared_controls_element).find('input, input:hidden');
  var shared_search_controls_dict = {};
  var motif_ic = []; 

  for ( var one_thing of shared_controls_inputs){
    var v = $(one_thing).val(); 
    var w = $(one_thing).attr('name');
    //console.log("hand iterating: k = " + w + "  v= " + v);
    if ( ((w == 'ic_filter')) && ( $(one_thing)[0].checked )) { motif_ic.push(v);  }else{
       shared_search_controls_dict[w] = v;    
    }
  }
  shared_search_controls_dict['ic_filter']  = motif_ic;
  shared_search_controls_dict['sort_order'] = 
             JSON.parse(shared_search_controls_dict['sort_order']);
  return shared_search_controls_dict;
}

function create_search_post(){
 var formElement = document.querySelector('div.active form');
 form_data = new FormData(formElement); 

 var search_type = pull_search_type(formElement);
 form_data.append('search_type', search_type);
 form_data.append('action',  'search');

 form_data.append('shared_controls', 
                  JSON.stringify(setup_shared_search_controls_dict()));

 //console.log("here's the form data in create_search_post"); 
 //console.log(form_data);

 hideControlsWhileLoading();

  $.ajax({
      beforeSend: function(xhr, settings) {
        csrfSafeSend(xhr, settings)
        msg = "atSNP Search is working. <br />Please wait...";
        show_or_hide_spinner(true, msg);
      },
      url: search_type + '/', 
      type: "POST", 
      data: form_data,     //was just form_data
      processData: false,
      cache: false,
      contentType: false,
      success: function(json) {
          handleResults(json.form_data, json);
          $("#type_of_shown_results").text(search_type);
      },
      error: function(xhr, errmsg, err) {
          console.log("xhr");
          console.log(xhr);
          console.log("errmsg");
          console.log(errmsg);
          show_or_hide_spinner(false);
          if (xhr.status == 504) {
             console.log("indicating a timeout");
             showTimeout();
          }else {
             console.log("not a timeout error, but an error");
             showFormErrors(xhr);
          }
      },
      complete: function(){
          show_or_hide_spinner(false);
      }
  });              
}

function create_paging_post(action_name, search_type){
 var val_text = $("div#current_search_params").text();
 var values = jQuery.parseJSON(val_text);

 values['action'] = action_name

 hideControlsWhileLoading();
 
 if ( ! ( typeof(values['sort_order']) == "string") ) {
   values['sort_order'] =  JSON.stringify(values['sort_order']);
 }

 if ( ! ( typeof(values['ic_filter']) == "string") ) {
   values['ic_filter'] =  JSON.stringify(values['ic_filter']);
 }

 $.ajax({
      beforeSend: function(xhr, settings) {
           csrfSafeSend(xhr, settings);
           var msg = "atSNP Search is working. <br />Please wait...";
           show_or_hide_spinner(true, msg);
      },
      url: search_type + '/', 
      type: "POST", 
      data: values , 
      success: function(json) {
          handleResults(values, json);
      },
      error: function(xhr, errmsg, err) {
          showFormErrors(xhr);
      },
      complete: function(){
          show_or_hide_spinner(false);
      }
  });              
} //also handles 'jump' action to jump to any valid page.


//shared between success handler for search and paging posts.
function handleResults(values, json){
    $("#drop-in").empty();     //remove the metadata type stuff. It's no longer needed.
    show_search_results(json); //the json here is no longer just json
   
    var message = $("#status-message-for-results").text();

    $("div.status_message").text(message);
    $("span.status_message").text(message);
    
    if (json.search_paging_info != null){ 
        values.page_of_results_shown =
            json.search_paging_info.page_of_results_to_display;
         //Sets the page number of displayed results.
    }else{ 
        //not setting the page of search results; but no error means 
        //that this is a non-error, but empty search results case.
        showStatusInCorrectPlace(true);
    }
}


function showTimeout(){
    var errlist = '<ul>';
    errlist += '<li> Search timed out. Further restrict your query or try agian later. </li>';
    errlist += '</ul>';
    $("div#form_errors").append(errlist);
    $("div.status_message").text("");
    showHidePrevNext(null); //hides the next and previous buttons.
    showStatusInCorrectPlace(true);
}



function showFormErrors(xhr){
    //console.log(xhr.status + ": " + xhr.responseText);
    var errorJSON = jQuery.parseJSON(xhr.responseText);
    var errlist = '<ul>';
    for ( var j = 0; j < errorJSON.form_errors.length; j++){
        errlist += '<li>' + errorJSON.form_errors[j] + '</li>';
    } 
    errlist += '</ul>';
    $("div#form_errors").append(errlist);
    $("div.status_message").text(errorJSON.status_message);
    showHidePrevNext(null); //hides the next and previous buttons.
    showStatusInCorrectPlace(true);
}

function check_if_set_can_be_downloaded(){
    var search_paging_info = jQuery.parseJSON($("#search_paging_info").text());
    var hitcount = search_paging_info['total_hitcount']; 
    if (hitcount > 5000){
        $("div.modal.fade").modal('show');
        return false;
    }
    return true;
}



//may be factored back into other create_post function; separate for now.
//SOURCE:
//http://stackoverflow.com/questions/28165424/download-file-via-jquery-ajax-post
function create_download_post(search_type) {

  if ( ! check_if_set_can_be_downloaded() ) {
    console.log("blocking a download that is too large.");
    return;
  }  

  var val_text = $("div#current_search_params").text();
  values = jQuery.parseJSON(val_text);
  values['action'] = 'Download Results';

 //this code is copied out of paging handler
 //TODO: factor it out into a sepearate function so it's not repeated.
 if ( ! ( typeof(values['sort_order']) == "string") ) {
   values['sort_order'] =  JSON.stringify(values['sort_order']);
 }

 if ( ! ( typeof(values['ic_filter']) == "string") ) {
   values['ic_filter'] =  JSON.stringify(values['ic_filter']);
 }

  var result_text = $("#status_above").text(); //Saved to be replaced after download.

  //Don't hide the download explanation box while preparing the download.
  $("div.status_message").text("Working... ");
  showStatusInCorrectPlace(true);//show the upper one, hide the lower

  var msg = "Downloads are limited to 5,000 rows. <br /> Please wait...";
  show_or_hide_spinner(true, msg);

  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      var a;
      if (xhttp.readyState === 4 && xhttp.status === 200) {
          a = document.createElement('a');
          a.href = window.URL.createObjectURL(xhttp.response);
          a.download = "search-results-download.csv";
          a.style.display = 'none';
          document.body.appendChild(a);
          a.click();
          $("div.status_message").text(result_text);
          //console.log("removed the link immediately, there");
          //a.remove();
      }
      if (xhttp.readyState == XMLHttpRequest.DONE) {
            show_or_hide_spinner(false);
           // console.log("removed the link, there");
           // a.remove();
      }
      console.log("the xhttp readyState will follow this:");
      console.log(xhttp.readyState);
  };

  xhttp.open("POST",search_type + '/');
  xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhttp.setRequestHeader("X-CSRFToken", csrftoken);

  // You should set responseType as blob for binary responses
  xhttp.responseType = 'blob';
  xhttp.withCredentials = true;
  xhttp.ontimeout = function () { alert("Timed out!!!"); }
  xhttp.send(JSON.stringify(values)); /* this is where timeouts are detected*/
}

//try to use everywhere the spinner appears. 
//true for show, false for hide.
function show_or_hide_spinner(showOrHide, msg=null){
  if (showOrHide === true){
    var target = $("body");
    var spinner = new Spinner().spin();
    target.append(spinner.el);
    console.log(spinner.el);

    if (msg != null){
        $("#loading_message p")[0].innerHTML = msg;
    } 

    $("#loading").show(); 
  }
  else{ 
        $("div.spinner").remove();
        $("#loading").hide(); 
  }
}

//true for upper, false for lower.
function showStatusInCorrectPlace(isUpper){
    if (isUpper === true){
        $("#status_above").show();
        $("#status_below").hide();
    }else{
        $("#status_above").hide();
        $("#status_below").show();
    }    
}

/*Don't let users jump past the end of the search results.
  use total_page_count or max_page_availabe, whichever one is greater. 
  Don't allow paging past max_result_window / page_size (666 for now) */
function setMaxValueOnJumpControl(search_paging_info){
   var maxPg;
   console.log("search paging info");
   if (search_paging_info.max_page_available <  
         search_paging_info.total_page_count){
        maxPg = search_paging_info.max_page_available;
      }else{
        maxPg = search_paging_info.total_page_count;
      }
      $("#user-page-number").attr('max',maxPg );
      $("#max_pg_available").text(maxPg);
}

function  hideControlsWhileLoading(){
   $("div.status_message").text("Working... ");
   showStatusInCorrectPlace(true);
   $("#download_button").hide();
   showHidePrevNext(null); 
}

//shared in beforeSend for paging and search requests.
function csrfSafeSend(xhr, settings){
  if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
  }

}
