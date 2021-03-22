let otslider = new OTSlider();
otslider.init({
    element : document.getElementById("main__slider"),
    direction : 'ltr',
    transition : 'slide',
    transitionTiming : 'ease',
    prevButton : '«',
    nextButton : '»',
    duration : 2000,
    transitionDuration : 500,
    autoPlay : true,
    pauseOnHover : true,
    showPrevNext : true,
    showNav : false,
    swipe : true,
    responsive : true,
    roundButtons : false,
    numericNav : true,
    itemsToShow : 1,
    itemsScrollBy : 1,
    padding : 0,
    teasing : 0,
    swipeFreely : false,
    centered : false
});

