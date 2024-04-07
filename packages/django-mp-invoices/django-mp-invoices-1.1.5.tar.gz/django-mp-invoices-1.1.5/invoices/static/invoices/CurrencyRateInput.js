
CurrencyRateInput = function (params) {

    var $container = params.$container,
        url = params.url;

    function handleChange() {
        $.post(
            url,
            {currency_rate: $(this).val()}
        ).done(function (response) {
            $.notify({message: response.message}, {type: 'success'});
        }).error(function (response) {
            $.notify({message: response.responseText}, {type: 'danger'});
        });
    }

    $container.on('change', handleChange);

};
