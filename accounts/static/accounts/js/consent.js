$(document).ready(function () {
    const form = $('#consentForm');
    const checkAll = $('#checkAll');
    const checkBoxes = $('input[name="agreement"]');
    const submitButton = $('input[type="button"]');


    const agreements = {
        termsOfService: false,
        privacyPolicy: false,
        allowPromotions: false,
    };

    checkBoxes.on('change', function () {
        const id = $(this).attr('id');
        agreements[id] = $(this).prop('checked');
        toggleCheckboxClass(this);
        checkAll.prop('checked', areAllChecked());
        toggleSubmitButton();
    });

    function toggleCheckboxClass(checkbox) {
        const isChecked = $(checkbox).prop('checked');
        $(checkbox).closest('.input_check').toggleClass('active', isChecked);
    }

    function areAllChecked() {
        return Object.values(agreements).every(val => val);
    }

    function toggleSubmitButton() {
        var submitButton = $('#submitButton');
        if (!agreements.termsOfService || !agreements.privacyPolicy) {
            submitButton.prop('disabled', true);
            submitButton.css('background-color', '#fff');
            submitButton.css('color', '#007bff');
        } else if (agreements.termsOfService || agreements.privacyPolicy) {
            submitButton.prop('disabled', false);
            submitButton.css('background-color', '#007bff');
            submitButton.css('color', '#fff');
        }
    }

    checkAll.on('change', function () {
        const isChecked = $(this).prop('checked');
        checkBoxes.prop('checked', isChecked).each(function () {
            const id = $(this).attr('id');
            agreements[id] = isChecked;
            toggleCheckboxClass(this);
        });
        toggleSubmitButton();
    });
});

function test(url) {
    // if (!$("#termsOfService").is(":checked")) {
    //     alert("이용약관 동의는 필수입니다.");
    //     return false;
    // } else if (!$("#privacyPolicy").is(":checked")) {
    //     alert("개인정보 수집 및 이용 동의는 필수입니다.");
    //     return false;
    // }
    if (!$("#termsOfService").is(":checked") ||!$("#privacyPolicy").is(":checked") ) {
        alert("개인정보 수집 및 이용과 이용약관 동의는 필수입니다.");
        return false;
    }
    location.href = url
}

