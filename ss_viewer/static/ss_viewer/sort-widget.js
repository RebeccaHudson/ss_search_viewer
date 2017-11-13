/* Controls the behavior of the sort-widget found 
 * in templates/ss_viewer/sort-widget.html */

/* try to parameterize the ids of each of the select functions.*/

    jQuery(document).ready(function ($) {
      var sort_order = readSortOrder();
      buildQuery();
 

      //TODO: this is now 4 buttons instead of 1 
      $(".sortflip").on('click', function(){
         //flips the sort direction for the currently displayed field.
         //also flips the icon indicating sort order.
         var selected_field = $("div.active .sort-select option");
         /* figure out what the index of this one is */
         console.log("the .sortflip that we clicked: ");
         console.log($(this));
         if ($(this).hasClass('glyphicon-sort-by-attributes')){
             showDescendingIcon(this);
             selected_field.attr('direction', 'desc'); 
         }else{ 
             showAscendingIcon(this);
             selected_field.attr('direction', 'asc'); 
         }    
          buildQuery();
      }); 
 
      //only hits the first active div.
      //$("div.active .sort-select option").on('click', function(){
      $(".sort-select option").on('click', function(){
       //this is no longer needed, as far as I can tell.
       /*var drctn = $(this).attr('direction');
       if (drctn == 'asc' ){ showAscendingIcon(this); }else{ 
          showDescendingIcon(this);
       }*/
      });

    } );//end of document.ready stuff here.

    function showAscendingIcon(target){
       var selector = $("div.active .sortflip");
       selector = $(target);
       //console.log("show ascending");
       selector.removeClass('glyphicon-sort-by-attributes-alt');
       selector.addClass('glyphicon-sort-by-attributes');
    }
    function showDescendingIcon(target){
       var selector = $("div.active .sortflip");
       //console.log("show descending");
       selector = $(target);
       selector.removeClass('glyphicon-sort-by-attributes');
       selector.addClass('glyphicon-sort-by-attributes-alt');
    }
 
    /* toggle the sort order for the selected element */
    function buildQuery(event=null){
      var active_form = $("#tabbed-forms div.active");
      if (event != null){ event.preventDefault();}
      var sort_order = readSortOrder();
      var sort_dict = { "sort" : sort_order };
      var jsd = JSON.stringify(sort_dict);
      /* not the right sort order */
      console.log("building this sort order");
      console.log(jsd);
      active_form.find("[id$=sort_order]").attr('value', jsd);
      console.log("called build query");
    }


   //http://stackoverflow.com/questions/24152459/
   //how-to-swap-placement-of-two-elements-including-their-classes-ids-with-onclick
   function swapAdjacent(el0, el1) {
     var  active_form = $("#tabbed-forms div.active div.sort-controls");
     if ( (el0 == null) || (el1 == null) ){ return; }
     var i1 = el0.index; var i2 = el1.index;
     el0.parentNode.insertBefore(el1, el0);
     //take the value that's in the i1th sort order graphic, 
     //and put it into the i2th soirt order graphic and vice versa.
     //
     //CLEAN UP THE FOLLOWING CODE:
     var tempSwap = $("div.active .sortflip")[i1]; //pull the sort order out of this.
     console.log(tempSwap);
     tempSwap = $(tempSwap);
     console.log(tempSwap.attr('class'));
     var tempSwapClass = tempSwap.attr('class');
     var swapB =  $("div.active .sortflip")[i2];
     tempSwap.attr('class', $(swapB).attr('class')); 
     $(swapB).attr('class', tempSwapClass);
   }

   function check_for_end(to_swap){
       if (to_swap.length > 0){ return to_swap[0]; }
       return null;
   }

   //TODO need to make the sort order graphics reflect the change in order.
   function priorityChange(event, up_or_down){
      event.preventDefault();
      var  active_form = $("#tabbed-forms div.active div.sort-controls");
      var selected = active_form.find(".sort-select").find(":selected");
      if (selected.length == 0){
        return; 
      }
      selected = selected[0];
      console.log("selected");
      console.log(selected);
      var index_of_selected = $(selected).index(); //gives index of selected element prior to move.
      var index_of_swapped;
      var to_swap;
      if (up_or_down == 'down'){ 
        index_of_swapped = index_of_selected + 1;
        console.log("index of downswapped " + index_of_swapped);
        to_swap = check_for_end(active_form.find(".sort-select").find(":selected").next());
        swapAdjacent(selected, to_swap); 
      } else {
        index_of_swapped = index_of_selected - 1;
        console.log("index of upswapped " + index_of_swapped);
        to_swap = check_for_end(active_form.find(".sort-select").find(":selected").prev());
        swapAdjacent(to_swap, selected); 
      }
     //update the query
     buildQuery();
   }
 
   /* Read the order of elements in the sort control */
   function readSortOrder(){
     var active_form = $("#tabbed-forms div.active div.sort-controls");
     var opts =  active_form.find(".sort-select").children();
     var sort_order = [];
     var flippers = $("div.active .sortflip"); /*this isn't pretty, but it works!*/
     for ( var i = 0; i < opts.length; i++){
       var key_for_term = opts[i].value;
       var order_for_term = $(opts[i]).attr("direction"); 
       /* these attributes aren't being changed */
       if ( $(flippers[i]).hasClass('glyphicon-sort-by-attributes') ){
           order_for_term = 'asc'; }else{
           order_for_term = 'desc'; }
       var d = {};
       d[key_for_term] = { 'order' : order_for_term };  
      sort_order.push(d);
     }
     return sort_order;
   }
 
   function check_for_end(to_swap){
       if (to_swap.length > 0){ return to_swap[0]; }
       return null;
   }
 
