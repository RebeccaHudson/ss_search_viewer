/* Controls the behavior of the sort-widget found 
 * in templates/ss_viewer/sort-widget.html */

/* try to parameterize the ids of each of the select functions.*/

    jQuery(document).ready(function ($) {
      var sort_order = readSortOrder();
      buildQuery();
      console.log("initial sort order: "); 
      console.log(sort_order);

    $('.sort-order-select option').on('click', function(){
    console.log("clicked!");
        if ( $(this).attr('value') == 'asc' ){
          $(this).attr('value', 'desc');   
          $(this).text('descending');
        }else {
          $(this).attr('value', 'asc');   
          $(this).text('ascending');
        }
      buildQuery();
    });
  


    } );
  
    /* toggle the sort order for the selected element */
    //var  active_form = $("#tabbed-forms div.active div.sort-controls");

    function buildQuery(event=null){
      var active_form = $("#tabbed-forms div.active");
      if (event != null){ event.preventDefault();}
      var sort_order = readSortOrder();
      var sort_dict = { "sort" : sort_order };
      var jsd = JSON.stringify(sort_dict);
      //$("#id_sort_order").attr('value', jsd);
      console.log("buildQuery has written : " + jsd);
      //active_form.find("#id_sort_order").attr('value', jsd);
      active_form.find("[id$=sort_order]").attr('value', jsd);
      //$("#id_sort_order").attr('value', jsd);
      //$("#id_sort_order").attr('value', jsd);
    }

   //http://stackoverflow.com/questions/24152459/
   //how-to-swap-placement-of-two-elements-including-their-classes-ids-with-onclick
   function swapAdjacent(el0, el1) {
     var  active_form = $("#tabbed-forms div.active div.sort-controls");
     if ( (el0 == null) || (el1 == null) ){ return; }
     var i1 = el0.index; var i2 = el1.index;
     el0.parentNode.insertBefore(el1, el0);
     //swap the orders too; pull the indices from the others.
     var a = active_form.find(".sort-order-select")[0].children[i1];
     var b = active_form.find(".sort-order-select")[0].children[i2];
     //var a = $("#sort-order-select")[0].children[i1];
     //var b = $("#sort-order-select")[0].children[i2];
     a.parentNode.insertBefore(b, a);
   }

   function check_for_end(to_swap){
       if (to_swap.length > 0){ return to_swap[0]; }
       return null;
   }
 
   function priorityChange(event, up_or_down){
      event.preventDefault();
      var  active_form = $("#tabbed-forms div.active div.sort-controls");
      var selected = active_form.find(".sort-select").find(":selected");
      //var selected = $("#sort-select").find(":selected");
      if (selected.length == 0){
        return; 
      }
      selected = selected[0];
      var to_swap;
      if (up_or_down == 'down'){ 
        to_swap = check_for_end(active_form.find(".sort-select").find(":selected").next());
        swapAdjacent(selected, to_swap); 
      } else {
        to_swap = check_for_end(active_form.find(".sort-select").find(":selected").prev());
        swapAdjacent(to_swap, selected); 
      }
     //update the query
     buildQuery();
   }
 
   /* Read the order of elements in the sort control */
   function readSortOrder(){
     var active_form = $("#tabbed-forms div.active div.sort-controls");
     var  opts =  active_form.find(".sort-select").children();
     var sort_orders = active_form.find(".sort-order-select").children();
     var sort_order = [];
     for ( var i = 0; i < opts.length; i++){
       var key_for_term = opts[i].value;
       var order_for_term = sort_orders[i].value;
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
 