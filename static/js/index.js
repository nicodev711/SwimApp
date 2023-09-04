$(document).ready(function() {
    // Function to toggle btn-sm class based on screen width
    function toggleButtonSize() {
        if ($(window).width() <= 767) { // Mobile screen width
            $('#searchButton').addClass('btn-sm');
        } else {
            $('#searchButton').removeClass('btn-sm');
        }
    }
    // Function to change heading level based on screen width
    function adjustTitleSize() {
        const title = $('.hereos h4');
        if ($(window).width() <= 767) { // Mobile screen width
            title.replaceWith('<h5 class="hereos-city">' + title.html() + '</h5>');
        } else {
            title.replaceWith('<h4 class="hereos-city">' + title.html() + '</h4>');
        }
    }

    // Initial toggle on page load
    toggleButtonSize();
    adjustTitleSize();

    // Toggle button size on window resize
    $(window).resize(function() {
        toggleButtonSize();
        adjustTitleSize();
    });
});