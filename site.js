// Shared behaviour for all pages. Each part only runs on pages that have the elements it needs.

// Collapse long author lists; the full list stays visible without JavaScript.
document.querySelectorAll("span.authors").forEach(function (el) {
  var toggle = el.querySelector(".toggle");
  var more = toggle.textContent;
  el.classList.add("collapsible", "collapsed");
  toggle.setAttribute("role", "button");
  toggle.setAttribute("aria-expanded", "false");
  toggle.addEventListener("click", function (e) {
    e.preventDefault();
    var collapsed = el.classList.toggle("collapsed");
    toggle.textContent = collapsed ? more : "[show less]";
    toggle.setAttribute("aria-expanded", String(!collapsed));
  });
});

// Match the photo height to the text next to it.
function fitPhoto() {
  var photo = document.querySelector("img.photo");
  if (!photo) {
    return;
  }
  var cell = photo.parentNode.nextElementSibling;
  var paragraphs = cell.getElementsByTagName("p");
  var top = cell.getElementsByTagName("name")[0].getBoundingClientRect().top;
  var bottom = paragraphs[paragraphs.length - 1].getBoundingClientRect().bottom;
  photo.style.height = Math.round(bottom - top) + "px";
}
window.addEventListener("load", fitPhoto);
if (document.fonts && document.fonts.ready) {
  document.fonts.ready.then(fitPhoto);
}

// Highlight the section currently on screen in the top bar.
var navLinks = document.querySelectorAll("div.topbar nav.sections a");
var clickedLink = null;
var settleTimer = null;

function setActive(link) {
  for (var i = 0; i < navLinks.length; i++) {
    navLinks[i].classList.toggle("on", navLinks[i] === link);
  }
}

function sectionOnScreen() {
  var current = null;
  for (var i = 0; i < navLinks.length; i++) {
    var section = document.getElementById(navLinks[i].getAttribute("href").slice(1));
    if (section.getBoundingClientRect().top <= window.innerHeight * 0.3) {
      current = navLinks[i];
    }
  }
  var page = document.scrollingElement || document.documentElement;
  if (navLinks.length && page.scrollTop + window.innerHeight >= page.scrollHeight - 2) {
    current = navLinks[navLinks.length - 1];
  }
  return current;
}

// A clicked section stays highlighted until its scroll has finished, even if the page
// cannot scroll far enough to bring that section to the top.
function holdClicked() {
  clearTimeout(settleTimer);
  settleTimer = setTimeout(function () {
    clickedLink = null;
  }, 200);
}

if (navLinks.length) {
  for (var k = 0; k < navLinks.length; k++) {
    navLinks[k].addEventListener("click", function () {
      clickedLink = this;
      setActive(clickedLink);
      holdClicked();
    });
    if (navLinks[k].getAttribute("href") === location.hash) {
      clickedLink = navLinks[k];
    }
  }

  window.addEventListener("scroll", function () {
    if (clickedLink) {
      holdClicked();
    } else {
      setActive(sectionOnScreen());
    }
  }, { passive: true });
  window.addEventListener("resize", function () {
    if (!clickedLink) {
      setActive(sectionOnScreen());
    }
  });
  setActive(clickedLink || sectionOnScreen());
  if (clickedLink) {
    holdClicked();
  }
}
