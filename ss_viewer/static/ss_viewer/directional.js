
function writeBothCutoffDirections(){
   var active_form = $("#tabbed-forms div.active");
   var btn_selector  = 'button[name=pvalue_snp]';
   var valueToWrite = active_form.find(btn_selector).attr('value'); 
   var btn_name = 'pvalue_snp';  
   writeCutoffDirection(valueToWrite, btn_name);
   btn_selector  = 'button[name=pvalue_ref]';
   valueToWrite = active_form.find(btn_selector).attr('value'); 
   btn_name = 'pvalue_ref';  
   writeCutoffDirection(valueToWrite, btn_name);
}


function switchDirection(event){
    event.preventDefault(); /* avoid form submission */
    var target = $(event.target);
    var direction_value = null;
    if (target.attr('value') == 'lt'){
      direction_value = 'gte';
      target.text('\u2265');
      /*TODO use the correct entity for this symbol*/
    } else { 
      direction_value = 'lt';
      target.text('<');
    }
      target.attr('value', direction_value);
      writeCutoffDirection(direction_value, target.attr('name'));
} 

function writeCutoffDirection(direction_value, button_name){ 
    var active_form = $("#tabbed-forms div.active"); 
    var id_for_hidden_field = button_name + '_direction';
    var hidden_field_selector = '[id$=' + id_for_hidden_field + ']';
    var field_to_write = active_form.find(hidden_field_selector);
    field_to_write.attr('value', direction_value);
}
