(function () {
  "use strict";

  /* ---------- Copy code block ---------- */
  var copyBtn = document.querySelector(".code-copy");
  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var pre = document.querySelector(copyBtn.getAttribute("data-copy"));
      var text = pre ? pre.textContent : "";
      var done = function () {
        copyBtn.textContent = "copied ✓";
        copyBtn.classList.add("copied");
        setTimeout(function () {
          copyBtn.textContent = "copy";
          copyBtn.classList.remove("copied");
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done).catch(done);
      } else {
        done();
      }
    });
  }

  /* ---------- Mobile menu ---------- */
  var menuBtn = document.getElementById("menu-toggle");
  var navLinks = document.querySelector(".nav-links");
  if (menuBtn && navLinks) {
    menuBtn.addEventListener("click", function () {
      navLinks.classList.toggle("open");
    });
    navLinks.addEventListener("click", function (e) {
      if (e.target.tagName === "A") navLinks.classList.remove("open");
    });
  }

  /* ---------- Animated counters ---------- */
  var counters = document.querySelectorAll(".stat-num[data-count]");
  var counted = false;
  function animateCounters() {
    if (counted) return;
    counted = true;
    counters.forEach(function (el) {
      var target = parseInt(el.getAttribute("data-count"), 10);
      var start = null;
      var dur = 900;
      function step(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        el.textContent = Math.floor(p * target);
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = target;
      }
      requestAnimationFrame(step);
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var cards = document.querySelectorAll(".card, .terminal, .code-block, details");
  cards.forEach(function (el) { el.classList.add("reveal"); });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) {
        en.target.classList.add("visible");
        io.unobserve(en.target);
      }
    });
  }, { threshold: 0.12 });

  cards.forEach(function (el) { io.observe(el); });

  var statsEl = document.getElementById("stats");
  if (statsEl && "IntersectionObserver" in window) {
    var statsObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { animateCounters(); statsObs.disconnect(); }
      });
    }, { threshold: 0.4 });
    statsObs.observe(statsEl);
  } else {
    animateCounters();
  }
})();
