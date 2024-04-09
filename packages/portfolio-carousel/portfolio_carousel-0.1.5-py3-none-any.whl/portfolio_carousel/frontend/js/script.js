function ellipsizeTextBox(class_name) {
    var elements = document.getElementsByClassName(class_name);
    for(var i = 0; i < elements.length; i++) {
        var el = elements[i];
        var wordArray = el.innerHTML.split(' ');
        while(el.scrollHeight > el.offsetHeight) {
            wordArray.pop();
            el.innerHTML = wordArray.join(' ') + '...';
        }
    }
}
  
ellipsizeTextBox('description');

var swiper = new Swiper(".slide-content", {
    slidesPerView: 2,
    spaceBetween: 25,
    loop: true,
    centerSlide: true,
    fade: true,
    gragCursor: true,
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
      dynamicBullets: true,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },

    breakpoints:{
        0: {
            slidesPerView: 1,
        },
        520: {
            slidesPerView: 2,
        },
    },
  });

