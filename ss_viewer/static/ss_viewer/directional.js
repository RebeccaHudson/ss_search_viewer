function writeBothCutoffDirections(){
   var active_form = $("#shared_controls");
   var btn_selector  = 'button[name=pvalue_snp]';
   var valueToWrite = active_form.find(btn_selector).attr('value'); 
   writeCutoffDirection(valueToWrite, 'pvalue_snp');
   btn_selector  = 'button[name=pvalue_ref]';
   valueToWrite = active_form.find(btn_selector).attr('value'); 
   writeCutoffDirection(valueToWrite, 'pvalue_ref');
}

function switchDirection(event){
    event.preventDefault(); /* avoid form submission */
    var target = $(event.target);
    var direction_value = null;
    if (target.attr('value') == 'lte'){
      direction_value = 'gt';
      target.text('\u003E');
    } else { 
      direction_value = 'lte';
      target.text("\u2264");
    }
      target.attr('value', direction_value);
      writeCutoffDirection(direction_value, target.attr('name'));
} 

function writeCutoffDirection(direction_value, button_name){ 
    var active_form = $("#shared_controls"); 
    var id_for_hidden_field = button_name + '_direction';
    var hidden_field_selector = '[id$=' + id_for_hidden_field + ']';
    var field_to_write = active_form.find(hidden_field_selector);
    field_to_write.attr('value', direction_value);
}
