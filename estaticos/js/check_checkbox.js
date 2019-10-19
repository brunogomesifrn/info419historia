check_checkbox = () => {
  $('input[type=checkbox]').parents('.form-control').each((i, el)=> {
    $(el).click((e) => {
        if (e.target !== el)
          return;
        $input = $(e.target).find('input');
        checked = $input.is(':checked');
        $input.prop('checked', !checked);
    });
  });
}
$(() => {
    check_checkbox()
});