﻿$(() => {
  $input_radio = $('input[type=radio]');
  $input_radio_checked = $input_radio.filter(':checked');

  $input_radio_checked
    .parents('.alternativa').addClass('selected');

  $input_radio_checked.filter(':disabled')
    .parents('.alternativa').addClass('sent').removeClass('cursor-pointer')
      .siblings('.alternativa').removeClass('cursor-pointer');

  $input_radio.change((e) => {
    $(e.target).parents('.alternativa').addClass('selected')
      .siblings('.selected').removeClass('selected')
  }).parents('.form-control, .alternativa').each((i, el) => {
    $(el).click((e) => {
      if (e.target !== el)
        return;
      $input = $(e.target).find('input');
      if ($input.is(':disabled'))
        return;
      name = $input.attr('name');
      $('input[name='+name+']:checked')
        .prop('checked', false)
      $input
        .prop('checked', true)
        .change();
    });
  });
});