/* Controls the behavior of the sort-widget found 
 * in templates/ss_viewer/sort-widget.html */

    jQuery(document).ready(function ($) {
      var sort_order = readSortOrder();
      buildQuery();

      $(".sortflip").on('click', function(){
         //Flips the sort order of the adjacent field in the select control.
         var selected_field = $("#shared_controls .sort-select option");

         if ($(this).hasClass('glyphicon-sort-by-attributes')){
             showDescendingIcon(this);
             selected_field.attr('direction', 'desc'); 
         }else{ 
             showAscendingIcon(this);
             selected_field.attr('direction', 'asc'); 
         }    
          buildQuery();
      }); 
    } );//end of document.ready stuff here.

    function showAscendingIcon(target){
       var selector = $("#shared_controls  .sortflip");
       selector = $(target);
       selector.removeClass('glyphicon-sort-by-attributes-alt');
       selector.addClass('glyphicon-sort-by-attributes');
    }

    function showDescendingIcon(target){
       var selector = $("#shared_controls  .sortflip");
       selector = $(target);
       selector.removeClass('glyphicon-sort-by-attributes');
       selector.addClass('glyphicon-sort-by-attributes-alt');
    }
 
    /* toggle the sort order for the selected element */
    function buildQuery(event=null){
      var active_form = $("#shared_controls");
      if (event != null){ event.preventDefault();}
      var sort_order = readSortOrder();
      var sort_dict = { "sort" : sort_order };

      var jsd = JSON.stringify(sort_dict);  
      
      /*console.log("building this sort order");
      console.log(jsd);*/
      active_form.find("[id$=sort_order]").attr('value', jsd);
    }


   //http://stackoverflow.com/questions/24152459/
   //how-to-swap-placement-of-two-elements-including-their-classes-ids-with-onclick
   function swapAdjacent(el0, el1) {
     var  active_form = $("#shared_controls  div.sort-controls");

     if ( (el0 == null) || (el1 == null) ){ return; }
     var i1 = el0.index; var i2 = el1.index;
     el0.parentNode.insertBefore(el1, el0);
     //take the value that's in the i1th sort order graphic, 
     //and put it into the i2th soirt order graphic and vice versa.
     
     var tempSwap = $("#shared_controls .sortflip")[i1];
     tempSwap = $(tempSwap);
     var tempSwapClass = tempSwap.attr('class');

     var swapB =  $("#shared_controls .sortflip")[i2];
     tempSwap.attr('class', $(swapB).attr('class')); 
     $(swapB).attr('class', tempSwapClass);
   }

   function check_for_end(to_swap){
       if (to_swap.length > 0){ return to_swap[0]; }
       return null;
   }

   function priorityChange(event, up_or_down){
      console.log("called priorityChange");
      event.preventDefault();
      var  active_form = $("#shared_controls div.sort-controls");
      var selected = active_form.find(".sort-select").find(":selected");
      if (selected.length == 0){
        return; 
      }
      selected = selected[0];
      var index_of_selected = $(selected).index(); //index of selected element prior to move.
      var index_of_swapped;
      var to_swap;
      if (up_or_down == 'down'){ 
        index_of_swapped = index_of_selected + 1;
        to_swap = check_for_end(active_form.find(".sort-select").find(":selected").next());
        swapAdjacent(selected, to_swap); 
      } else {
        index_of_swapped = index_of_selected - 1;
        to_swap = check_for_end(active_form.find(".sort-select").find(":selected").prev());
        swapAdjacent(to_swap, selected); 
      }
     buildQuery();
   }
 
   /* Read the order of elements in the sort control */
   function readSortOrder(){
     var active_form = $('#shared_controls div.sort-controls');

     var opts =  active_form.find(".sort-select").children();
     var sort_order = [];
     var flippers = $("#shared_controls .sortflip");

     for ( var i = 0; i < opts.length; i++){
       var key_for_term = opts[i].value;
       var order_for_term = $(opts[i]).attr("direction"); 
       if ( $(flippers[i]).hasClass('glyphicon-sort-by-attributes') ){
           order_for_term = 'asc';  }else{
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
 
