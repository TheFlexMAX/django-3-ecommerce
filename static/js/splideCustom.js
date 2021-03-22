document.addEventListener( 'DOMContentLoaded', function () {
    let secondarySlider = new Splide( '#secondary-slider', {
        pagination : false,
        fixedWidth  : 60,
        height      : 60,
        gap         : 5,
        arrows      : false,
        cover       : false,
        isNavigation: true,
        focus       : 'center',
        breakpoints : {
            '600': {
                fixedWidth: 66,
                height    : 40,
            }
        },
    } ).mount();

    let primarySlider = new Splide( '#primary-slider', {
        type       : 'fade',
        heightRatio: 1,
        pagination : false,
        arrows     : true,
        arrowPath  : 'm',
        cover      : true,
        classes: {
            arrows: 'splide__arrows viewer__arrows',
            arrow : 'splide__arrow viewer__arrow',
            prev  : 'splide__arrow--prev viewer__arrow--prev',
            next  : 'splide__arrow--next viewer__arrow--next',
        },
    } ); // do not call mount() here.

    primarySlider.sync( secondarySlider ).mount();
} );
