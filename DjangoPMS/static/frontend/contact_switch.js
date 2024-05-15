let currentSlideIndex = 0;

function nextSlide() {
  location.hash = "#slide" + currentSlideIndex;
  currentSlideIndex = (currentSlideIndex % 5) + 1;
}

setInterval(nextSlide, 3000);
