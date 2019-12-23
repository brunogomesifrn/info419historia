format_all_checkboxes = function($parent){
  $parent.find($('.form-group:has(input[type="checkbox"])')).each((i, el) => {
      format_checkboxes($(el))
  });
}

format_checkboxes = function($parent_div, show_all=false) {
  var $checked = $(),
      $not_checked = $(),
      $filtrar = $parent_div.find('input[type="text"]'),
      $mais = $parent_div.find('div.mais').hide(),
      $menos = $parent_div.find('div.menos').hide(),
      $checkboxes_divs = $parent_div.find('.form-control:has(input[type="checkbox"])').hide();
  if ($filtrar.length && $filtrar.val()) {
    $checkboxes_divs = $checkboxes_divs.filter(function(){
      return $(this).text().toLowerCase().indexOf($filtrar.val().toLowerCase()) !== -1
    });
  }
  $checkboxes_divs.each((j, el) => {
    var $div = $(el),
        $input = $div.find('input'),
        checked = $input.is(':checked');
    if (!$div[0].hasAttribute('formated')) {
      $div.attr('formated', '')
      $div.click(function(e) {
          checked = $(this).find('input').is(':checked')
          $input.prop('checked', !checked).change();
      });
      $input.change(function(e) {
        format_checkboxes($parent_div, show_all)
      });
    }
    if (checked)
      $checked = $checked.add($div)
    else
      $not_checked = $not_checked.add($div)
  });
  quant = $checkboxes_divs.length;
  if (quant > 8){
    if (show_all){
      if (!$menos.length) {
        $menos = $('<div class="form-control cursor-pointer menos">Menos <i class="fas fa-caret-up"></i></div>').click(function(e){
          format_checkboxes($parent_div);
        });
      }
      $checkboxes_divs.show().last().after($menos.show());
    } else {
      $first = $checkboxes_divs.first();
      if (!$filtrar.length) {
        $filtrar = $('<input type="text" class="form-control" placeholder="Filtrar" />').keyup($.debounce(500, function(e) {
          format_checkboxes($parent_div, $show_all)
          $(this).focus()
        })).insertBefore($first);
      }
      if (!$mais.length) {
        $mais = $('<div class="form-control cursor-pointer mais">Mais <i class="fas fa-caret-down"></i></div>').click(function(e){
          format_checkboxes($parent_div, true);
        });
      }
      quantChecked = $checked.show().length;
      quant_not_checked = 8-quantChecked < 0? 0 : 8-quantChecked
      $not_checked_last = $not_checked.slice(0, quant_not_checked).show().last();
      $checked_last = $checked.last();
      $last = $checkboxes_divs.index($checked_last) > $checkboxes_divs.index($not_checked_last)?
              $checked_last :
              $not_checked_last;
      $last.after($mais.show())
    }
  } else
    $checkboxes_divs.show()
}
$(() => {
    format_all_checkboxes($('body'))
});